# 🔒 Security Policy

**UNL Accessibility Remediator - Security Documentation**

## 🛡️ Security Overview

This tool has undergone comprehensive security auditing and hardening to ensure safe deployment in university environments with sensitive course materials.

## 📋 Security Audit Results

**Last Security Audit**: December 2024  
**Status**: ✅ **ALL CRITICAL VULNERABILITIES PATCHED**

### 🔴 Critical Vulnerabilities Fixed

| Vulnerability | Severity | Status | Fix Applied |
|---------------|----------|--------|-------------|
| Unauthenticated Admin Endpoints | Critical | ✅ Fixed | Localhost-only access control |
| Path Traversal in File Uploads | Critical | ✅ Fixed | Filename sanitization |
| Command Injection via Filenames | Critical | ✅ Fixed | Subprocess argument separation |
| Cross-Site Scripting (XSS) | High | ✅ Fixed | HTML output escaping |
| Insecure Docker Configuration | High | ✅ Fixed | Version pinning |
| Information Disclosure | Medium | ✅ Fixed | Error message sanitization |

## 🔐 Security Features

### Access Control
- **Admin Functions**: Restricted to localhost (127.0.0.1) access only
- **File System**: Upload paths validated and sanitized
- **Network**: Local-only deployment, no external network access required

### Input Validation
- **File Uploads**: Filenames sanitized to prevent directory traversal
- **User Input**: All inputs validated and HTML-escaped
- **Command Execution**: Arguments properly separated to prevent injection

### Container Security
- **Base Images**: Pinned to specific, tested versions
- **Network Isolation**: Docker internal networking only
- **Minimal Attack Surface**: Only necessary ports exposed

### Data Protection
- **Local Processing**: All data stays on the local machine
- **No External Transmission**: Zero data sent to external servers
- **File Isolation**: Processed files contained within designated directories

## 🚨 Reporting Security Issues

### For Security Researchers
If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** create a public GitHub issue
2. **Email**: [Create GitHub security advisory](https://github.com/chrischizinski/unl-accessibility-remediator/security/advisories/new)
3. **Include**: Detailed description, reproduction steps, and impact assessment
4. **Response Time**: We aim to respond within 48 hours

### For UNL IT Departments
University IT departments can request security documentation:

1. **Contact**: Via GitHub issues for non-sensitive questions
2. **Documentation**: This SECURITY.md file contains full disclosure
3. **Audit Trail**: All security fixes are documented in git history
4. **Compliance**: Tool designed to meet university security standards

## 🔍 Security Best Practices

### Deployment Recommendations

#### ✅ Recommended Deployment
- Deploy on university-managed computers with IT approval
- Use behind university firewall
- Regular Docker image updates through IT processes
- Monitor logs for unusual activity

#### ⚠️ Security Considerations
- Admin panel accessible only from localhost
- File upload directory has size/type restrictions
- All processing happens locally (no cloud dependencies)
- Container runs with minimal necessary privileges

#### ❌ Avoid These Configurations
- Exposing ports to external networks
- Running with root privileges unnecessarily
- Using `latest` Docker tags in production
- Disabling built-in security validations

### Monitoring and Logging

**Log Locations:**
- Application logs: Container stdout/stderr
- Access logs: FastAPI automatically generated
- Error logs: Detailed logging for debugging (localhost only)

**Monitor For:**
- Unusual file upload patterns
- Failed authentication attempts to admin endpoints
- Unexpected subprocess executions
- Container restart patterns

## 📚 Security References

### Standards Compliance
- **Input Validation**: OWASP Input Validation Cheat Sheet
- **File Upload Security**: OWASP File Upload Cheat Sheet  
- **Container Security**: NIST Container Security Guidelines
- **Web Application Security**: OWASP Top 10 mitigations

### Technical Implementation
- **FastAPI Security**: Built-in security features utilized
- **Docker Security**: Following Docker security best practices
- **Python Security**: Secure coding practices applied
- **Subprocess Security**: Argument injection prevention

## 🔄 Security Update Process

### Regular Updates
1. **Dependency Scanning**: Monitor for vulnerable dependencies
2. **Docker Image Updates**: Pin to latest secure versions
3. **Security Patches**: Apply promptly via git updates
4. **Testing**: Validate security fixes don't break functionality

### Emergency Updates
1. **Critical Issues**: Immediate patching and communication
2. **Hotfixes**: Fast-track deployment for security fixes
3. **Notification**: IT departments notified of critical updates
4. **Documentation**: Security advisories published

## 📞 Contact Information

**Project Maintainer**: UNL Faculty (Independent Project)  
**Security Contact**: GitHub Security Advisories  
**Issue Reporting**: [GitHub Issues](https://github.com/chrischizinski/unl-accessibility-remediator/issues) (non-security)  
**Documentation**: See `REPORTING-ISSUES.md` for general support

---

**Security Commitment**: This tool is designed for university environments handling sensitive course materials. Security is a top priority, and we maintain responsible disclosure practices for any discovered vulnerabilities.

**Last Updated**: December 2024  
**Next Review**: Continuous monitoring and updates as needed