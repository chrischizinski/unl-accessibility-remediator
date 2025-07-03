# Changelog

All notable changes to the UNL Accessibility Remediator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

### Added
- Initial release of UNL Accessibility Remediator
- AI-powered WCAG 2.1 Level AA compliance checking
- Support for PowerPoint (.pptx) and HTML slide decks
- Automatic alt text generation using local LLM
- Color contrast validation with WCAG ratios
- Link text analysis and improvement suggestions
- UNL-branded web interface with scarlet and cream styling
- One-click startup scripts for Windows, Mac, and Linux
- Comprehensive documentation for technical and non-technical users
- Docker containerization for easy deployment
- Global port manager to prevent conflicts
- Automatic port detection and configuration

### Features
- **AI Assistant Integration**: Local Ollama LLM for intelligent accessibility analysis
- **PowerPoint Processing**: Complete .pptx file analysis and modification
- **Contrast Checking**: WCAG 2.1 compliant color contrast validation
- **Alt Text Generation**: Context-aware alternative text suggestions
- **Web Interface**: Professional UNL-branded user interface
- **Batch Processing**: Support for multiple file processing
- **Detailed Reports**: Comprehensive accessibility analysis reports
- **Automatic Fixes**: Safe accessibility improvements applied automatically

### Documentation
- Simple setup guide for non-technical users
- Detailed instructions with troubleshooting
- Contributing guidelines for developers
- UNL compliance information and deadlines
- Complete API and technical documentation

### Compliance
- WCAG 2.1 Level AA standard compliance
- ADA Title II requirements support
- UNL-specific accessibility guidelines
- Federal deadline preparation (April 24, 2026)

---

## [1.1.0] - 2025-07-03

### Added
- **PDF Support**: Accessibility analysis for `.pdf` files, including detection of missing alt text, heading structure issues, and color contrast violations.
- **Word Document Support**: Accessibility checking for `.docx` files, including alt text validation, heading hierarchy checks, and reading order structure.
- Expanded filetype detection to include PDFs and Word documents in batch processing.
- Automatic alt text generation now available for PDF and Word images.

### Changed
- Updated batch processing engine to support additional MIME types.
- Improved UI feedback and messaging when analyzing multiple file formats.

### Documentation
- Updated user guide to include instructions for PDF and Word document processing.
- Expanded troubleshooting section for common document-specific issues.
- Clarified compliance workflows for multi-format instructional materials.

### UNL Specific
- Aligns with faculty accessibility needs across a wider range of instructional materials.
- Supports Title II digital accessibility requirements for PDF and DOCX formats, in preparation for the **April 24, 2026** compliance deadline.

---

## Release Notes Template

When releasing new versions, use this template:

## [X.Y.Z] - YYYY-MM-DD

### Added
- New features and capabilities

### Changed
- Changes to existing functionality

### Deprecated
- Features marked for removal in future versions

### Removed
- Features removed in this version

### Fixed
- Bug fixes and corrections

### Security
- Security improvements and fixes

### UNL Specific
- Changes specific to UNL requirements or workflows

---

**University of Nebraska–Lincoln**  
*Digital Accessibility Initiative*