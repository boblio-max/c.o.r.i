import cv2
import numpy as np
import tensorflow as tf
import os
import sys

# Make parent dir importable if ik_solver and ws_client live there
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ik_solver import IKSolver
from ws_client import PersistentWebSocketClient

IMAGE_HEIGHT = 128
IMAGE_WIDTH = 128
MODEL_PATH = 'vector_model.h5'   # 3-output model
HOST = '192.168.1.20'
PORT = 8765


def norm360(x):
    return (x % 360 + 360) % 360


def clamp0_180(x):
    return max(0, min(180, x))


def main():
    print('Loading model...')
    model = tf.keras.models.load_model(MODEL_PATH)
    print('Model loaded.')

    ik = IKSolver()
    ws = PersistentWebSocketClient(host=HOST, port=PORT)
    ws.start()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('Error: Could not open webcam.')
        ws.stop()
        return

    print('Press q to quit.')

    joint_angles = [180.0, 180.0, 90.0, 90.0, 0.0, 0.0]

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print('Failed to grab frame.')
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = cv2.resize(rgb, (IMAGE_WIDTH, IMAGE_HEIGHT))
            rgb = rgb.astype(np.float32) / 255.0

            inp = np.expand_dims(rgb, axis=0)

            # 1) AI: frame -> 3D vector
            pred_vec = model.predict(inp, verbose=0)[0]   # (3,)
            vx, vy, vz = pred_vec
            vector_scaled = [vx * 3.0, -vy * 3.0, vz * 3.0]

            # 2) IK: vector -> joint angles
            vector_pass = f"{float(vector_scaled[0])} {float(vector_scaled[1])} {float(vector_scaled[2])}"

            try:
                angles = ik.update(vector_pass)
            except Exception as e:
                print('IK error:', e)
                angles = None

            if angles is not None:
                try:
                    a1 = float(angles.get('A1', joint_angles[0]))
                    a2 = float(angles.get('A2', joint_angles[1]))
                    a3 = float(angles.get('A3', joint_angles[2]))
                    a4 = float(angles.get('A4', joint_angles[3]))
                except Exception as e:
                    print('Angle parse error:', e)
                    a1, a2, a3, a4, _, _ = joint_angles

                joint_angles = [
                    round(norm360(a1)),
                    round(clamp0_180(a2)),
                    round(clamp0_180(a3)),
                    round(clamp0_180(a4)),
                    0.0,
                    0.0
                ]

            # 3) Send joint angles list to Pi
            ws.send(joint_angles)

            # Show debug
            vec_text = f"vec: [{vector_scaled[0]:.2f}, {vector_scaled[1]:.2f}, {vector_scaled[2]:.2f}]"
            ang_text = f"angles: {joint_angles}"
            cv2.putText(frame, vec_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, ang_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            cv2.imshow('AI Vector -> IK', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        ws.stop()


if __name__ == '__main__':
    main()