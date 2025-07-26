# File: run_tests.py
# Path: /home/herb/Desktop/AndyLibrary/run_tests.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-23
# Last Modified: 2025-07-23 09:40AM

import subprocess
import sys
import argparse

def RunTests(test_type="all", verbose=True, coverage=False):
    """Run the test suite with various options"""
    
    cmd = ["python", "-m", "pytest"]
    
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=Source", "--cov-report=html", "--cov-report=term"])
    
    cmd.append("Tests/")
    
    print(f"🧪 Running tests: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Run AndyLibrary test suite")
    parser.add_argument("--type", choices=["all", "unit", "integration", "api", "fast"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    
    args = parser.parse_args()
    
    return_code = RunTests(
        test_type=args.type,
        verbose=not args.quiet,
        coverage=args.coverage
    )
    
    sys.exit(return_code)

if __name__ == "__main__":
    main()