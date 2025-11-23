# Enterprise MCP Server

A production-ready Model Context Protocol (MCP) server with multiple free API integrations for weather, IP geolocation, dictionary lookups, and currency exchange rates.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [AWS EC2 Deployment](#aws-ec2-deployment)
- [Configuration](#configuration)
- [API Tools](#api-tools)
- [Development](#development)
- [Documentation](#documentation)

## Features

### 🌟 Enterprise-Grade Architecture

- **Multi-Stage Docker Builds**: Optimized with UV package manager for fast builds
- **Nginx Reverse Proxy**: Production-ready with SSL/TLS support
- **YAML Configuration**: Type-safe configuration with Pydantic validation
- **Structured Logging**: JSON and text logging with file rotation
- **Error Handling**: Comprehensive error handling with custom exceptions and retry logic
- **Type Safety**: Full type hints throughout the codebase
- **Extensible**: Easy to add new tools using base classes

### 🛠️ Free API Tools (No API Keys Required)

1. **Weather Information** (`get_weather`)

   - Current weather conditions for any location
   - Temperature, humidity, wind speed, pressure, etc.
   - Powered by wttr.in

2. **IP Geolocation** (`get_ip_info`)

   - Geolocation data for any IP address
   - City, country, timezone, coordinates
   - ISP and network information
   - Powered by ipapi.co

3. **Dictionary Lookup** (`lookup_word`)

   - Word definitions, pronunciations, and examples
   - Parts of speech, synonyms, and antonyms
   - Powered by Free Dictionary API

4. **Currency Exchange Rates** (`get_exchange_rate`)
   - Real-time exchange rates for 160+ currencies
   - Currency conversion
   - Powered by exchangerate-api.com

## Project Structure

```
first_try_mcp/
├── src/
│   ├── servers/
│   │   └── http_server.py     # Main MCP server
│   ├── clients/
│   │   └── http_client.py     # Test client
│   ├── config/
│   │   └── settings.py        # YAML configuration loader
│   ├── tools/
│   │   ├── base.py            # Base tool classes
│   │   ├── weather.py         # Weather tool
│   │   ├── ip_info.py         # IP geolocation tool
│   │   ├── dictionary.py      # Dictionary tool
│   │   └── exchange_rate.py   # Exchange rate tool
│   └── utils/
│       ├── logger.py          # Logging utilities
│       ├── http_client.py     # HTTP client with retry
│       └── exceptions.py      # Custom exceptions
├── tests/
│   └── test_tools.py          # Unit tests
├── docs/
│   ├── API.md                 # API documentation
│   ├── GETTING_STARTED.md     # Getting started guide
│   ├── DOCKER.md              # Docker deployment guide
│   └── REFACTORING_SUMMARY.md # Refactoring notes
├── nginx/
│   ├── nginx.conf             # Main Nginx config
│   ├── conf.d/                # Server configurations
│   └── README.md              # Nginx setup guide
├── Dockerfile                 # Multi-stage Dockerfile
├── Dockerfile.prod            # Production Dockerfile
├── docker-compose.yml         # Development compose
├── docker-compose.prod.yml    # Production compose
├── config.yaml                # Configuration file
├── pyproject.toml
├── Makefile
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.13+
- UV package manager (recommended) or pip
- Docker and Docker Compose (for containerized deployment)

### Local Development

```bash
# 1. Clone the repository
git clone <repository-url>
cd first_try_mcp

# 2. Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# 4. Copy and configure settings
cp config.yaml.example config.yaml
# Edit config.yaml as needed

# 5. Run the server
python -m src.servers.http_server

# 6. In another terminal, test the client
python -m src.clients.http_client
```

## Docker Deployment

### Development with Docker

```bash
# Build and start services
make docker-build
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

### Production with Docker

```bash
# Build and start production services
make docker-prod

# Stop production services
make docker-prod-down
```

### Manual Docker Commands

```bash
# Development
docker compose build
docker compose up -d

# Production
docker compose -f docker-compose.prod.yml up -d --build
```

## AWS EC2 Deployment

### Step 1: Launch EC2 Instance

1. **Login to AWS Console**

   - Navigate to https://console.aws.amazon.com
   - Sign in with your credentials

2. **Launch EC2 Instance**

   - Go to EC2 Dashboard
   - Click "Launch Instance"
   - **Name**: `mcp-server-prod`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: `t2.medium` (minimum recommended) or `t2.large` for better performance
   - **Key Pair**: Create new or select existing key pair (save `.pem` file securely)

3. **Configure Network Settings**

   - Create or select VPC
   - Enable "Auto-assign public IP"
   - **Security Group**: Create new security group with rules:
     - SSH (22) - Your IP only
     - HTTP (80) - 0.0.0.0/0
     - HTTPS (443) - 0.0.0.0/0
     - Custom TCP (8000) - Your IP only (for direct server access)

4. **Configure Storage**

   - **Root Volume**: 20 GB GP3 (minimum)
   - Recommended: 30 GB for logs and data

5. **Launch Instance**
   - Click "Launch Instance"
   - Wait for instance state to be "running"

### Step 2: Connect to EC2 via SSH

```bash
# Change permissions on your key pair file
chmod 400 your-key-pair.pem

# Connect to EC2 instance
ssh -i your-key-pair.pem ubuntu@<EC2-PUBLIC-IP>
```

### Step 3: Install Dependencies on EC2

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose -y

# Install Git
sudo apt install git -y

# Install UV (optional, for local development)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Logout and login again to apply docker group changes
exit
```

**Reconnect to EC2:**

```bash
ssh -i your-key-pair.pem ubuntu@<EC2-PUBLIC-IP>
```

### Step 4: Deploy Application

```bash
# Clone your repository
git clone <your-repository-url>
cd first_try_mcp

# Copy and configure settings
cp config.yaml.example config.yaml
nano config.yaml  # Edit configuration as needed

# For production, update server_host in config.yaml:
# server:
#   host: "0.0.0.0"
#   port: 8000

# Build and start services
docker compose -f docker-compose.prod.yml up -d --build

# Check if services are running
docker ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### Step 5: Configure Domain and SSL (Optional)

#### Option A: Using Let's Encrypt for SSL

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Stop Nginx container temporarily
docker compose -f docker-compose.prod.yml stop nginx

# Generate SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to project
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
sudo chown ubuntu:ubuntu nginx/ssl/*.pem

# Update Nginx configuration
cd nginx/conf.d
cp mcp-server-ssl.conf.example mcp-server-ssl.conf
nano mcp-server-ssl.conf  # Update server_name to your domain

# Restart services
docker compose -f docker-compose.prod.yml up -d
```

#### Option B: Using AWS Route 53 for DNS

1. **Register Domain** in Route 53 or use existing domain
2. **Create Hosted Zone** for your domain
3. **Create A Record** pointing to EC2 Public IP
4. **Wait for DNS propagation** (5-30 minutes)
5. **Follow Option A** to set up SSL certificate

### Step 6: Verify Deployment

```bash
# Test from EC2 instance
curl http://localhost/health

# Test from your local machine
curl http://<EC2-PUBLIC-IP>

# Test MCP server (if port 8000 is open)
curl http://<EC2-PUBLIC-IP>:8000/mcp
```

### Step 7: Set Up Auto-Start on Reboot

```bash
# Create systemd service
sudo nano /etc/systemd/system/mcp-server.service
```

Add the following content:

```ini
[Unit]
Description=MCP Server Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/first_try_mcp
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
User=ubuntu

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable mcp-server

# Start service
sudo systemctl start mcp-server

# Check status
sudo systemctl status mcp-server
```

### Step 8: Monitor and Maintain

```bash
# View application logs
docker compose -f docker-compose.prod.yml logs -f mcp-server

# View Nginx logs
docker compose -f docker-compose.prod.yml logs -f nginx

# Monitor resource usage
docker stats

# Update application
cd /home/ubuntu/first_try_mcp
git pull
docker compose -f docker-compose.prod.yml up -d --build

# Clean up old images
docker system prune -a
```

### Security Best Practices for AWS Deployment

1. **SSH Access**

   - Only allow SSH from your IP address
   - Use strong key pairs
   - Consider using AWS Systems Manager Session Manager instead of SSH

2. **Firewall Rules**

   - Minimize open ports in Security Group
   - Use separate security groups for different services
   - Enable AWS WAF for DDoS protection

3. **SSL/TLS**

   - Always use HTTPS in production
   - Keep SSL certificates updated
   - Use strong cipher suites (configured in Nginx)

4. **Monitoring**

   - Enable CloudWatch monitoring
   - Set up alarms for high CPU/memory usage
   - Monitor application logs regularly

5. **Backups**

   - Create EC2 AMI snapshots regularly
   - Backup configuration files
   - Store logs in S3 or CloudWatch Logs

6. **Updates**
   - Keep system packages updated
   - Update Docker images regularly
   - Monitor security advisories

### Troubleshooting EC2 Deployment

**Cannot connect via SSH:**

```bash
# Check security group allows your IP on port 22
# Verify key pair permissions: chmod 400 your-key.pem
# Check instance public IP hasn't changed
```

**Docker containers not starting:**

```bash
# Check Docker service
sudo systemctl status docker

# View detailed logs
docker compose -f docker-compose.prod.yml logs

# Check disk space
df -h
```

**Port 80/443 not accessible:**

```bash
# Check security group rules in AWS Console
# Verify Nginx is running
docker ps | grep nginx

# Check Nginx logs
docker logs mcp-nginx
```

**Application errors:**

```bash
# Check server logs
docker logs mcp-server

# Verify config.yaml settings
cat config.yaml

# Restart services
docker compose -f docker-compose.prod.yml restart
```

## Configuration

## Configuration

The server uses YAML-based configuration with Pydantic validation. Copy `config.yaml.example` to `config.yaml` and customize:

```yaml
server:
  name: "Enterprise MCP Server"
  host: "0.0.0.0"
  port: 8000
  transport: "http"

logging:
  level: "INFO"
  format: "json" # json or text
  file: "logs/mcp_server.log"

api:
  request_timeout: 30
  max_retries: 3
  retry_delay: 1.0

features:
  enable_weather_tool: true
  enable_ip_info_tool: true
  enable_dictionary_tool: true
  enable_exchange_rate_tool: true

development:
  debug_mode: false
  environment: "development"
```

## API Tools

### Weather Information

```bash
# Using client
python -c "
from src.clients.http_client import MCPClient
import asyncio

async def get_weather():
    client = MCPClient()
    result = await client.call_tool('get_weather', {'location': 'Tokyo'})
    print(result)

asyncio.run(get_weather())
"
```

### IP Geolocation

```bash
# Current IP
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_ip_info", "arguments": {"ip_address": ""}}'

# Specific IP
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_ip_info", "arguments": {"ip_address": "8.8.8.8"}}'
```

### Dictionary Lookup

```python
result = await client.call_tool("lookup_word", {"word": "ephemeral"})
```

### Currency Exchange

```python
# Convert 100 USD to JPY
result = await client.call_tool("get_exchange_rate", {
    "base_currency": "USD",
    "target_currency": "JPY",
    "amount": 100
})
```

## Development

### Running Tests

```bash
# Install test dependencies
uv pip install pytest pytest-asyncio pytest-cov

# Run tests
make test

# With coverage
make test-coverage
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check
```

### Adding a New Tool

1. Create a new file in `src/tools/` (e.g., `my_tool.py`)
2. Inherit from `BaseTool` or `APIBasedTool`
3. Implement required methods
4. Register in `src/servers/http_server.py`

Example:

```python
from src.tools.base import APIBasedTool, ToolMetadata
from typing import Any, Dict

class MyTool(APIBasedTool):
    def __init__(self):
        super().__init__(base_url="https://api.example.com")

    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="my_tool",
            description="Does something awesome",
            version="1.0.0",
            requires_api_key=False,
        )

    def validate_input(self, **kwargs: Any) -> None:
        # Validate inputs
        pass

    async def execute(self, param: str, **kwargs: Any) -> Dict[str, Any]:
        # Implement tool logic
        url = self._build_url("/endpoint")
        async with HTTPClient() as client:
            data = await client.get(url)
        return data
```

## Documentation

- **[API Documentation](docs/API.md)**: Complete API reference
- **[Getting Started](docs/GETTING_STARTED.md)**: Detailed setup guide
- **[Docker Guide](docs/DOCKER.md)**: Docker deployment details
- **[Nginx Setup](nginx/README.md)**: Nginx configuration guide

## Makefile Commands

```bash
# Server management
make run              # Run the server
make run-server       # Run the server (alias)
make run-client       # Run the test client

# Docker commands
make docker-build     # Build Docker images
make docker-up        # Start containers
make docker-down      # Stop containers
make docker-logs      # View logs
make docker-restart   # Restart containers
make docker-ps        # List containers
make docker-clean     # Clean up containers and volumes
make docker-prod      # Start production containers
make docker-prod-down # Stop production containers

# Development
make test             # Run tests
make test-coverage    # Run tests with coverage
make format           # Format code
make lint             # Lint code
make clean            # Clean cache files
make install          # Install dependencies
```

## Monitoring and Logs

### View Logs

```bash
# Application logs (local)
tail -f logs/mcp_server.log

# Docker logs
docker logs mcp-server -f
docker logs mcp-nginx -f

# All services
docker compose logs -f
```

### Health Checks

```bash
# Check server health
curl http://localhost:8000/mcp

# Check via Nginx
curl http://localhost/
```

## Performance Tuning

### Docker Resources

Edit `docker-compose.prod.yml`:

```yaml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "1"
          memory: 1G
```

### Nginx Optimization

See `nginx/README.md` for detailed optimization guides including:

- Worker processes and connections
- Caching strategies
- Compression settings
- Rate limiting

## Troubleshooting

**Import warnings:**

```bash
# Ignore frozen runpy warnings, they don't affect functionality
python -W ignore::RuntimeWarning -m src.servers.http_server
```

**Port already in use:**

```bash
# Check what's using the port
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

**Docker build fails:**

```bash
# Clean Docker cache
docker builder prune -a

# Rebuild without cache
docker compose build --no-cache
```

**Rate limiting on free APIs:**

- IP Info API (ipapi.co): Limited to 1,000 requests/day
- Use specific IPs instead of current IP to reduce requests
- Consider upgrading to paid tier for production use

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests and linters
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:

- GitHub Issues: Create an issue
- Documentation: See `docs/` directory
- Email: support@example.com

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP framework
- [UV](https://github.com/astral-sh/uv) - Fast Python package installer
- [wttr.in](https://wttr.in) - Weather API
- [ipapi.co](https://ipapi.co) - IP Geolocation API
- [Free Dictionary API](https://dictionaryapi.dev) - Dictionary API
- [ExchangeRate-API](https://www.exchangerate-api.com) - Currency API
