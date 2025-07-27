# File: TestWorkflows.py
# Path: /home/herb/Desktop/AndyLibrary/Scripts/TestWorkflows.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-27
# Last Modified: 2025-07-27 11:59PM

"""
GitHub Actions workflow validator and local tester
Prevents the 9th consecutive CI/CD error by validating workflows locally
"""

import os
import yaml
import sys
from pathlib import Path

class WorkflowTester:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        
    def ValidateWorkflowSyntax(self, workflow_file):
        """Validate YAML syntax of workflow file"""
        try:
            with open(workflow_file, 'r') as f:
                yaml.safe_load(f)
            return True, "Valid YAML syntax"
        except yaml.YAMLError as e:
            return False, f"YAML syntax error: {e}"
        except Exception as e:
            return False, f"Error reading file: {e}"
    
    def CheckRequiredFiles(self, workflow_file):
        """Check if files referenced in workflow exist"""
        issues = []
        
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # Check for Standalone directory and key files
        if "Standalone" in content:
            standalone_dir = self.repo_root / "Standalone"
            if not standalone_dir.exists():
                issues.append("Standalone directory does not exist")
            else:
                key_file = standalone_dir / "StandaloneAndyLibrary.py"
                if not key_file.exists():
                    issues.append("StandaloneAndyLibrary.py missing in Standalone directory")
        
        return len(issues) == 0, issues
    
    def ValidatePowerShellSyntax(self, workflow_file):
        """Check for common PowerShell syntax issues"""
        issues = []
        
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # Check for batch syntax in Windows workflows
        if "runs-on: windows" in content:
            if "if exist" in content:
                issues.append("Found 'if exist' (batch syntax) - use 'Test-Path' in PowerShell")
            if "echo " in content and "Write-Host" not in content:
                issues.append("Found 'echo' - consider using 'Write-Host' for PowerShell")
            if "dir " in content and "Get-ChildItem" not in content:
                issues.append("Found 'dir' - consider using 'Get-ChildItem' for PowerShell")
        
        return len(issues) == 0, issues
    
    def TestWorkflow(self, workflow_name):
        """Test a specific workflow file"""
        workflow_file = self.workflows_dir / workflow_name
        
        if not workflow_file.exists():
            print(f"❌ Workflow file not found: {workflow_file}")
            return False
        
        print(f"🧪 Testing workflow: {workflow_name}")
        print("=" * 50)
        
        # Test 1: YAML syntax
        valid_yaml, yaml_msg = self.ValidateWorkflowSyntax(workflow_file)
        if valid_yaml:
            print("✅ YAML syntax: Valid")
        else:
            print(f"❌ YAML syntax: {yaml_msg}")
            return False
        
        # Test 2: Required files
        files_exist, file_issues = self.CheckRequiredFiles(workflow_file)
        if files_exist:
            print("✅ Required files: All present")
        else:
            print("❌ Required files: Issues found")
            for issue in file_issues:
                print(f"   - {issue}")
            return False
        
        # Test 3: PowerShell syntax
        ps_valid, ps_issues = self.ValidatePowerShellSyntax(workflow_file)
        if ps_valid:
            print("✅ PowerShell syntax: Clean")
        else:
            print("⚠️ PowerShell syntax: Potential issues")
            for issue in ps_issues:
                print(f"   - {issue}")
        
        print("🎉 Workflow validation complete!")
        return True
    
    def TestAllWorkflows(self):
        """Test all workflow files"""
        if not self.workflows_dir.exists():
            print("❌ No .github/workflows directory found")
            return False
        
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        
        if not workflow_files:
            print("❌ No workflow files found")
            return False
        
        print(f"🧪 Testing {len(workflow_files)} workflow files...")
        print("=" * 60)
        
        all_passed = True
        for workflow_file in workflow_files:
            if not self.TestWorkflow(workflow_file.name):
                all_passed = False
            print()
        
        if all_passed:
            print("🎉 All workflows passed validation!")
        else:
            print("❌ Some workflows failed validation")
        
        return all_passed

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Test specific workflow
        workflow_name = sys.argv[1]
        tester = WorkflowTester()
        success = tester.TestWorkflow(workflow_name)
        sys.exit(0 if success else 1)
    else:
        # Test all workflows
        tester = WorkflowTester()
        success = tester.TestAllWorkflows()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()