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
    print("[Orchestrator] Launching 3D Vector Visualizer...")
    vectors_process = subprocess.Popen(
        [sys.executable, os.path.join(script_dir, "3dvectors.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("[Orchestrator] Launching Main Dashboard...")
    dashboard_process = subprocess.Popen(
        [sys.executable, os.path.join(script_dir, "dashboard.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Now we just wait. If either one closes, the whole band stops.
    print("[Orchestrator] All systems running. Close any window to exit.")
    vectors_process.wait()
    dashboard_process.wait()
    print("[Orchestrator] Shutting down.")