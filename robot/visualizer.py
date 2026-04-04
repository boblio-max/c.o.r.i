import mujoco
import mujoco.viewer
from pathlib import Path
import msvcrt

# Build a safe path to the URDF next to this script and verify it exists
urdf_path = Path(__file__).resolve().parent / "robot_arm.urdf"
if not urdf_path.exists():
    raise FileNotFoundError(f"URDF not found at {urdf_path}")

# Load the URDF model
model = mujoco.MjModel.from_xml_path(str(urdf_path))
data = mujoco.MjData(model)

# Simple keyboard control mapping (Windows):
#  - 'a' / 'd' : decrease/increase joint 0
#  - 'w' / 's' : decrease/increase joint 1
#  - 'r'        : reset qpos to zeros
#  - 'q'        : quit viewer
JOINT_STEP = 0.05
CTRL_STEP = 0.1

def clamp_index(i):
    return max(0, min(i, int(data.qpos.size) - 1))

# Launch the interactive viewer and accept simple keyboard input
with mujoco.viewer.launch_passive(model, data) as viewer:
    print("Controls: ',' '.' select joint, a/d adjust, m toggle mode, n set via input, r reset, q quit")
    # Try to set OpenGL clear color to white so the background is white
    try:
        from OpenGL import GL
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
    except Exception:
        # If PyOpenGL isn't available or setting fails, ignore and continue
        pass

    # interactive control state
    selected = 0
    mode = 'qpos' if data.qpos.size > 0 else 'ctrl' if data.ctrl.size > 0 else 'none'
    print(f"Mode: {mode}, selected joint: {selected} / {int(data.qpos.size)-1}")

    while viewer.is_running():
        # handle keypresses (non-blocking)
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch == 'q':
                break
            if ch == 'r':
                data.qpos[:] = 0.0
                mujoco.mj_forward(model, data)
                print('Reset qpos to zeros')
            elif ch == ',':
                selected = clamp_index(selected - 1)
                print(f'Selected joint {selected}')
            elif ch == '.':
                selected = clamp_index(selected + 1)
                print(f'Selected joint {selected}')
            elif ch == 'm':
                # toggle mode between qpos and ctrl if available
                if mode == 'qpos' and data.ctrl.size > 0:
                    mode = 'ctrl'
                elif mode == 'ctrl' and data.qpos.size > 0:
                    mode = 'qpos'
                print(f'Mode -> {mode}')
            elif ch == 'n':
                # prompt user to set '<index> <value>' in the terminal
                try:
                    user = input('Enter "index value" to set (e.g. "1 0.5"): ')
                    parts = user.strip().split()
                    if len(parts) >= 2:
                        idx = int(parts[0])
                        val = float(parts[1])
                        idx = clamp_index(idx)
                        if mode == 'qpos':
                            data.qpos[idx] = val
                            mujoco.mj_forward(model, data)
                            print(f'set qpos[{idx}] = {val}')
                        elif mode == 'ctrl':
                            ctrl_idx = min(idx, int(data.ctrl.size)-1)
                            data.ctrl[ctrl_idx] = val
                            print(f'set ctrl[{ctrl_idx}] = {val}')
                except Exception as e:
                    print('Invalid input:', e)
            elif ch in ('a', 'd'):
                delta = -JOINT_STEP if ch == 'a' else JOINT_STEP
                if mode == 'qpos':
                    idx = clamp_index(selected)
                    data.qpos[idx] = float(data.qpos[idx]) + delta
                    mujoco.mj_forward(model, data)
                    print(f'qpos[{idx}] -> {data.qpos[idx]:.3f}')
                elif mode == 'ctrl':
                    if data.ctrl.size > 0:
                        ctrl_idx = min(selected, int(data.ctrl.size)-1)
                        data.ctrl[ctrl_idx] = float(data.ctrl[ctrl_idx]) + (CTRL_STEP if ch == 'd' else -CTRL_STEP)
                        print(f'ctrl[{ctrl_idx}] -> {data.ctrl[ctrl_idx]:.3f}')

        # Step the simulation and sync viewer
        mujoco.mj_step(model, data)
        # Ensure clear color is applied each frame (some viewers recreate context)
        try:
            GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        except Exception:
            pass
        viewer.sync()
