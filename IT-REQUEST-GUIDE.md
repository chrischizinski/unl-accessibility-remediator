# 🏢 IT Request Guide for Docker Installation

**For UNL Faculty submitting IT service requests for Docker Desktop installation**

## 📋 Quick Copy-Paste Request Template

Use this template when submitting your IT service request:

---

**Subject**: Docker Desktop Installation Request - ADA Compliance Tool

**Request Type**: Software Installation

**Software Requested**: Docker Desktop

**Business Justification**:
```
Requesting Docker Desktop installation to support ADA Title II compliance 
requirements. Federal mandate requires all digital course materials to meet 
WCAG 2.1 Level AA standards by April 24, 2026.

This installation is needed to run the UNL Accessibility Remediator, an 
independent tool developed by UNL faculty to help colleagues analyze and 
improve accessibility of PowerPoint presentations, PDFs, and HTML content.

Tool Details:
- Purpose: Accessibility compliance analysis and remediation
- Requirement: Docker Desktop for containerized AI processing
- Repository: https://github.com/chrischizinski/unl-accessibility-remediator
- Processing: 100% local (no data leaves the machine)
- Security: Open source, auditable code

Without this tool, manual accessibility compliance will require significantly 
more time and may not meet federal standards, potentially exposing the 
university to compliance issues.
```

**Priority**: Medium (Regulatory Compliance)

**Needed By**: [Add your preferred date - allow 2-3 weeks]

---

## 🛡️ Information for IT Departments

### What is Docker Desktop?
- **Official software** from Docker Inc.
- **Enterprise-grade** containerization platform used by Fortune 500 companies
- **No security risk** when properly configured
- **Standard tool** in academic and enterprise environments

### Why is this needed?
- **Federal compliance**: ADA Title II deadline April 24, 2026
- **University requirement**: All digital course materials must be accessible
- **Efficiency**: Automated analysis vs. manual checking saves significant faculty time
- **Accuracy**: AI-powered analysis catches issues human review might miss

### Security Considerations
- ✅ **Local processing only**: No data sent to external servers
- ✅ **Open source**: Code is publicly auditable
- ✅ **Containerized**: Isolated from host system
- ✅ **No network requirements**: Tool runs offline after initial setup
- ✅ **Standard ports**: Uses common Docker ports (no firewall changes needed)

### System Requirements
- **RAM**: 8GB recommended (4GB minimum)
- **Storage**: 5GB for Docker Desktop + containers
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **Admin rights**: Required for Docker installation only

### Alternative Approaches if Denied
If Docker installation cannot be approved, faculty will need to:
1. Use personal devices (potential FERPA/data concerns)
2. Manually check accessibility (time-intensive, error-prone)
3. Risk non-compliance with federal accessibility requirements

## 📞 Common IT Questions & Answers

**Q: Is this officially supported by UNL?**
A: This is an independent faculty tool. While not officially endorsed, it addresses a university-wide compliance requirement.

**Q: Can faculty use web-based alternatives?**
A: Web tools don't provide the same level of analysis and require uploading sensitive course materials to external servers.

**Q: What about security risks?**
A: Docker Desktop is enterprise software used by major organizations. The accessibility tool runs locally with no external data transmission.

**Q: Why can't faculty install this themselves?**
A: Docker requires administrator privileges that faculty don't have on university-managed computers.

**Q: What's the urgency?**
A: Federal ADA Title II compliance deadline is April 24, 2026. Early preparation is essential to avoid last-minute compliance issues.

## 📚 Supporting Documentation

- **Federal Requirement**: [ADA Title II Final Rule](https://www.ada.gov/resources/title-ii-final-rule/)
- **Docker Security**: [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- **Tool Repository**: [UNL Accessibility Remediator](https://github.com/chrischizinski/unl-accessibility-remediator)
- **WCAG Guidelines**: [Web Content Accessibility Guidelines 2.1](https://www.w3.org/WAI/WCAG21/quickref/)

## 💡 Tips for Success

1. **Emphasize compliance**: Frame as regulatory requirement, not optional tool
2. **Highlight efficiency**: Tool saves time vs. manual accessibility checking
3. **Mention deadlines**: Federal deadline creates urgency
4. **Offer pilot**: Suggest trial installation for evaluation
5. **Reference security**: Docker is standard enterprise software

---

**Need help with your IT request?** See `REPORTING-ISSUES.md` for additional support resources.