accessibility_remediator/
├── Dockerfile
├── docker-compose.yml
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py                # Entry point for batch processing
│   ├── pptx_processor.py      # Handles PowerPoint files
│   ├── html_processor.py      # Handles HTML slide decks
│   ├── ai_assistant.py        # Interface to local Ollama model
│   ├── contrast_checker.py    # WCAG contrast validation
│   ├── alt_text_generator.py  # Image captioning and alt text via LLM
│   ├── link_checker.py        # Finds and rewrites vague link text
│   ├── report_generator.py    # Markdown or HTML reports
│   ├── utils.py               # Shared helpers (color parsing, etc.)
│   └── templates/
│       └── report_template.md.jinja  # Jinja2 template for reports
└── test_data/
    ├── sample.pptx
    └── sample.html