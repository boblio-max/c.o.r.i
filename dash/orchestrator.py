import subprocess
import os
import sys

if __name__ == "__main__":
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run both processes simultaneously
    vectors_process = subprocess.Popen(
        [sys.executable, os.path.join(script_dir, "3dvectors.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    dashboard_process = subprocess.Popen(
        [sys.executable, os.path.join(script_dir, "testdash.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for both to finish
    vectors_process.wait()
    dashboard_process.wait()