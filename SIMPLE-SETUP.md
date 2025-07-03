# 🎯 UNL Accessibility Tool - Simple Setup Guide

**For non-technical users who want to analyze slide decks for accessibility**

## 📦 What You Need (One-Time Setup)

### Step 1: Install Docker Desktop
1. **Go to**: [docker.com/products/docker-desktop](https://docker.com/products/docker-desktop)
2. **Click**: "Download Docker Desktop"
3. **Choose**: Your operating system (Windows, Mac, or Linux)
4. **Download** and **install** (just like any other software)
5. **Start Docker Desktop** from your Applications/Programs

*That's it! Docker Desktop includes everything you need.*

### Step 2: Get the Accessibility Tool
1. **Download** this project as a ZIP file (click green "Code" button → "Download ZIP")
2. **Extract** the ZIP file to your Desktop or Documents folder
3. **Remember** where you put it!

## 🚀 Using the Tool (Every Time)

### Method 1: Double-Click Setup (Easiest)

1. **Open** the folder where you extracted the tool
2. **Double-click** on one of these files:
   - **Windows**: `START-HERE-WINDOWS.bat`
   - **Mac**: `START-HERE-MAC.command` *(If you see a security warning, see `MACOS-SECURITY.md`)*
   - **Linux**: `START-HERE-LINUX.sh`

3. **Wait** for the tool to start (may take 2-3 minutes first time)
4. **Look for** a message like: "🌐 Open: http://localhost:8003"
5. **Click** that link or copy it to your web browser

### Method 2: Using Applications Menu

**On Windows:**
1. Open "Command Prompt" from Start Menu
2. Type: `cd ` (with a space after cd)
3. Drag the accessibility tool folder into the window
4. Press Enter
5. Type: `start-tool.bat`
6. Press Enter

**On Mac:**
1. Open "Terminal" from Applications → Utilities
2. Type: `cd ` (with a space after cd)  
3. Drag the accessibility tool folder into the window
4. Press Enter
5. Type: `./start-tool.sh`
6. Press Enter

## 📁 Using the Web Interface

Once the tool is running:

1. **Open your web browser** (Chrome, Firefox, Safari, Edge)
2. **Go to** the URL shown (like http://localhost:8003)
3. **Upload** your PowerPoint (.pptx) or HTML slide deck
4. **Check** "Apply automatic fixes" (recommended)
5. **Click** "Analyze Accessibility"
6. **Wait** for analysis to complete
7. **Review** the detailed report
8. **Download** improved files if automatic fixes were applied

## 📂 Finding Your Files

After processing:
- **Reports**: Look in the `reports` folder
- **Improved files**: Look in the `output` folder
- **Original files**: Stay in the `input` folder

## ❓ Troubleshooting

### "Docker is not running"
- **Make sure** Docker Desktop is open and running
- **Look for** the Docker whale icon in your system tray/menu bar
- **Wait** a minute after starting Docker Desktop before trying again

### "Port already in use"
- **Close** other development tools or web servers
- **Try again** - the tool will automatically find another port

### "Can't find the file"
- **Make sure** you extracted the ZIP file completely
- **Look for** files ending in `.bat`, `.command`, or `.sh`
- **Right-click** and choose "Run" or "Open"

### Still having trouble?
1. **Restart** Docker Desktop
2. **Restart** your computer
3. **Try** the command line method below

## 🛟 Need Help?

**For UNL Faculty:**
- Digital Accessibility Training in Bridge
- Center for Transformative Teaching resources
- IT Help Desk for Docker installation issues

**Before asking for help:**
- Make sure Docker Desktop is installed and running
- Try restarting Docker Desktop
- Note any error messages you see

---

## 🔧 Advanced Users (Command Line)

If you're comfortable with command line:

```bash
# Quick start
./start-accessibility-tool.sh

# Manual Docker
docker-compose up --build

# Check ports
./port-manager check 8000
```

See `README.md` for full technical documentation.

---

**University of Nebraska–Lincoln**  
*Making digital course materials accessible for all students*