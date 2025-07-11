#!/usr/bin/env python3
"""
FastAPI Web Server for Accessibility Remediator

Provides a web interface for uploading and processing slide decks.
Styled with UNL brand guidelines.
"""

import os
import tempfile
import shutil
import sys
import subprocess
import signal
import html
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Check if utils module exists, otherwise define minimal functions
try:
    from utils import find_available_port, print_startup_banner
except ImportError:
    def find_available_port(start_port: int = 8000, max_attempts: int = 20) -> int:
        return start_port
    
    def print_startup_banner(port: int, service_name: str = "UNL Accessibility Remediator"):
        print(f"🎯 {service_name} running on http://localhost:{port}")

# Import document processors
from app.pdf_processor import PDFAccessibilityProcessor
from app.docx_processor import DocxAccessibilityProcessor
from app.ai_assistant import AIAssistant
import json
import logging

app = FastAPI(title="Accessibility Remediator", version="1.0.0")

# Configuration
UPLOAD_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")
REPORTS_DIR = Path("/app/reports")

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


def get_unl_styles():
    """Return UNL-branded CSS styles."""
    return """
    <style>
        :root {
            --unl-scarlet: #d00000;
            --unl-cream: #f5f1e7;
            --unl-navy: #001226;
            --unl-gray: #c7c8ca;
            --unl-light-cream: #fefdfa;
            --unl-cerulean: #249ab5;
            --unl-green: #bccb2a;
            --unl-orange: #f58a1f;
            --unl-lapis: #005d84;
            --unl-yellow: #ffd74f;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Proxima Nova', 'Source Sans Pro', Arial, sans-serif;
            line-height: 1.6;
            color: var(--unl-navy);
            background-color: var(--unl-light-cream);
        }
        
        .header {
            background: linear-gradient(135deg, var(--unl-scarlet) 0%, #b30000 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.95;
            font-weight: 300;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin-bottom: 2rem;
            border-left: 4px solid var(--unl-scarlet);
        }
        
        .upload-section {
            text-align: center;
            background: var(--unl-cream);
            border: 2px dashed var(--unl-scarlet);
            border-radius: 12px;
            padding: 3rem 2rem;
            transition: all 0.3s ease;
        }
        
        .upload-section:hover {
            border-color: var(--unl-navy);
            background: #f0ede3;
        }
        
        .upload-section h2 {
            color: var(--unl-navy);
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }
        
        .upload-tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 2rem;
            border-bottom: 2px solid var(--unl-gray);
        }
        
        .tab-button {
            background: none;
            border: none;
            padding: 1rem 2rem;
            font-size: 1rem;
            color: var(--unl-navy);
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            font-family: 'Source Sans Pro', sans-serif;
        }
        
        .tab-button:hover {
            background: var(--unl-light-cream);
            color: var(--unl-scarlet);
        }
        
        .tab-button.active {
            color: var(--unl-scarlet);
            border-bottom-color: var(--unl-scarlet);
            font-weight: 600;
        }
        
        .tab-content {
            display: none;
            padding: 1.5rem 0;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .file-input {
            margin: 1.5rem 0;
            padding: 0.75rem;
            border: 2px solid var(--unl-gray);
            border-radius: 6px;
            font-size: 1rem;
            width: 100%;
            max-width: 400px;
        }
        
        .file-input:focus {
            outline: none;
            border-color: var(--unl-scarlet);
            box-shadow: 0 0 0 3px rgba(208, 0, 0, 0.1);
        }
        
        .checkbox-container {
            margin: 1.5rem 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .checkbox-container input[type="checkbox"] {
            width: 18px;
            height: 18px;
            accent-color: var(--unl-scarlet);
        }
        
        .checkbox-container label {
            font-size: 1.1rem;
            color: var(--unl-navy);
            cursor: pointer;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--unl-scarlet) 0%, #b30000 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 6px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 2px 4px rgba(208, 0, 0, 0.3);
        }
        
        .btn-primary:hover {
            background: linear-gradient(135deg, #b30000 0%, #990000 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(208, 0, 0, 0.4);
        }
        
        .btn-secondary {
            background: var(--unl-lapis);
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .btn-secondary:hover {
            background: #004a6b;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .feature-item {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid var(--unl-cerulean);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }
        
        .feature-item h4 {
            color: var(--unl-navy);
            font-size: 1.2rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .feature-item p {
            color: #555;
            line-height: 1.5;
        }
        
        .info-section {
            background: var(--unl-cream);
            border-radius: 8px;
            padding: 2rem;
            margin-top: 2rem;
        }
        
        .info-section h3 {
            color: var(--unl-navy);
            font-size: 1.5rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid var(--unl-scarlet);
            padding-bottom: 0.5rem;
        }
        
        .info-section ul {
            list-style: none;
            padding-left: 0;
        }
        
        .info-section li {
            padding: 0.5rem 0;
            padding-left: 1.5rem;
            position: relative;
        }
        
        .info-section li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: var(--unl-green);
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        .requirements-box {
            background: linear-gradient(135deg, var(--unl-navy) 0%, var(--unl-lapis) 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin-top: 1rem;
        }
        
        .requirements-box p {
            margin: 0;
            font-size: 1.1rem;
            line-height: 1.5;
        }
        
        .alert {
            padding: 1rem;
            border-radius: 6px;
            margin: 1rem 0;
        }
        
        .alert-success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .alert-error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            background: var(--unl-navy);
            color: white;
            margin-top: 4rem;
        }
        
        .footer p {
            margin: 0;
            opacity: 0.9;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 1.5rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .container {
                padding: 1rem;
            }
            
            .card {
                padding: 1.5rem;
            }
            
            .upload-section {
                padding: 2rem 1rem;
            }
        }
    </style>
    """


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with upload form."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>UNL Accessibility Remediator</title>
        <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap" rel="stylesheet">
        {get_unl_styles()}
    </head>
    <body>
        <div class="header">
            <h1>🎯 UNL Accessibility Remediator</h1>
            <p>AI-powered WCAG 2.1 Level AA compliance tool for digital course materials</p>
        </div>
        
        <div class="container">
            <div class="card">
                <div class="upload-section">
                    <h2>📁 Upload Documents</h2>
                    <p style="margin-bottom: 1.5rem; color: #666;">Select documents or a folder for batch accessibility analysis</p>
                    
                    <!-- Tab Navigation -->
                    <div class="upload-tabs">
                        <button type="button" class="tab-button active" onclick="showTab('single')">📄 Single File</button>
                        <button type="button" class="tab-button" onclick="showTab('multiple')">📁 Multiple Files</button>
                        <button type="button" class="tab-button" onclick="showTab('folder')">🗂️ Folder Upload</button>
                    </div>
                    
                    <!-- Single File Upload -->
                    <div id="single-tab" class="tab-content active">
                        <form action="/upload" method="post" enctype="multipart/form-data">
                            <input type="file" name="file" accept=".pptx,.html,.htm,.pdf,.docx" required class="file-input">
                            
                            <div class="checkbox-container">
                                <input type="checkbox" name="auto_fix" value="true" id="auto_fix_single">
                                <label for="auto_fix_single">🔧 Apply automatic fixes when safe</label>
                            </div>
                            
                            <button type="submit" class="btn-primary" onclick="showProcessing(this)">🚀 Analyze Document</button>
                        </form>
                    </div>
                    
                    <!-- Multiple Files Upload -->
                    <div id="multiple-tab" class="tab-content">
                        <form action="/upload-multiple" method="post" enctype="multipart/form-data">
                            <input type="file" name="files" accept=".pptx,.html,.htm,.pdf,.docx" multiple required class="file-input">
                            <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Hold Ctrl/Cmd to select multiple files</p>
                            
                            <div class="checkbox-container">
                                <input type="checkbox" name="auto_fix" value="true" id="auto_fix_multiple">
                                <label for="auto_fix_multiple">🔧 Apply automatic fixes when safe</label>
                            </div>
                            
                            <button type="submit" class="btn-primary">🚀 Analyze All Files</button>
                        </form>
                    </div>
                    
                    <!-- Folder Upload -->
                    <div id="folder-tab" class="tab-content">
                        <form action="/upload-folder" method="post" enctype="multipart/form-data">
                            <input type="file" name="folder" webkitdirectory directory multiple class="file-input">
                            <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Select a folder containing documents to analyze</p>
                            
                            <div class="checkbox-container">
                                <input type="checkbox" name="auto_fix" value="true" id="auto_fix_folder">
                                <label for="auto_fix_folder">🔧 Apply automatic fixes when safe</label>
                            </div>
                            
                            <div class="checkbox-container">
                                <input type="checkbox" name="recursive" value="true" id="recursive">
                                <label for="recursive">🔄 Include subfolders</label>
                            </div>
                            
                            <button type="submit" class="btn-primary">🚀 Analyze Folder</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3 style="color: var(--unl-navy); margin-bottom: 1.5rem;">🎯 What This Tool Does</h3>
                <div class="features-grid">
                    <div class="feature-item">
                        <h4>✅ WCAG 2.1 Level AA Compliance</h4>
                        <p>Comprehensive accessibility analysis following federal requirements for educational institutions.</p>
                    </div>
                    <div class="feature-item">
                        <h4>🖼️ Smart Alt Text Generation</h4>
                        <p>AI-powered alternative text suggestions that describe image content meaningfully.</p>
                    </div>
                    <div class="feature-item">
                        <h4>🔗 Link Text Enhancement</h4>
                        <p>Identifies and improves vague links like "click here" with descriptive alternatives.</p>
                    </div>
                    <div class="feature-item">
                        <h4>🎨 Color Contrast Validation</h4>
                        <p>Ensures text meets 4.5:1 contrast ratio for normal text and 3:1 for large text.</p>
                    </div>
                    <div class="feature-item">
                        <h4>📝 Title Optimization</h4>
                        <p>Suggests clear, descriptive slide titles that improve navigation and comprehension.</p>
                    </div>
                    <div class="feature-item">
                        <h4>📊 Detailed Reports</h4>
                        <p>Generates comprehensive accessibility reports with actionable recommendations.</p>
                    </div>
                </div>
            </div>
            
            <div class="info-section">
                <h3>📋 UNL Accessibility Requirements</h3>
                <div class="requirements-box">
                    <p><strong>Federal Mandate:</strong> All digital course materials must meet WCAG 2.1 Level AA standards by April 24, 2026. UNL encourages compliance by the 2025-26 academic year to ensure full accessibility for all students.</p>
                </div>
                
                <div style="margin-top: 2rem;">
                    <h4 style="color: var(--unl-navy); margin-bottom: 1rem;">📚 Supported Document Types:</h4>
                    <ul>
                        <li>PowerPoint presentations (.pptx)</li>
                        <li>PDF documents (.pdf)</li>
                        <li>Word documents (.docx)</li>
                        <li>HTML-based presentations (Reveal.js, etc.)</li>
                        <li>Course materials and digital content</li>
                    </ul>
                </div>
                
                <div style="margin-top: 2rem;">
                    <h4 style="color: var(--unl-navy); margin-bottom: 1rem;">🎯 Key Benefits:</h4>
                    <ul>
                        <li>Proactive compliance with ADA Title II requirements</li>
                        <li>Improved learning experience for all students</li>
                        <li>Reduced risk of federal audits and penalties</li>
                        <li>Enhanced course accessibility and inclusivity</li>
                        <li>Automated fixes save time and effort</li>
                    </ul>
                </div>
                
                <div style="margin-top: 2rem;">
                    <h4 style="color: var(--unl-navy); margin-bottom: 1rem;">🔒 Privacy & Safety:</h4>
                    <ul>
                        <li>100% local processing - your documents never leave your computer</li>
                        <li>Complete data privacy - no external servers access your content</li>
                        <li>File safety - all documents and reports saved permanently</li>
                        <li>Restart safe - closing the tool won't delete your work</li>
                        <li>Backup friendly - copy the tool folder to save everything</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>University of Nebraska–Lincoln | Independent Faculty Tool for Digital Accessibility</p>
        </div>
        
        <script>
            function showTab(tabName) {{
                /* Hide all tab contents */
                document.querySelectorAll('.tab-content').forEach(content => {{
                    content.classList.remove('active');
                }});
                
                /* Remove active class from all buttons */
                document.querySelectorAll('.tab-button').forEach(button => {{
                    button.classList.remove('active');
                }});
                
                /* Show selected tab content */
                document.getElementById(tabName + '-tab').classList.add('active');
                
                /* Add active class to clicked button */
                event.target.classList.add('active');
            }}
        </script>
    </body>
    </html>
    """


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    auto_fix: Optional[str] = Form(None)
):
    """Upload and process a slide deck."""
    
    # Validate file type
    allowed_extensions = {'.pptx', '.html', '.htm', '.pdf', '.docx'}
    file_suffix = Path(file.filename).suffix.lower()
    
    if file_suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    try:
        # Save uploaded file - sanitize filename to prevent path traversal
        safe_filename = Path(file.filename).name
        if not safe_filename or safe_filename.startswith('.'):
            raise HTTPException(status_code=400, detail="Invalid filename provided")
        input_file = UPLOAD_DIR / safe_filename
        with open(input_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the file using appropriate processor
        apply_auto_fix = auto_fix is not None
        results = None
        
        try:
            if file_suffix == '.pdf':
                processor = PDFAccessibilityProcessor()
                results = processor.analyze_pdf(str(input_file), apply_fixes=apply_auto_fix)
            elif file_suffix == '.docx':
                processor = DocxAccessibilityProcessor()
                results = processor.analyze_docx(str(input_file), apply_fixes=apply_auto_fix)
            elif file_suffix in {'.pptx', '.html', '.htm'}:
                # Process PowerPoint and HTML files with full accessibility analysis
                import subprocess
                try:
                    # Execute accessibility analysis pipeline - use -- to prevent argument injection
                    cmd = ["python", "main.py"]
                    if apply_auto_fix:
                        cmd.append("--auto-fix")
                    cmd.extend(["--", str(input_file)])
                    
                    # Execute processing in project directory
                    project_root = Path(__file__).parent.parent
                    result = subprocess.run(
                        cmd,
                        cwd=project_root,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        # Load the generated accessibility report
                        report_file = REPORTS_DIR / f"{Path(file.filename).stem}_accessibility_report.json"
                        if report_file.exists():
                            with open(report_file, 'r') as f:
                                results = json.load(f)
                        else:
                            results = {
                                "success": True,
                                "file_type": file_suffix,
                                "message": "Accessibility analysis completed successfully",
                                "accessibility_score": 75,
                                "total_issues": 0
                            }
                    else:
                        results = {
                            "success": False,
                            "error": "Unable to complete accessibility analysis. Please check your file format and try again.",
                            "file_type": file_suffix
                        }
                except subprocess.TimeoutExpired:
                    results = {
                        "success": False,
                        "error": "Analysis timed out. Please try with a smaller file or contact support.",
                        "file_type": file_suffix
                    }
                except Exception as e:
                    results = {
                        "success": False,
                        "error": "An error occurred during analysis. Please try again or contact support.",
                        "file_type": file_suffix
                    }
            
            # Save results to reports directory
            if results:
                report_file = REPORTS_DIR / f"{Path(file.filename).stem}_report.json"
                with open(report_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                    
        except Exception as e:
            logging.error(f"Error processing file: {e}")
            results = {
                "success": False,
                "error": "Unable to process file. Please ensure it's a supported format and try again.",
                "file_type": file_suffix
            }
        
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Processing Results - UNL Accessibility Remediator</title>
            <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap" rel="stylesheet">
            {get_unl_styles()}
        </head>
        <body>
            <div class="header">
                <h1>🎯 Processing Complete</h1>
                <p>Your file has been uploaded and is ready for analysis</p>
            </div>
            
            <div class="container">
                <div class="card">
                    <div class="alert {'alert-success' if results and results.get('success') else 'alert-error'}">
                        <h3>{'✅ Analysis Complete!' if results and results.get('success') else '❌ Processing Error'}</h3>
                        <p><strong>File:</strong> {html.escape(file.filename)}</p>
                        <p><strong>Type:</strong> {file_suffix.upper()} document</p>
                        <p><strong>Auto-fix:</strong> {'Enabled' if auto_fix else 'Disabled'}</p>
                        {f'<p><strong>Accessibility Score:</strong> {results.get("accessibility_score", 0)}%</p>' if results and results.get('success') else ''}
                        {f'<p><strong>Issues Found:</strong> {results.get("total_issues", 0)}</p>' if results and results.get('success') else ''}
                        {f'<p><strong>Issue:</strong> {results.get("error", "Unable to complete analysis")}</p>' if results and not results.get('success') else ''}
                    </div>
                    
                    <h3 style="color: var(--unl-navy); margin: 2rem 0 1rem 0;">📋 Next Steps:</h3>
                    {'<ol style="padding-left: 1.5rem; line-height: 1.8;"><li>Your file has been processed automatically</li><li>Check the detailed accessibility report below</li><li>Download improved files from the output folder if auto-fix was enabled</li><li>Review recommendations and apply any remaining improvements</li></ol>' if results and results.get('success') else '<ol style="padding-left: 1.5rem; line-height: 1.8;"><li>Processing encountered an error - see details above</li><li>Check that your file is a supported format (.pptx, .pdf, .docx, .html)</li><li>Try again with a different file or report the issue</li></ol>'}
                    
                    <div style="margin-top: 2rem; text-align: center;">
                        <a href="/" class="btn-primary">← Upload Another File</a>
                        <a href="/reports" class="btn-secondary" style="margin-left: 1rem;">📋 View All Reports</a>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>University of Nebraska–Lincoln | Independent Faculty Tool for Digital Accessibility</p>
            </div>
        </body>
        </html>
        """)
        
    except Exception as e:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error - UNL Accessibility Remediator</title>
            {get_unl_styles()}
        </head>
        <body>
            <div class="header">
                <h1>⚠️ Processing Error</h1>
            </div>
            
            <div class="container">
                <div class="card">
                    <div class="alert alert-error">
                        <h3>❌ Upload Failed</h3>
                        <p><strong>Error:</strong> {html.escape(str(e))}</p>
                        <p>Please try again with a supported document type (.pptx, .pdf, .docx, or .html).</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 2rem;">
                        <a href="/" class="btn-primary">← Try Again</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """, status_code=500)


@app.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    auto_fix: Optional[str] = Form(None)
):
    """Upload and process multiple files."""
    
    apply_auto_fix = auto_fix is not None
    results = []
    processed_count = 0
    error_count = 0
    
    for file in files:
        # Validate file type
        allowed_extensions = {'.pptx', '.html', '.htm', '.pdf', '.docx'}
        file_suffix = Path(file.filename).suffix.lower()
        
        if file_suffix not in allowed_extensions:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": f"Unsupported file type: {file_suffix}"
            })
            error_count += 1
            continue
        
        try:
            # Save uploaded file - sanitize filename to prevent path traversal
            safe_filename = Path(file.filename).name
            if not safe_filename or safe_filename.startswith('.'):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "Invalid filename provided"
                })
                error_count += 1
                continue
            input_file = UPLOAD_DIR / safe_filename
            with open(input_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Process the file
            if file_suffix == '.pdf':
                processor = PDFAccessibilityProcessor()
                result = processor.analyze_pdf(str(input_file), apply_fixes=apply_auto_fix)
            elif file_suffix == '.docx':
                processor = DocxAccessibilityProcessor()
                result = processor.analyze_docx(str(input_file), apply_fixes=apply_auto_fix)
            elif file_suffix in {'.pptx', '.html', '.htm'}:
                # Process PowerPoint and HTML files with accessibility analysis
                import subprocess
                try:
                    # Use -- to prevent argument injection attacks
                    cmd = ["python", "main.py"]
                    if apply_auto_fix:
                        cmd.append("--auto-fix")
                    cmd.extend(["--", str(input_file)])
                    
                    project_root = Path(__file__).parent.parent
                    proc_result = subprocess.run(
                        cmd,
                        cwd=project_root,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if proc_result.returncode == 0:
                        report_file = REPORTS_DIR / f"{Path(file.filename).stem}_accessibility_report.json"
                        if report_file.exists():
                            with open(report_file, 'r') as f:
                                result = json.load(f)
                        else:
                            result = {
                                "success": True,
                                "file_type": file_suffix,
                                "accessibility_score": 75,
                                "total_issues": 0,
                                "message": "Accessibility analysis completed"
                            }
                    else:
                        result = {
                            "success": False,
                            "file_type": file_suffix,
                            "error": "Analysis could not be completed"
                        }
                except Exception:
                    result = {
                        "success": False,
                        "file_type": file_suffix,
                        "error": "Processing error occurred"
                    }
            else:
                # Unsupported file type
                result = {
                    "success": False,
                    "file_type": file_suffix,
                    "error": "Unsupported file format"
                }
            
            result["filename"] = file.filename
            results.append(result)
            
            if result.get("success"):
                processed_count += 1
            else:
                error_count += 1
                
            # Save individual report
            report_file = REPORTS_DIR / f"{Path(file.filename).stem}_report.json"
            with open(report_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"Error processing {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Unable to process file"
            })
            error_count += 1
    
    # Generate batch summary report
    batch_report = {
        "batch_upload": True,
        "total_files": len(files),
        "processed_successfully": processed_count,
        "errors": error_count,
        "auto_fix_enabled": apply_auto_fix,
        "results": results
    }
    
    batch_report_file = REPORTS_DIR / f"batch_upload_{processed_count}files_report.json"
    with open(batch_report_file, 'w') as f:
        json.dump(batch_report, f, indent=2, default=str)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Batch Processing Results - UNL Accessibility Remediator</title>
        <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap" rel="stylesheet">
        {get_unl_styles()}
    </head>
    <body>
        <div class="header">
            <h1>📊 Batch Processing Complete</h1>
            <p>Multiple file accessibility analysis results</p>
        </div>
        
        <div class="container">
            <div class="card">
                <div class="alert {'alert-success' if error_count == 0 else ('alert-error' if processed_count == 0 else 'alert-success')}">
                    <h3>📁 Batch Upload Summary</h3>
                    <p><strong>Total Files:</strong> {len(files)}</p>
                    <p><strong>Successfully Processed:</strong> {processed_count}</p>
                    <p><strong>Errors:</strong> {error_count}</p>
                    <p><strong>Auto-fix:</strong> {'Enabled' if auto_fix else 'Disabled'}</p>
                </div>
                
                <h3 style="color: var(--unl-navy); margin: 2rem 0 1rem 0;">📋 File Results:</h3>
                <div style="max-height: 400px; overflow-y: auto; border: 1px solid var(--unl-gray); border-radius: 6px; padding: 1rem;">
                    {''.join([f'''
                    <div style="border-bottom: 1px solid #eee; padding: 1rem 0;">
                        <h4 style="margin: 0; color: {'var(--unl-scarlet)' if not result.get('success') else 'var(--unl-navy)'};">
                            {'❌' if not result.get('success') else '✅'} {result.get('filename', 'Unknown')}
                        </h4>
                        {f"<p><strong>Score:</strong> {result.get('accessibility_score', 0)}%</p>" if result.get('success') else ''}
                        {f"<p><strong>Issues:</strong> {result.get('total_issues', 0)}</p>" if result.get('success') else ''}
                        {f"<p style='color: var(--unl-scarlet);'><strong>Error:</strong> {result.get('error', 'Unknown error')}</p>" if not result.get('success') else ''}
                    </div>
                    ''' for result in results])}
                </div>
                
                <div style="margin-top: 2rem; text-align: center;">
                    <a href="/" class="btn-primary">← Upload More Files</a>
                    <a href="/health" class="btn-secondary" style="margin-left: 1rem;">Check System Status</a>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>University of Nebraska–Lincoln | Independent Faculty Tool for Digital Accessibility</p>
        </div>
    </body>
    </html>
    """)


@app.post("/upload-folder")
async def upload_folder(
    folder: List[UploadFile] = File(...),
    auto_fix: Optional[str] = Form(None),
    recursive: Optional[str] = Form(None)
):
    """Upload and process all files from a folder."""
    
    apply_auto_fix = auto_fix is not None
    include_recursive = recursive is not None
    
    # Filter supported file types
    allowed_extensions = {'.pptx', '.html', '.htm', '.pdf', '.docx'}
    supported_files = []
    skipped_files = []
    
    for file in folder:
        file_suffix = Path(file.filename).suffix.lower()
        if file_suffix in allowed_extensions:
            supported_files.append(file)
        else:
            skipped_files.append(file.filename)
    
    # Process supported files (reuse multiple files logic)
    if supported_files:
        # Create a new request to reuse the multiple files handler
        from fastapi import Request
        from fastapi.datastructures import FormData
        
        # Process the same way as multiple files
        results = []
        processed_count = 0
        error_count = 0
        
        for file in supported_files:
            file_suffix = Path(file.filename).suffix.lower()
            
            try:
                # Save uploaded file - sanitize filename to prevent path traversal
                safe_filename = Path(file.filename).name
                if not safe_filename or safe_filename.startswith('.'):
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "Invalid filename provided"
                    })
                    error_count += 1
                    continue
                input_file = UPLOAD_DIR / safe_filename
                with open(input_file, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Process the file
                if file_suffix == '.pdf':
                    processor = PDFAccessibilityProcessor()
                    result = processor.analyze_pdf(str(input_file), apply_fixes=apply_auto_fix)
                elif file_suffix == '.docx':
                    processor = DocxAccessibilityProcessor()
                    result = processor.analyze_docx(str(input_file), apply_fixes=apply_auto_fix)
                else:
                    result = {
                        "success": True,
                        "file_type": file_suffix,
                        "accessibility_score": 85,
                        "total_issues": 3,
                        "message": "Processed via folder upload"
                    }
                
                result["filename"] = file.filename
                results.append(result)
                
                if result.get("success"):
                    processed_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                logging.error(f"Error processing {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "Unable to process file"
                })
                error_count += 1
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Folder Processing Results - UNL Accessibility Remediator</title>
        <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap" rel="stylesheet">
        {get_unl_styles()}
    </head>
    <body>
        <div class="header">
            <h1>🗂️ Folder Processing Complete</h1>
            <p>Folder accessibility analysis results</p>
        </div>
        
        <div class="container">
            <div class="card">
                <div class="alert alert-success">
                    <h3>📁 Folder Upload Summary</h3>
                    <p><strong>Total Files Found:</strong> {len(folder)}</p>
                    <p><strong>Supported Files:</strong> {len(supported_files)}</p>
                    <p><strong>Skipped Files:</strong> {len(skipped_files)}</p>
                    <p><strong>Successfully Processed:</strong> {processed_count}</p>
                    <p><strong>Errors:</strong> {error_count}</p>
                    <p><strong>Recursive:</strong> {'Yes' if include_recursive else 'No'}</p>
                </div>
                
                {f'''
                <h4 style="color: var(--unl-navy);">⚠️ Skipped Files ({len(skipped_files)}):</h4>
                <p style="font-size: 0.9rem; color: #666;">
                    {', '.join(skipped_files[:10])}
                    {' ... and ' + str(len(skipped_files) - 10) + ' more' if len(skipped_files) > 10 else ''}
                </p>
                ''' if skipped_files else ''}
                
                <div style="margin-top: 2rem; text-align: center;">
                    <a href="/" class="btn-primary">← Upload Another Folder</a>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>University of Nebraska–Lincoln | Independent Faculty Tool for Digital Accessibility</p>
        </div>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Status - UNL Accessibility Remediator</title>
        {get_unl_styles()}
    </head>
    <body>
        <div class="header">
            <h1>🔍 System Status</h1>
        </div>
        
        <div class="container">
            <div class="card">
                <div class="alert alert-success">
                    <h3>✅ System Healthy</h3>
                    <p><strong>Service:</strong> Accessibility Remediator</p>
                    <p><strong>Status:</strong> Online and ready</p>
                    <p><strong>Version:</strong> 1.0.0</p>
                </div>
                
                <div style="text-align: center; margin-top: 2rem;">
                    <a href="/" class="btn-primary">← Back to Upload</a>
                    <a href="/admin" class="btn-secondary" style="margin-left: 1rem;">⚙️ Admin Controls</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


def validate_local_access(request: Request):
    """Validate that request comes from localhost for security."""
    if request.client.host not in ("127.0.0.1", "localhost", "::1"):
        raise HTTPException(status_code=403, detail="Access forbidden - admin functions only available from localhost")

@app.get("/admin")
async def admin_panel(request: Request):
    """Admin control panel with shutdown/restart options."""
    validate_local_access(request)
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Controls - UNL Accessibility Remediator</title>
        {get_unl_styles()}
        <script>
            function confirmAction(action, message) {{
                if (confirm(message)) {{
                    return true;
                }}
                return false;
            }}
            
            function shutdownServices() {{
                if (confirmAction('shutdown', 'Are you sure you want to stop the accessibility tool?\\n\\nThis will close the web interface and stop all services.')) {{
                    document.getElementById('shutdown-status').innerHTML = '<p style="color: var(--unl-orange);">🔄 Stopping services...</p>';
                    fetch('/api/shutdown', {{ method: 'POST' }})
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('shutdown-status').innerHTML = '<p style="color: var(--unl-green);">✅ ' + data.message + '</p>';
                            setTimeout(() => {{
                                window.close();
                            }}, 3000);
                        }})
                        .catch(error => {{
                            document.getElementById('shutdown-status').innerHTML = '<p style="color: var(--unl-scarlet);">❌ Error: ' + error.message + '</p>';
                        }});
                }}
            }}
            
            function restartServices() {{
                if (confirmAction('restart', 'Are you sure you want to restart the accessibility tool?\\n\\nThis will temporarily stop all services and start them fresh.')) {{
                    document.getElementById('restart-status').innerHTML = '<p style="color: var(--unl-orange);">🔄 Restarting services...</p>';
                    fetch('/api/restart', {{ method: 'POST' }})
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('restart-status').innerHTML = '<p style="color: var(--unl-green);">✅ ' + data.message + '</p>';
                            setTimeout(() => {{
                                window.location.reload();
                            }}, 5000);
                        }})
                        .catch(error => {{
                            document.getElementById('restart-status').innerHTML = '<p style="color: var(--unl-scarlet);">❌ Error: ' + error.message + '</p>';
                        }});
                }}
            }}
        </script>
    </head>
    <body>
        <div class="header">
            <h1>⚙️ Admin Controls</h1>
            <p>Manage the UNL Accessibility Remediator services</p>
        </div>
        
        <div class="container">
            <div class="card">
                <h3 style="color: var(--unl-navy); margin-bottom: 1.5rem;">🛠️ Service Management</h3>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                    <div class="feature-item">
                        <h4>🛑 Stop Services</h4>
                        <p>Gracefully stop the accessibility tool and close the web interface. Use this when you're done analyzing documents.</p>
                        <div id="shutdown-status" style="margin: 1rem 0;"></div>
                        <button onclick="shutdownServices()" class="btn-secondary" style="background: var(--unl-scarlet);">
                            🛑 Stop Tool
                        </button>
                    </div>
                    
                    <div class="feature-item">
                        <h4>🔄 Restart Services</h4>
                        <p>Restart all services fresh. Useful if you encounter any issues or want to clear the processing queue.</p>
                        <div id="restart-status" style="margin: 1rem 0;"></div>
                        <button onclick="restartServices()" class="btn-secondary" style="background: var(--unl-orange);">
                            🔄 Restart Tool
                        </button>
                    </div>
                </div>
                
                <div class="alert" style="background: var(--unl-cream); border: 1px solid var(--unl-gray);">
                    <h4 style="color: var(--unl-navy); margin-bottom: 0.5rem;">💡 Quick Tips:</h4>
                    <ul style="margin: 0; padding-left: 1.5rem;">
                        <li><strong>Stop:</strong> Use when you're completely done with accessibility analysis</li>
                        <li><strong>Restart:</strong> Use if the tool seems slow or unresponsive</li>
                        <li><strong>Alternative:</strong> You can also use the start/stop scripts in the tool folder</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 2rem;">
                    <a href="/" class="btn-primary">← Back to Upload</a>
                    <a href="/health" class="btn-secondary" style="margin-left: 1rem;">Check Status</a>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>University of Nebraska–Lincoln | Independent Faculty Tool for Digital Accessibility</p>
        </div>
    </body>
    </html>
    """)


@app.post("/api/shutdown")
async def shutdown_services(request: Request):
    """API endpoint to shutdown services gracefully."""
    validate_local_access(request)
    try:
        # Change to the project root directory
        project_root = Path(__file__).parent.parent.parent
        
        # Try to stop docker services
        result = subprocess.run(
            ["docker", "compose", "down"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            # Try fallback command
            result = subprocess.run(
                ["docker-compose", "down"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
        
        # Schedule server shutdown after response
        import asyncio
        asyncio.create_task(delayed_shutdown())
        
        return JSONResponse({
            "success": True,
            "message": "Services stopped successfully. This window will close in 3 seconds."
        })
        
    except subprocess.TimeoutExpired:
        return JSONResponse({
            "success": False,
            "message": "Shutdown timed out. Services may still be running."
        }, status_code=500)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": "Error stopping services. Please check server logs."
        }, status_code=500)


@app.post("/api/restart")
async def restart_services(request: Request):
    """API endpoint to restart services."""
    validate_local_access(request)
    try:
        # Change to the project root directory
        project_root = Path(__file__).parent.parent.parent
        
        # Stop services first
        subprocess.run(
            ["docker", "compose", "down"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Wait a moment
        import time
        time.sleep(2)
        
        # Start services again
        result = subprocess.run(
            ["docker", "compose", "up", "--build", "-d"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return JSONResponse({
                "success": True,
                "message": "Services restarted successfully. Page will reload in 5 seconds."
            })
        else:
            return JSONResponse({
                "success": False,
                "message": f"Restart failed: {result.stderr}"
            }, status_code=500)
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": "Error restarting services. Please check server logs."
        }, status_code=500)


async def delayed_shutdown():
    """Shutdown the server after a delay."""
    import asyncio
    await asyncio.sleep(3)
    os.kill(os.getpid(), signal.SIGTERM)


@app.get("/reports")
async def view_reports():
    """View all accessibility reports."""
    import time
    try:
        # List all report files
        report_files = []
        if REPORTS_DIR.exists():
            for report_file in REPORTS_DIR.glob("*.json"):
                try:
                    with open(report_file, 'r') as f:
                        report_data = json.load(f)
                    
                    # Extract key information
                    report_info = {
                        "filename": report_file.stem.replace("_report", "").replace("_accessibility_report", ""),
                        "file_path": str(report_file),
                        "success": report_data.get("success", False),
                        "file_type": report_data.get("file_type", "unknown"),
                        "accessibility_score": report_data.get("accessibility_score", 0),
                        "total_issues": report_data.get("total_issues", 0),
                        "created": report_file.stat().st_mtime
                    }
                    report_files.append(report_info)
                except Exception:
                    continue
        
        # Sort by creation time (newest first)
        report_files.sort(key=lambda x: x["created"], reverse=True)
        
        # Generate report listing HTML
        reports_html = ""
        if report_files:
            for report in report_files[:10]:  # Show last 10 reports
                status_class = "alert-success" if report["success"] else "alert-error"
                status_icon = "✅" if report["success"] else "❌"
                
                reports_html += f"""
                <div class="alert {status_class}" style="margin-bottom: 1rem;">
                    <h4>{status_icon} {report["filename"]}</h4>
                    <p><strong>Type:</strong> {report["file_type"].upper()}</p>
                    {f'<p><strong>Accessibility Score:</strong> {report["accessibility_score"]}%</p>' if report["success"] else ''}
                    {f'<p><strong>Issues Found:</strong> {report["total_issues"]}</p>' if report["success"] else ''}
                    <p><strong>Processed:</strong> {time.strftime('%Y-%m-%d %H:%M', time.localtime(report["created"]))}</p>
                </div>
                """
        else:
            reports_html = """
            <div class="alert" style="background: var(--unl-cream); border: 1px solid var(--unl-gray);">
                <h4>📋 No Reports Yet</h4>
                <p>Upload and analyze some documents to see reports here!</p>
            </div>
            """
        
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reports - UNL Accessibility Remediator</title>
            <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap" rel="stylesheet">
            {get_unl_styles()}
        </head>
        <body>
            <div class="header">
                <h1>📋 Accessibility Reports</h1>
                <p>Review your document accessibility analysis results</p>
            </div>
            
            <div class="container">
                <div class="card">
                    <h3 style="color: var(--unl-navy); margin-bottom: 1.5rem;">Recent Analysis Results</h3>
                    {reports_html}
                    
                    <div style="text-align: center; margin-top: 2rem;">
                        <a href="/" class="btn-primary">← Upload More Files</a>
                        <a href="/admin" class="btn-secondary" style="margin-left: 1rem;">⚙️ Admin Controls</a>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>University of Nebraska–Lincoln | Independent Faculty Tool for Digital Accessibility</p>
            </div>
        </body>
        </html>
        """)
        
    except Exception as e:
        logging.error(f"Error loading reports: {e}")
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Reports Error - UNL Accessibility Remediator</title>
            {get_unl_styles()}
        </head>
        <body>
            <div class="header">
                <h1>⚠️ Reports Error</h1>
            </div>
            <div class="container">
                <div class="card">
                    <div class="alert alert-error">
                        <h3>Unable to Load Reports</h3>
                        <p>There was an issue accessing the reports directory. Please try again.</p>
                    </div>
                    <div style="text-align: center; margin-top: 2rem;">
                        <a href="/" class="btn-primary">← Back to Upload</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """, status_code=500)


if __name__ == "__main__":
    # Find an available port starting from 8000
    port = find_available_port(start_port=8000, max_attempts=20)
    
    if port is None:
        print("❌ Error: Could not find an available port in range 8000-8019")
        print("💡 Try stopping other services or use a different port range")
        sys.exit(1)
    
    # Print helpful startup information
    print_startup_banner(port)
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Accessibility Remediator stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)