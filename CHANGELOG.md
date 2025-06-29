# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-27

### Added
- **History Tracking**: SQLite database untuk menyimpan status history
- **Downtime Detection**: Automatic detection dan tracking downtime events
- **Real-time Alerts**: Visual notifications untuk status changes
- **Browser Notifications**: Desktop notifications dengan permission
- **Statistics Dashboard**: 7-day uptime statistics dan performance metrics
- **Individual History**: 24-hour timeline per tunnel
- **API Endpoints**: Comprehensive REST API untuk history dan statistics
- **Rate Limiting**: Responsible monitoring dengan safety controls
- **Security Analysis**: Comprehensive security documentation
- **Mobile Responsiveness**: Enhanced mobile experience

### Changed
- **Database**: Migrated from in-memory to persistent SQLite storage
- **Monitoring Logic**: Enhanced with status change detection
- **Dashboard UI**: Improved with history and statistics sections
- **API Structure**: Extended with history and downtime endpoints
- **Configuration**: Added safety and performance settings
- **Documentation**: Complete rewrite dengan comprehensive guides

### Fixed
- **Memory Leaks**: Improved memory management
- **Error Handling**: Enhanced error recovery dan logging
- **Performance**: Optimized database queries dengan indexes
- **Concurrent Access**: Thread-safe database operations

### Security
- **Rate Limiting**: Implemented responsible monitoring practices
- **Timeout Controls**: Added connection timeout limits
- **Concurrent Limits**: Maximum simultaneous check restrictions
- **Industry Compliance**: Aligned dengan monitoring standards

## [1.0.0] - 2024-12-20

### Added
- **Initial Release**: Basic tunnel monitoring functionality
- **Flask Dashboard**: Web-based monitoring interface
- **TCP Monitoring**: Port connectivity checking
- **Ping Monitoring**: Host reachability testing
- **Auto-refresh**: Automatic dashboard updates
- **Railway Deployment**: Cloud deployment configuration
- **Responsive Design**: Mobile-friendly interface
- **Error Handling**: Basic error recovery
- **Configuration**: JSON-based tunnel configuration
- **API Endpoints**: Basic status API

### Features
- Monitor 9 Mikrotik tunnels simultaneously
- Real-time status updates
- TCP port checking dengan timeout
- ICMP ping monitoring
- Web dashboard dengan auto-refresh
- JSON API untuk external integration
- Railway deployment ready
- Mobile responsive design

---

## Planned Features (Roadmap)

### [2.1.0] - Planned
- **Email Notifications**: SMTP integration untuk downtime alerts
- **Export Reports**: PDF/Excel export functionality
- **Webhook Integration**: External system notifications
- **User Authentication**: Login dan role management

### [2.2.0] - Planned
- **Mobile App**: Native Android/iOS applications
- **Push Notifications**: Mobile push notifications
- **Multi-language**: Indonesian dan English support
- **Advanced Charts**: Real-time performance charts

### [3.0.0] - Future
- **Multi-tenant**: Support multiple organizations
- **Advanced Analytics**: Machine learning predictions
- **Custom Dashboards**: User-configurable layouts
- **Integration Hub**: Third-party service integrations

---

## Migration Guide

### From v1.0.0 to v2.0.0

1. **Backup Configuration**
   ```bash
   cp config.json config.json.backup
   ```

2. **Update Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Migration**
   - SQLite database akan auto-created on first run
   - No manual migration required

4. **Configuration Updates**
   - New settings added to config.json
   - Old configuration remains compatible

5. **API Changes**
   - All existing APIs remain functional
   - New history APIs available
   - No breaking changes

---

## Support

For questions about this changelog or migration assistance:
- Open an issue on GitHub
- Check the documentation
- Join our discussions

---

**Note**: This project follows semantic versioning. Major version changes may include breaking changes, minor versions add functionality, and patch versions include bug fixes.
