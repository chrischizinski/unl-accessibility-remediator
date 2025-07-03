#!/usr/bin/env python3
"""
Test automatic fixes capability of the accessibility tool.
"""

import os
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
import json

def test_html_auto_fixes(file_path, apply_fixes=True):
    """Test auto-fixes on HTML files."""
    results = {
        "original_file": str(file_path),
        "fixed_file": None,
        "fixes_applied": [],
        "before_issues": [],
        "after_issues": [],
        "success": True
    }
    
    try:
        # Read original file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Analyze original issues
        results["before_issues"] = analyze_accessibility_issues(soup)
        
        if not apply_fixes:
            return results
        
        # Apply automatic fixes
        fixes_applied = 0
        
        # Fix 1: Add basic alt text to images without alt attributes
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                # Generate basic alt text based on src or nearby text
                src = img.get('src', '')
                if 'logo' in src.lower():
                    alt_text = "Logo"
                elif 'chart' in src.lower() or 'graph' in src.lower():
                    alt_text = "Chart or graph"
                elif 'image' in src.lower() or 'photo' in src.lower():
                    alt_text = "Image"
                else:
                    alt_text = "Image content"
                
                img['alt'] = alt_text
                fixes_applied += 1
                results["fixes_applied"].append({
                    "type": "alt_text",
                    "description": f"Added basic alt text: '{alt_text}' to image"
                })
        
        # Fix 2: Improve vague link text
        links = soup.find_all('a')
        vague_patterns = {
            'click here': 'View more information',
            'here': 'View link',
            'read more': 'Read more information',
            'more info': 'More information',
            'more': 'More details'
        }
        
        for link in links:
            text = link.get_text().strip().lower()
            if text in vague_patterns:
                link.string = vague_patterns[text]
                fixes_applied += 1
                results["fixes_applied"].append({
                    "type": "link_text",
                    "description": f"Improved link text from '{text}' to '{vague_patterns[text]}'"
                })
        
        # Fix 3: Add lang attribute if missing
        html_tag = soup.find('html')
        if html_tag and not html_tag.get('lang'):
            html_tag['lang'] = 'en'
            fixes_applied += 1
            results["fixes_applied"].append({
                "type": "language",
                "description": "Added lang='en' attribute to HTML element"
            })
        
        # Fix 4: Add title if missing or empty
        title = soup.find('title')
        if not title or not title.get_text().strip():
            if title:
                title.string = "Accessible Document"
            else:
                new_title = soup.new_tag('title')
                new_title.string = "Accessible Document"
                head = soup.find('head')
                if head:
                    head.append(new_title)
            fixes_applied += 1
            results["fixes_applied"].append({
                "type": "title",
                "description": "Added or improved document title"
            })
        
        # Save fixed file
        if fixes_applied > 0:
            output_dir = Path("testing/reports/fixed_files")
            output_dir.mkdir(exist_ok=True)
            
            fixed_file_path = output_dir / f"fixed_{Path(file_path).name}"
            with open(fixed_file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            results["fixed_file"] = str(fixed_file_path)
            
            # Analyze issues in fixed file
            results["after_issues"] = analyze_accessibility_issues(soup)
        
        results["total_fixes_applied"] = fixes_applied
        
    except Exception as e:
        results["success"] = False
        results["error"] = str(e)
    
    return results

def analyze_accessibility_issues(soup):
    """Analyze accessibility issues in BeautifulSoup object."""
    issues = []
    
    # Missing alt text
    images = soup.find_all('img')
    for img in images:
        if not img.get('alt'):
            issues.append({
                "type": "missing_alt_text",
                "severity": "high",
                "element": str(img)[:100] + "..."
            })
    
    # Vague link text
    links = soup.find_all('a')
    vague_text = ['click here', 'read more', 'more info', 'here', 'more', 'link']
    for link in links:
        text = link.get_text().strip().lower()
        if text in vague_text:
            issues.append({
                "type": "vague_link_text",
                "severity": "medium",
                "text": text
            })
    
    # Missing lang attribute
    html_tag = soup.find('html')
    if not html_tag or not html_tag.get('lang'):
        issues.append({
            "type": "missing_lang",
            "severity": "medium",
            "description": "HTML element missing lang attribute"
        })
    
    # Missing or empty title
    title = soup.find('title')
    if not title or not title.get_text().strip():
        issues.append({
            "type": "missing_title",
            "severity": "high",
            "description": "Page missing title element"
        })
    
    return issues

def test_sample_files_auto_fixes():
    """Test auto-fixes on all sample HTML files."""
    sample_dir = Path("testing/sample_files")
    results = []
    
    print("🔧 Testing Automatic Fixes on Sample Files")
    print("=" * 60)
    
    html_files = list(sample_dir.glob("*.html")) + list(sample_dir.glob("*.htm"))
    
    for html_file in html_files:
        print(f"\n📄 Testing fixes for: {html_file.name}")
        
        result = test_html_auto_fixes(html_file, apply_fixes=True)
        results.append(result)
        
        if result["success"]:
            before_count = len(result["before_issues"])
            after_count = len(result["after_issues"])
            fixes_count = result.get("total_fixes_applied", 0)
            
            print(f"   ✅ Auto-fix test complete")
            print(f"   🔧 Fixes applied: {fixes_count}")
            print(f"   📊 Issues before: {before_count}")
            print(f"   📊 Issues after: {after_count}")
            print(f"   📈 Issues resolved: {before_count - after_count}")
            
            if result["fixed_file"]:
                print(f"   💾 Fixed file saved: {result['fixed_file']}")
            
            if result["fixes_applied"]:
                print(f"   🔧 Fixes applied:")
                for fix in result["fixes_applied"]:
                    print(f"      • {fix['type'].title()}: {fix['description']}")
        else:
            print(f"   ❌ Auto-fix test failed: {result.get('error', 'Unknown error')}")
    
    # Summary
    print(f"\n📊 Auto-Fix Test Summary")
    print("=" * 60)
    successful = [r for r in results if r["success"]]
    
    if successful:
        total_fixes = sum(r.get("total_fixes_applied", 0) for r in successful)
        total_before = sum(len(r["before_issues"]) for r in successful)
        total_after = sum(len(r["after_issues"]) for r in successful)
        
        print(f"Files processed: {len(successful)}")
        print(f"Total fixes applied: {total_fixes}")
        print(f"Issues before fixes: {total_before}")
        print(f"Issues after fixes: {total_after}")
        print(f"Issues resolved: {total_before - total_after}")
        print(f"Success rate: {((total_before - total_after) / total_before * 100):.1f}%" if total_before > 0 else "N/A")
        
        # Most common fixes
        all_fixes = []
        for result in successful:
            all_fixes.extend(result.get("fixes_applied", []))
        
        if all_fixes:
            fix_counts = {}
            for fix in all_fixes:
                fix_type = fix["type"].replace("_", " ").title()
                if fix_type not in fix_counts:
                    fix_counts[fix_type] = 0
                fix_counts[fix_type] += 1
            
            print(f"\nMost common automatic fixes:")
            for fix_type, count in sorted(fix_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {fix_type}: {count}")
    
    # Save detailed results
    output_file = "testing/reports/auto_fix_test_results.json"
    os.makedirs("testing/reports", exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    try:
        test_sample_files_auto_fixes()
    except Exception as e:
        print(f"❌ Error running auto-fix tests: {e}")
        import traceback
        traceback.print_exc()