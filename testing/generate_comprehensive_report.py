#!/usr/bin/env python3
"""
Generate comprehensive accessibility reports for UNL documents.
Creates slide-by-slide or page-by-page detailed analysis with remediation status.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import re

def generate_comprehensive_html_report(file_path, analysis_results, fixes_results=None):
    """Generate a comprehensive slide-by-slide accessibility report for HTML presentations."""
    
    report = {
        "document_info": {
            "file_name": Path(file_path).name,
            "file_path": str(file_path),
            "analysis_date": datetime.now().isoformat(),
            "total_slides": 0,
            "file_type": "HTML Presentation"
        },
        "executive_summary": {
            "overall_score": 0,
            "total_issues": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "fixes_applied": 0,
            "manual_review_needed": 0
        },
        "slides": [],
        "remediation_summary": {
            "automatic_fixes": [],
            "manual_actions_needed": [],
            "wcag_compliance_status": {}
        }
    }
    
    try:
        # Read HTML file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract slides (look for common slide patterns)
        slides = (soup.find_all('div', class_='slide') or 
                 soup.find_all('section') or 
                 soup.find_all('div', class_='reveal'))
        
        if not slides:
            # If no clear slide structure, treat as single page
            slides = [soup]
        
        report["document_info"]["total_slides"] = len(slides)
        
        slide_number = 1
        for slide in slides:
            slide_analysis = analyze_slide_accessibility(slide, slide_number)
            
            # Add remediation status if fixes were applied
            if fixes_results:
                slide_analysis["remediation"] = get_slide_remediation_status(
                    slide_analysis, fixes_results
                )
            
            report["slides"].append(slide_analysis)
            slide_number += 1
        
        # Calculate summary statistics
        calculate_summary_statistics(report)
        
        # Generate remediation summary
        generate_remediation_summary(report, fixes_results)
        
    except Exception as e:
        report["error"] = f"Error analyzing file: {str(e)}"
    
    return report

def analyze_slide_accessibility(slide, slide_number):
    """Analyze accessibility issues for a single slide."""
    
    slide_analysis = {
        "slide_number": slide_number,
        "slide_title": extract_slide_title(slide),
        "content_summary": extract_content_summary(slide),
        "issues": [],
        "accessibility_score": 100,
        "elements_analyzed": {
            "images": 0,
            "links": 0,
            "headings": 0,
            "tables": 0,
            "forms": 0
        }
    }
    
    # Analyze images
    images = slide.find_all('img')
    slide_analysis["elements_analyzed"]["images"] = len(images)
    
    for i, img in enumerate(images):
        img_issues = analyze_image_accessibility(img, i + 1, slide_number)
        slide_analysis["issues"].extend(img_issues)
    
    # Analyze links
    links = slide.find_all('a')
    slide_analysis["elements_analyzed"]["links"] = len(links)
    
    for i, link in enumerate(links):
        link_issues = analyze_link_accessibility(link, i + 1, slide_number)
        slide_analysis["issues"].extend(link_issues)
    
    # Analyze headings
    headings = slide.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    slide_analysis["elements_analyzed"]["headings"] = len(headings)
    
    heading_issues = analyze_heading_structure(headings, slide_number)
    slide_analysis["issues"].extend(heading_issues)
    
    # Analyze tables
    tables = slide.find_all('table')
    slide_analysis["elements_analyzed"]["tables"] = len(tables)
    
    for i, table in enumerate(tables):
        table_issues = analyze_table_accessibility(table, i + 1, slide_number)
        slide_analysis["issues"].extend(table_issues)
    
    # Analyze text content
    text_issues = analyze_text_accessibility(slide, slide_number)
    slide_analysis["issues"].extend(text_issues)
    
    # Calculate slide accessibility score
    slide_analysis["accessibility_score"] = calculate_slide_score(slide_analysis["issues"])
    
    return slide_analysis

def analyze_image_accessibility(img, img_number, slide_number):
    """Analyze accessibility issues for a single image."""
    issues = []
    
    alt_text = img.get('alt', '')
    src = img.get('src', img.get('data-src', ''))
    
    if not alt_text:
        issues.append({
            "type": "missing_alt_text",
            "severity": "high",
            "element_type": "image",
            "element_number": img_number,
            "slide": slide_number,
            "description": f"Image {img_number} missing alternative text",
            "current_state": "No alt attribute",
            "required_action": "Add descriptive alt text explaining the image content and purpose",
            "wcag_criterion": "1.1.1 Non-text Content",
            "priority": "Must Fix",
            "estimated_time": "2-5 minutes",
            "technical_details": {
                "element": str(img)[:200] + "...",
                "src": src[:100] + "..." if len(src) > 100 else src
            }
        })
    
    elif alt_text.lower() in ['image', 'photo', 'picture', 'graphic', 'img'] or len(alt_text) < 3:
        issues.append({
            "type": "poor_alt_text",
            "severity": "medium",
            "element_type": "image",
            "element_number": img_number,
            "slide": slide_number,
            "description": f"Image {img_number} has poor quality alt text: '{alt_text}'",
            "current_state": f"Alt text: '{alt_text}'",
            "required_action": "Replace with descriptive alt text that explains the image's content and purpose",
            "wcag_criterion": "1.1.1 Non-text Content",
            "priority": "Should Fix",
            "estimated_time": "3-7 minutes",
            "technical_details": {
                "element": str(img)[:200] + "...",
                "current_alt": alt_text,
                "src": src[:100] + "..." if len(src) > 100 else src
            }
        })
    
    return issues

def analyze_link_accessibility(link, link_number, slide_number):
    """Analyze accessibility issues for a single link."""
    issues = []
    
    link_text = link.get_text().strip()
    href = link.get('href', '')
    
    vague_patterns = ['click here', 'here', 'read more', 'more info', 'more', 'link', 'download']
    
    if link_text.lower() in vague_patterns:
        issues.append({
            "type": "vague_link_text",
            "severity": "medium",
            "element_type": "link",
            "element_number": link_number,
            "slide": slide_number,
            "description": f"Link {link_number} has vague text: '{link_text}'",
            "current_state": f"Link text: '{link_text}'",
            "required_action": "Replace with descriptive text that explains the link's destination or purpose",
            "wcag_criterion": "2.4.4 Link Purpose",
            "priority": "Should Fix",
            "estimated_time": "2-3 minutes",
            "technical_details": {
                "element": str(link)[:200] + "...",
                "current_text": link_text,
                "href": href[:100] + "..." if len(href) > 100 else href
            },
            "suggestions": [
                f"'View {href.split('/')[-1]}'" if href else "View resource",
                "Learn more about [topic]",
                "Download [document type]"
            ]
        })
    
    return issues

def analyze_heading_structure(headings, slide_number):
    """Analyze heading structure for accessibility."""
    issues = []
    
    if not headings:
        return issues
    
    prev_level = 0
    for i, heading in enumerate(headings):
        level = int(heading.name[1])
        
        if level > prev_level + 1:
            issues.append({
                "type": "heading_hierarchy",
                "severity": "medium",
                "element_type": "heading",
                "element_number": i + 1,
                "slide": slide_number,
                "description": f"Heading level jumps from h{prev_level} to h{level}",
                "current_state": f"Heading hierarchy: h{prev_level} → h{level}",
                "required_action": "Use sequential heading levels (h1, h2, h3, etc.) without skipping",
                "wcag_criterion": "1.3.1 Info and Relationships",
                "priority": "Should Fix",
                "estimated_time": "1-2 minutes",
                "technical_details": {
                    "element": str(heading)[:200] + "...",
                    "text": heading.get_text()[:100],
                    "expected_level": f"h{prev_level + 1}"
                }
            })
        
        prev_level = level
    
    return issues

def analyze_table_accessibility(table, table_number, slide_number):
    """Analyze table accessibility."""
    issues = []
    
    # Check for header row
    has_thead = table.find('thead') is not None
    has_th = table.find('th') is not None
    
    if not has_thead and not has_th:
        rows = table.find_all('tr')
        if len(rows) > 1:
            issues.append({
                "type": "missing_table_headers",
                "severity": "medium",
                "element_type": "table",
                "element_number": table_number,
                "slide": slide_number,
                "description": f"Table {table_number} missing header row",
                "current_state": "No <th> elements or <thead> section",
                "required_action": "Mark first row as headers using <th> elements or add <thead>",
                "wcag_criterion": "1.3.1 Info and Relationships",
                "priority": "Should Fix",
                "estimated_time": "3-5 minutes",
                "technical_details": {
                    "element": str(table)[:200] + "...",
                    "rows": len(rows),
                    "columns": len(rows[0].find_all(['td', 'th'])) if rows else 0
                }
            })
    
    return issues

def analyze_text_accessibility(slide, slide_number):
    """Analyze text accessibility issues."""
    issues = []
    
    # Check for all caps text
    all_text = slide.get_text()
    paragraphs = slide.find_all(['p', 'div', 'span'])
    
    all_caps_count = 0
    for para in paragraphs:
        text = para.get_text().strip()
        if len(text) > 10 and text.isupper():
            all_caps_count += 1
    
    if all_caps_count > 0:
        issues.append({
            "type": "all_caps_text",
            "severity": "medium",
            "element_type": "text",
            "slide": slide_number,
            "description": f"{all_caps_count} text blocks in ALL CAPS",
            "current_state": f"{all_caps_count} text elements using all capital letters",
            "required_action": "Convert to sentence case, use bold or emphasis for importance",
            "wcag_criterion": "1.4.8 Visual Presentation",
            "priority": "Should Fix",
            "estimated_time": f"{all_caps_count * 2}-{all_caps_count * 3} minutes",
            "technical_details": {
                "count": all_caps_count,
                "examples": [p.get_text()[:50] + "..." for p in paragraphs 
                           if p.get_text().isupper() and len(p.get_text()) > 10][:3]
            }
        })
    
    return issues

def extract_slide_title(slide):
    """Extract title from slide."""
    title_element = (slide.find('h1') or 
                    slide.find('h2') or 
                    slide.find('[data-title]') or
                    slide.find('.slide-title'))
    
    if title_element:
        return title_element.get_text().strip()[:100]
    
    # Try to get first meaningful text
    text = slide.get_text().strip()
    if text:
        first_line = text.split('\n')[0].strip()
        return first_line[:100] if first_line else "Untitled Slide"
    
    return "Untitled Slide"

def extract_content_summary(slide):
    """Extract content summary from slide."""
    text = slide.get_text().strip()
    images = len(slide.find_all('img'))
    links = len(slide.find_all('a'))
    tables = len(slide.find_all('table'))
    
    summary = []
    if text:
        word_count = len(text.split())
        summary.append(f"{word_count} words")
    if images:
        summary.append(f"{images} image{'s' if images != 1 else ''}")
    if links:
        summary.append(f"{links} link{'s' if links != 1 else ''}")
    if tables:
        summary.append(f"{tables} table{'s' if tables != 1 else ''}")
    
    return ", ".join(summary) if summary else "No content"

def calculate_slide_score(issues):
    """Calculate accessibility score for a slide."""
    score = 100
    
    for issue in issues:
        if issue["severity"] == "critical":
            score -= 25
        elif issue["severity"] == "high":
            score -= 15
        elif issue["severity"] == "medium":
            score -= 10
        elif issue["severity"] == "low":
            score -= 5
    
    return max(0, score)

def get_slide_remediation_status(slide_analysis, fixes_results):
    """Get remediation status for a slide."""
    remediation = {
        "automatic_fixes_applied": 0,
        "manual_actions_remaining": 0,
        "fixes_details": [],
        "status": "Not Processed"
    }
    
    if fixes_results and "fixes_applied" in fixes_results:
        for fix in fixes_results["fixes_applied"]:
            remediation["fixes_details"].append({
                "type": fix.get("type", "unknown"),
                "description": fix.get("description", ""),
                "status": "Applied Automatically"
            })
            remediation["automatic_fixes_applied"] += 1
    
    # Count remaining manual actions
    for issue in slide_analysis["issues"]:
        if issue.get("priority") in ["Must Fix", "Should Fix"]:
            remediation["manual_actions_remaining"] += 1
    
    # Determine overall status
    if remediation["automatic_fixes_applied"] > 0 and remediation["manual_actions_remaining"] == 0:
        remediation["status"] = "Fully Remediated"
    elif remediation["automatic_fixes_applied"] > 0:
        remediation["status"] = "Partially Remediated"
    elif remediation["manual_actions_remaining"] > 0:
        remediation["status"] = "Manual Review Required"
    else:
        remediation["status"] = "No Issues Found"
    
    return remediation

def calculate_summary_statistics(report):
    """Calculate summary statistics for the report."""
    total_issues = 0
    total_score = 0
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for slide in report["slides"]:
        total_score += slide["accessibility_score"]
        for issue in slide["issues"]:
            total_issues += 1
            severity = issue.get("severity", "low")
            if severity in severity_counts:
                severity_counts[severity] += 1
    
    report["executive_summary"]["overall_score"] = (
        total_score // len(report["slides"]) if report["slides"] else 0
    )
    report["executive_summary"]["total_issues"] = total_issues
    report["executive_summary"]["critical_issues"] = severity_counts["critical"]
    report["executive_summary"]["high_issues"] = severity_counts["high"]
    report["executive_summary"]["medium_issues"] = severity_counts["medium"]
    report["executive_summary"]["low_issues"] = severity_counts["low"]

def generate_remediation_summary(report, fixes_results):
    """Generate remediation summary with action items."""
    
    # Group issues by type for actionable recommendations
    issue_groups = {}
    for slide in report["slides"]:
        for issue in slide["issues"]:
            issue_type = issue["type"]
            if issue_type not in issue_groups:
                issue_groups[issue_type] = {
                    "count": 0,
                    "priority": issue.get("priority", "Should Fix"),
                    "estimated_total_time": 0,
                    "slides_affected": set(),
                    "wcag_criterion": issue.get("wcag_criterion", ""),
                    "example_action": issue.get("required_action", "")
                }
            
            issue_groups[issue_type]["count"] += 1
            issue_groups[issue_type]["slides_affected"].add(issue["slide"])
            
            # Parse estimated time
            time_str = issue.get("estimated_time", "2-3 minutes")
            avg_time = parse_time_estimate(time_str)
            issue_groups[issue_type]["estimated_total_time"] += avg_time
    
    # Create manual action items
    manual_actions = []
    for issue_type, data in issue_groups.items():
        action = {
            "issue_type": issue_type.replace("_", " ").title(),
            "count": data["count"],
            "slides_affected": sorted(list(data["slides_affected"])),
            "priority": data["priority"],
            "total_estimated_time": f"{data['estimated_total_time']:.0f} minutes",
            "wcag_criterion": data["wcag_criterion"],
            "action_needed": data["example_action"],
            "status": "Manual Review Required"
        }
        manual_actions.append(action)
    
    # Sort by priority and count
    priority_order = {"Must Fix": 0, "Should Fix": 1, "Could Fix": 2}
    manual_actions.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["count"]))
    
    report["remediation_summary"]["manual_actions_needed"] = manual_actions
    
    # Add automatic fixes if available
    if fixes_results and "fixes_applied" in fixes_results:
        report["remediation_summary"]["automatic_fixes"] = fixes_results["fixes_applied"]
        report["executive_summary"]["fixes_applied"] = len(fixes_results["fixes_applied"])

def parse_time_estimate(time_str):
    """Parse time estimate string to get average minutes."""
    try:
        # Extract numbers from string like "2-5 minutes" or "3 minutes"
        numbers = re.findall(r'\d+', time_str)
        if len(numbers) >= 2:
            return (int(numbers[0]) + int(numbers[1])) / 2
        elif len(numbers) == 1:
            return int(numbers[0])
    except:
        pass
    return 3  # Default estimate

def generate_html_report_output(report, output_file):
    """Generate HTML report file."""
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report - {report['document_info']['file_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #d00000; color: white; padding: 20px; margin-bottom: 20px; }}
        .summary {{ background: #f5f1e7; padding: 15px; margin: 20px 0; border-left: 5px solid #d00000; }}
        .slide {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; }}
        .slide-header {{ background: #f8f8f8; padding: 10px; margin: -15px -15px 15px -15px; }}
        .issue {{ margin: 10px 0; padding: 10px; border-left: 4px solid #orange; background: #fff3cd; }}
        .issue.high {{ border-left-color: #dc3545; background: #f8d7da; }}
        .issue.medium {{ border-left-color: #fd7e14; background: #fff3cd; }}
        .issue.low {{ border-left-color: #28a745; background: #d4edda; }}
        .remediation {{ background: #e8f5e8; padding: 10px; margin: 10px 0; }}
        .score {{ font-size: 1.2em; font-weight: bold; }}
        .score.good {{ color: #28a745; }}
        .score.fair {{ color: #fd7e14; }}
        .score.poor {{ color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f2f2f2; }}
        .priority-must {{ color: #dc3545; font-weight: bold; }}
        .priority-should {{ color: #fd7e14; font-weight: bold; }}
        .priority-could {{ color: #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 UNL Accessibility Report</h1>
        <h2>{report['document_info']['file_name']}</h2>
        <p>Generated: {datetime.fromisoformat(report['document_info']['analysis_date']).strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>

    <div class="summary">
        <h2>📊 Executive Summary</h2>
        <div class="score {'good' if report['executive_summary']['overall_score'] >= 80 else 'fair' if report['executive_summary']['overall_score'] >= 60 else 'poor'}">
            Overall Accessibility Score: {report['executive_summary']['overall_score']}%
        </div>
        <p><strong>Document:</strong> {report['document_info']['total_slides']} slides analyzed</p>
        <p><strong>Issues Found:</strong> {report['executive_summary']['total_issues']} total 
           ({report['executive_summary']['high_issues']} high, 
           {report['executive_summary']['medium_issues']} medium, 
           {report['executive_summary']['low_issues']} low priority)</p>
        <p><strong>Automatic Fixes:</strong> {report['executive_summary'].get('fixes_applied', 0)} applied</p>
    </div>
"""

    # Add remediation summary
    if report['remediation_summary']['manual_actions_needed']:
        html_template += """
    <div class="summary">
        <h2>🔧 Action Items Needed</h2>
        <table>
            <tr><th>Issue Type</th><th>Count</th><th>Slides</th><th>Priority</th><th>Est. Time</th><th>WCAG</th></tr>
"""
        for action in report['remediation_summary']['manual_actions_needed']:
            priority_class = f"priority-{action['priority'].split()[0].lower()}"
            slides_text = f"Slides {', '.join(map(str, action['slides_affected']))}"
            html_template += f"""
            <tr>
                <td>{action['issue_type']}</td>
                <td>{action['count']}</td>
                <td>{slides_text}</td>
                <td class="{priority_class}">{action['priority']}</td>
                <td>{action['total_estimated_time']}</td>
                <td>{action['wcag_criterion']}</td>
            </tr>
"""
        html_template += """
        </table>
    </div>
"""

    # Add slide-by-slide details
    html_template += """
    <h2>📑 Slide-by-Slide Analysis</h2>
"""

    for slide in report['slides']:
        score_class = 'good' if slide['accessibility_score'] >= 80 else 'fair' if slide['accessibility_score'] >= 60 else 'poor'
        
        html_template += f"""
    <div class="slide">
        <div class="slide-header">
            <h3>Slide {slide['slide_number']}: {slide['slide_title']}</h3>
            <div class="score {score_class}">Accessibility Score: {slide['accessibility_score']}%</div>
            <p><strong>Content:</strong> {slide['content_summary']}</p>
        </div>
"""
        
        if slide['issues']:
            html_template += "<h4>🔍 Issues Found:</h4>"
            for issue in slide['issues']:
                severity_class = issue.get('severity', 'low')
                html_template += f"""
        <div class="issue {severity_class}">
            <h5>{issue['description']}</h5>
            <p><strong>Current State:</strong> {issue.get('current_state', 'Not specified')}</p>
            <p><strong>Required Action:</strong> {issue.get('required_action', 'Review needed')}</p>
            <p><strong>Priority:</strong> {issue.get('priority', 'Should Fix')} | 
               <strong>Est. Time:</strong> {issue.get('estimated_time', 'Unknown')} | 
               <strong>WCAG:</strong> {issue.get('wcag_criterion', 'General')}</p>
        </div>
"""
        else:
            html_template += "<p>✅ No accessibility issues found on this slide.</p>"
        
        # Add remediation status if available
        if 'remediation' in slide:
            rem = slide['remediation']
            html_template += f"""
        <div class="remediation">
            <h4>🔧 Remediation Status: {rem['status']}</h4>
            <p>Automatic fixes applied: {rem['automatic_fixes_applied']} | 
               Manual actions remaining: {rem['manual_actions_remaining']}</p>
        </div>
"""
        
        html_template += "</div>"

    html_template += """
    <div class="summary">
        <h2>📞 Need Help?</h2>
        <p>For assistance with accessibility remediation:</p>
        <ul>
            <li>Digital Accessibility Training in Bridge</li>
            <li>Faculty Development Workshops</li>
            <li>Contact: Center for Transformative Teaching</li>
        </ul>
        <p><em>University of Nebraska–Lincoln | Digital Accessibility Initiative</em></p>
    </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

def test_comprehensive_reporting():
    """Test comprehensive report generation on sample files."""
    sample_dir = Path("testing/sample_files")
    reports_dir = Path("testing/reports/comprehensive")
    reports_dir.mkdir(exist_ok=True)
    
    print("📋 Generating Comprehensive Accessibility Reports")
    print("=" * 60)
    
    html_files = list(sample_dir.glob("*.html"))
    
    for html_file in html_files:
        print(f"\n📄 Generating report for: {html_file.name}")
        
        # Load previous analysis if available
        analysis_file = Path("testing/reports/sample_analysis_results.json")
        fixes_file = Path("testing/reports/auto_fix_test_results.json")
        
        analysis_results = None
        fixes_results = None
        
        if analysis_file.exists():
            with open(analysis_file) as f:
                all_analysis = json.load(f)
                for result in all_analysis:
                    if Path(result["file"]).name == html_file.name:
                        analysis_results = result
                        break
        
        if fixes_file.exists():
            with open(fixes_file) as f:
                all_fixes = json.load(f)
                for result in all_fixes:
                    if Path(result["original_file"]).name == html_file.name:
                        fixes_results = result
                        break
        
        # Generate comprehensive report
        comprehensive_report = generate_comprehensive_html_report(
            str(html_file), analysis_results, fixes_results
        )
        
        # Save JSON report
        json_output = reports_dir / f"{html_file.stem}_comprehensive_report.json"
        with open(json_output, 'w') as f:
            json.dump(comprehensive_report, f, indent=2, default=str)
        
        # Generate HTML report
        html_output = reports_dir / f"{html_file.stem}_accessibility_report.html"
        generate_html_report_output(comprehensive_report, html_output)
        
        print(f"   ✅ Comprehensive report generated")
        print(f"   📊 {comprehensive_report['document_info']['total_slides']} slides analyzed")
        print(f"   📋 {comprehensive_report['executive_summary']['total_issues']} issues documented")
        print(f"   💾 Reports saved:")
        print(f"      • JSON: {json_output}")
        print(f"      • HTML: {html_output}")
    
    print(f"\n🎉 All comprehensive reports generated in: {reports_dir}")
    return True

if __name__ == "__main__":
    try:
        test_comprehensive_reporting()
    except Exception as e:
        print(f"❌ Error generating reports: {e}")
        import traceback
        traceback.print_exc()