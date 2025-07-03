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

**Latest Release**: [Download the latest version](https://github.com/YOUR_USERNAME/unl-accessibility-remediator/releases/latest)

- **For colleagues**: Download the ZIP file, extract, and follow `SIMPLE-SETUP.md`
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

### Option 1: One-Click Startup (Recommended)

```bash
# Clone or download this project
git clone [repository-url]
cd title_ii_compliance

# Run the automated setup script
./start-accessibility-tool.sh
```

The script will:
- ✅ Check that Docker is installed and running
- 🔍 Automatically find available ports (no conflicts!)
- 🚀 Start all services with proper configuration
- 🌐 Open the web interface at the correct URL

### Option 2: Manual Docker Setup

If you prefer manual control:

```bash
# Build and start services
docker-compose up --build

# If you get port conflicts, edit docker-compose.yml to use different ports
# Then try again
```

## 📋 Requirements

- **Docker Desktop** (includes Docker Compose)
- **8GB+ RAM** recommended for AI processing
- **Internet connection** for initial setup

### Installing Docker Desktop

1. **Windows/Mac**: Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. **Linux**: Follow [docs.docker.com/desktop/install](https://docs.docker.com/desktop/install/)

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
# Restart Docker Desktop
# Then try again with:
./start-accessibility-tool.sh
```

### Memory Issues
- Close other applications
- Ensure Docker has at least 4GB RAM allocated
- Try processing smaller files first

## 📞 Support

- **UNL Digital Accessibility Training**: Available in Bridge
- **Center for Transformative Teaching**: Accessibility resources
- **Technical Issues**: Check Docker Desktop status and restart if needed

## 🏛️ University Branding

This tool follows UNL's official brand guidelines with:
- Scarlet (#d00000) and Cream (#f5f1e7) color scheme
- Official typography and styling
- Professional, accessible interface design

---

**University of Nebraska–Lincoln**  
*Center for Transformative Teaching | Digital Accessibility Initiative*