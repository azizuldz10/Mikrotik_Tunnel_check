# Contributing to Mikrotik Tunnel Monitor

Thank you for your interest in contributing to Mikrotik Tunnel Monitor! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### 1. **Fork the Repository**
```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/azizuldz10/Mikrotik_Tunnel_check.git
cd Mikrotik_Tunnel_check
```

### 2. **Set Up Development Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### 3. **Create Feature Branch**
```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description
```

### 4. **Make Changes**
- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed

### 5. **Test Your Changes**
```bash
# Run application locally
python app.py

# Test all features
# - Dashboard loading
# - API endpoints
# - History functionality
# - Alert system
```

### 6. **Commit Changes**
```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "Add: New feature description"
# or
git commit -m "Fix: Bug description"
# or
git commit -m "Update: Documentation improvement"
```

### 7. **Push and Create Pull Request**
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

## 📋 Contribution Guidelines

### **Code Style**
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Keep functions small and focused
- Add docstrings for functions and classes

### **Commit Messages**
Use conventional commit format:
```
Type: Brief description

Detailed explanation if needed

Types:
- Add: New features
- Fix: Bug fixes
- Update: Documentation or minor improvements
- Remove: Removing code or files
- Refactor: Code restructuring
```

### **Pull Request Guidelines**
- Provide clear description of changes
- Reference related issues if applicable
- Include screenshots for UI changes
- Ensure all tests pass
- Update documentation if needed

## 🐛 Bug Reports

### **Before Reporting**
- Check existing issues
- Test with latest version
- Verify it's not a configuration issue

### **Bug Report Template**
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to...
2. Click on...
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python Version: [e.g., 3.9.0]
- Browser: [e.g., Chrome 96]

**Additional Context**
Screenshots, logs, etc.
```

## 💡 Feature Requests

### **Feature Request Template**
```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Mockups, examples, etc.
```

## 🔧 Development Setup

### **Project Structure**
```
mikrotik-tunnel-monitor/
├── app.py                 # Main Flask application
├── config.json           # Tunnel configuration
├── requirements.txt      # Python dependencies
├── templates/
│   └── dashboard.html    # Main dashboard template
├── static/              # Static files (if any)
├── tests/               # Test files
└── docs/                # Documentation
```

### **Key Components**
- **TunnelMonitor**: Main monitoring class
- **TunnelHistoryDB**: Database operations
- **Flask Routes**: Web endpoints
- **Dashboard**: Frontend interface

### **Database Schema**
```sql
-- Status History
tunnel_status_history (
    id, tunnel_name, host, port, status,
    response_time, error_message, timestamp
)

-- Downtime Events
downtime_events (
    id, tunnel_name, host, port, down_start,
    down_end, duration_seconds, is_resolved, error_message
)
```

## 🧪 Testing

### **Manual Testing**
1. **Dashboard Loading**
   - Verify all tunnels display
   - Check status updates
   - Test responsive design

2. **API Endpoints**
   - Test `/api/status`
   - Test `/api/history/<name>`
   - Test `/api/statistics`

3. **History Features**
   - Verify database logging
   - Test downtime detection
   - Check alert notifications

### **Automated Testing** (Future)
```bash
# Run tests (when implemented)
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

## 📚 Documentation

### **Documentation Updates**
- Update README.md for new features
- Add API documentation for new endpoints
- Update configuration examples
- Include screenshots for UI changes

### **Code Documentation**
```python
def example_function(param1: str, param2: int) -> dict:
    """
    Brief description of function.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: Description of when raised
    """
    pass
```

## 🚀 Release Process

### **Version Numbering**
- Major: Breaking changes (2.0.0)
- Minor: New features (2.1.0)
- Patch: Bug fixes (2.1.1)

### **Release Checklist**
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Test all features
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag release

## 🎯 Priority Areas

### **High Priority**
- Bug fixes and stability improvements
- Performance optimizations
- Security enhancements
- Documentation improvements

### **Medium Priority**
- New monitoring features
- UI/UX improvements
- API enhancements
- Mobile optimizations

### **Low Priority**
- Advanced analytics
- Third-party integrations
- Experimental features

## 📞 Getting Help

### **Communication Channels**
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Reviews**: Code-specific discussions

### **Response Times**
- Issues: Within 48 hours
- Pull Requests: Within 72 hours
- Security Issues: Within 24 hours

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Mikrotik Tunnel Monitor!** 🚀

Your contributions help make network monitoring better for everyone.
