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
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils import find_available_port, print_startup_banner

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
                    <h2>📁 Upload Your Slide Deck</h2>
                    <p style="margin-bottom: 1.5rem; color: #666;">Select a PowerPoint (.pptx) or HTML slide deck for accessibility analysis</p>
                    
                    <form action="/upload" method="post" enctype="multipart/form-data">
                        <input type="file" name="file" accept=".pptx,.html,.htm" required class="file-input">
                        
                        <div class="checkbox-container">
                            <input type="checkbox" name="auto_fix" value="true" id="auto_fix">
                            <label for="auto_fix">🔧 Apply automatic fixes when safe</label>
                        </div>
                        
                        <button type="submit" class="btn-primary">🚀 Analyze Accessibility</button>
                    </form>
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
                    <h4 style="color: var(--unl-navy); margin-bottom: 1rem;">📚 Covered Content Types:</h4>
                    <ul>
                        <li>PowerPoint presentations and slide decks</li>
                        <li>HTML-based presentations (Reveal.js, etc.)</li>
                        <li>Course materials posted on Canvas</li>
                        <li>Digital documents and multimedia content</li>
                        <li>Third-party vendor content and applications</li>
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
            </div>
        </div>
        
        <div class="footer">
            <p>University of Nebraska–Lincoln | Center for Transformative Teaching | Digital Accessibility Initiative</p>
        </div>
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
    allowed_extensions = {'.pptx', '.html', '.htm'}
    file_suffix = Path(file.filename).suffix.lower()
    
    if file_suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    try:
        # Save uploaded file
        input_file = UPLOAD_DIR / file.filename
        with open(input_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # TODO: Process the file using the main processing pipeline
        # For now, return a placeholder response
        
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
                    <div class="alert alert-success">
                        <h3>✅ File uploaded successfully!</h3>
                        <p><strong>File:</strong> {file.filename}</p>
                        <p><strong>Auto-fix:</strong> {'Enabled' if auto_fix else 'Disabled'}</p>
                        <p><strong>Status:</strong> Ready for processing</p>
                    </div>
                    
                    <h3 style="color: var(--unl-navy); margin: 2rem 0 1rem 0;">📋 Next Steps:</h3>
                    <ol style="padding-left: 1.5rem; line-height: 1.8;">
                        <li>Your file has been saved to the processing queue</li>
                        <li>Run the CLI tool to process: <code style="background: var(--unl-cream); padding: 0.25rem 0.5rem; border-radius: 4px;">python main.py input/{file.filename}</code></li>
                        <li>Check the reports directory for detailed accessibility analysis</li>
                        <li>Review recommendations and apply suggested improvements</li>
                    </ol>
                    
                    <div style="margin-top: 2rem; text-align: center;">
                        <a href="/" class="btn-primary">← Upload Another File</a>
                        <a href="/health" class="btn-secondary" style="margin-left: 1rem;">Check System Status</a>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>University of Nebraska–Lincoln | Digital Accessibility Compliance Tool</p>
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
                        <p><strong>Error:</strong> {str(e)}</p>
                        <p>Please try again with a valid PowerPoint (.pptx) or HTML file.</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 2rem;">
                        <a href="/" class="btn-primary">← Try Again</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """, status_code=500)


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
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


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