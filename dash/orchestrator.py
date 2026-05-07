# C.O.R.I Orchestrator
# This is the "Grand Conductor" of our project. Instead of opening multiple 
# terminal windows, we just run this one script and it launches everything. 
import subprocess
import os
import sys

if __name__ == "__main__":
    # First, we figure out where we are so we can find the other scripts.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # We're launching the 3D visualizer and the main Dashboard simultaneously.
    # It's using subprocess so they run in the background.
    vectors_process = subprocess.Popen(
        [sys.executable, os.path.join(script_dir, "3dvectors.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    dashboard_process = subprocess.Popen(
        [sys.executable, os.path.join(script_dir, "dashboard.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Now we just wait. If either one closes, the whole band stops.
    vectors_process.wait()
    dashboard_process.wait()