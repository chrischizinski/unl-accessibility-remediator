#!/usr/bin/env python3
"""
Quick accessibility analysis test for sample files.
Analyzes HTML files without requiring full Docker setup.
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import json

def analyze_html_accessibility(file_path):
    """Analyze HTML file for accessibility issues."""
    results = {
        "file": str(file_path),
        "success": True,
        "issues": [],
        "total_issues": 0,
        "accessibility_score": 100
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check for missing alt text
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                results["issues"].append({
                    "type": "missing_alt_text",
                    "severity": "high",
                    "description": f"Image missing alt text: {img.get('src', 'unknown')}"
                })
        
        # Check for empty alt text (decorative images should have alt="")
        for img in images:
            alt = img.get('alt', '')
            src = img.get('src', '')
            if alt in ['image', 'photo', 'picture', 'graphic'] or (alt and len(alt) < 3):
                results["issues"].append({
                    "type": "poor_alt_text", 
                    "severity": "medium",
                    "description": f"Poor alt text '{alt}' for image: {src}"
                })
        
        # Check for heading structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        prev_level = 0
        for heading in headings:
            level = int(heading.name[1])
            if level > prev_level + 1:
                results["issues"].append({
                    "type": "heading_hierarchy",
                    "severity": "medium", 
                    "description": f"Heading level jumps from h{prev_level} to h{level}"
                })
            prev_level = level
        
        # Check for vague link text
        links = soup.find_all('a')
        vague_text = ['click here', 'read more', 'more info', 'here', 'more', 'link']
        for link in links:
            text = link.get_text().strip().lower()
            if text in vague_text:
                results["issues"].append({
                    "type": "vague_link_text",
                    "severity": "medium",
                    "description": f"Vague link text: '{text}'"
                })
        
        # Check for missing form labels
        inputs = soup.find_all(['input', 'textarea', 'select'])
        for input_elem in inputs:
            input_id = input_elem.get('id')
            input_type = input_elem.get('type', 'text')
            if input_type not in ['hidden', 'submit', 'button']:
                # Look for associated label
                if input_id:
                    label = soup.find('label', {'for': input_id})
                    if not label:
                        results["issues"].append({
                            "type": "missing_form_label",
                            "severity": "high",
                            "description": f"Form input missing label: {input_type}"
                        })
        
        # Check for missing page title
        title = soup.find('title')
        if not title or not title.get_text().strip():
            results["issues"].append({
                "type": "missing_title",
                "severity": "high", 
                "description": "Page missing title element"
            })
        
        # Check for language attribute
        html_tag = soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            results["issues"].append({
                "type": "missing_lang",
                "severity": "medium",
                "description": "HTML element missing lang attribute"
            })
        
        # Calculate accessibility score
        total_issues = len(results["issues"])
        results["total_issues"] = total_issues
        
        # Rough scoring: start at 100, deduct points for issues
        score = 100
        for issue in results["issues"]:
            if issue["severity"] == "high":
                score -= 15
            elif issue["severity"] == "medium": 
                score -= 10
            else:
                score -= 5
        
        results["accessibility_score"] = max(0, score)
        
        # Add summary stats
        results["stats"] = {
            "total_images": len(images),
            "images_with_alt": len([img for img in images if img.get('alt') is not None]),
            "total_links": len(links),
            "total_headings": len(headings),
            "total_inputs": len(inputs)
        }
        
    except Exception as e:
        results["success"] = False
        results["error"] = str(e)
    
    return results

def analyze_sample_files():
    """Analyze all sample files in the testing directory."""
    sample_dir = Path("testing/sample_files")
    results = []
    
    print("🧪 UNL Accessibility Remediator - Sample File Analysis")
    print("=" * 60)
    
    # Find HTML files
    html_files = list(sample_dir.glob("*.html")) + list(sample_dir.glob("*.htm"))
    
    for html_file in html_files:
        print(f"\n📄 Analyzing: {html_file.name}")
        result = analyze_html_accessibility(html_file)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ Analysis complete")
            print(f"   📊 Accessibility Score: {result['accessibility_score']}%")
            print(f"   🔍 Issues Found: {result['total_issues']}")
            
            if result["issues"]:
                print(f"   📋 Issues by type:")
                issue_types = {}
                for issue in result["issues"]:
                    issue_type = issue["type"].replace("_", " ").title()
                    if issue_type not in issue_types:
                        issue_types[issue_type] = 0
                    issue_types[issue_type] += 1
                
                for issue_type, count in issue_types.items():
                    print(f"      • {issue_type}: {count}")
        else:
            print(f"   ❌ Analysis failed: {result.get('error', 'Unknown error')}")
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 60)
    successful = [r for r in results if r["success"]]
    if successful:
        avg_score = sum(r["accessibility_score"] for r in successful) / len(successful)
        total_issues = sum(r["total_issues"] for r in successful)
        print(f"Files analyzed: {len(successful)}")
        print(f"Average accessibility score: {avg_score:.1f}%") 
        print(f"Total issues found: {total_issues}")
        
        # Most common issues
        all_issues = []
        for result in successful:
            all_issues.extend(result["issues"])
        
        if all_issues:
            issue_counts = {}
            for issue in all_issues:
                issue_type = issue["type"].replace("_", " ").title()
                if issue_type not in issue_counts:
                    issue_counts[issue_type] = 0
                issue_counts[issue_type] += 1
            
            print(f"\nMost common issues:")
            for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  • {issue_type}: {count}")
    
    # Save detailed results
    output_file = "testing/reports/sample_analysis_results.json"
    os.makedirs("testing/reports", exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    try:
        analyze_sample_files()
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        import traceback
        traceback.print_exc()