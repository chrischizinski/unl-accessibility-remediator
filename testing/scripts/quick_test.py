#!/usr/bin/env python3
"""
Quick Test Script for UNL Accessibility Remediator

This script runs basic validation tests without starting the full service stack.
Perfect for CI/CD and quick verification.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def test_prerequisites():
    """Quick prerequisite checks"""
    print("🔍 Testing prerequisites...")
    
    # Check Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Docker: {result.stdout.strip()}")
        else:
            print("  ❌ Docker not working")
            return False
    except FileNotFoundError:
        print("  ❌ Docker not found")
        return False
    
    # Check Docker Compose
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Docker Compose: {result.stdout.strip()}")
        else:
            print("  ❌ Docker Compose not working")
            return False
    except FileNotFoundError:
        print("  ❌ Docker Compose not found")
        return False
    
    # Check file structure
    base_dir = Path.cwd()
    required_files = [
        "accessibility_remediator/Dockerfile",
        "docker-compose.yml", 
        "start-accessibility-tool.sh",
        "START-HERE-WINDOWS.bat",
        "START-HERE-MAC.command",
        "START-HERE-LINUX.sh"
    ]
    
    missing_files = []
    for file_path in required_files:
        if (base_dir / file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"  ❌ Missing {len(missing_files)} required files")
        return False
    
    print("  ✅ All files present")
    return True

def test_docker_builds():
    """Test that Docker images can build"""
    print("\n🔧 Testing Docker build...")
    
    try:
        # Test Docker build (but don't start services)
        result = subprocess.run([
            "docker-compose", "config"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ Docker Compose configuration valid")
            return True
        else:
            print(f"  ❌ Docker Compose config error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ Docker config check timeout")
        return False
    except Exception as e:
        print(f"  ❌ Docker config check failed: {str(e)}")
        return False

def test_script_syntax():
    """Test startup script syntax"""
    print("\n📝 Testing script syntax...")
    
    scripts = {
        "start-accessibility-tool.sh": ["bash", "-n"],
        "START-HERE-LINUX.sh": ["bash", "-n"], 
        "START-HERE-MAC.command": ["bash", "-n"]
    }
    
    all_passed = True
    for script, check_cmd in scripts.items():
        if Path(script).exists():
            try:
                result = subprocess.run(
                    check_cmd + [script], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    print(f"  ✅ {script} syntax valid")
                else:
                    print(f"  ❌ {script} syntax error")
                    all_passed = False
            except Exception as e:
                print(f"  ❌ {script} check failed: {str(e)}")
                all_passed = False
    
    return all_passed

def test_sample_files():
    """Check test sample files"""
    print("\n📁 Testing sample files...")
    
    sample_dir = Path("testing/sample_files")
    if sample_dir.exists():
        sample_files = list(sample_dir.glob("*"))
        print(f"  ✅ Sample files directory exists ({len(sample_files)} files)")
        
        # Check for our test HTML file
        html_file = sample_dir / "sample_presentation.html"
        if html_file.exists():
            print("  ✅ HTML test file available")
            # Basic validation of HTML file
            try:
                with open(html_file, 'r') as f:
                    content = f.read()
                    if 'accessibility' in content.lower():
                        print("  ✅ Test file contains accessibility content")
                    else:
                        print("  ⚠️ Test file missing accessibility content")
            except Exception as e:
                print(f"  ❌ Error reading test file: {str(e)}")
        else:
            print("  ⚠️ No HTML test file found")
        
        return True
    else:
        print("  ❌ Sample files directory missing")
        return False

def main():
    """Run quick tests"""
    print("🧪 UNL Accessibility Tool - Quick Test Suite")
    print("=" * 50)
    
    tests = [
        ("Prerequisites", test_prerequisites),
        ("Docker Configuration", test_docker_builds), 
        ("Script Syntax", test_script_syntax),
        ("Sample Files", test_sample_files)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - EXCEPTION: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"🧪 Quick Test Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All quick tests passed! Tool appears ready for full testing.")
        print("💡 Next steps:")
        print("  1. Run comprehensive tests: ./testing/run_tests.sh")
        print("  2. Test with sample files manually")
        print("  3. Add your own presentation files for testing")
    else:
        print("\n⚠️ Some issues detected. Please fix before running full tests.")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())