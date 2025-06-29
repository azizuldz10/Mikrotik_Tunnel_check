# 🔧 Setup Instructions

## 🔒 Privacy & Security Setup

This repository contains **example tunnel configurations** for demonstration purposes. Follow these steps to configure your real tunnels securely.

## 📋 Quick Setup

### **1. Clone Repository**
```bash
git clone https://github.com/azizuldz10/Mikrotik_Tunnel_check.git
cd Mikrotik_Tunnel_check
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Configure Your Tunnels**

#### **Option A: Copy Example Configuration**
```bash
# Copy example to create your config
cp config_example.json config.json

# Edit with your real tunnel details
nano config.json
```

#### **Option B: Create New Configuration**
```bash
# Create new config file
touch config.json
```

Then add your tunnel configuration:
```json
{
  "tunnels": [
    {
      "name": "YOUR_TUNNEL_NAME",
      "host": "your-tunnel-host.com",
      "port": 8080,
      "description": "Your tunnel description",
      "location": "Your Location"
    }
  ],
  "settings": {
    "timeout": 5,
    "ping_count": 2,
    "monitor_interval": 30,
    "web_refresh_interval": 15,
    "fast_mode": true,
    "adaptive_interval": true,
    "max_concurrent_checks": 3,
    "rate_limit_delay": 1,
    "responsible_monitoring": true
  }
}
```

### **4. Run Application**
```bash
python app.py
```

### **5. Access Dashboard**
```
Open browser: http://localhost:5000
```

## 🔒 Privacy Protection

### **Configuration Files**
- `config_example.json` - Example configuration (safe to commit)
- `config.json` - Your real configuration (automatically ignored by git)
- `config_real.json` - Backup of real config (automatically ignored by git)

### **Automatic Privacy Protection**
The `.gitignore` file automatically excludes:
```
# Privacy - Real tunnel configurations
config_real.json
config_production.json
config_private.json
*_real.json
*_private.json
*_production.json

# Database files
tunnel_history.db
*.db
*.sqlite
*.sqlite3
```

### **Best Practices**
1. **Never commit real tunnel details** to public repositories
2. **Use example configurations** for documentation
3. **Keep real configs local** or in private repositories
4. **Use environment variables** for sensitive data in production
5. **Regular security audits** of your configurations

## 🚀 Deployment Options

### **Local Development**
```bash
# Use config.json with your real tunnels
python app.py
```

### **Production Deployment**
```bash
# Set environment variables for sensitive data
export TUNNEL_HOST_1="your-real-host.com"
export TUNNEL_PORT_1="8080"

# Or use production config file
cp config_production.json config.json
python app.py
```

### **Railway Deployment**
1. Fork this repository
2. Create `config.json` with your tunnel details
3. Deploy to Railway (config.json will be private to your deployment)

### **Docker Deployment**
```bash
# Build with your config
docker build -t tunnel-monitor .

# Run with volume mount for config
docker run -v $(pwd)/config.json:/app/config.json -p 5000:5000 tunnel-monitor
```

## 🔧 Configuration Options

### **Tunnel Configuration**
```json
{
  "name": "TUNNEL_NAME",           // Display name
  "host": "hostname.com",          // Hostname or IP
  "port": 8080,                    // Port number
  "description": "Description",    // Optional description
  "location": "Location"           // Optional location
}
```

### **Settings Configuration**
```json
{
  "timeout": 5,                    // Connection timeout (seconds)
  "ping_count": 2,                 // Number of ping packets
  "monitor_interval": 30,          // Background check interval (seconds)
  "web_refresh_interval": 15,      // Dashboard refresh interval (seconds)
  "fast_mode": true,               // Enable fast mode
  "adaptive_interval": true,       // Enable adaptive intervals
  "max_concurrent_checks": 3,      // Maximum simultaneous checks
  "rate_limit_delay": 1,           // Minimum delay between requests (seconds)
  "responsible_monitoring": true   // Enable responsible monitoring
}
```

## 🔍 Troubleshooting

### **Common Issues**

#### **Config File Not Found**
```bash
# Error: config.json not found
# Solution: Copy example configuration
cp config_example.json config.json
```

#### **Permission Denied**
```bash
# Error: Permission denied for ping
# Solution: Run with appropriate permissions
sudo python app.py  # Linux/Mac
# Or run as Administrator on Windows
```

#### **Port Already in Use**
```bash
# Error: Address already in use
# Solution: Change port or kill existing process
lsof -ti:5000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :5000   # Windows
```

#### **Tunnel Always Offline**
```bash
# Check network connectivity
ping your-tunnel-host.com
telnet your-tunnel-host.com 8080

# Verify configuration
cat config.json
```

## 📞 Support

If you need help with setup:
1. Check this setup guide
2. Review the main [README.md](README.md)
3. Open an issue on GitHub
4. Check existing issues for solutions

## 🔒 Security Notes

- **Never share real tunnel details** in public
- **Use strong authentication** for production deployments
- **Regular security updates** for dependencies
- **Monitor access logs** for suspicious activity
- **Use HTTPS** in production environments

---

**Happy monitoring! 🚀**
