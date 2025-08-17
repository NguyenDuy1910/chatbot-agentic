import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.finx.internal.db import get_db
from backend.finx.models.connections import (
    Connection, ConnectionLog, ConnectionStatus,
    ConnectionCreateForm
)
from backend.finx.utils.connections import test_connection, create_connection_log
from backend.finx.utils.security import decrypt_credentials

log = logging.getLogger(__name__)

class HealthMonitor:
    """Background health monitoring for connections"""
    
    def __init__(self):
        self.is_running = False
        self.check_interval = 60  # Check every minute
        self.max_concurrent_checks = 10
        
    async def start_monitoring(self):
        """Start the health monitoring background task"""
        if self.is_running:
            log.warning("Health monitor is already running")
            return
        
        self.is_running = True
        log.info("Starting connection health monitoring")
        
        while self.is_running:
            try:
                await self.perform_health_checks()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                log.error(f"Error in health monitoring loop: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop the health monitoring"""
        self.is_running = False
        log.info("Stopping connection health monitoring")
    
    async def perform_health_checks(self):
        """Perform health checks for all active connections"""
        try:
            db = next(get_db())
            
            # Get connections that need health checks
            connections_to_check = self.get_connections_for_health_check(db)
            
            if not connections_to_check:
                return
            
            log.info(f"Performing health checks for {len(connections_to_check)} connections")
            
            # Process connections in batches to avoid overwhelming the system
            semaphore = asyncio.Semaphore(self.max_concurrent_checks)
            tasks = []
            
            for connection in connections_to_check:
                task = self.check_single_connection(db, connection, semaphore)
                tasks.append(task)
            
            # Wait for all health checks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            log.error(f"Error performing health checks: {str(e)}")
        finally:
            if 'db' in locals():
                db.close()
    
    def get_connections_for_health_check(self, db: Session) -> List[Connection]:
        """Get connections that need health checks"""
        now = datetime.utcnow()
        
        # Get active connections with health checks enabled
        connections = db.query(Connection).filter(
            and_(
                Connection.is_active == True,
                Connection.status.in_([ConnectionStatus.ACTIVE, ConnectionStatus.ERROR])
            )
        ).all()
        
        connections_to_check = []
        
        for connection in connections:
            health_check_config = connection.health_check or {}
            
            # Skip if health checks are disabled
            if not health_check_config.get('enabled', True):
                continue
            
            # Check if it's time for a health check
            interval_minutes = health_check_config.get('interval', 5)
            last_check = connection.last_health_check
            
            if not last_check:
                # Never checked before
                connections_to_check.append(connection)
            else:
                # Check if enough time has passed
                next_check_time = last_check + timedelta(minutes=interval_minutes)
                if now >= next_check_time:
                    connections_to_check.append(connection)
        
        return connections_to_check
    
    async def check_single_connection(self, db: Session, connection: Connection, semaphore: asyncio.Semaphore):
        """Perform health check for a single connection"""
        async with semaphore:
            try:
                # Decrypt credentials for testing
                decrypted_creds = decrypt_credentials(connection.credentials) if connection.credentials else {}
                
                # Create test form data
                test_data = ConnectionCreateForm(
                    name=connection.name,
                    type=connection.type,
                    config=connection.config or {},
                    credentials=decrypted_creds
                )
                
                # Perform the health check
                health_check_config = connection.health_check or {}
                test_endpoint = health_check_config.get('endpoint')
                test_method = health_check_config.get('method', 'GET')
                
                result = await test_connection(test_data, test_endpoint, test_method)
                
                # Update connection status based on result
                previous_status = connection.status
                
                if result.success:
                    connection.status = ConnectionStatus.ACTIVE
                    connection.last_connected = datetime.utcnow()
                    connection.success_count += 1
                    connection.last_error = None
                else:
                    connection.status = ConnectionStatus.ERROR
                    connection.error_count += 1
                    connection.last_error = result.error or result.message
                
                connection.last_health_check = datetime.utcnow()
                
                # Log status change if it occurred
                if previous_status != connection.status:
                    await create_connection_log(
                        db, str(connection.id), 
                        "info" if result.success else "error",
                        f"Health check status changed from {previous_status} to {connection.status}",
                        {"health_check_result": result.dict()}
                    )
                    
                    # Send notification for status changes
                    await self.send_status_change_notification(connection, previous_status, connection.status, result)
                
                # Log health check result
                await create_connection_log(
                    db, str(connection.id), 
                    "debug",
                    f"Health check completed: {result.message}",
                    {
                        "success": result.success,
                        "response_time": result.response_time,
                        "status_code": result.status_code
                    }
                )
                
                db.commit()
                
            except Exception as e:
                log.error(f"Error checking connection {connection.id}: {str(e)}")
                
                # Mark connection as error if health check fails
                connection.status = ConnectionStatus.ERROR
                connection.error_count += 1
                connection.last_error = f"Health check failed: {str(e)}"
                connection.last_health_check = datetime.utcnow()
                
                await create_connection_log(
                    db, str(connection.id), "error",
                    f"Health check failed with exception: {str(e)}",
                    {"exception": str(e)}
                )
                
                db.commit()
    
    async def send_status_change_notification(self, connection: Connection, old_status: str, new_status: str, result):
        """Send notification when connection status changes"""
        try:
            # This is where you would integrate with your notification system
            # For now, we'll just log the notification
            
            if new_status == ConnectionStatus.ERROR:
                log.warning(
                    f"Connection '{connection.name}' ({connection.id}) failed health check. "
                    f"Status changed from {old_status} to {new_status}. "
                    f"Error: {result.error or result.message}"
                )
                
                # You could send email, Slack notification, etc. here
                await self.send_error_notification(connection, result)
                
            elif new_status == ConnectionStatus.ACTIVE and old_status == ConnectionStatus.ERROR:
                log.info(
                    f"Connection '{connection.name}' ({connection.id}) recovered. "
                    f"Status changed from {old_status} to {new_status}."
                )
                
                # Send recovery notification
                await self.send_recovery_notification(connection, result)
                
        except Exception as e:
            log.error(f"Error sending status change notification: {str(e)}")
    
    async def send_error_notification(self, connection: Connection, result):
        """Send error notification (implement based on your notification system)"""
        # Placeholder for error notification logic
        # You could integrate with:
        # - Email service
        # - Slack/Teams webhooks
        # - SMS service
        # - Push notifications
        pass
    
    async def send_recovery_notification(self, connection: Connection, result):
        """Send recovery notification"""
        # Placeholder for recovery notification logic
        pass
    
    async def get_connection_health_summary(self, db: Session) -> Dict[str, Any]:
        """Get overall health summary of all connections"""
        try:
            total_connections = db.query(Connection).filter(Connection.is_active == True).count()
            active_connections = db.query(Connection).filter(
                and_(Connection.is_active == True, Connection.status == ConnectionStatus.ACTIVE)
            ).count()
            error_connections = db.query(Connection).filter(
                and_(Connection.is_active == True, Connection.status == ConnectionStatus.ERROR)
            ).count()
            
            # Get connections that haven't been checked recently
            stale_threshold = datetime.utcnow() - timedelta(hours=1)
            stale_connections = db.query(Connection).filter(
                and_(
                    Connection.is_active == True,
                    Connection.last_health_check < stale_threshold
                )
            ).count()
            
            # Calculate uptime percentage
            uptime_percentage = (active_connections / total_connections * 100) if total_connections > 0 else 100
            
            return {
                "total_connections": total_connections,
                "active_connections": active_connections,
                "error_connections": error_connections,
                "stale_connections": stale_connections,
                "uptime_percentage": round(uptime_percentage, 2),
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            log.error(f"Error getting health summary: {str(e)}")
            return {
                "error": "Failed to get health summary",
                "last_check": datetime.utcnow().isoformat()
            }

# Global health monitor instance
health_monitor = HealthMonitor()

# Convenience functions
async def start_health_monitoring():
    """Start the global health monitor"""
    await health_monitor.start_monitoring()

def stop_health_monitoring():
    """Stop the global health monitor"""
    health_monitor.stop_monitoring()

async def force_health_check(connection_id: str) -> bool:
    """Force a health check for a specific connection"""
    try:
        db = next(get_db())
        connection = db.query(Connection).filter(Connection.id == connection_id).first()
        
        if not connection:
            return False
        
        semaphore = asyncio.Semaphore(1)
        await health_monitor.check_single_connection(db, connection, semaphore)
        return True
        
    except Exception as e:
        log.error(f"Error forcing health check for {connection_id}: {str(e)}")
        return False
    finally:
        if 'db' in locals():
            db.close()

async def get_health_summary() -> Dict[str, Any]:
    """Get connection health summary"""
    try:
        db = next(get_db())
        return await health_monitor.get_connection_health_summary(db)
    except Exception as e:
        log.error(f"Error getting health summary: {str(e)}")
        return {"error": "Failed to get health summary"}
    finally:
        if 'db' in locals():
            db.close()
