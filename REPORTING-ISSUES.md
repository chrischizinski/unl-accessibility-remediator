# 🐛 How to Report Problems (Simple Guide)

Having trouble with the UNL Accessibility Tool? This guide will help you report problems so we can fix them quickly!

## 🚨 When to Report a Problem

Report an issue if:
- ✅ The tool won't start or crashes
- ✅ Your files won't upload or process
- ✅ You get error messages you don't understand
- ✅ The results don't look right
- ✅ Something that used to work suddenly doesn't

## 📝 How to Report (3 Easy Steps)

### Step 1: Go to the Issues Page
1. Visit: https://github.com/chrischizinski/unl-accessibility-remediator/issues
2. Click the green **"New issue"** button
3. Choose **"Bug report"**

### Step 2: Fill Out the Form
**Don't worry about being technical!** Just describe:

**What went wrong?**
- Example: "The tool won't start when I double-click the file"
- Example: "My PowerPoint uploaded but no report was generated"

**What were you trying to do?**
- Example: "I was trying to analyze my lecture slides for accessibility"
- Example: "I wanted to upload a 20-slide presentation"

**What did you expect to happen?**
- Example: "I expected to see an accessibility report"
- Example: "I thought the tool would start and open in my browser"

### Step 3: Add Helpful Details

**Your Computer Info** (copy/paste is fine):
- Operating System: Windows 10, macOS, or Linux
- Which file you double-clicked to start the tool

**Screenshots** (super helpful!):
- Take a screenshot of any error messages
- Show what your screen looks like when the problem happens

## 🆘 Quick Help Before Reporting

Try these first (might save you time!):

### Tool Won't Start?
1. **Check Docker Desktop** - Make sure it's running (look for whale icon in taskbar)
2. **Restart everything** - Close Docker Desktop, restart it, try again
3. **Try the other startup file** - If `start-accessibility-tool.bat` doesn't work, try `start-accessibility-tool.sh`

### File Won't Upload?
1. **Check file size** - Files larger than 50MB might have problems
2. **Check file type** - We support .pptx, .pdf, .docx, and .html files
3. **Try a different file** - Test with a simple 3-slide PowerPoint first

### Browser Problems?
1. **Try a different browser** - Chrome usually works best
2. **Check the web address** - Should be `http://localhost:8001` (or similar number)
3. **Wait a bit longer** - First-time startup can take 3-5 minutes

## 💡 What Makes a Good Bug Report

**Great Example:**
> "Hi! I'm a UNL professor trying to check my lecture slides. When I double-click START-HERE-WINDOWS.bat, I get a black window that says 'Docker is not installed.' But I installed Docker Desktop yesterday and can see the whale icon in my taskbar. I'm on Windows 11. Here's a screenshot of the error message."

**Not So Helpful:**
> "It doesn't work."

## 🎓 UNL Faculty Notes

When reporting, mention:
- That you're UNL faculty/staff
- What type of course materials you're working with
- If this is for the 2026 compliance deadline

This helps us prioritize fixes that affect our primary users!

## 📞 Other Ways to Get Help

**For UNL Faculty:**
- **IT Help Desk**: For Docker installation problems
- **Digital Accessibility Training**: Available in Bridge
- **Center for Transformative Teaching**: General accessibility guidance

**For Technical Users:**
- Check `DETAILED-INSTRUCTIONS.md` for advanced troubleshooting
- Review Docker Desktop logs for detailed error information

## 🙏 Thank You!

Your bug reports help make this tool better for all UNL faculty and staff. Even if the problem seems small or obvious to you, it helps us improve the experience for everyone!

---

**Not sure if it's a bug?** Report it anyway! We'd rather help with something simple than miss a real problem.