"""
Contrast Checker Module

Validates color contrast ratios according to WCAG 2.1 Level AA requirements.
Implements UNL's accessibility standards for digital course materials.

WCAG 2.1 Level AA Requirements:
- Normal text: 4.5:1 minimum contrast ratio
- Large text (18pt+ or 14pt+ bold): 3:1 minimum contrast ratio
- Non-text elements: 3:1 minimum contrast ratio
"""

import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from colorzero import Color
from dataclasses import dataclass


@dataclass
class ContrastResult:
    """Result of a contrast ratio check."""
    foreground_color: str
    background_color: str
    contrast_ratio: float
    meets_aa_normal: bool  # 4.5:1 for normal text
    meets_aa_large: bool   # 3:1 for large text
    meets_aaa_normal: bool # 7:1 for normal text (optional)
    meets_aaa_large: bool  # 4.5:1 for large text (optional)
    element_type: str
    text_content: Optional[str] = None
    font_size: Optional[float] = None
    is_bold: bool = False


class ContrastChecker:
    """
    WCAG 2.1 Level AA contrast ratio checker.
    
    Follows UNL's accessibility requirements for digital course materials.
    """
    
    # WCAG contrast ratio thresholds
    AA_NORMAL_RATIO = 4.5
    AA_LARGE_RATIO = 3.0
    AAA_NORMAL_RATIO = 7.0
    AAA_LARGE_RATIO = 4.5
    
    # Large text thresholds (in points)
    LARGE_TEXT_SIZE = 18.0
    LARGE_TEXT_BOLD_SIZE = 14.0
    
    def __init__(self):
        """Initialize contrast checker."""
        self.logger = logging.getLogger(__name__)
    
    def check_contrast(
        self,
        foreground: str,
        background: str,
        element_type: str = "text",
        text_content: str = None,
        font_size: float = None,
        is_bold: bool = False
    ) -> ContrastResult:
        """
        Check contrast ratio between foreground and background colors.
        
        Args:
            foreground: Foreground color (hex, rgb, or named)
            background: Background color (hex, rgb, or named)
            element_type: Type of element (text, heading, button, etc.)
            text_content: Actual text content (for context)
            font_size: Font size in points
            is_bold: Whether text is bold
            
        Returns:
            ContrastResult with compliance information
        """
        try:
            # Parse colors
            fg_color = self._parse_color(foreground)
            bg_color = self._parse_color(background)
            
            if not fg_color or not bg_color:
                self.logger.warning(f"Could not parse colors: {foreground}, {background}")
                return self._create_error_result(foreground, background, element_type)
            
            # Calculate contrast ratio
            ratio = self._calculate_contrast_ratio(fg_color, bg_color)
            
            # Determine if text is considered "large"
            is_large_text = self._is_large_text(font_size, is_bold)
            
            # Check compliance levels
            meets_aa_normal = ratio >= self.AA_NORMAL_RATIO
            meets_aa_large = ratio >= self.AA_LARGE_RATIO
            meets_aaa_normal = ratio >= self.AAA_NORMAL_RATIO
            meets_aaa_large = ratio >= self.AAA_LARGE_RATIO
            
            result = ContrastResult(
                foreground_color=foreground,
                background_color=background,
                contrast_ratio=ratio,
                meets_aa_normal=meets_aa_normal,
                meets_aa_large=meets_aa_large,
                meets_aaa_normal=meets_aaa_normal,
                meets_aaa_large=meets_aaa_large,
                element_type=element_type,
                text_content=text_content,
                font_size=font_size,
                is_bold=is_bold
            )
            
            # Log results for debugging
            compliance_status = self._get_compliance_status(result, is_large_text)
            self.logger.debug(f"Contrast check: {ratio:.2f}:1 - {compliance_status}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking contrast: {e}")
            return self._create_error_result(foreground, background, element_type)
    
    def check_multiple_contrasts(self, color_data: List[Dict[str, Any]]) -> List[ContrastResult]:
        """
        Check contrast for multiple color combinations.
        
        Args:
            color_data: List of dictionaries with color information
            
        Returns:
            List of ContrastResult objects
        """
        results = []
        
        for data in color_data:
            result = self.check_contrast(
                foreground=data.get('foreground', '#000000'),
                background=data.get('background', '#ffffff'),
                element_type=data.get('element_type', 'text'),
                text_content=data.get('text_content'),
                font_size=data.get('font_size'),
                is_bold=data.get('is_bold', False)
            )
            results.append(result)
        
        return results
    
    def get_accessibility_issues(self, results: List[ContrastResult]) -> List[Dict[str, Any]]:
        """
        Extract accessibility issues from contrast check results.
        
        Args:
            results: List of ContrastResult objects
            
        Returns:
            List of issues with recommendations
        """
        issues = []
        
        for result in results:
            # Determine if this is large text
            is_large = self._is_large_text(result.font_size, result.is_bold)
            
            # Check AA compliance (required for UNL)
            if is_large and not result.meets_aa_large:
                issues.append(self._create_issue(result, "AA Large Text", is_large))
            elif not is_large and not result.meets_aa_normal:
                issues.append(self._create_issue(result, "AA Normal Text", is_large))
        
        return issues
    
    def suggest_color_fixes(self, result: ContrastResult) -> List[Dict[str, str]]:
        """
        Suggest color modifications to meet WCAG requirements.
        
        Args:
            result: ContrastResult that failed compliance
            
        Returns:
            List of suggested color fixes
        """
        suggestions = []
        
        try:
            fg_color = self._parse_color(result.foreground_color)
            bg_color = self._parse_color(result.background_color)
            
            if not fg_color or not bg_color:
                return suggestions
            
            # Determine target ratio based on text size
            is_large = self._is_large_text(result.font_size, result.is_bold)
            target_ratio = self.AA_LARGE_RATIO if is_large else self.AA_NORMAL_RATIO
            
            # Try darkening foreground
            darker_fg = self._adjust_brightness(fg_color, target_ratio, bg_color, darken=True)
            if darker_fg:
                suggestions.append({
                    "type": "darken_foreground",
                    "description": f"Darken text color to {darker_fg}",
                    "original_color": result.foreground_color,
                    "suggested_color": darker_fg
                })
            
            # Try lightening background
            lighter_bg = self._adjust_brightness(bg_color, target_ratio, fg_color, darken=False)
            if lighter_bg:
                suggestions.append({
                    "type": "lighten_background",
                    "description": f"Lighten background color to {lighter_bg}",
                    "original_color": result.background_color,
                    "suggested_color": lighter_bg
                })
            
            # Try high contrast alternatives
            if target_ratio >= self.AA_NORMAL_RATIO:
                suggestions.extend(self._get_high_contrast_alternatives(result))
            
        except Exception as e:
            self.logger.warning(f"Could not generate color suggestions: {e}")
        
        return suggestions
    
    def _parse_color(self, color_str: str) -> Optional[Color]:
        """Parse color string into Color object."""
        try:
            color_str = color_str.strip()
            
            # Handle hex colors
            if color_str.startswith('#'):
                return Color(color_str)
            
            # Handle rgb() format
            if color_str.startswith('rgb'):
                rgb_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
                if rgb_match:
                    r, g, b = map(int, rgb_match.groups())
                    return Color(r/255, g/255, b/255)
            
            # Handle named colors
            try:
                return Color(color_str)
            except ValueError:
                pass
            
            # Default to black if parsing fails
            self.logger.warning(f"Could not parse color: {color_str}")
            return Color('#000000')
            
        except Exception as e:
            self.logger.error(f"Color parsing error: {e}")
            return None
    
    def _calculate_contrast_ratio(self, color1: Color, color2: Color) -> float:
        """
        Calculate contrast ratio between two colors.
        
        Uses WCAG formula: (L1 + 0.05) / (L2 + 0.05)
        where L1 is lighter color luminance and L2 is darker color luminance.
        """
        lum1 = self._get_relative_luminance(color1)
        lum2 = self._get_relative_luminance(color2)
        
        # Ensure lighter color is in numerator
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        ratio = (lighter + 0.05) / (darker + 0.05)
        return round(ratio, 2)
    
    def _get_relative_luminance(self, color: Color) -> float:
        """Calculate relative luminance using WCAG formula."""
        def gamma_correct(value):
            if value <= 0.03928:
                return value / 12.92
            else:
                return pow((value + 0.055) / 1.055, 2.4)
        
        r = gamma_correct(color.r)
        g = gamma_correct(color.g)
        b = gamma_correct(color.b)
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def _is_large_text(self, font_size: Optional[float], is_bold: bool) -> bool:
        """Determine if text qualifies as "large" per WCAG definition."""
        if font_size is None:
            return False
        
        if is_bold:
            return font_size >= self.LARGE_TEXT_BOLD_SIZE
        else:
            return font_size >= self.LARGE_TEXT_SIZE
    
    def _get_compliance_status(self, result: ContrastResult, is_large_text: bool) -> str:
        """Get human-readable compliance status."""
        if is_large_text:
            if result.meets_aa_large:
                return "✓ Passes AA (Large Text)"
            else:
                return "✗ Fails AA (Large Text)"
        else:
            if result.meets_aa_normal:
                return "✓ Passes AA (Normal Text)"
            else:
                return "✗ Fails AA (Normal Text)"
    
    def _create_error_result(self, foreground: str, background: str, element_type: str) -> ContrastResult:
        """Create error result when contrast cannot be calculated."""
        return ContrastResult(
            foreground_color=foreground,
            background_color=background,
            contrast_ratio=0.0,
            meets_aa_normal=False,
            meets_aa_large=False,
            meets_aaa_normal=False,
            meets_aaa_large=False,
            element_type=element_type
        )
    
    def _create_issue(self, result: ContrastResult, compliance_level: str, is_large: bool) -> Dict[str, Any]:
        """Create accessibility issue dictionary."""
        target_ratio = self.AA_LARGE_RATIO if is_large else self.AA_NORMAL_RATIO
        
        return {
            "type": "contrast",
            "severity": "high" if result.contrast_ratio < 3.0 else "medium",
            "element": result.element_type,
            "current_ratio": result.contrast_ratio,
            "required_ratio": target_ratio,
            "meets_aa": result.meets_aa_large if is_large else result.meets_aa_normal,
            "foreground": result.foreground_color,
            "background": result.background_color,
            "text_content": result.text_content,
            "recommendation": f"Increase contrast to at least {target_ratio}:1 for {compliance_level}",
            "is_large_text": is_large
        }
    
    def _adjust_brightness(self, color: Color, target_ratio: float, 
                          other_color: Color, darken: bool) -> Optional[str]:
        """Attempt to adjust color brightness to meet target contrast ratio."""
        try:
            current_ratio = self._calculate_contrast_ratio(color, other_color)
            
            if current_ratio >= target_ratio:
                return None  # Already meets requirement
            
            # Try adjusting in steps
            for factor in [0.8, 0.6, 0.4, 0.2] if darken else [1.2, 1.4, 1.6, 1.8]:
                if darken:
                    adjusted = Color(
                        min(1.0, max(0.0, color.r * factor)),
                        min(1.0, max(0.0, color.g * factor)),
                        min(1.0, max(0.0, color.b * factor))
                    )
                else:
                    adjusted = Color(
                        min(1.0, color.r + (1 - color.r) * (factor - 1)),
                        min(1.0, color.g + (1 - color.g) * (factor - 1)),
                        min(1.0, color.b + (1 - color.b) * (factor - 1))
                    )
                
                new_ratio = self._calculate_contrast_ratio(adjusted, other_color)
                if new_ratio >= target_ratio:
                    return f"#{int(adjusted.r*255):02x}{int(adjusted.g*255):02x}{int(adjusted.b*255):02x}"
            
            return None
            
        except Exception:
            return None
    
    def _get_high_contrast_alternatives(self, result: ContrastResult) -> List[Dict[str, str]]:
        """Get high contrast color alternatives."""
        return [
            {
                "type": "high_contrast",
                "description": "Use black text on white background",
                "original_color": result.foreground_color,
                "suggested_color": "#000000",
                "background_color": "#ffffff"
            },
            {
                "type": "high_contrast", 
                "description": "Use white text on dark background",
                "original_color": result.foreground_color,
                "suggested_color": "#ffffff",
                "background_color": "#1a1a1a"
            }
        ]