# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Title II compliance project focused on accessibility remediation. The project is currently in planning/documentation phase with a proposed architecture for an accessibility tool that processes PowerPoint and HTML slide decks.

## Project Structure

- `docs/` - Contains project documentation including:
  - `accessibility_tool_structure.md` - Detailed architecture for the planned accessibility remediator tool
  - Word documents with Title II compliance information

## Planned Architecture (Not Yet Implemented)

Based on the documentation, this project plans to implement an `accessibility_remediator` tool with the following structure:

- **Python-based application** using Docker containerization
- **Core processors**: PowerPoint (`pptx_processor.py`) and HTML (`html_processor.py`) slide deck handlers
- **AI integration**: Local Ollama model interface (`ai_assistant.py`) for intelligent accessibility improvements
- **Accessibility features**:
  - WCAG contrast validation (`contrast_checker.py`)
  - AI-powered alt text generation (`alt_text_generator.py`)
  - Link text analysis and improvement (`link_checker.py`)
- **Reporting**: Markdown/HTML report generation with Jinja2 templates
- **Testing**: Sample files for validation

## Development Status

This repository currently contains only documentation and planning materials. The actual codebase described in the architecture documentation has not yet been implemented.

## Future Development Notes

When implementing the planned architecture:
- The main application entry point will be `app/main.py`
- Docker setup will use `Dockerfile` and `docker-compose.yml`
- Python dependencies will be managed via `requirements.txt`
- Testing data should be placed in `test_data/` directory