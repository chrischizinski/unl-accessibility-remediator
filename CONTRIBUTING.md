# Contributing to UNL Accessibility Remediator

Thank you for your interest in improving digital accessibility! This project helps educational institutions comply with ADA Title II requirements and WCAG 2.1 Level AA standards.

## 🎯 Project Goals

- Help faculty create accessible digital course materials
- Automate WCAG 2.1 Level AA compliance checking
- Provide AI-powered accessibility improvements
- Support UNL's goal of full compliance by 2025-26 academic year

## 🤝 How to Contribute

### Reporting Issues

**Before submitting an issue:**
1. Check existing issues to avoid duplicates
2. Test with the latest version
3. Try the troubleshooting steps in documentation

**When submitting an issue:**
- Use descriptive titles
- Include your operating system and Docker version
- Provide sample files (if applicable and non-sensitive)
- Include error messages and logs
- Describe expected vs actual behavior

### Suggesting Features

We welcome suggestions for:
- Additional accessibility checks
- New file format support
- UI/UX improvements
- Integration with other tools
- Performance optimizations

### Code Contributions

**Development Setup:**
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/unl-accessibility-remediator.git
cd unl-accessibility-remediator

# Start development environment
docker-compose up --build

# Run tests (when available)
docker-compose exec accessibility-remediator python -m pytest
```

**Pull Request Process:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Update documentation as needed
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request with description of changes

**Code Standards:**
- Follow PEP 8 for Python code
- Include docstrings for functions and classes
- Add type hints where appropriate
- Write tests for new features
- Update CLAUDE.md for AI-related changes

### Documentation Improvements

Help improve:
- Setup instructions for different operating systems
- Troubleshooting guides
- Accessibility best practices
- User interface documentation
- API documentation

### Testing

**Test Categories:**
- Unit tests for individual functions
- Integration tests for AI components
- End-to-end tests for full workflows
- Accessibility testing of the web interface
- Cross-platform compatibility testing

**Test Files:**
```
tests/
├── unit/
│   ├── test_contrast_checker.py
│   ├── test_alt_text_generator.py
│   └── test_pptx_processor.py
├── integration/
│   ├── test_ai_assistant.py
│   └── test_web_interface.py
└── fixtures/
    ├── sample.pptx
    └── sample.html
```

## 🏗️ Project Structure

```
unl-accessibility-remediator/
├── accessibility_remediator/     # Main application code
│   ├── app/                     # Core processing modules
│   ├── web/                     # Web interface
│   └── utils.py                 # Utility functions
├── docs/                        # Documentation and guides
├── tests/                       # Test suite
├── scripts/                     # Setup and utility scripts
└── README.md                    # Main documentation
```

## 🔍 Accessibility Focus Areas

When contributing, please consider:

**WCAG 2.1 Level AA Requirements:**
- Perceivable: Alt text, color contrast, text scaling
- Operable: Keyboard navigation, timing, seizures
- Understandable: Readable text, predictable functionality
- Robust: Assistive technology compatibility

**Priority Areas for Improvement:**
1. Alt text generation accuracy
2. Color contrast detection and suggestions
3. Link text analysis and improvements
4. Heading structure validation
5. Table accessibility checking
6. Form accessibility (future)

## 🎓 Educational Context

This tool serves educational institutions, so contributions should:
- Understand academic workflows
- Consider faculty time constraints
- Support diverse technical skill levels
- Integrate with common educational tools
- Respect student privacy and data security

## 📋 Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Community help needed
- `accessibility`: Accessibility-related improvements
- `ai-model`: AI/ML model improvements
- `web-interface`: Frontend/UI changes
- `docker`: Docker or deployment issues

## 🚀 Release Process

**Version Numbering:**
- Major releases: Breaking changes or major new features
- Minor releases: New features, backwards compatible
- Patch releases: Bug fixes and small improvements

**Release Checklist:**
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers bumped
- [ ] GitHub release created
- [ ] Docker images updated

## 📞 Getting Help

**For Contributors:**
- Open an issue for questions
- Check existing documentation
- Review similar projects for inspiration

**For UNL Faculty:**
- Use the tool's web interface
- Refer to user documentation
- Contact UNL support resources

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs

Thank you for helping make digital education more accessible!

---

**University of Nebraska–Lincoln**  
*Digital Accessibility Initiative*