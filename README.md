# 🎯 UNL Accessibility Remediator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![WCAG 2.1](https://img.shields.io/badge/WCAG-2.1%20AA-green.svg)](https://www.w3.org/WAI/WCAG21/quickref/)
[![UNL](https://img.shields.io/badge/UNL-Accessibility-red.svg)](https://www.unl.edu)

AI-powered WCAG 2.1 Level AA compliance tool for documents and presentations, designed for University of Nebraska-Lincoln faculty and staff to meet ADA Title II requirements by April 2026.

**Supported Formats:**
- 📊 PowerPoint presentations (.pptx)
- 📄 PDF documents (.pdf) 
- 📝 Word documents (.docx)
- 🌐 HTML presentations (.html)

## 📥 Quick Download

**Latest Release**: [Download the latest version](https://github.com/chrischizinski/unl-accessibility-remediator/releases/latest)

- **For colleagues**: Download the ZIP file, extract, and follow `SIMPLE-SETUP.md`
- **🍎 macOS Users**: If you see a security warning, see `MACOS-SECURITY.md` for easy fix
- **For developers**: Clone or fork this repository

## 🎯 Purpose

This tool helps UNL faculty meet the new **ADA Title II requirements** by automatically analyzing and improving the accessibility of digital course materials. All digital course materials must comply with **WCAG 2.1 Level AA** standards by **April 24, 2026**.

## ✨ Features

- **🔍 WCAG 2.1 Level AA Analysis** - Comprehensive accessibility compliance checking for all document types
- **🖼️ Smart Alt Text Generation** - AI-powered alternative text for images (PowerPoint/HTML)
- **🔗 Link Text Enhancement** - Improves vague links like "click here"
- **🎨 Color Contrast Validation** - Ensures proper contrast ratios (4.5:1 for normal text, 3:1 for large text)
- **📝 Document Structure Analysis** - Validates headings, titles, and navigation
- **📊 Detailed Reports** - Actionable recommendations for accessibility improvements
- **🔧 Automatic Fixes** - Safe improvements applied automatically when possible
- **📄 PDF Analysis** - Detects scanned documents, missing tags, and accessibility barriers
- **📝 Word Document Processing** - Analyzes styles, structure, and formatting issues

## 🚀 Quick Start for Colleagues

### ⚡ One-Button Solution (Recommended)

**macOS/Linux:**
```bash
./start-accessibility-tool.sh     # Start the tool
./stop-accessibility-tool.sh      # Stop the tool
```

**Windows:**
```cmd
start-accessibility-tool.bat      # Start the tool
stop-accessibility-tool.bat       # Stop the tool
```

**That's it!** The script automatically:
- ✅ Checks prerequisites (Docker)
- ✅ Finds available ports (handles conflicts automatically)  
- ✅ Starts the accessibility tool
- ✅ Opens your browser to the web interface

**Zero configuration needed** - just run the script and start using the tool.

### Alternative: Manual Docker Setup

If you prefer manual control:

```bash
# Build and start services
docker-compose up --build
```

**Note**: The one-button script handles port conflicts automatically. Manual setup may require editing ports if conflicts occur.

## 📋 Requirements

- **Docker Desktop** or **OrbStack** (includes Docker Compose)
- **8GB+ RAM** recommended for AI processing
- **Internet connection** for initial setup

### Installing Docker

#### 🏢 **University-Owned Computers**
**Cannot install Docker yourself?** Most UNL faculty computers are university-managed and require IT assistance:

1. **Submit IT Request**: Use the [UNL IT Service Portal](https://unl.teamdynamix.com/TDClient/1946/Portal/Home/)
2. **Use our template**: See `IT-REQUEST-GUIDE.md` for complete copy-paste request
3. **Essential points**: Docker Desktop for ADA compliance, April 2026 deadline
4. **Reference**: Independent UNL Accessibility Remediator tool
5. **Include**: This GitHub repository link

**Alternative Options:**
- Use personal laptop if permitted for work
- Access lab computers with admin privileges
- Collaborate with colleagues who have Docker

#### 💻 **Personal Computers (Admin Required)**

**Option 1: Docker Desktop**
1. **Windows/Mac**: Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. **Linux**: Follow [docs.docker.com/desktop/install](https://docs.docker.com/desktop/install/)

**Option 2: OrbStack (macOS alternative)**
1. **macOS**: Download from [orbstack.dev](https://orbstack.dev) - Faster, lighter alternative to Docker Desktop

## 🖥️ Using the Tool

1. **Open the web interface** (URL shown in startup script output)
2. **Upload your document** (.pptx, .pdf, .docx, or .html files)
3. **Choose options**:
   - ☑️ Apply automatic fixes (recommended for Word/PowerPoint)
4. **Click "Analyze Accessibility"**
5. **Review the report** with specific recommendations
6. **Download** improved files from the `./output/` directory

## 📁 File Structure

```
title_ii_compliance/
├── input/          # Place documents here
├── output/         # Processed files appear here
├── reports/        # Accessibility reports
├── start-accessibility-tool.sh  # One-click startup
└── docker-compose.yml          # Manual Docker config
```

### 🔒 **Privacy & File Safety**

**Your data stays completely private and secure:**

#### Privacy Protection
- **🏠 100% Local Processing**: All AI analysis happens on your computer
- **🚫 No Internet Upload**: Your documents never leave your machine  
- **🔐 Complete Control**: You control all your materials and data
- **🛡️ Privacy Protected**: No external servers can access your content

#### File Safety
- **📁 Input files**: Stored in `./input/` folder - never deleted
- **📊 Processed files**: Saved to `./output/` folder - yours to keep forever
- **📋 Reports**: Saved to `./reports/` folder - review anytime
- **🔄 Restart safe**: Closing/restarting the tool won't delete anything
- **💾 Backup friendly**: Copy the entire folder to backup all your work
- **🚀 Portable**: Move the folder to any computer and continue working

**Even if you uninstall Docker, your files remain safely in these folders!**

## 🎓 UNL Compliance Information

### Legal Requirements

- **Deadline**: April 24, 2026 (UNL encourages compliance by 2025-26 academic year)
- **Standard**: WCAG 2.1 Level AA
- **Coverage**: All digital course materials including PowerPoint, PDF, Word documents, HTML, Canvas content
- **Enforcement**: Federal audits, potential fines for non-compliance

### What Gets Analyzed

- ✅ **Images**: Alt text quality and appropriateness
- ✅ **Links**: Descriptive text instead of "click here"
- ✅ **Colors**: Contrast ratios for readability
- ✅ **Structure**: Proper headings and organization
- ✅ **Text**: Font sizes and readability

## 🛠️ Troubleshooting

### Port Conflicts
The startup script automatically handles port conflicts. If you still have issues:
```bash
# Check what's using ports
lsof -i :8000
lsof -i :11434

# Kill processes if needed
kill -9 [PID]
```

### Docker Issues
```bash
# For Docker Desktop: Restart Docker Desktop application
# For OrbStack: Restart OrbStack application
# Then try again with:
./start-accessibility-tool.sh
```

### Memory Issues
- Close other applications
- Ensure Docker has at least 4GB RAM allocated
- Try processing smaller files first

## 📞 Support

### 🐛 Having Problems?
**→ [Report a Bug or Issue](REPORTING-ISSUES.md)** ← Simple guide for non-technical users!

### UNL Faculty Resources
- **UNL Digital Accessibility Training**: Available in Bridge
- **Center for Transformative Teaching**: Accessibility resources
- **Docker Support**: See [docs.docker.com/support](https://docs.docker.com/support) for installation help

### Technical Support
- **Quick Fixes**: Check Docker Desktop status and restart if needed
- **Detailed Guide**: See `DETAILED-INSTRUCTIONS.md` for advanced troubleshooting
- **GitHub Issues**: [Report technical bugs](https://github.com/chrischizinski/unl-accessibility-remediator/issues)

## 🏛️ University Branding

This tool uses UNL's brand colors for familiarity:
- Scarlet (#d00000) and Cream (#f5f1e7) color scheme
- Clean typography and styling
- Professional, accessible interface design

---

**Disclaimer**: This is an independent tool created by a UNL faculty member to help colleagues meet accessibility requirements. It is not officially endorsed or supported by the University of Nebraska–Lincoln.

**University of Nebraska–Lincoln**  
*Supporting Faculty in Digital Accessibility Compliance*