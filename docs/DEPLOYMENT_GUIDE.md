# FinX Backend CI/CD Deployment Guide

This guide provides comprehensive instructions for setting up CI/CD pipeline for the FinX backend to deploy on VPS.

## 🗄️ Database Options

The FinX backend supports multiple database providers:

### 1. Supabase (Recommended for Production)
- Managed PostgreSQL with additional features
- Built-in authentication and real-time capabilities
- Automatic backups and scaling
- Easy setup and management

### 2. PostgreSQL (Self-managed)
- Full control over database configuration
- Suitable for on-premise deployments
- Requires manual backup and maintenance
- Included docker-compose configuration

### 3. Database Setup

#### Option A: Supabase Setup
1. Create a Supabase project at https://supabase.com
2. Get your project credentials from the dashboard
3. Update `.env` file with Supabase credentials

#### Option B: PostgreSQL Setup
1. Use the provided `docker-compose.postgres.yml`
2. Set strong passwords in environment variables
3. Configure backup strategy

```bash
# For PostgreSQL deployment
docker-compose -f docker-compose.postgres.yml up -d
```

## 🏗️ Architecture Overview

```
GitHub Repository
    ↓ (Push to main)
GitHub Actions CI/CD
    ↓ (Build, Test, Deploy)
VPS Server
    ↓ (Docker Container)
FinX Backend API
    ↓ (Database Connection)
Supabase/PostgreSQL Database
```

## 📋 Prerequisites

### Local Development
- Docker and Docker Compose
- Git
- Node.js (for frontend)
- Python 3.12+ (for backend development)

### VPS Server
- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose installed
- SSH access configured
- Domain name (optional but recommended)
- SSL certificate (for production)

### GitHub Repository
- Repository secrets configured
- Actions enabled

## 🔧 Setup Instructions

### 1. VPS Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create deployment directory
mkdir -p ~/finx-deployment
cd ~/finx-deployment

# Create logs and data directories
mkdir -p logs data

# Set permissions
sudo chown -R $USER:$USER ~/finx-deployment
```

### 2. GitHub Secrets Configuration

Add the following secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

| Secret Name | Description | Example |
|------------|-------------|---------|
| `SSH_PRIVATE_KEY` | Private SSH key for VPS access | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `KNOWN_HOSTS` | Known hosts entry for your VPS | `your-vps-ip ssh-rsa AAAAB3NzaC1yc2E...` |
| `VPS_HOST` | VPS IP address or domain | `192.168.1.100` or `your-domain.com` |
| `VPS_USER` | SSH username for VPS | `ubuntu` or `root` |
| `VPS_PATH` | Deployment path on VPS | `/home/ubuntu/finx-deployment` |

#### Database Secrets (choose one option):

**For Supabase:**
| Secret Name | Description | Example |
|------------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://your-project.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anon key | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |

**For PostgreSQL:**
| Secret Name | Description | Example |
|------------|-------------|---------|
| `POSTGRES_PASSWORD` | PostgreSQL password | `your-secure-password` |

#### Test Database Secrets:
| Secret Name | Description |
|------------|-------------|
| `TEST_SUPABASE_URL` | Test Supabase project URL |
| `TEST_SUPABASE_ANON_KEY` | Test Supabase anon key |
| `TEST_SUPABASE_SERVICE_ROLE_KEY` | Test Supabase service role key |

#### Optional Registry Secrets (for private Docker registry):
| Secret Name | Description |
|------------|-------------|
| `DOCKER_REGISTRY_URL` | Docker registry URL |
| `DOCKER_REGISTRY_USERNAME` | Registry username |
| `DOCKER_REGISTRY_PASSWORD` | Registry password |

### 3. Environment Configuration

Create `.env` file on your VPS:

```bash
# On VPS
cd ~/finx-deployment
cp .env.example .env
nano .env
```

Update the environment variables according to your production needs.

## 🚀 Deployment Process

The CI/CD pipeline consists of three main jobs:

### 1. Test Job
- Runs on every push and pull request
- Sets up Python environment
- Installs dependencies
- Runs linting (black, isort, flake8)
- Runs security scanning (safety, bandit)
- Executes tests with coverage
- Uploads coverage reports

### 2. Build Job
- Runs only on pushes to main/develop
- Builds Docker image
- Tests the built image
- Optionally pushes to Docker registry
- Creates image artifact

### 3. Deploy Job
- Runs only on pushes to main branch
- Downloads built image
- Transfers files to VPS via SSH
- Deploys using Docker Compose
- Performs health checks
- Runs post-deployment tests

## 📊 Monitoring and Logs

### Health Check Endpoints
- **Health**: `http://your-domain.com/health`
- **API Docs**: `http://your-domain.com/docs`

### Viewing Logs
```bash
# On VPS
cd ~/finx-deployment

# View container logs
docker-compose logs -f backend

# View system logs
journalctl -u docker -f
```

### Container Management
```bash
# Check status
docker-compose ps

# Restart services
docker-compose restart backend

# Update deployment
./deploy.sh production

# Shell access
docker-compose exec backend bash

# Resource usage
docker stats finx-backend
```

## 🔒 Security Considerations

1. **Environment Variables**: Never commit sensitive data to repository
2. **SSH Keys**: Use dedicated deployment keys with minimal permissions
3. **Firewall**: Configure UFW or iptables to restrict access
4. **SSL/TLS**: Always use HTTPS in production
5. **Updates**: Regularly update system and dependencies
6. **Backups**: Implement database and file backups
7. **Monitoring**: Set up log monitoring and alerting

### Firewall Configuration
```bash
# Basic UFW setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8000  # For direct backend access
sudo ufw enable
```

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**
   - Check GitHub Actions logs
   - Verify requirements.txt is up to date
   - Ensure tests are passing locally

2. **Deployment Failures**
   - Verify SSH connection and permissions
   - Check VPS disk space and memory
   - Review container logs

3. **Health Check Failures**
   - Verify environment variables
   - Check database connectivity
   - Review application logs

4. **Backend Connection Issues**
   - Verify backend is running on port 8000
   - Check firewall settings
   - Review container logs

### Debug Commands
```bash
# Test SSH connection
ssh -i ~/.ssh/your-key user@your-vps "echo 'Connection successful'"

# Test Docker
docker run hello-world

# Test application locally
cd deployment
docker-compose up backend

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep finx
```

## 📈 Performance Optimization

1. **Docker Image Size**
   - Use multi-stage builds
   - Minimize layers
   - Use .dockerignore

2. **Application Performance**
   - Enable database connection pooling
   - Configure appropriate worker processes
   - Use Redis for caching (optional)

3. **Server Performance**
   - Configure appropriate resource limits for containers
   - Enable compression at application level
   - Set appropriate resource limits

## 🔄 Rollback Procedure

If deployment fails or issues are detected:

```bash
# On VPS
cd ~/finx-deployment

# Stop current deployment
docker-compose down

# Revert to previous image (if available)
docker tag finx-backend:previous finx-backend:latest

# Start with previous version
docker-compose up -d backend

# Verify health
curl -f http://localhost:8000/health
```

## 📧 Support and Maintenance

- **Logs**: Monitor application and system logs daily
- **Updates**: Plan regular maintenance windows for updates
- **Backups**: Implement automated backup strategies
- **Monitoring**: Set up uptime monitoring and alerting
- **Documentation**: Keep deployment documentation updated

## 🎯 Next Steps

1. Set up monitoring with tools like Prometheus/Grafana
2. Implement automated backups
3. Configure log aggregation (ELK stack)
4. Set up staging environment
5. Implement blue-green deployments
6. Add performance monitoring
7. Set up alerting for critical issues

For additional support or questions, refer to the project documentation or contact the development team.
