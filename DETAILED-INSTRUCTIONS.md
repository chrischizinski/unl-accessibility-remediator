# 📚 UNL Accessibility Tool - Complete User Guide

**Comprehensive instructions for faculty, staff, and IT administrators**

## Table of Contents
- [Quick Start for Non-Technical Users](#quick-start)
- [Detailed Setup Instructions](#detailed-setup)
- [Using the Web Interface](#using-the-web-interface)
- [Understanding Reports](#understanding-reports)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)
- [UNL Compliance Information](#unl-compliance)

---

## 🚀 Quick Start for Non-Technical Users {#quick-start}

### What You Need
- **Computer** with Windows, Mac, or Linux
- **Internet connection** for initial setup
- **PowerPoint or HTML slide decks** to analyze

### Installation (One Time Only)

#### Step 1: Install Docker Desktop
1. **Go to**: [docker.com/products/docker-desktop](https://docker.com/products/docker-desktop)
2. **Download** the version for your operating system
3. **Install** Docker Desktop (like any other program)
4. **Start** Docker Desktop after installation

#### Step 2: Get the Accessibility Tool  
1. **Download** this project as a ZIP file
2. **Extract** the ZIP to your Desktop or Documents
3. **Remember** the folder location

### Running the Tool

1. **Open** the extracted folder
2. **Double-click** the appropriate file:
   - **Windows**: `START-HERE-WINDOWS.bat`
   - **Mac**: `START-HERE-MAC.command`
   - **Linux**: `START-HERE-LINUX.sh`
3. **Wait** for the tool to start (2-3 minutes first time)
4. **Open** the web link shown (like http://localhost:8003)

### Using the Tool
1. **Upload** your slide deck (.pptx or .html)
2. **Check** "Apply automatic fixes" 
3. **Click** "Analyze Accessibility"
4. **Wait** for analysis (1-5 minutes depending on file size)
5. **Review** the detailed report
6. **Download** improved files from the interface

---

## 🔧 Detailed Setup Instructions {#detailed-setup}

### System Requirements

**Minimum:**
- 4GB RAM
- 2GB free disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

**Recommended:**
- 8GB+ RAM (for faster AI processing)
- 5GB+ free disk space
- Stable internet connection

### Docker Desktop Installation

#### Windows
1. **Download**: Docker Desktop for Windows
2. **Run** the installer as Administrator
3. **Follow** the installation wizard
4. **Restart** computer when prompted
5. **Start** Docker Desktop from Start Menu
6. **Accept** license terms and complete setup

#### Mac
1. **Download**: Docker Desktop for Mac (Intel or Apple Silicon)
2. **Drag** Docker.app to Applications folder
3. **Launch** Docker Desktop from Applications
4. **Grant** necessary permissions when prompted
5. **Complete** initial setup

#### Linux (Ubuntu/Debian)
```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Install Docker
sudo apt update
sudo apt install docker-ce docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Restart and test
sudo systemctl start docker
docker --version
```

### Verifying Installation

1. **Open** Terminal/Command Prompt
2. **Type**: `docker --version`
3. **Should see**: Docker version information
4. **Type**: `docker-compose --version`
5. **Should see**: Docker Compose version information

---

## 🖥️ Using the Web Interface {#using-the-web-interface}

### Main Dashboard

The web interface provides a clean, UNL-branded interface with:

- **Header**: Tool name and description
- **Upload Area**: Drag-and-drop or click to select files
- **Options**: Checkbox for automatic fixes
- **Information**: Tool capabilities and UNL requirements

### Uploading Files

**Supported Formats:**
- PowerPoint (.pptx files)
- HTML presentations (.html, .htm files)
- Reveal.js slide decks
- Other HTML-based presentations

**File Size Limits:**
- Up to 50MB per file
- Larger files may take longer to process

**Upload Methods:**
1. **Click** "Choose File" button
2. **Drag and drop** files onto upload area
3. **Browse** and select from file explorer

### Processing Options

**Automatic Fixes (Recommended):**
- ✅ **Enabled**: Tool will apply safe improvements automatically
  - Adds missing alt text to images
  - Improves vague link text
  - Fixes minor formatting issues
  - Creates backup of original file

- ❌ **Disabled**: Analysis only, no changes made
  - Generates report with recommendations
  - You manually implement suggested changes
  - Original file remains unchanged

### Processing Time

**Typical Processing Times:**
- Small presentation (5-10 slides): 1-2 minutes
- Medium presentation (15-30 slides): 3-5 minutes  
- Large presentation (50+ slides): 5-10 minutes
- Complex presentations with many images: 10+ minutes

**Factors Affecting Speed:**
- Number of slides
- Number of images requiring alt text
- Complexity of content
- System performance
- First-time AI model loading

---

## 📊 Understanding Reports {#understanding-reports}

### Report Structure

Each accessibility report includes:

1. **Executive Summary**
   - Overall accessibility score (0-100)
   - Total issues found
   - Automatic fixes applied
   - Manual review items

2. **Slide-by-Slide Analysis**
   - Individual slide scores
   - Specific issues identified
   - Recommendations for improvement
   - Priority levels (High, Medium, Low)

3. **Issue Categories**
   - Missing or poor alt text
   - Insufficient color contrast
   - Vague link text
   - Missing slide titles
   - Structural problems

4. **Compliance Status**
   - WCAG 2.1 Level AA compliance
   - UNL-specific requirements
   - Federal deadline compliance

### Issue Severity Levels

**🔴 Critical (Must Fix)**
- Missing alt text on informative images
- Color contrast below 3:1 ratio
- Links with no descriptive text
- Heading structure violations

**🟡 High Priority**  
- Poor quality alt text
- Color contrast below 4.5:1 for normal text
- Vague link text ("click here", "read more")
- Missing slide titles

**🟠 Medium Priority**
- Generic alt text ("image", "photo")
- Moderately low contrast (3:1 to 4.5:1)
- Long or overly detailed alt text
- Minor structural issues

**🟢 Low Priority**
- Style improvements
- Optimization suggestions
- Best practice recommendations
- Enhancement opportunities

### Automatic Fix Details

**What Gets Fixed Automatically:**
- ✅ Missing alt text (AI-generated)
- ✅ Obvious link text improvements  
- ✅ Basic formatting corrections
- ✅ Simple title suggestions

**What Requires Manual Review:**
- ❌ Complex images needing detailed descriptions
- ❌ Color scheme changes
- ❌ Structural reorganization
- ❌ Content that needs human judgment

---

## 🛠️ Troubleshooting {#troubleshooting}

### Common Issues and Solutions

#### "Docker is not installed"
**Problem**: System can't find Docker
**Solution**: 
1. Install Docker Desktop from docker.com
2. Restart computer after installation
3. Try again

#### "Docker is not running"  
**Problem**: Docker Desktop isn't started
**Solution**:
1. Start Docker Desktop application
2. Wait for whale icon to appear (system tray/menu bar)
3. Ensure Docker Desktop shows "Running" status

#### "Port already in use"
**Problem**: Another service is using the port
**Solution**:
1. Close other development tools
2. Try the startup script again (it finds new ports automatically)
3. If still failing, restart computer

#### "Can't connect to web interface"
**Problem**: Browser can't reach the tool
**Solution**:
1. Wait 2-3 minutes for full startup
2. Check Docker Desktop shows containers running
3. Try refreshing browser page
4. Check firewall isn't blocking localhost connections

#### "File upload fails"
**Problem**: Can't upload presentation files
**Solution**:
1. Check file format (.pptx, .html only)
2. Ensure file size under 50MB
3. Close PowerPoint if file is open
4. Try a different browser

#### "Analysis takes too long"
**Problem**: Processing seems stuck
**Solution**:
1. Wait longer (complex files take 10+ minutes)
2. Check Docker Desktop for error messages
3. Try smaller/simpler file first
4. Restart the tool if no progress after 20 minutes

#### "Out of memory" errors
**Problem**: System runs out of RAM
**Solution**:
1. Close other applications
2. Increase Docker memory allocation (Docker Desktop → Settings → Resources)
3. Try processing smaller files
4. Restart Docker Desktop

### Getting Help

**For UNL Faculty/Staff:**
1. **IT Help Desk**: For Docker installation issues
2. **Center for Transformative Teaching**: For accessibility questions
3. **Digital Accessibility Training**: Available in Bridge

**Before Contacting Support:**
1. Note exact error messages
2. Check Docker Desktop status
3. Try restarting Docker Desktop
4. Test with a small, simple file

---

## ⚙️ Advanced Usage {#advanced-usage}

### Command Line Interface

For technical users who prefer command line:

```bash
# Quick start
./start-accessibility-tool.sh

# Manual Docker commands
docker-compose up --build
docker-compose down

# Process specific file
docker-compose exec accessibility-remediator python main.py input/presentation.pptx --auto-fix

# Check logs
docker-compose logs accessibility-remediator
```

### Configuration Options

**Environment Variables:**
```bash
# Custom Ollama model
export OLLAMA_MODEL=llama3
export OLLAMA_HOST=localhost:11434

# Output settings
export OUTPUT_FORMAT=detailed
export REPORT_FORMAT=html
```

**Docker Compose Overrides:**
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  accessibility-remediator:
    ports:
      - "9000:8000"  # Use port 9000 instead
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
```

### Batch Processing

For processing multiple files:

```bash
# Place all files in input/ directory
cp *.pptx input/

# Process all files
for file in input/*.pptx; do
    docker-compose exec accessibility-remediator python main.py "$file" --auto-fix
done

# Results appear in output/ and reports/ directories
```

### Custom AI Models

To use different AI models with Ollama:

```bash
# Download specific model
docker-compose exec ollama ollama pull llama3.1

# Use in processing
docker-compose exec accessibility-remediator python main.py input/file.pptx --model llama3.1
```

---

## 🎓 UNL Compliance Information {#unl-compliance}

### Legal Requirements

**Federal Mandate:**
- **Law**: ADA Title II
- **Standard**: WCAG 2.1 Level AA
- **Deadline**: April 24, 2026
- **UNL Goal**: Compliance by 2025-26 academic year

**Coverage:**
- All digital course materials
- PowerPoint presentations
- HTML slide decks
- Canvas content
- Third-party tools and content
- Password-protected materials

### WCAG 2.1 Level AA Requirements

**Perceivable:**
- Alt text for all informative images
- Color contrast ratios (4.5:1 normal, 3:1 large text)
- Resizable text up to 200%
- Audio descriptions for videos

**Operable:**
- Keyboard navigation
- No seizure-inducing content
- Reasonable time limits
- Clear navigation

**Understandable:**
- Readable text
- Predictable functionality
- Input assistance
- Error identification

**Robust:**
- Compatible with assistive technologies
- Valid HTML/markup
- Future-proof coding practices

### Consequences of Non-Compliance

**Federal Enforcement:**
- Department of Justice audits
- Required remediation plans
- Ongoing monitoring
- Potential litigation

**Financial Impact:**
- Investigation costs
- Remediation expenses
- Legal fees
- Potential fines

**Institutional Impact:**
- Reputation damage
- Student accessibility barriers
- Faculty workload increases
- Compliance burden

### UNL Support Resources

**Training:**
- Digital Accessibility Training (Bridge)
- Workshop series on accessibility
- Canvas-based accessibility course

**Support:**
- Center for Transformative Teaching
- Services for Students with Disabilities
- Institutional Equity and Compliance
- University Libraries
- Information Technology Services

**Tools and Templates:**
- UNL-branded PowerPoint templates
- Accessibility checklists
- WCAG validation tools
- Screen reader testing resources

---

## 📞 Contact and Support

**Technical Issues:**
- IT Help Desk: [contact information]
- Docker Support: docs.docker.com/support

**Accessibility Questions:**
- Center for Transformative Teaching
- Digital Accessibility Team
- UNL Accessibility Services

**Training and Resources:**
- Bridge training platform
- UNL accessibility website
- Faculty development workshops

---

**University of Nebraska–Lincoln**  
*Committed to accessible education for all students*

*Last updated: [Date]*  
*Version: 1.0*