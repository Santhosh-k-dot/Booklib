#!/usr/bin/env python3
"""
Quick Start Script for Load Testing

Provides easy commands to run different test types:
1. Load Test
2. Stress Test  
3. Spike Test
4. Full Test Suite

Usage:
    python run_tests.py load
    python run_tests.py stress
    python run_tests.py spike
    python run_tests.py all
"""

import subprocess
import sys
import time
import os
from datetime import datetime


class TestRunner:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.results_dir = f"test_results_{self.timestamp}"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("\n" + "="*70)
        print("🔍 CHECKING PREREQUISITES")
        print("="*70 + "\n")
        
        # Check if locust is installed
        try:
            subprocess.run(["locust", "--version"], capture_output=True, check=True)
            print("✅ Locust is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Locust is not installed")
            print("   Install with: pip install locust")
            return False
        
        # Check if FastAPI server is running
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ FastAPI server is running")
            else:
                print("⚠️  FastAPI server returned non-200 status")
        except Exception as e:
            print("❌ FastAPI server is not reachable")
            print("   Start with: python -m uvicorn app.main:app --reload")
            return False
        
        # Check if test file exists
        if not os.path.exists("locustfile_comprehensive.py"):
            print("❌ locustfile_comprehensive.py not found")
            return False
        print("✅ Test files found")
        
        print("\n✅ All prerequisites met!\n")
        return True
    
    def run_load_test(self):
        """Run load test - normal traffic"""
        print("\n" + "="*70)
        print("📊 RUNNING LOAD TEST")
        print("="*70)
        print("Simulating normal expected traffic...")
        print("Users: 50 | Spawn Rate: 5/s | Duration: 5m\n")
        
        output_file = os.path.join(self.results_dir, "load_test_report.html")
        
        cmd = [
            "locust",
            "-f", "locustfile_comprehensive.py",
            "--users", "50",
            "--spawn-rate", "5",
            "--run-time", "5m",
            "--html", output_file,
            "--headless"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"\n✅ Load test completed! Report: {output_file}\n")
            return True
        except subprocess.CalledProcessError:
            print("\n❌ Load test failed!\n")
            return False
    
    def run_stress_test(self):
        """Run stress test - beyond normal capacity"""
        print("\n" + "="*70)
        print("💪 RUNNING STRESS TEST")
        print("="*70)
        print("Pushing system beyond normal capacity...")
        print("Users: 200 | Spawn Rate: 10/s | Duration: 10m\n")
        
        output_file = os.path.join(self.results_dir, "stress_test_report.html")
        
        cmd = [
            "locust",
            "-f", "locustfile_comprehensive.py",
            "--users", "200",
            "--spawn-rate", "10",
            "--run-time", "10m",
            "--html", output_file,
            "--headless"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"\n✅ Stress test completed! Report: {output_file}\n")
            return True
        except subprocess.CalledProcessError:
            print("\n❌ Stress test failed!\n")
            return False
    
    def run_spike_test(self):
        """Run spike test - sudden traffic burst"""
        print("\n" + "="*70)
        print("🚀 RUNNING SPIKE TEST")
        print("="*70)
        print("Simulating sudden traffic burst...")
        print("Users: 500 | Spawn Rate: 50/s | Duration: 2m\n")
        
        output_file = os.path.join(self.results_dir, "spike_test_report.html")
        
        # Use dedicated spike test file if available
        test_file = "locustfile_spike.py" if os.path.exists("locustfile_spike.py") else "locustfile_comprehensive.py"
        
        cmd = [
            "locust",
            "-f", test_file,
            "--users", "500",
            "--spawn-rate", "50",
            "--run-time", "2m",
            "--html", output_file,
            "--headless"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"\n✅ Spike test completed! Report: {output_file}\n")
            return True
        except subprocess.CalledProcessError:
            print("\n❌ Spike test failed!\n")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "="*70)
        print("🎯 RUNNING FULL TEST SUITE")
        print("="*70)
        print("This will run: Load → Stress → Spike tests")
        print("Estimated time: 17+ minutes\n")
        
        input("Press Enter to continue or Ctrl+C to cancel...")
        
        results = {
            "load": self.run_load_test(),
            "stress": self.run_stress_test(),
            "spike": self.run_spike_test()
        }
        
        # Summary
        print("\n" + "="*70)
        print("📋 TEST SUITE SUMMARY")
        print("="*70)
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.upper()} TEST: {status}")
        print(f"\nAll reports saved in: {self.results_dir}/")
        print("="*70 + "\n")
    
    def interactive_menu(self):
        """Show interactive menu"""
        while True:
            print("\n" + "="*70)
            print("🧪 LOAD TESTING MENU")
            print("="*70)
            print("\n1. Run Load Test (5 min)")
            print("2. Run Stress Test (10 min)")
            print("3. Run Spike Test (2 min)")
            print("4. Run All Tests (~17 min)")
            print("5. Open Locust Web UI (manual testing)")
            print("6. Exit")
            print("\n" + "="*70)
            
            choice = input("\nSelect an option (1-6): ").strip()
            
            if choice == "1":
                self.run_load_test()
            elif choice == "2":
                self.run_stress_test()
            elif choice == "3":
                self.run_spike_test()
            elif choice == "4":
                self.run_all_tests()
            elif choice == "5":
                print("\n🌐 Starting Locust Web UI...")
                print("Open http://localhost:8089 in your browser")
                print("Press Ctrl+C to stop\n")
                try:
                    subprocess.run([
                        "locust",
                        "-f", "locustfile_comprehensive.py"
                    ])
                except KeyboardInterrupt:
                    print("\n\nWeb UI stopped.\n")
            elif choice == "6":
                print("\n👋 Goodbye!\n")
                sys.exit(0)
            else:
                print("\n❌ Invalid option. Please try again.")


def main():
    runner = TestRunner()
    
    # Check prerequisites first
    if not runner.check_prerequisites():
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "load":
            runner.run_load_test()
        elif command == "stress":
            runner.run_stress_test()
        elif command == "spike":
            runner.run_spike_test()
        elif command == "all":
            runner.run_all_tests()
        elif command == "menu":
            runner.interactive_menu()
        else:
            print(f"\n❌ Unknown command: {command}")
            print("\nUsage:")
            print("  python run_tests.py load    - Run load test")
            print("  python run_tests.py stress  - Run stress test")
            print("  python run_tests.py spike   - Run spike test")
            print("  python run_tests.py all     - Run all tests")
            print("  python run_tests.py menu    - Show interactive menu")
            sys.exit(1)
    else:
        # No arguments - show interactive menu
        runner.interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted by user.\n")
        sys.exit(0)