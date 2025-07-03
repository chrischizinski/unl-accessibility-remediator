"""
PDF Accessibility Processor for UNL Accessibility Remediator

This module analyzes PDF documents for WCAG 2.1 Level AA compliance issues
and provides recommendations for improvement.
"""

import os
import io
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# PDF processing libraries
try:
    import PyPDF2
    import fitz  # PyMuPDF
    import pdfplumber
except ImportError as e:
    logging.warning(f"PDF processing libraries not available: {e}")
    PyPDF2 = None
    fitz = None
    pdfplumber = None

# OCR for scanned documents
try:
    import pytesseract
    from PIL import Image
except ImportError as e:
    logging.warning(f"OCR libraries not available: {e}")
    pytesseract = None
    Image = None

# Text analysis
try:
    import textstat
except ImportError:
    textstat = None

from .contrast_checker import ContrastChecker

logger = logging.getLogger(__name__)

class PDFAccessibilityProcessor:
    """Analyzes PDF documents for accessibility compliance"""
    
    def __init__(self):
        self.contrast_checker = ContrastChecker()
        self.issues = []
        self.fixes_applied = []
        
    def analyze_pdf(self, file_path: str, apply_fixes: bool = False) -> Dict[str, Any]:
        """
        Analyze a PDF document for accessibility issues
        
        Args:
            file_path: Path to the PDF file
            apply_fixes: Whether to attempt automatic fixes
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting PDF accessibility analysis: {file_path}")
        
        if not self._check_dependencies():
            return self._create_error_result("Required PDF processing libraries not available")
        
        try:
            # Reset for new analysis
            self.issues = []
            self.fixes_applied = []
            
            # Basic file validation
            if not os.path.exists(file_path):
                return self._create_error_result(f"File not found: {file_path}")
            
            # Open and analyze PDF
            with open(file_path, 'rb') as file:
                # Try multiple PDF libraries for best results
                pdf_info = self._extract_pdf_info(file_path)
                text_content = self._extract_text_content(file_path)
                images = self._extract_images(file_path)
                structure = self._analyze_structure(file_path)
                
            # Perform accessibility checks
            self._check_document_structure(pdf_info, structure)
            self._check_text_accessibility(text_content)
            self._check_image_accessibility(images)
            self._check_navigation_accessibility(pdf_info)
            self._check_color_accessibility(file_path)
            
            # Calculate accessibility score
            score = self._calculate_accessibility_score()
            
            # Apply fixes if requested
            if apply_fixes:
                self._apply_automatic_fixes(file_path)
            
            return self._create_analysis_result(
                file_path=file_path,
                score=score,
                pdf_info=pdf_info,
                text_content=text_content,
                images=images,
                structure=structure
            )
            
        except Exception as e:
            logger.error(f"Error analyzing PDF: {str(e)}")
            return self._create_error_result(f"Analysis failed: {str(e)}")
    
    def _check_dependencies(self) -> bool:
        """Check if required libraries are available"""
        missing = []
        if not PyPDF2:
            missing.append("PyPDF2")
        if not fitz:
            missing.append("PyMuPDF")
        if not pdfplumber:
            missing.append("pdfplumber")
            
        if missing:
            logger.error(f"Missing PDF processing libraries: {', '.join(missing)}")
            return False
        return True
    
    def _extract_pdf_info(self, file_path: str) -> Dict[str, Any]:
        """Extract basic PDF metadata and properties"""
        info = {
            "title": None,
            "author": None,
            "subject": None,
            "pages": 0,
            "has_bookmarks": False,
            "is_tagged": False,
            "has_forms": False,
            "language": None,
            "security": {}
        }
        
        try:
            # Using PyPDF2 for metadata
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                info["pages"] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    info["title"] = pdf_reader.metadata.get("/Title")
                    info["author"] = pdf_reader.metadata.get("/Author")
                    info["subject"] = pdf_reader.metadata.get("/Subject")
                
                # Check for bookmarks/outlines
                info["has_bookmarks"] = pdf_reader.outline is not None and len(pdf_reader.outline) > 0
                
                # Check if encrypted
                info["security"]["encrypted"] = pdf_reader.is_encrypted
            
            # Using PyMuPDF for additional metadata
            doc = fitz.open(file_path)
            metadata = doc.metadata
            
            # Check if PDF is tagged (structured)
            info["is_tagged"] = "XML" in str(doc.get_xml_metadata()) if doc.get_xml_metadata() else False
            
            # Check for form fields
            for page_num in range(doc.page_count):
                page = doc[page_num]
                if page.get_form_fields():
                    info["has_forms"] = True
                    break
            
            # Language
            if metadata.get("language"):
                info["language"] = metadata["language"]
            
            doc.close()
            
        except Exception as e:
            logger.warning(f"Error extracting PDF info: {str(e)}")
        
        return info
    
    def _extract_text_content(self, file_path: str) -> Dict[str, Any]:
        """Extract and analyze text content from PDF"""
        content = {
            "pages": [],
            "total_chars": 0,
            "readable_text": True,
            "font_info": [],
            "reading_level": None
        }
        
        try:
            # Use pdfplumber for better text extraction
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    
                    # Get character-level details
                    chars = page.chars
                    
                    page_info = {
                        "page_number": page_num + 1,
                        "text": page_text,
                        "char_count": len(page_text),
                        "fonts": []
                    }
                    
                    # Analyze font usage
                    if chars:
                        fonts_used = {}
                        for char in chars:
                            font_key = f"{char.get('fontname', 'Unknown')}_{char.get('size', 0)}"
                            if font_key not in fonts_used:
                                fonts_used[font_key] = {
                                    "fontname": char.get('fontname', 'Unknown'),
                                    "size": char.get('size', 0),
                                    "count": 0
                                }
                            fonts_used[font_key]["count"] += 1
                        
                        page_info["fonts"] = list(fonts_used.values())
                        content["font_info"].extend(page_info["fonts"])
                    
                    content["pages"].append(page_info)
                    content["total_chars"] += len(page_text)
            
            # Calculate reading level if textstat is available
            if textstat and content["total_chars"] > 100:
                full_text = " ".join([page["text"] for page in content["pages"]])
                content["reading_level"] = {
                    "flesch_reading_ease": textstat.flesch_reading_ease(full_text),
                    "flesch_kincaid_grade": textstat.flesch_kincaid_grade(full_text),
                    "automated_readability_index": textstat.automated_readability_index(full_text)
                }
            
        except Exception as e:
            logger.warning(f"Error extracting text content: {str(e)}")
            content["readable_text"] = False
        
        return content
    
    def _extract_images(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract and analyze images from PDF"""
        images = []
        
        try:
            doc = fitz.open(file_path)
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Extract image
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Basic image info
                        image_info = {
                            "page": page_num + 1,
                            "index": img_index,
                            "width": base_image["width"],
                            "height": base_image["height"],
                            "colorspace": base_image["colorspace"],
                            "has_alt_text": False,  # PDFs don't typically have alt text
                            "is_decorative": False,
                            "size_bytes": len(image_bytes)
                        }
                        
                        # Try to determine if image contains text (needs OCR)
                        if pytesseract and Image:
                            try:
                                pil_image = Image.open(io.BytesIO(image_bytes))
                                extracted_text = pytesseract.image_to_string(pil_image).strip()
                                image_info["contains_text"] = len(extracted_text) > 10
                                image_info["extracted_text"] = extracted_text[:200]  # First 200 chars
                            except Exception:
                                image_info["contains_text"] = False
                        
                        images.append(image_info)
                        
                    except Exception as e:
                        logger.warning(f"Error processing image {img_index} on page {page_num + 1}: {str(e)}")
            
            doc.close()
            
        except Exception as e:
            logger.warning(f"Error extracting images: {str(e)}")
        
        return images
    
    def _analyze_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze document structure and navigation"""
        structure = {
            "has_headings": False,
            "heading_levels": [],
            "has_toc": False,
            "has_bookmarks": False,
            "reading_order": "unknown",
            "tables": [],
            "links": []
        }
        
        try:
            doc = fitz.open(file_path)
            
            # Check for table of contents
            toc = doc.get_toc()
            structure["has_toc"] = len(toc) > 0
            structure["has_bookmarks"] = len(toc) > 0
            
            if toc:
                structure["heading_levels"] = [item[0] for item in toc]  # Extract levels
                structure["has_headings"] = True
            
            # Analyze each page for structure
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Look for tables
                tables = page.find_tables()
                for table in tables:
                    structure["tables"].append({
                        "page": page_num + 1,
                        "rows": table.row_count if hasattr(table, 'row_count') else 0,
                        "cols": table.col_count if hasattr(table, 'col_count') else 0
                    })
                
                # Look for links
                links = page.get_links()
                for link in links:
                    structure["links"].append({
                        "page": page_num + 1,
                        "type": link.get("kind", "unknown"),
                        "uri": link.get("uri", ""),
                        "text": "Unknown"  # Would need more analysis to get link text
                    })
            
            doc.close()
            
        except Exception as e:
            logger.warning(f"Error analyzing structure: {str(e)}")
        
        return structure
    
    def _check_document_structure(self, pdf_info: Dict, structure: Dict):
        """Check document structure accessibility"""
        
        # Check for document title
        if not pdf_info.get("title"):
            self.issues.append({
                "type": "structure",
                "severity": "high",
                "issue": "Missing document title",
                "description": "PDF document should have a descriptive title in metadata",
                "recommendation": "Add a descriptive title in PDF properties",
                "wcag_criterion": "2.4.2 Page Titled"
            })
        
        # Check for document language
        if not pdf_info.get("language"):
            self.issues.append({
                "type": "structure", 
                "severity": "high",
                "issue": "Missing document language",
                "description": "PDF document should specify its primary language",
                "recommendation": "Set document language in PDF properties",
                "wcag_criterion": "3.1.1 Language of Page"
            })
        
        # Check if document is tagged
        if not pdf_info.get("is_tagged"):
            self.issues.append({
                "type": "structure",
                "severity": "critical",
                "issue": "Document is not tagged",
                "description": "PDF is not structured for screen readers",
                "recommendation": "Re-create PDF with proper tagging or use accessibility tools",
                "wcag_criterion": "4.1.2 Name, Role, Value"
            })
        
        # Check for navigation aids
        if not structure.get("has_bookmarks") and pdf_info.get("pages", 0) > 5:
            self.issues.append({
                "type": "navigation",
                "severity": "medium",
                "issue": "Missing bookmarks/navigation",
                "description": "Long documents should have bookmarks for navigation",
                "recommendation": "Add bookmarks for major sections",
                "wcag_criterion": "2.4.5 Multiple Ways"
            })
        
        # Check heading structure
        if not structure.get("has_headings") and pdf_info.get("pages", 0) > 2:
            self.issues.append({
                "type": "structure",
                "severity": "medium",
                "issue": "Missing heading structure",
                "description": "Documents should use headings to organize content",
                "recommendation": "Use proper heading styles in source document",
                "wcag_criterion": "1.3.1 Info and Relationships"
            })
    
    def _check_text_accessibility(self, text_content: Dict):
        """Check text accessibility issues"""
        
        # Check if text is readable
        if not text_content.get("readable_text"):
            self.issues.append({
                "type": "text",
                "severity": "critical", 
                "issue": "Text not extractable",
                "description": "Document appears to be scanned images without OCR",
                "recommendation": "Apply OCR to make text searchable and readable",
                "wcag_criterion": "1.3.1 Info and Relationships"
            })
            return
        
        # Check font sizes
        for font in text_content.get("font_info", []):
            if font.get("size", 0) < 9:  # Very small text
                self.issues.append({
                    "type": "text",
                    "severity": "medium",
                    "issue": f"Very small font size: {font['size']}pt",
                    "description": "Text may be too small for some users to read",
                    "recommendation": "Use minimum 9pt font size, preferably 12pt or larger",
                    "wcag_criterion": "1.4.12 Text Spacing"
                })
        
        # Check reading level if available
        reading_level = text_content.get("reading_level")
        if reading_level:
            grade_level = reading_level.get("flesch_kincaid_grade", 0)
            if grade_level > 12:  # College level
                self.issues.append({
                    "type": "text",
                    "severity": "low",
                    "issue": f"Complex reading level: Grade {grade_level:.1f}",
                    "description": "Content may be difficult for some users to understand",
                    "recommendation": "Consider simplifying language where possible",
                    "wcag_criterion": "3.1.5 Reading Level"
                })
    
    def _check_image_accessibility(self, images: List[Dict]):
        """Check image accessibility"""
        
        for img in images:
            # PDFs typically don't have alt text, so flag all images
            self.issues.append({
                "type": "images",
                "severity": "high",
                "issue": f"Image on page {img['page']} missing alternative text",
                "description": "Images in PDFs typically lack alternative text for screen readers",
                "recommendation": "Ensure images have descriptions in surrounding text or recreate as tagged PDF",
                "wcag_criterion": "1.1.1 Non-text Content",
                "details": {
                    "page": img["page"],
                    "size": f"{img['width']}x{img['height']}",
                    "contains_text": img.get("contains_text", False)
                }
            })
            
            # Flag images with text
            if img.get("contains_text"):
                self.issues.append({
                    "type": "images",
                    "severity": "critical",
                    "issue": f"Image with text on page {img['page']}",
                    "description": "Image contains text that may not be accessible",
                    "recommendation": "Use actual text instead of text in images",
                    "wcag_criterion": "1.4.5 Images of Text",
                    "details": {
                        "page": img["page"],
                        "extracted_text": img.get("extracted_text", "")[:100]
                    }
                })
    
    def _check_navigation_accessibility(self, pdf_info: Dict):
        """Check navigation and form accessibility"""
        
        # Check for forms without proper labeling
        if pdf_info.get("has_forms"):
            # This would need more detailed form analysis
            self.issues.append({
                "type": "forms",
                "severity": "medium",
                "issue": "Document contains forms",
                "description": "Forms in PDFs may lack proper labeling",
                "recommendation": "Verify all form fields have appropriate labels",
                "wcag_criterion": "1.3.1 Info and Relationships"
            })
    
    def _check_color_accessibility(self, file_path: str):
        """Check color and contrast accessibility"""
        
        # Note: Full color analysis of PDFs is complex and would require
        # rendering pages as images and analyzing pixel colors
        # For now, we'll add a general recommendation
        
        self.issues.append({
            "type": "color",
            "severity": "medium",
            "issue": "Color contrast not verified",
            "description": "PDF color contrast cannot be automatically verified",
            "recommendation": "Manually verify color contrast meets WCAG 2.1 AA standards (4.5:1 for normal text, 3:1 for large text)",
            "wcag_criterion": "1.4.3 Contrast (Minimum)"
        })
    
    def _calculate_accessibility_score(self) -> int:
        """Calculate overall accessibility score"""
        if not self.issues:
            return 100
        
        # Weight issues by severity
        severity_weights = {
            "critical": 20,
            "high": 10,
            "medium": 5,
            "low": 2
        }
        
        total_deductions = sum(
            severity_weights.get(issue["severity"], 5) 
            for issue in self.issues
        )
        
        # Cap minimum score at 0
        score = max(0, 100 - total_deductions)
        return score
    
    def _apply_automatic_fixes(self, file_path: str):
        """Apply automatic fixes where possible"""
        
        # Note: PDF modification is complex and risky
        # For now, we'll just document what could be fixed automatically
        
        potential_fixes = [
            "Adding document title and metadata",
            "Setting document language",
            "Adding basic document structure tags"
        ]
        
        # In a full implementation, we'd use libraries like reportlab
        # to create a new, more accessible version of the PDF
        
        self.fixes_applied = [{
            "type": "metadata",
            "description": "PDF fixes require manual remediation or specialized tools",
            "recommendation": "Use Adobe Acrobat Pro or similar tools for PDF accessibility fixes"
        }]
    
    def _create_analysis_result(self, file_path: str, score: int, **kwargs) -> Dict[str, Any]:
        """Create standardized analysis result"""
        return {
            "success": True,
            "file_path": file_path,
            "file_type": "pdf",
            "accessibility_score": score,
            "total_issues": len(self.issues),
            "critical_issues": len([i for i in self.issues if i["severity"] == "critical"]),
            "high_issues": len([i for i in self.issues if i["severity"] == "high"]),
            "medium_issues": len([i for i in self.issues if i["severity"] == "medium"]),
            "low_issues": len([i for i in self.issues if i["severity"] == "low"]),
            "issues": self.issues,
            "fixes_applied": self.fixes_applied,
            "document_info": kwargs.get("pdf_info", {}),
            "recommendations": self._generate_recommendations(),
            "wcag_compliance": self._assess_wcag_compliance()
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result"""
        return {
            "success": False,
            "error": error_message,
            "file_type": "pdf",
            "accessibility_score": 0,
            "total_issues": 0,
            "issues": [],
            "fixes_applied": []
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        critical_issues = [i for i in self.issues if i["severity"] == "critical"]
        high_issues = [i for i in self.issues if i["severity"] == "high"]
        
        if critical_issues:
            recommendations.append("❗ CRITICAL: Address document tagging and text extraction issues first")
            
        if high_issues:
            recommendations.append("🔥 HIGH PRIORITY: Add document metadata and image descriptions")
            
        recommendations.extend([
            "📚 Consider recreating the PDF from accessible source documents",
            "🔧 Use Adobe Acrobat Pro or similar tools for advanced PDF accessibility",
            "✅ Test with screen readers after making improvements"
        ])
        
        return recommendations
    
    def _assess_wcag_compliance(self) -> Dict[str, str]:
        """Assess WCAG 2.1 Level AA compliance"""
        critical_issues = [i for i in self.issues if i["severity"] == "critical"]
        high_issues = [i for i in self.issues if i["severity"] == "high"]
        
        if critical_issues:
            return {
                "level": "Non-compliant",
                "status": "Major accessibility barriers present",
                "next_steps": "Address critical issues before using in courses"
            }
        elif high_issues:
            return {
                "level": "Partially compliant", 
                "status": "Some accessibility improvements needed",
                "next_steps": "Address high-priority issues for better compliance"
            }
        else:
            return {
                "level": "Mostly compliant",
                "status": "Meets most WCAG 2.1 AA requirements",
                "next_steps": "Address remaining minor issues for full compliance"
            }