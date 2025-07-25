# File: run_tests.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/run_tests.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-23
# Last Modified: 2025-07-23 10:58PM

"""
Enhanced test runner for AndyLibrary
Provides comprehensive test execution with coverage, reporting, and filtering
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

class TestRunner:
    """Advanced test runner for AndyLibrary"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = Path(__file__).parent
        self.reports_dir = self.tests_dir / "Reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_tests(self, test_type=None, coverage=False, verbose=False, fast_only=False, generate_report=True):
        """Run tests with specified options"""
        print("🧪 AndyLibrary Test Suite")
        print("=" * 50)
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        # Add test directory
        if test_type:
            if test_type == "api":
                cmd.append(str(self.tests_dir / "test_api_endpoints.py"))
            elif test_type == "database":
                cmd.append(str(self.tests_dir / "test_database_operations.py"))
            elif test_type == "integration":
                cmd.append(str(self.tests_dir / "test_google_drive_integration.py"))
            elif test_type == "unit":
                cmd.extend(["-m", "unit"])
            else:
                cmd.append(str(self.tests_dir))
        else:
            cmd.append(str(self.tests_dir))
        
        # Add verbosity
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Add fast-only filter
        if fast_only:
            cmd.extend(["-m", "not slow"])
        
        # Add coverage
        if coverage:
            cmd.extend([
                "--cov=Source",
                "--cov-report=html:Tests/Reports/coverage_html",
                "--cov-report=term-missing",
                "--cov-report=xml:Tests/Reports/coverage.xml"
            ])
        
        # Add test report
        if generate_report:
            cmd.extend([
                "--html=Tests/Reports/test_report.html",
                "--self-contained-html",
                "--junit-xml=Tests/Reports/junit.xml"
            ])
        
        # Add other useful options
        cmd.extend([
            "--tb=short",  # Shorter traceback format
            "--strict-markers",  # Be strict about markers
            "--disable-warnings"  # Reduce warning noise
        ])
        
        print(f"📋 Running command: {' '.join(cmd)}")
        print("-" * 50)
        
        # Change to project root directory
        original_cwd = os.getcwd()
        os.chdir(self.project_root)
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=False)
            end_time = time.time()
            
            print("-" * 50)
            print(f"⏱️ Test execution time: {end_time - start_time:.2f} seconds")
            
            if result.returncode == 0:
                print("✅ All tests passed!")
            else:
                print(f"❌ Tests failed with exit code: {result.returncode}")
            
            # Show report locations
            if generate_report:
                print(f"📊 HTML Report: {self.reports_dir / 'test_report.html'}")
                if coverage:
                    print(f"📈 Coverage Report: {self.reports_dir / 'coverage_html' / 'index.html'}")
            
            return result.returncode == 0
            
        finally:
            os.chdir(original_cwd)
    
    def run_specific_test(self, test_file, test_function=None):
        """Run a specific test file or function"""
        cmd = ["python", "-m", "pytest", "-v"]
        
        if test_function:
            cmd.append(f"{test_file}::{test_function}")
        else:
            cmd.append(test_file)
        
        os.chdir(self.project_root)
        return subprocess.run(cmd).returncode == 0
    
    def run_performance_tests(self):
        """Run performance-focused tests"""
        print("🚀 Running Performance Tests")
        print("-" * 30)
        
        cmd = [
            "python", "-m", "pytest", 
            str(self.tests_dir),
            "-m", "not slow",
            "--benchmark-only",
            "--benchmark-sort=mean",
            "--benchmark-columns=min,max,mean,stddev",
            "-v"
        ]
        
        os.chdir(self.project_root)
        return subprocess.run(cmd).returncode == 0
    
    def validate_test_environment(self):
        """Validate test environment setup"""
        print("🔍 Validating Test Environment")
        print("-" * 35)
        
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required (current: {sys.version})")
        else:
            print(f"✅ Python version: {sys.version.split()[0]}")
        
        # Check required packages
        required_packages = [
            'pytest',
            'pytest-cov',
            'pytest-html',
            'fastapi',
            'sqlite3'
        ]
        
        for package in required_packages:
            try:
                if package == 'sqlite3':
                    import sqlite3
                else:
                    __import__(package.replace('-', '_'))
                print(f"✅ {package} available")
            except ImportError:
                issues.append(f"Missing package: {package}")
                print(f"❌ {package} not available")
        
        # Check project structure
        required_dirs = [
            'Source/API',
            'Source/Core', 
            'Source/Utils',
            'Config',
            'Data/Local',
            'Tests'
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                print(f"✅ Directory: {dir_path}")
            else:
                issues.append(f"Missing directory: {dir_path}")
                print(f"❌ Directory missing: {dir_path}")
        
        # Check test database accessibility
        test_db_path = self.project_root / "Data/Local/cached_library.db"
        if test_db_path.exists():
            print(f"✅ Test database: {test_db_path}")
        else:
            print(f"⚠️ Test database not found: {test_db_path}")
        
        if issues:
            print("\n❌ Environment Issues Found:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("\n✅ Test environment is ready!")
            return True
    
    def generate_test_summary(self):
        """Generate a test summary report"""
        summary_file = self.reports_dir / "test_summary.md"
        
        with open(summary_file, 'w') as f:
            f.write("# AndyLibrary Test Summary\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Test Categories\n\n")
            f.write("- **API Tests**: Test all FastAPI endpoints\n")
            f.write("- **Database Tests**: Test database operations and integrity\n")
            f.write("- **Integration Tests**: Test Google Drive integration\n")
            f.write("- **Unit Tests**: Test individual components\n\n")
            
            f.write("## Test Files\n\n")
            test_files = list(self.tests_dir.glob("test_*.py"))
            for test_file in test_files:
                f.write(f"- `{test_file.name}`\n")
            
            f.write("\n## Running Tests\n\n")
            f.write("```bash\n")
            f.write("# Run all tests\n")
            f.write("python Tests/run_tests.py\n\n")
            f.write("# Run with coverage\n")
            f.write("python Tests/run_tests.py --coverage\n\n")
            f.write("# Run specific test type\n")
            f.write("python Tests/run_tests.py --type api\n")
            f.write("```\n")
        
        print(f"📋 Test summary generated: {summary_file}")

def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(
        description="Enhanced test runner for AndyLibrary",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --coverage         # Run with coverage report
  python run_tests.py --type api         # Run only API tests
  python run_tests.py --type unit        # Run only unit tests
  python run_tests.py --fast             # Run only fast tests
  python run_tests.py --validate         # Validate test environment
  
Test Types:
  - api: API endpoint tests
  - database: Database operation tests  
  - integration: Google Drive integration tests
  - unit: Unit tests (marked with @pytest.mark.unit)
        """
    )
    
    parser.add_argument('--type', choices=['api', 'database', 'integration', 'unit'],
                       help='Run specific test type')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--fast', action='store_true',
                       help='Run only fast tests (exclude slow tests)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate test environment and exit')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests only')
    parser.add_argument('--summary', action='store_true',
                       help='Generate test summary report')
    parser.add_argument('--no-report', action='store_true',
                       help='Skip generating HTML/XML reports')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Validate environment if requested
    if args.validate:
        success = runner.validate_test_environment()
        sys.exit(0 if success else 1)
    
    # Generate summary if requested
    if args.summary:
        runner.generate_test_summary()
        return
    
    # Run performance tests if requested
    if args.performance:
        success = runner.run_performance_tests()
        sys.exit(0 if success else 1)
    
    # Validate environment before running tests
    if not runner.validate_test_environment():
        print("❌ Environment validation failed. Please fix issues before running tests.")
        sys.exit(1)
    
    # Run tests
    success = runner.run_tests(
        test_type=args.type,
        coverage=args.coverage,
        verbose=args.verbose,
        fast_only=args.fast,
        generate_report=not args.no_report
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()