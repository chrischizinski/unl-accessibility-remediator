"""
AI Assistant Module

Interfaces with Ollama for accessibility analysis and recommendations.
Sends structured slide data and receives JSON responses with improvement suggestions.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SlideAnalysis:
    """Structured analysis result for a single slide."""
    slide_number: int
    title: Optional[str]
    suggested_title: Optional[str]
    alt_text_suggestions: List[Dict[str, str]]  # {"image_id": "...", "suggested_alt": "..."}
    link_improvements: List[Dict[str, str]]     # {"original_text": "...", "suggested_text": "..."}
    contrast_issues: List[Dict[str, Any]]       # {"element": "...", "current_ratio": float, "meets_aa": bool}
    content_issues: List[str]                   # General content structure issues
    auto_fixable: List[str]                     # Issues that can be fixed automatically
    manual_review: List[str]                    # Issues requiring human review
    confidence_score: float                     # AI confidence in analysis (0-1)


@dataclass
class AccessibilityResults:
    """Complete accessibility analysis results for a slide deck."""
    slides: List[SlideAnalysis]
    overall_score: float
    total_issues: int
    auto_fixable_count: int
    manual_review_count: int
    processing_time: float
    automatic_fixes: List[Dict[str, Any]] = None  # Applied fixes (if any)


class AIAssistant:
    """Interface to Ollama for accessibility analysis."""
    
    def __init__(self, host: str = "localhost:11434", model: str = "llama2"):
        """
        Initialize AI assistant with Ollama connection.
        
        Args:
            host: Ollama server host:port
            model: Model name to use for analysis
        """
        self.host = host.rstrip('/')
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Validate connection
        self._validate_connection()
    
    def _validate_connection(self) -> None:
        """Test connection to Ollama server."""
        try:
            response = requests.get(f"http://{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            self.logger.info(f"Successfully connected to Ollama at {self.host}")
        except requests.RequestException as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
            raise ConnectionError(f"Cannot connect to Ollama at {self.host}: {e}")
    
    def analyze_slide(self, slide_data: Dict[str, Any]) -> SlideAnalysis:
        """
        Analyze a single slide for accessibility issues.
        
        Args:
            slide_data: Dictionary containing slide content:
                - slide_number: int
                - title: str or None
                - text_content: List[str]
                - images: List[Dict] with 'id', 'description', 'alt_text'
                - links: List[Dict] with 'text', 'url'
                - colors: List[Dict] with 'foreground', 'background', 'element_type'
        
        Returns:
            SlideAnalysis object with AI recommendations
        """
        self.logger.debug(f"Analyzing slide {slide_data.get('slide_number', 'unknown')}")
        
        prompt = self._build_analysis_prompt(slide_data)
        
        try:
            response = self._query_ollama(prompt)
            analysis = self._parse_analysis_response(response, slide_data['slide_number'])
            
            self.logger.debug(f"Analysis completed for slide {slide_data['slide_number']}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing slide {slide_data['slide_number']}: {e}")
            # Return empty analysis on failure
            return SlideAnalysis(
                slide_number=slide_data['slide_number'],
                title=slide_data.get('title'),
                suggested_title=None,
                alt_text_suggestions=[],
                link_improvements=[],
                contrast_issues=[],
                content_issues=[f"Analysis failed: {str(e)}"],
                auto_fixable=[],
                manual_review=["Manual review required due to analysis failure"],
                confidence_score=0.0
            )
    
    def _build_analysis_prompt(self, slide_data: Dict[str, Any]) -> str:
        """Build the prompt for Ollama analysis."""
        prompt = f"""
You are an accessibility expert analyzing slide content for WCAG 2.1 AA compliance.

Analyze this slide and provide recommendations in JSON format:

SLIDE DATA:
- Number: {slide_data['slide_number']}
- Title: {slide_data.get('title', 'No title')}
- Text Content: {slide_data.get('text_content', [])}
- Images: {slide_data.get('images', [])}
- Links: {slide_data.get('links', [])}
- Colors: {slide_data.get('colors', [])}

REQUIREMENTS:
1. Check if title is descriptive (suggest improvement if needed)
2. Generate alt text for images missing descriptions
3. Identify vague link text ("click here", "read more") and suggest improvements
4. Flag color contrast issues (need 4.5:1 ratio for normal text, 3:1 for large text)
5. Identify missing structure or confusing content organization
6. Classify issues as auto-fixable vs requiring manual review

Respond with ONLY valid JSON in this exact format:
{{
    "suggested_title": "Better title text or null",
    "alt_text_suggestions": [
        {{"image_id": "img1", "suggested_alt": "Descriptive alt text"}}
    ],
    "link_improvements": [
        {{"original_text": "click here", "suggested_text": "View the full report"}}
    ],
    "contrast_issues": [
        {{"element": "heading", "current_ratio": 2.1, "meets_aa": false, "recommendation": "Use darker text"}}
    ],
    "content_issues": ["List of content structure problems"],
    "auto_fixable": ["Issues that can be fixed automatically"],
    "manual_review": ["Issues requiring human judgment"],
    "confidence_score": 0.85
}}
"""
        return prompt
    
    def _query_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and get response."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more consistent JSON
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(
                f"http://{self.host}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.RequestException as e:
            self.logger.error(f"Ollama API request failed: {e}")
            raise
    
    def _parse_analysis_response(self, response: str, slide_number: int) -> SlideAnalysis:
        """Parse JSON response from Ollama into SlideAnalysis object."""
        try:
            # Try to extract JSON from response (model might include extra text)
            response = response.strip()
            if not response.startswith('{'):
                # Find JSON block
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    response = response[start:end]
            
            data = json.loads(response)
            
            return SlideAnalysis(
                slide_number=slide_number,
                title=None,  # Will be set by processor
                suggested_title=data.get('suggested_title'),
                alt_text_suggestions=data.get('alt_text_suggestions', []),
                link_improvements=data.get('link_improvements', []),
                contrast_issues=data.get('contrast_issues', []),
                content_issues=data.get('content_issues', []),
                auto_fixable=data.get('auto_fixable', []),
                manual_review=data.get('manual_review', []),
                confidence_score=data.get('confidence_score', 0.5)
            )
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            self.logger.debug(f"Raw response: {response[:500]}...")
            
            # Return minimal analysis on parse failure
            return SlideAnalysis(
                slide_number=slide_number,
                title=None,
                suggested_title=None,
                alt_text_suggestions=[],
                link_improvements=[],
                contrast_issues=[],
                content_issues=["JSON parsing failed - manual review needed"],
                auto_fixable=[],
                manual_review=["Response parsing failed"],
                confidence_score=0.0
            )
    
    def generate_alt_text(self, image_description: str, context: str = "") -> str:
        """
        Generate alt text for a specific image.
        
        Args:
            image_description: Visual description of the image
            context: Surrounding slide context
            
        Returns:
            Suggested alt text
        """
        prompt = f"""
Generate concise, descriptive alt text for this image in slide context.

Image: {image_description}
Context: {context}

Requirements:
- Be concise but descriptive
- Focus on relevant information for slide content
- Avoid "image of" or "picture of"
- Consider the educational/presentation context

Respond with ONLY the alt text, no quotes or extra text:
"""
        
        try:
            response = self._query_ollama(prompt)
            alt_text = response.strip().strip('"\'')
            return alt_text[:150]  # Limit length
            
        except Exception as e:
            self.logger.error(f"Failed to generate alt text: {e}")
            return f"Image: {image_description[:50]}..."