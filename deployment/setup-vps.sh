#!/bin/bash

# FinX VPS Setup Script
# Run this script on your VPS to prepare it for deployment

set -e

echo " Setting up VPS for FinX Backend Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. It's recommended to run this script as a regular user with sudo privileges."
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated successfully"

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_success "Docker installed successfully"
else
    print_success "Docker is already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed successfully"
else
    print_success "Docker Compose is already installed"
fi

# Install additional useful tools
print_status "Installing additional tools..."
sudo apt install -y curl wget git htop nano vim ufw
print_success "Additional tools installed"

# Create deployment directory
DEPLOY_DIR="$HOME/finx-deployment"
print_status "Creating deployment directory at $DEPLOY_DIR..."
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

# Create necessary subdirectories
mkdir -p logs deployment

# Set permissions
sudo chown -R $USER:$USER "$DEPLOY_DIR"
print_success "Deployment directory created successfully"

# Configure firewall
print_status "Configuring UFW firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8000  # For direct backend access

print_warning "Firewall rules configured but not enabled yet. Run 'sudo ufw enable' to activate."

# Create basic environment file
print_status "Creating basic environment configuration..."
cat > "$DEPLOY_DIR/.env" << 'EOF'
# FinX Backend Production Environment
ENVIRONMENT=production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_RELOAD=false

# Database Configuration
DATABASE_PROVIDER=supabase

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here
SUPABASE_DB_URL=postgresql://postgres:your-password@db.your-project-id.supabase.co:5432/postgres

# Security Configuration
SECRET_KEY=change-this-super-secret-key-in-production
JWT_SECRET_KEY=change-this-jwt-secret-key-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
EOF

print_success "Basic environment file created"

# Create systemd service for easier management (optional)
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/finx-backend.service > /dev/null << EOF
[Unit]
Description=FinX Backend Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/local/bin/docker-compose up -d backend
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
print_success "Systemd service created"

# Create helpful aliases
print_status "Creating helpful aliases..."
cat >> "$HOME/.bashrc" << 'EOF'

# FinX Backend aliases
alias finx-logs='cd ~/finx-deployment && docker-compose logs -f backend'
alias finx-status='cd ~/finx-deployment && docker-compose ps'
alias finx-restart='cd ~/finx-deployment && docker-compose restart backend'
alias finx-shell='cd ~/finx-deployment && docker-compose exec backend bash'
alias finx-deploy='cd ~/finx-deployment && ./deploy.sh production'
alias finx-cd='cd ~/finx-deployment'
EOF

print_success "Helpful aliases added to .bashrc"

# Display summary
echo ""
echo "=========================================="
echo "VPS Setup Complete!"
echo "=========================================="
echo ""
echo "Deployment directory: $DEPLOY_DIR"
echo "Environment file: $DEPLOY_DIR/.env"
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker-compose --version)"
echo ""
echo "Next Steps:"
echo "1. Configure your GitHub repository secrets:"
echo "   - SSH_PRIVATE_KEY"
echo "   - KNOWN_HOSTS"
echo "   - VPS_HOST ($(hostname -I | awk '{print $1}'))"
echo "   - VPS_USER ($USER)"
echo "   - VPS_PATH ($DEPLOY_DIR)"
echo ""
echo "2. Update environment variables in: $DEPLOY_DIR/.env"
echo ""
echo "3. Enable firewall: sudo ufw enable"
echo ""
echo "4. Test SSH connection from GitHub Actions"
echo ""
echo "🔧 Useful commands:"
echo "   finx-logs      - View backend logs"
echo "   finx-status    - Check service status"
echo "   finx-restart   - Restart backend service"
echo "   finx-shell     - Access backend container shell"
echo "   finx-cd        - Go to deployment directory"
echo ""
echo "Your VPS is now ready for CI/CD deployment!"

# Final reminders
echo ""
print_warning "IMPORTANT REMINDERS:"
print_warning "1. Update the .env file with your production values"
print_warning "2. Change default secret keys in .env file"
print_warning "3. Configure proper CORS origins for production"
print_warning "4. Enable firewall: sudo ufw enable"
print_warning "5. Log out and log back in for Docker group membership to take effect"

echo ""
print_status "Setup completed successfully!"
