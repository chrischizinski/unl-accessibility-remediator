"""
Alt Text Generator Module

Generates meaningful alternative text for images using AI assistance.
Follows UNL's accessibility guidelines and WCAG 2.1 Level AA requirements.

Key principles from UNL's LISTS framework:
- Images should have meaningful alternative text that describes the content and purpose
- Decorative images should have empty alt text (alt="")
- Complex images may need longer descriptions
- Alt text should be concise but descriptive
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from .ai_assistant import AIAssistant


@dataclass
class AltTextSuggestion:
    """Suggestion for alt text improvement."""
    image_id: str
    current_alt_text: str
    suggested_alt_text: str
    confidence: float
    reasoning: str
    image_type: str  # "informative", "decorative", "complex", "functional"
    context: str
    is_empty_appropriate: bool  # True if image is decorative and should have empty alt


@dataclass
class ImageAnalysis:
    """Analysis result for a single image."""
    image_id: str
    has_alt_text: bool
    current_alt_text: str
    image_description: str
    context: str
    accessibility_issues: List[str]
    suggestions: List[AltTextSuggestion]
    priority: str  # "high", "medium", "low"


class AltTextGenerator:
    """
    Generates and improves alt text for images using AI assistance.
    
    Implements UNL's accessibility standards for digital course materials.
    """
    
    # Common problematic alt text patterns to flag
    POOR_ALT_TEXT_PATTERNS = [
        "image", "picture", "photo", "graphic", "screenshot",
        "click here", "see image", "view image", "image of",
        "picture of", "photo of", "graphic of"
    ]
    
    # Maximum recommended alt text length (per WCAG guidelines)
    MAX_ALT_TEXT_LENGTH = 125
    
    def __init__(self, ai_assistant: AIAssistant):
        """
        Initialize alt text generator.
        
        Args:
            ai_assistant: AI assistant for generating alt text
        """
        self.ai_assistant = ai_assistant
        self.logger = logging.getLogger(__name__)
    
    def analyze_images(self, images: List[Dict[str, Any]], 
                      slide_context: str = "") -> List[ImageAnalysis]:
        """
        Analyze multiple images for alt text quality.
        
        Args:
            images: List of image dictionaries with metadata
            slide_context: Context from the slide containing the images
            
        Returns:
            List of ImageAnalysis objects
        """
        analyses = []
        
        for image in images:
            try:
                analysis = self.analyze_single_image(image, slide_context)
                analyses.append(analysis)
            except Exception as e:
                self.logger.error(f"Failed to analyze image {image.get('id', 'unknown')}: {e}")
                # Create error analysis
                analyses.append(self._create_error_analysis(image))
        
        return analyses
    
    def analyze_single_image(self, image: Dict[str, Any], 
                           slide_context: str = "") -> ImageAnalysis:
        """
        Analyze a single image for alt text quality.
        
        Args:
            image: Image dictionary with metadata
            slide_context: Context from the slide
            
        Returns:
            ImageAnalysis object
        """
        image_id = image.get('id', 'unknown')
        current_alt = image.get('alt_text', '')
        description = image.get('description', '')
        
        self.logger.debug(f"Analyzing alt text for image {image_id}")
        
        # Check current alt text quality
        has_alt = bool(current_alt.strip())
        issues = self._identify_alt_text_issues(current_alt)
        
        # Generate suggestions using AI
        suggestions = self._generate_alt_text_suggestions(
            image, slide_context, current_alt
        )
        
        # Determine priority based on issues found
        priority = self._calculate_priority(has_alt, issues, suggestions)
        
        return ImageAnalysis(
            image_id=image_id,
            has_alt_text=has_alt,
            current_alt_text=current_alt,
            image_description=description,
            context=slide_context,
            accessibility_issues=issues,
            suggestions=suggestions,
            priority=priority
        )
    
    def generate_alt_text(self, image_description: str, 
                         context: str = "",
                         image_type: str = "informative") -> str:
        """
        Generate alt text for an image using AI.
        
        Args:
            image_description: Description of the image content
            context: Surrounding context (slide content, purpose)
            image_type: Type of image (informative, decorative, complex, functional)
            
        Returns:
            Generated alt text
        """
        try:
            if image_type == "decorative":
                return ""  # Decorative images should have empty alt text
            
            # Use AI assistant to generate contextual alt text
            alt_text = self.ai_assistant.generate_alt_text(image_description, context)
            
            # Post-process the generated text
            cleaned_alt = self._clean_alt_text(alt_text)
            
            self.logger.debug(f"Generated alt text: '{cleaned_alt}'")
            return cleaned_alt
            
        except Exception as e:
            self.logger.error(f"Failed to generate alt text: {e}")
            # Fallback to basic description
            return self._create_fallback_alt_text(image_description)
    
    def improve_alt_text(self, current_alt: str, image_description: str,
                        context: str = "") -> Optional[str]:
        """
        Improve existing alt text using AI suggestions.
        
        Args:
            current_alt: Current alt text
            image_description: Description of the image
            context: Surrounding context
            
        Returns:
            Improved alt text or None if no improvement needed
        """
        # Check if current alt text needs improvement
        issues = self._identify_alt_text_issues(current_alt)
        
        if not issues:
            return None  # Alt text is already good
        
        try:
            # Generate improved alt text
            prompt = self._build_improvement_prompt(current_alt, image_description, context, issues)
            improved_alt = self.ai_assistant._query_ollama(prompt)
            
            # Clean and validate the improved text
            cleaned_alt = self._clean_alt_text(improved_alt)
            
            # Only return if it's actually better
            if self._is_better_alt_text(current_alt, cleaned_alt):
                return cleaned_alt
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to improve alt text: {e}")
            return None
    
    def _identify_alt_text_issues(self, alt_text: str) -> List[str]:
        """Identify issues with current alt text."""
        issues = []
        
        if not alt_text.strip():
            issues.append("Missing alt text")
            return issues
        
        alt_lower = alt_text.lower().strip()
        
        # Check for problematic patterns
        for pattern in self.POOR_ALT_TEXT_PATTERNS:
            if pattern in alt_lower:
                issues.append(f"Contains generic term: '{pattern}'")
        
        # Check length
        if len(alt_text) > self.MAX_ALT_TEXT_LENGTH:
            issues.append(f"Too long ({len(alt_text)} chars, max {self.MAX_ALT_TEXT_LENGTH})")
        
        # Check for redundant phrases
        if alt_text.lower().startswith(('image of', 'picture of', 'photo of')):
            issues.append("Starts with redundant phrase")
        
        # Check if it's too generic
        if len(alt_text.strip()) < 5:
            issues.append("Too short/generic")
        
        # Check for non-descriptive text
        non_descriptive = ['image', 'photo', 'picture', 'graphic', 'screenshot']
        if alt_lower.strip() in non_descriptive:
            issues.append("Non-descriptive alt text")
        
        return issues
    
    def _generate_alt_text_suggestions(self, image: Dict[str, Any],
                                     context: str, current_alt: str) -> List[AltTextSuggestion]:
        """Generate AI-powered alt text suggestions."""
        suggestions = []
        
        try:
            image_id = image.get('id', 'unknown')
            description = image.get('description', '')
            
            # Determine image type based on context and description
            image_type = self._classify_image_type(description, context)
            
            # Generate suggestion based on image type
            if image_type == "decorative":
                # Decorative images should have empty alt text
                if current_alt.strip():
                    suggestions.append(AltTextSuggestion(
                        image_id=image_id,
                        current_alt_text=current_alt,
                        suggested_alt_text="",
                        confidence=0.9,
                        reasoning="Image appears decorative and should have empty alt text",
                        image_type=image_type,
                        context=context,
                        is_empty_appropriate=True
                    ))
            else:
                # Generate descriptive alt text for informative images
                suggested_alt = self.generate_alt_text(description, context, image_type)
                
                if suggested_alt and suggested_alt != current_alt:
                    suggestions.append(AltTextSuggestion(
                        image_id=image_id,
                        current_alt_text=current_alt,
                        suggested_alt_text=suggested_alt,
                        confidence=0.8,
                        reasoning=f"Generated descriptive alt text for {image_type} image",
                        image_type=image_type,
                        context=context,
                        is_empty_appropriate=False
                    ))
        
        except Exception as e:
            self.logger.warning(f"Failed to generate suggestions: {e}")
        
        return suggestions
    
    def _classify_image_type(self, description: str, context: str) -> str:
        """
        Classify image type based on description and context.
        
        Returns:
            Image type: "informative", "decorative", "complex", or "functional"
        """
        desc_lower = description.lower()
        context_lower = context.lower()
        
        # Patterns suggesting decorative images
        decorative_patterns = [
            'border', 'divider', 'decoration', 'ornament',
            'background', 'texture', 'pattern'
        ]
        
        # Patterns suggesting functional images
        functional_patterns = [
            'button', 'icon', 'link', 'navigation', 'menu',
            'close', 'open', 'download', 'search'
        ]
        
        # Patterns suggesting complex images
        complex_patterns = [
            'chart', 'graph', 'diagram', 'flowchart',
            'table', 'data', 'statistics', 'timeline'
        ]
        
        # Check for patterns
        for pattern in decorative_patterns:
            if pattern in desc_lower:
                return "decorative"
        
        for pattern in functional_patterns:
            if pattern in desc_lower:
                return "functional"
        
        for pattern in complex_patterns:
            if pattern in desc_lower or pattern in context_lower:
                return "complex"
        
        # Default to informative
        return "informative"
    
    def _clean_alt_text(self, alt_text: str) -> str:
        """Clean and standardize generated alt text."""
        if not alt_text:
            return ""
        
        cleaned = alt_text.strip()
        
        # Remove redundant phrases
        redundant_prefixes = [
            'image of ', 'picture of ', 'photo of ', 'graphic of ',
            'screenshot of ', 'image: ', 'alt text: '
        ]
        
        for prefix in redundant_prefixes:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):]
        
        # Remove quotes if present
        cleaned = cleaned.strip('\'"')
        
        # Ensure proper capitalization
        if cleaned and not cleaned[0].isupper():
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        # Truncate if too long
        if len(cleaned) > self.MAX_ALT_TEXT_LENGTH:
            cleaned = cleaned[:self.MAX_ALT_TEXT_LENGTH - 3] + "..."
        
        return cleaned
    
    def _create_fallback_alt_text(self, description: str) -> str:
        """Create basic fallback alt text when AI generation fails."""
        if not description:
            return "Image"
        
        # Use first part of description
        fallback = description.split('.')[0]  # First sentence
        return self._clean_alt_text(fallback)
    
    def _build_improvement_prompt(self, current_alt: str, description: str,
                                context: str, issues: List[str]) -> str:
        """Build prompt for improving existing alt text."""
        prompt = f"""
Improve this alt text for better accessibility:

Current alt text: "{current_alt}"
Image description: {description}
Context: {context}
Issues found: {', '.join(issues)}

Create improved alt text that:
- Is concise and descriptive
- Avoids redundant phrases like "image of"
- Focuses on relevant information for the context
- Is under {self.MAX_ALT_TEXT_LENGTH} characters

Respond with ONLY the improved alt text, no quotes or extra text:
"""
        return prompt
    
    def _is_better_alt_text(self, current: str, improved: str) -> bool:
        """Check if improved alt text is actually better than current."""
        if not improved or improved == current:
            return False
        
        # Check if improved version has fewer issues
        current_issues = len(self._identify_alt_text_issues(current))
        improved_issues = len(self._identify_alt_text_issues(improved))
        
        return improved_issues < current_issues
    
    def _calculate_priority(self, has_alt: bool, issues: List[str],
                          suggestions: List[AltTextSuggestion]) -> str:
        """Calculate priority level for alt text improvements."""
        if not has_alt:
            return "high"  # Missing alt text is high priority
        
        if any("Missing alt text" in issue for issue in issues):
            return "high"
        
        if len(issues) >= 3:
            return "high"
        elif len(issues) >= 1:
            return "medium"
        else:
            return "low"
    
    def _create_error_analysis(self, image: Dict[str, Any]) -> ImageAnalysis:
        """Create error analysis when image processing fails."""
        return ImageAnalysis(
            image_id=image.get('id', 'unknown'),
            has_alt_text=False,
            current_alt_text="",
            image_description="",
            context="",
            accessibility_issues=["Analysis failed"],
            suggestions=[],
            priority="medium"
        )