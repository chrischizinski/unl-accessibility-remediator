#!/usr/bin/env python3
"""
Accessibility Remediator Tool - Main CLI Entry Point

This tool analyzes slide decks (.pptx and .html) for WCAG 2.1 AA accessibility issues
and uses AI to suggest or apply fixes automatically.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from app.pptx_processor import PowerPointProcessor
from app.html_processor import HTMLProcessor
from app.ai_assistant import AIAssistant
from app.report_generator import ReportGenerator


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_file_path(file_path: str) -> Path:
    """Validate that the input file exists and has supported extension."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    supported_extensions = {'.pptx', '.html', '.htm'}
    if path.suffix.lower() not in supported_extensions:
        raise ValueError(f"Unsupported file type: {path.suffix}. Supported: {supported_extensions}")
    
    return path


def process_slide_deck(
    input_file: Path,
    output_dir: Path,
    ollama_host: str,
    model_name: str,
    auto_fix: bool,
    verbose: bool
) -> None:
    """Process a single slide deck file."""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting processing of: {input_file}")
    logger.info(f"Output directory: {output_dir}")
    
    # Initialize AI assistant
    try:
        ai_assistant = AIAssistant(host=ollama_host, model=model_name)
        logger.info(f"Connected to Ollama at {ollama_host} using model '{model_name}'")
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        sys.exit(1)
    
    # Choose appropriate processor based on file extension
    processor = None
    if input_file.suffix.lower() == '.pptx':
        processor = PowerPointProcessor(ai_assistant=ai_assistant)
        logger.info("Using PowerPoint processor")
    elif input_file.suffix.lower() in {'.html', '.htm'}:
        processor = HTMLProcessor(ai_assistant=ai_assistant)
        logger.info("Using HTML processor")
    
    if not processor:
        logger.error(f"No processor available for file type: {input_file.suffix}")
        sys.exit(1)
    
    # Process the slide deck
    try:
        logger.info("Analyzing slide deck for accessibility issues...")
        analysis_results = processor.analyze_accessibility(input_file)
        
        logger.info(f"Found {len(analysis_results.slides)} slides to process")
        
        # Apply automatic fixes if requested
        if auto_fix:
            logger.info("Applying automatic fixes...")
            fixed_results = processor.apply_fixes(analysis_results, input_file, output_dir)
            logger.info(f"Applied {len(fixed_results.automatic_fixes)} automatic fixes")
        else:
            logger.info("Skipping automatic fixes (use --auto-fix to enable)")
            fixed_results = analysis_results
        
        # Generate report
        logger.info("Generating accessibility report...")
        report_generator = ReportGenerator()
        report_path = output_dir / f"{input_file.stem}_accessibility_report.md"
        
        report_generator.generate_report(
            results=fixed_results,
            output_path=report_path,
            original_file=input_file
        )
        
        logger.info(f"Report generated: {report_path}")
        logger.info("Processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error processing slide deck: {e}")
        if verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered accessibility remediation tool for slide decks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a PowerPoint file
  python main.py input.pptx --output ./reports

  # Auto-fix a presentation with custom Ollama settings
  python main.py slides.pptx --auto-fix --ollama-host localhost:11434 --model llama2

  # Process HTML slides with verbose logging
  python main.py deck.html --output ./output --verbose
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the slide deck file (.pptx or .html)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./output",
        help="Output directory for processed files and reports (default: ./output)"
    )
    
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically apply safe fixes (alt text, link improvements, etc.)"
    )
    
    parser.add_argument(
        "--ollama-host",
        type=str,
        default="localhost:11434",
        help="Ollama server host:port (default: localhost:11434)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="llama2",
        help="Ollama model name to use (default: llama2)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate input file
        input_path = validate_file_path(args.input_file)
        
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process the slide deck
        process_slide_deck(
            input_file=input_path,
            output_dir=output_path,
            ollama_host=args.ollama_host,
            model_name=args.model,
            auto_fix=args.auto_fix,
            verbose=args.verbose
        )
        
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Input validation error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()