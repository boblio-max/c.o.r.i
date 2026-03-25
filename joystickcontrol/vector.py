# ...existing code...
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

ax.set_xlim([-5, 5])
ax.set_ylim([-5, 5])
ax.set_zlim([-5, 5])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D vectors')

L = 1.0

# initial end vector as numeric
n = "1 1 1"
ns = np.array(n.split(), dtype=float)

A = (0.0, 0.0, 0.0)
A1 = A2 = A3 = A4 = 0.0

B = (L * np.cos(A2) * np.cos(A1), L * np.cos(A2) * np.sin(A1), L * np.sin(A2))
C = np.add(B, (L * np.cos(A2 + A3) * np.cos(A1), L * np.cos(A2 + A3) * np.sin(A1), L * np.sin(A2 + A3)))
D = np.add(C, (L * np.cos(A2 + A3 + A4) * np.cos(A1), L * np.cos(A2 + A3 + A4) * np.sin(A1), L * np.sin(A2 + A3 + A4)))

# quiver artists (use numeric values)
quiver_object = ax.quiver(0, 0, 0, ns[0], ns[1], ns[2], color='r', label='End Vector')
quiver1 = ax.quiver(0, 0, 0, B[0], B[1], B[2], color='b', label='Shoulder Vector')
quiver2 = ax.quiver(B[0], B[1], B[2], C[0] - B[0], C[1] - B[1], C[2] - B[2], color='y', label='Elbow Vector')
quiver3 = ax.quiver(C[0], C[1], C[2], D[0] - C[0], D[1] - C[1], D[2] - C[2], color='r', label='Wrist Vector')

ax.legend()

# utility class (renamed to avoid shadowing)
class Vector:
    def __init__(self, ax=ax, L=L):
        self.ax = ax
        self.L = float(L)
        # use the module-level quiver objects created above
        self.quiver_end = quiver_object
        self.quiver_shoulder = quiver1
        self.quiver_elbow = quiver2
        self.quiver_wrist = quiver3

    def _parse_vector(self, v):
        # accept list/tuple/ndarray or "x y z" string
        if isinstance(v, (list, tuple, np.ndarray)):
            arr = np.asarray(v, dtype=float)
            if arr.shape != (3,):
                raise ValueError("vector must be length-3")
            return arr
        if isinstance(v, str):
            parts = v.split()
            return np.array([float(parts[0]), float(parts[1]), float(parts[2])], dtype=float)
        raise TypeError("unsupported vector type")

    def update(self, vec):
        dx, dy, dz = self._parse_vector(vec)

        # base angles and IK
        A1 = np.arctan2(dy, dx)
        r = np.hypot(dx, dy)
        s = dz

        A2 = A3 = A4 = 0.0
        try:
            # avoid divide-by-zero
            if r == 0:
                raise ValueError("r == 0")
            c2 = (r*r + s*s - 3*self.L*self.L) / (2*self.L*r)
            if abs(c2) > 1.0:
                raise ValueError("point out of reach")
            A2 = np.arctan2(s, r) - np.arctan2(np.sqrt(max(0.0, 1 - c2*c2)), c2)

            c23 = (r - self.L*np.cos(A2)) / (2*self.L)
            c23 = np.clip(c23, -1.0, 1.0)
            A3 = np.arccos(c23) - A2
            A4 = A3
        except Exception:
            A2 = A3 = A4 = 0.0

        # joint positions as arrays
        B = np.array([self.L*np.cos(A2)*np.cos(A1),
                      self.L*np.cos(A2)*np.sin(A1),
                      self.L*np.sin(A2)])
        C = B + np.array([self.L*np.cos(A2 + A3)*np.cos(A1),
                          self.L*np.cos(A2 + A3)*np.sin(A1),
                          self.L*np.sin(A2 + A3)])
        D = C + np.array([self.L*np.cos(A2 + A3 + A4)*np.cos(A1),
                          self.L*np.cos(A2 + A3 + A4)*np.sin(A1),
                          self.L*np.sin(A2 + A3 + A4)])

        # update quiver segments (each segment is [[x0,y0,z0],[x1,y1,z1]])
        try:
            self.quiver_end.set_segments([np.array([[0.0, 0.0, 0.0], [dx, dy, dz]])])
            self.quiver_shoulder.set_segments([np.array([[0.0, 0.0, 0.0], B])])
            self.quiver_elbow.set_segments([np.array([B, C])])
            self.quiver_wrist.set_segments([np.array([C, D])])
        except Exception:
            # fallback: recreate quivers if set_segments not supported
            self.quiver_end.remove()
            self.quiver_shoulder.remove()
            self.quiver_elbow.remove()
            self.quiver_wrist.remove()
            self.quiver_end = self.ax.quiver(0, 0, 0, dx, dy, dz, color='r')
            self.quiver_shoulder = self.ax.quiver(0, 0, 0, B[0], B[1], B[2], color='b')
            self.quiver_elbow = self.ax.quiver(B[0], B[1], B[2], C[0]-B[0], C[1]-B[1], C[2]-B[2], color='y')
            self.quiver_wrist = self.ax.quiver(C[0], C[1], C[2], D[0]-C[0], D[1]-C[1], D[2]-C[2], color='r')

        return self.quiver_end, self.quiver_shoulder, self.quiver_elbow, self.quiver_wrist
# ...existing code...