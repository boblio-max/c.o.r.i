# C.O.R.I Orchestrator
# Launches the dashboard and 3D visualizer as subprocesses.
import subprocess
import os
import sys

if __name__ == "__main__":
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
    # Note: stdout/stderr are captured. Set to None to see live output in this terminal.

    print("[Orchestrator] All systems running. Close any window to exit.")
    vectors_process.wait()
    dashboard_process.wait()
    print("[Orchestrator] Shutting down.")