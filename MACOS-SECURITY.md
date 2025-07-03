# 🍎 macOS Security Instructions

When downloading and running the UNL Accessibility Remediator on macOS, you may encounter a security warning. This is normal for software downloaded from the internet.

## 🚨 Common Security Warning

You may see this message:
```
"START-HERE-MAC.command" cannot be opened because Apple cannot verify that it is free of malware.
```

Or:
```
Apple could not verify "START-HERE-MAC.command" is free of malware that may harm your Mac or compromise your privacy.
```

## ✅ Solution: Override Security Settings

### **Method 1: Right-Click Override (Recommended)**

1. **Right-click** (or Control+click) on `START-HERE-MAC.command`
2. Select **"Open"** from the context menu
3. A dialog will appear with the warning
4. Click **"Open"** to confirm you want to run it
5. The script will now run and won't ask again

### **Method 2: System Preferences Override**

1. Go to **System Preferences** > **Security & Privacy**
2. Click the **"General"** tab
3. You'll see a message about the blocked app
4. Click **"Open Anyway"** next to the message
5. Confirm by clicking **"Open"** in the dialog

### **Method 3: Terminal Override (Advanced Users)**

If the above methods don't work:

1. Open **Terminal** (Applications > Utilities > Terminal)
2. Navigate to the downloaded folder:
   ```bash
   cd ~/Downloads/unl-accessibility-remediator-1.2.0
   ```
3. Make the script executable:
   ```bash
   chmod +x START-HERE-MAC.command
   ```
4. Remove the quarantine attribute:
   ```bash
   xattr -d com.apple.quarantine START-HERE-MAC.command
   ```
5. Run the script:
   ```bash
   ./START-HERE-MAC.command
   ```

## 🔒 Why This Happens

- **Gatekeeper Protection**: macOS protects users from unsigned software
- **Download Source**: Files downloaded from the internet are "quarantined"
- **Code Signing**: Our script isn't signed with an Apple Developer Certificate
- **Normal Behavior**: This is standard for open-source tools and scripts

## ✅ Is It Safe?

**Yes, this is completely safe:**
- ✅ **Open Source**: All code is publicly visible on GitHub
- ✅ **University Project**: Developed for UNL accessibility compliance
- ✅ **No Installation**: Runs in Docker containers, doesn't modify your system
- ✅ **No Network Access**: Only uses local ports (8001, 11435)
- ✅ **Transparent**: You can read exactly what the script does

## 🛡️ What the Script Does

The `START-HERE-MAC.command` script only:
1. Checks if Docker is installed and running
2. Finds available network ports (8001, 11435)
3. Creates a Docker configuration file
4. Starts the accessibility tool in Docker containers
5. Opens your web browser to the tool interface

**No system files are modified** - everything runs in isolated Docker containers.

## 🚨 Still Concerned?

If you're still uncomfortable running the script:

### **Alternative: Manual Docker Setup**

1. Install Docker Desktop for Mac
2. Open Terminal and run:
   ```bash
   cd ~/Downloads/unl-accessibility-remediator-1.2.0
   docker-compose up
   ```
3. Open your browser to: `http://localhost:8001`

### **IT Department Approval**

For institutional use, your IT department can:
- Review the source code on GitHub
- Test in a sandboxed environment
- Add to approved software list
- Code sign for your organization

## 📞 Need Help?

If you continue to have issues:
1. **Port Conflicts**: See `PORT-CONFLICTS.md` if you get "port already allocated" errors
2. **Check Documentation**: Review `SIMPLE-SETUP.md` for alternatives
3. **Contact IT**: Your IT department can whitelist the application
4. **GitHub Issues**: Report problems at the GitHub repository
5. **Manual Installation**: Use Docker directly without the convenience script

---

**University of Nebraska–Lincoln**  
*Digital Accessibility Initiative - Secure & Trusted*