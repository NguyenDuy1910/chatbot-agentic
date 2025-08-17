#!/usr/bin/env python3
"""
FINX Backend Test Runner
Runs all tests in the test suite with comprehensive reporting
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

####################
# Test Configuration
####################

TEST_MODULES = {
    "models": {
        "file": "test_models.py",
        "description": "Database models and CRUD operations",
        "category": "core"
    },
    "connections": {
        "file": "test_connections.py", 
        "description": "Data connection providers and management",
        "category": "core"
    },
    "logging": {
        "file": "test_logging.py",
        "description": "Logging system and integrations", 
        "category": "utils"
    }
}

####################
# Test Runner Class
####################

class TestRunner:
    """Main test runner for FINX backend"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        self.start_time = None
        self.total_time = 0
    
    def setup_test_environment(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Create test logs directory
        logs_dir = self.test_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Set environment variables for testing
        os.environ["ENVIRONMENT"] = "testing"
        os.environ["LOG_LEVEL"] = "WARNING"
        os.environ["LOG_DIR"] = str(logs_dir)
        
        print("   ✅ Test environment ready")
    
    def run_single_test(self, test_name: str, test_info: Dict) -> Tuple[bool, float, str]:
        """Run a single test module"""
        test_file = self.test_dir / test_info["file"]
        
        if not test_file.exists():
            return False, 0.0, f"Test file {test_info['file']} not found"
        
        print(f"\n🧪 Running {test_name} tests...")
        print(f"   Description: {test_info['description']}")
        print(f"   File: {test_info['file']}")
        
        start_time = time.time()
        
        try:
            # Run the test as a subprocess
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=str(self.test_dir.parent),
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"   ✅ {test_name} tests PASSED ({execution_time:.2f}s)")
                return True, execution_time, result.stdout
            else:
                print(f"   ❌ {test_name} tests FAILED ({execution_time:.2f}s)")
                print(f"   Error output: {result.stderr}")
                return False, execution_time, result.stderr
                
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"   ⏰ {test_name} tests TIMEOUT ({execution_time:.2f}s)")
            return False, execution_time, "Test timed out after 60 seconds"
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"   💥 {test_name} tests ERROR ({execution_time:.2f}s)")
            print(f"   Exception: {str(e)}")
            return False, execution_time, str(e)
    
    def run_all_tests(self, categories: List[str] = None) -> Dict:
        """Run all tests or tests in specific categories"""
        self.start_time = time.time()
        
        # Filter tests by category if specified
        tests_to_run = TEST_MODULES
        if categories:
            tests_to_run = {
                name: info for name, info in TEST_MODULES.items()
                if info["category"] in categories
            }
        
        print(f"🚀 Running {len(tests_to_run)} test modules...")
        
        for test_name, test_info in tests_to_run.items():
            success, exec_time, output = self.run_single_test(test_name, test_info)
            
            self.results[test_name] = {
                "success": success,
                "execution_time": exec_time,
                "output": output,
                "description": test_info["description"],
                "category": test_info["category"]
            }
        
        self.total_time = time.time() - self.start_time
        return self.results
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        if not self.results:
            return "No tests have been run yet."
        
        passed = sum(1 for r in self.results.values() if r["success"])
        total = len(self.results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        report = []
        report.append("=" * 80)
        report.append("FINX BACKEND TEST SUITE REPORT")
        report.append("=" * 80)
        report.append(f"Total Tests: {total}")
        report.append(f"Passed: {passed}")
        report.append(f"Failed: {total - passed}")
        report.append(f"Success Rate: {success_rate:.1f}%")
        report.append(f"Total Execution Time: {self.total_time:.2f}s")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 40)
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            report.append(f"{status} {test_name:15} ({result['execution_time']:.2f}s)")
            report.append(f"     Category: {result['category']}")
            report.append(f"     Description: {result['description']}")
            
            if not result["success"]:
                # Show error details for failed tests
                error_lines = result["output"].split('\n')[:3]  # First 3 lines of error
                for line in error_lines:
                    if line.strip():
                        report.append(f"     Error: {line.strip()}")
            report.append("")
        
        # Summary by category
        categories = {}
        for result in self.results.values():
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "passed": 0}
            categories[cat]["total"] += 1
            if result["success"]:
                categories[cat]["passed"] += 1
        
        report.append("RESULTS BY CATEGORY:")
        report.append("-" * 40)
        for category, stats in categories.items():
            success_rate = (stats["passed"] / stats["total"]) * 100
            report.append(f"{category:10} {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = None):
        """Save test report to file"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.txt"
        
        report_file = self.test_dir / filename
        
        with open(report_file, 'w') as f:
            f.write(self.generate_report())
        
        print(f"\n📄 Test report saved to: {report_file}")

####################
# CLI Interface
####################

def main():
    """Main function with CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FINX Backend Test Runner")
    parser.add_argument(
        "--category", 
        choices=["core", "utils", "api", "auth"],
        help="Run tests for specific category only"
    )
    parser.add_argument(
        "--test",
        choices=list(TEST_MODULES.keys()),
        help="Run specific test module only"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Save detailed report to file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true", 
        help="Show verbose output"
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner()
    
    print("🚀 FINX BACKEND TEST SUITE")
    print("=" * 50)
    
    # Setup test environment
    runner.setup_test_environment()
    
    # Determine which tests to run
    if args.test:
        # Run single test
        if args.test in TEST_MODULES:
            test_info = TEST_MODULES[args.test]
            success, exec_time, output = runner.run_single_test(args.test, test_info)
            
            if args.verbose:
                print(f"\nTest Output:\n{output}")
            
            return 0 if success else 1
        else:
            print(f"❌ Test '{args.test}' not found")
            return 1
    
    elif args.category:
        # Run tests by category
        results = runner.run_all_tests([args.category])
    else:
        # Run all tests
        results = runner.run_all_tests()
    
    # Generate and display report
    report = runner.generate_report()
    print(f"\n{report}")
    
    # Save report if requested
    if args.report:
        runner.save_report()
    
    # Return appropriate exit code
    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
