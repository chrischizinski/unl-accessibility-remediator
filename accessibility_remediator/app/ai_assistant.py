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
    """Interface to Ollama for accessibility analysis with multi-model support."""
    
    # Recommended models in order of preference
    MODEL_HIERARCHY = [
        "llama3.1:8b",      # Primary: Better accuracy and reasoning
        "qwen2.5:14b",      # Advanced: Specialized reasoning
        "llama3:8b",        # Backup: Stable alternative
        "phi3:3.8b",        # Fast: Quick backup
        "llama2",           # Fallback: Original model
    ]
    
    def __init__(self, host: str = "localhost:11434", model: str = None, enable_fallback: bool = True):
        """
        Initialize AI assistant with Ollama connection and model selection.
        
        Args:
            host: Ollama server host:port
            model: Specific model name (if None, auto-selects best available)
            enable_fallback: Whether to fall back to other models on failure
        """
        self.host = host.rstrip('/')
        self.enable_fallback = enable_fallback
        self.logger = logging.getLogger(__name__)
        
        # Select best available model
        self.model = self._select_best_model(model)
        self.available_models = self._get_available_models()
        
        # Validate connection
        self._validate_connection()
    
    def _get_available_models(self) -> List[str]:
        """Get list of available models from Ollama server."""
        try:
            response = requests.get(f"http://{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            self.logger.debug(f"Available models: {models}")
            return models
        except requests.RequestException as e:
            self.logger.warning(f"Could not fetch available models: {e}")
            return []
    
    def _select_best_model(self, preferred_model: str = None) -> str:
        """Select the best available model from hierarchy."""
        available_models = self._get_available_models()
        
        # If specific model requested and available, use it
        if preferred_model:
            if preferred_model in available_models:
                self.logger.info(f"Using requested model: {preferred_model}")
                return preferred_model
            else:
                self.logger.warning(f"Requested model '{preferred_model}' not available, selecting from hierarchy")
        
        # Select best available from hierarchy
        for model in self.MODEL_HIERARCHY:
            if model in available_models:
                self.logger.info(f"Selected model: {model}")
                return model
        
        # Fallback to first available model
        if available_models:
            fallback = available_models[0]
            self.logger.warning(f"Using fallback model: {fallback}")
            return fallback
        
        # Ultimate fallback
        self.logger.error("No models available, using default 'llama2'")
        return "llama2"
    
    def _validate_connection(self) -> None:
        """Test connection to Ollama server."""
        try:
            response = requests.get(f"http://{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            self.logger.info(f"Successfully connected to Ollama at {self.host} with model '{self.model}'")
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
        """Build the enhanced WCAG-expert prompt for Ollama analysis."""
        prompt = f"""
You are a certified WCAG 2.1 Level AA accessibility expert with 10+ years experience in higher education digital accessibility compliance. You specialize in UNL's accessibility requirements and ADA Title II compliance for universities.

## EXPERT CONTEXT:
- University faculty must meet WCAG 2.1 AA by April 2026 (ADA Title II rule)
- You've remediated 1000+ academic presentations
- You understand both technical compliance AND educational effectiveness
- You know common faculty accessibility mistakes and practical solutions

## ANALYSIS METHODOLOGY:
Use systematic POUR framework analysis:
1. **PERCEIVABLE**: Check alt text, color contrast, text alternatives
2. **OPERABLE**: Verify keyboard navigation, focus management, timing
3. **UNDERSTANDABLE**: Assess readability, consistent navigation, error prevention
4. **ROBUST**: Ensure compatibility with assistive technologies

## SLIDE TO ANALYZE:
- Slide #{slide_data['slide_number']}
- Title: "{slide_data.get('title', 'No title')}"
- Content: {slide_data.get('text_content', [])}
- Images: {slide_data.get('images', [])}
- Links: {slide_data.get('links', [])}
- Color Data: {slide_data.get('colors', [])}

## EXPERT ANALYSIS EXAMPLES:

**Example 1 - Image Analysis:**
If image shows "Bar chart showing enrollment trends":
- Bad alt: "chart" or "image of chart"
- Expert alt: "Bar chart: Fall enrollment increased 15% from 2020 (1,200) to 2023 (1,380 students)"
- Reasoning: Describes both content AND key data insights for academic context

**Example 2 - Link Analysis:**
- Bad: "Click here for more information"
- Expert: "View the complete 2024 Sustainability Report (PDF, 2.1MB)"
- Reasoning: Describes destination, format, and file size for informed decisions

**Example 3 - Title Analysis:**
- Bad: "Slide 5" or "Overview"
- Expert: "Key Findings: Student Satisfaction Increased 23% After New Support Programs"
- Reasoning: Descriptive, specific, conveys main message clearly

## CRITICAL WCAG 2.1 AA CRITERIA TO CHECK:
- 1.1.1 Non-text Content: All images need meaningful alt text
- 1.4.3 Contrast Minimum: 4.5:1 normal text, 3:1 large text (18pt+/14pt+ bold)
- 2.4.2 Page Titled: Each slide needs descriptive title
- 2.4.4 Link Purpose: Links must describe destination
- 1.3.1 Info and Relationships: Proper heading structure
- 3.1.5 Reading Level: Consider academic but accessible language

## UNIVERSITY-SPECIFIC CONSIDERATIONS:
- Faculty time constraints: Prioritize high-impact, quick fixes
- Student diversity: Consider ESL learners, varying abilities
- Academic content: Maintain scholarly rigor while improving accessibility
- Compliance deadline: Focus on Title II requirements

Think step-by-step through each WCAG criterion, then provide your expert analysis in this EXACT JSON format:

{{
    "suggested_title": "Specific descriptive title or null if current is adequate",
    "alt_text_suggestions": [
        {{"image_id": "img1", "suggested_alt": "Comprehensive alt text with context and key information"}}
    ],
    "link_improvements": [
        {{"original_text": "vague link text", "suggested_text": "Descriptive link with destination and format info"}}
    ],
    "contrast_issues": [
        {{"element": "specific element type", "current_ratio": 2.1, "meets_aa": false, "recommendation": "Specific color improvement suggestion"}}
    ],
    "content_issues": ["Specific structural or comprehension problems with actionable solutions"],
    "auto_fixable": ["Issues that can be automatically resolved without losing meaning"],
    "manual_review": ["Issues requiring faculty judgment to maintain academic integrity"],
    "confidence_score": 0.95
}}

Provide ONLY the JSON response, no additional text."""
        return prompt
    
    def _query_ollama(self, prompt: str, max_retries: int = 3) -> str:
        """Send prompt to Ollama and get response with fallback models."""
        models_to_try = [self.model]
        
        # Add fallback models if enabled
        if self.enable_fallback:
            for model in self.MODEL_HIERARCHY:
                if model != self.model and model in self.available_models:
                    models_to_try.append(model)
        
        last_error = None
        
        for attempt, model in enumerate(models_to_try[:max_retries]):
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent JSON
                    "top_p": 0.9,
                    "num_predict": 2048  # Limit response length
                }
            }
            
            try:
                self.logger.debug(f"Attempt {attempt + 1}: Trying model '{model}'")
                response = requests.post(
                    f"http://{self.host}/api/generate",
                    json=payload,
                    timeout=90  # Increased timeout for larger models
                )
                response.raise_for_status()
                
                result = response.json()
                response_text = result.get('response', '')
                
                if response_text.strip():  # Valid response
                    if model != self.model:
                        self.logger.info(f"Successfully used fallback model: {model}")
                    return response_text
                else:
                    self.logger.warning(f"Empty response from model '{model}'")
                    last_error = "Empty response"
                    continue
                
            except requests.RequestException as e:
                self.logger.warning(f"Model '{model}' failed: {e}")
                last_error = e
                continue
        
        # All models failed
        self.logger.error(f"All models failed. Last error: {last_error}")
        raise ConnectionError(f"Failed to get response from any model. Last error: {last_error}")
    
    def _parse_analysis_response(self, response: str, slide_number: int) -> SlideAnalysis:
        """Parse JSON response from Ollama with robust validation and fallbacks."""
        # Try multiple parsing strategies
        parsed_data = self._extract_json_with_fallbacks(response)
        
        if parsed_data is None:
            # All parsing failed - create analysis from text patterns
            return self._create_fallback_analysis(response, slide_number)
        
        # Validate and sanitize the parsed data
        validated_data = self._validate_and_sanitize_json(parsed_data)
        
        return SlideAnalysis(
            slide_number=slide_number,
            title=None,  # Will be set by processor
            suggested_title=validated_data.get('suggested_title'),
            alt_text_suggestions=validated_data.get('alt_text_suggestions', []),
            link_improvements=validated_data.get('link_improvements', []),
            contrast_issues=validated_data.get('contrast_issues', []),
            content_issues=validated_data.get('content_issues', []),
            auto_fixable=validated_data.get('auto_fixable', []),
            manual_review=validated_data.get('manual_review', []),
            confidence_score=validated_data.get('confidence_score', 0.5)
        )
    
    def _extract_json_with_fallbacks(self, response: str) -> Optional[Dict[str, Any]]:
        """Try multiple strategies to extract JSON from AI response."""
        response = response.strip()
        
        # Strategy 1: Response is pure JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Find JSON block between braces
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_block = response[start:end]
                return json.loads(json_block)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Find JSON in code blocks (```json)
        try:
            import re
            json_pattern = r'```(?:json)?\s*({.*?})\s*```'
            match = re.search(json_pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return json.loads(match.group(1))
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Strategy 4: Clean common formatting issues
        try:
            # Remove markdown formatting
            cleaned = re.sub(r'`{1,3}(?:json)?', '', response, flags=re.IGNORECASE)
            
            # Fix common JSON issues
            cleaned = cleaned.replace('\n', ' ')  # Remove newlines
            cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
            cleaned = cleaned.replace("'", '"')  # Fix quotes
            
            # Try to extract JSON again
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            if start >= 0 and end > start:
                json_block = cleaned[start:end]
                return json.loads(json_block)
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Strategy 5: Partial JSON reconstruction
        try:
            return self._reconstruct_partial_json(response)
        except Exception:
            pass
        
        self.logger.warning(f"All JSON parsing strategies failed for response: {response[:200]}...")
        return None
    
    def _reconstruct_partial_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Attempt to reconstruct JSON from partial or malformed response."""
        import re
        
        # Initialize result structure
        result = {
            "suggested_title": None,
            "alt_text_suggestions": [],
            "link_improvements": [],
            "contrast_issues": [],
            "content_issues": [],
            "auto_fixable": [],
            "manual_review": [],
            "confidence_score": 0.3  # Lower confidence for reconstructed
        }
        
        # Extract suggested title
        title_pattern = r'"suggested_title"\s*:\s*"([^"]+)"'
        title_match = re.search(title_pattern, response)
        if title_match:
            result["suggested_title"] = title_match.group(1)
        
        # Extract confidence score
        confidence_pattern = r'"confidence_score"\s*:\s*([0-9.]+)'
        confidence_match = re.search(confidence_pattern, response)
        if confidence_match:
            try:
                result["confidence_score"] = float(confidence_match.group(1))
            except ValueError:
                pass
        
        # Extract arrays (simplified)
        array_patterns = {
            "content_issues": r'"content_issues"\s*:\s*\[([^\]]+)\]',
            "auto_fixable": r'"auto_fixable"\s*:\s*\[([^\]]+)\]',
            "manual_review": r'"manual_review"\s*:\s*\[([^\]]+)\]'
        }
        
        for key, pattern in array_patterns.items():
            match = re.search(pattern, response)
            if match:
                # Simple string extraction (not perfect but functional)
                items_text = match.group(1)
                items = re.findall(r'"([^"]+)"', items_text)
                result[key] = items
        
        # Only return if we found some useful data
        has_data = (result["suggested_title"] or 
                   result["content_issues"] or 
                   result["auto_fixable"] or 
                   result["manual_review"])
        
        return result if has_data else None
    
    def _validate_and_sanitize_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize parsed JSON data."""
        validated = {}
        
        # Validate suggested_title
        title = data.get('suggested_title')
        if title and isinstance(title, str) and title.strip() and title.lower() != 'null':
            validated['suggested_title'] = title.strip()[:200]  # Limit length
        else:
            validated['suggested_title'] = None
        
        # Validate arrays
        array_fields = [
            'alt_text_suggestions', 'link_improvements', 'contrast_issues',
            'content_issues', 'auto_fixable', 'manual_review'
        ]
        
        for field in array_fields:
            value = data.get(field, [])
            if isinstance(value, list):
                # Sanitize list items
                if field in ['content_issues', 'auto_fixable', 'manual_review']:
                    # Simple string arrays
                    validated[field] = [str(item).strip() for item in value 
                                      if item and str(item).strip()][:10]  # Limit count
                elif field in ['alt_text_suggestions', 'link_improvements', 'contrast_issues']:
                    # Object arrays
                    validated[field] = [item for item in value 
                                      if isinstance(item, dict)][:5]  # Limit count
                else:
                    validated[field] = value
            else:
                validated[field] = []
        
        # Validate confidence_score
        confidence = data.get('confidence_score', 0.5)
        try:
            confidence = float(confidence)
            validated['confidence_score'] = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
        except (ValueError, TypeError):
            validated['confidence_score'] = 0.5  # Default
        
        return validated
    
    def _create_fallback_analysis(self, response: str, slide_number: int) -> SlideAnalysis:
        """Create analysis from text patterns when JSON parsing fails completely."""
        self.logger.info(f"Creating fallback analysis from text patterns for slide {slide_number}")
        
        # Extract issues from common text patterns
        content_issues = []
        manual_review = ["AI response parsing failed - manual review recommended"]
        
        # Look for common accessibility keywords in the response
        response_lower = response.lower()
        
        if 'alt text' in response_lower or 'alt-text' in response_lower:
            content_issues.append("Images may need alternative text")
        
        if 'contrast' in response_lower:
            content_issues.append("Color contrast may need review")
        
        if 'link' in response_lower and ('click here' in response_lower or 'more info' in response_lower):
            content_issues.append("Links may need more descriptive text")
        
        if 'title' in response_lower:
            content_issues.append("Slide title may need improvement")
        
        # If no specific issues found, add general review
        if not content_issues:
            content_issues = ["General accessibility review needed"]
        
        return SlideAnalysis(
            slide_number=slide_number,
            title=None,
            suggested_title=None,
            alt_text_suggestions=[],
            link_improvements=[],
            contrast_issues=[],
            content_issues=content_issues,
            auto_fixable=[],
            manual_review=manual_review,
            confidence_score=0.2  # Low confidence for fallback
        )
    
    def generate_alt_text(self, image_description: str, context: str = "") -> str:
        """
        Generate alt text for a specific image using WCAG expert methodology.
        
        Args:
            image_description: Visual description of the image
            context: Surrounding slide context
            
        Returns:
            Suggested alt text
        """
        prompt = f"""
You are a WCAG 2.1 AA accessibility expert specializing in academic content. Generate optimal alt text for university presentations.

## IMAGE ANALYSIS:
Visual Description: {image_description}
Slide Context: {context}

## EXPERT ALT TEXT PRINCIPLES:
1. **Academic Context**: Provide meaningful information for learning objectives
2. **Data Priority**: For charts/graphs, include key trends and specific values
3. **Concise but Complete**: Under 125 characters while conveying essential information
4. **No Redundancy**: Avoid "image of", "picture of", "chart showing"
5. **Functional Purpose**: Focus on why the image supports the content

## EXAMPLES BY IMAGE TYPE:

**Data Visualization:**
- Poor: "Bar chart about enrollment"
- Expert: "Enrollment rose 23% from 1,200 (2020) to 1,476 students (2023)"

**Process Diagram:**
- Poor: "Flowchart showing steps"
- Expert: "Four-step research process: hypothesis → data collection → analysis → conclusions"

**Decorative Images:**
- Poor: "University logo"
- Expert: "" (empty alt for decorative)

**Conceptual Illustration:**
- Poor: "Picture of teamwork"
- Expert: "Diverse team collaborating around conference table, representing inclusive leadership"

## ANALYSIS CHECKLIST:
□ Does alt text serve the image's educational purpose?
□ Would a student understand the key information without seeing the image?
□ Is it specific enough to differentiate from similar images?
□ Does it support the slide's learning objective?

Provide ONLY the optimized alt text (no quotes, explanations, or formatting):
"""
        
        try:
            response = self._query_ollama(prompt)
            alt_text = response.strip().strip('"\'')
            return alt_text[:150]  # Limit length
            
        except Exception as e:
            self.logger.error(f"Failed to generate alt text: {e}")
            return f"Image: {image_description[:50]}..."