# 📁 Test Sample Files

This directory contains sample files for testing the UNL Accessibility Remediator.

## 📄 Available Test Files

### `sample_presentation.html`
- **Type**: HTML slide presentation
- **Size**: ~5KB
- **Slides**: 5 slides with various accessibility issues
- **Purpose**: Test comprehensive accessibility analysis

**Intentional Issues Included:**
- ❌ Missing alt text on images
- ❌ Poor alt text ("image", "decorative border graphic")
- ❌ Poor color contrast text
- ❌ Vague link text ("click here", "more info")
- ❌ Missing heading hierarchy (h3 without h2)
- ❌ Very small text (8px)
- ❌ All caps text
- ✅ Some correctly implemented accessibility features for comparison

### PowerPoint Test Files

**Note**: PowerPoint (.pptx) files are binary and cannot be created as text files. To create test PowerPoint files:

1. **Create in PowerPoint** with these intentional issues:
   - Images without alt text
   - Vague link text ("click here")
   - Poor color contrast
   - Missing slide titles
   - Very small fonts
   - All caps text

2. **Good examples to include**:
   - Proper alt text descriptions
   - Descriptive link text
   - Good color contrast
   - Clear slide titles
   - Appropriate font sizes

3. **Suggested test presentations**:
   - `small_presentation.pptx` (5-10 slides)
   - `medium_presentation.pptx` (15-25 slides)
   - `large_presentation.pptx` (50+ slides)
   - `complex_presentation.pptx` (many images, charts, multimedia)

## 🧪 Using Test Files

### Quick Test
```bash
# Test with HTML file
./start-accessibility-tool.sh
# Upload sample_presentation.html via web interface
```

### Comprehensive Testing
```bash
# Run full test suite
./testing/run_tests.sh
```

### Manual Testing Steps

1. **Start the tool**
2. **Upload sample files**
3. **Review generated reports**
4. **Verify issues detected**:
   - Missing/poor alt text
   - Color contrast problems
   - Link text issues
   - Structural problems
   - Font size issues

## 📊 Expected Test Results

### For `sample_presentation.html`

**Expected Issues Detected:**
- 🔍 **Images**: 3-4 alt text issues
- 🎨 **Colors**: 1-2 contrast issues  
- 🔗 **Links**: 2-3 vague link text issues
- 📝 **Structure**: 1 heading hierarchy issue
- 📖 **Text**: 2 text formatting issues

**Expected Accessibility Score**: 60-70% (multiple issues present)

**Expected Fixes Applied** (if automatic fixes enabled):
- Basic alt text added to images without descriptions
- Some link text improvements
- Font size corrections where safe

**Expected Manual Review Items**:
- Complex image descriptions
- Color scheme adjustments
- Heading structure reorganization
- All caps text conversion

## 🎯 Creating Your Own Test Files

### Good Test Presentations Should Include:

**Positive Examples (should pass)**:
- Images with descriptive alt text
- High contrast color combinations
- Clear, descriptive link text
- Proper heading hierarchy
- Appropriate font sizes
- Mixed case text

**Negative Examples (should be flagged)**:
- Images with no alt text
- Images with poor alt text ("image", "photo")
- Low contrast text/background combinations
- Vague links ("click here", "read more", "more info")
- Skipped heading levels (h1 → h3)
- Very small text (< 12px)
- All uppercase text
- Color as the only way to convey information

### Real-World Test Cases

Consider testing with:
- **Course syllabi converted to slides**
- **Lecture presentations with charts/graphs** 
- **Student presentation templates**
- **Meeting slide decks**
- **Training materials**

## 📞 Support

If you have sample files to contribute or need help creating test cases:
- Add files to this directory
- Update this README with descriptions
- Test files should represent real UNL use cases
- Include both problematic and well-designed examples

---

**University of Nebraska–Lincoln**  
*Digital Accessibility Testing*