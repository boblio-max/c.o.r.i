import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# A1 = base rotation
# A2 = shoulder rotation
# A3 = elbow rotation
# A4 = wrist rotation

ax.set_xlim([-5, 5])
ax.set_ylim([-5, 5])
ax.set_zlim([-5, 5])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D vectors')
L = 1
# Lm = 1.57079 # This variable seems unused, can be removed if not needed later
A1 = 0
A2 = 0
A3 = 0
A4 = 0

# Initial setup for the quivers - these will be updated by the vector class
A = np.array([0.0, 0.0, 0.0])
B = np.array([0.0, 0.0, 0.0])
C = np.array([0.0, 0.0, 0.0])
D = np.array([0.0, 0.0, 0.0])

# N = (ns[0], ns[1], ns[2]) # N is the target vector, it will be updated
# Initialize with a default target, e.g., pointing along x-axis
dx_init, dy_init, dz_init = 1.0, 0.0, 0.0

quiver_object = ax.quiver(A[0], A[1], A[2], dx_init, dy_init, dz_init, color='r', label='End Vector')
quiver1 = ax.quiver(A[0], A[1], A[2], B[0], B[1], B[2], color='b', label='Shoulder Vector')
quiver2 = ax.quiver(B[0], B[1], B[2], C[0], C[1], C[2], color='y', label='Elbow Vector')
quiver3 = ax.quiver(C[0], C[1], C[2], D[0], D[1], D[2], color='g', label='Wrist Vector') # Changed color for visibility

ax.legend()

class vector:
    def __init__(self):

        self.quiver_object = quiver_object
        self.quiver1 = quiver1
        self.quiver2 = quiver2
        self.quiver3 = quiver3
        self.L = L # Link length

    def update(self, target_vector_str):
        # Parse target vector components
        target_coords = [float(c) for c in target_vector_str.split(" ")]
        dx, dy, dz = target_coords

        # Inverse Kinematics for a 3-link arm
        # Assume wrist is aligned with the end effector for simplicity

        # Calculate A1 (base rotation around Z-axis)
        A1 = np.arctan2(dy, dx)

        # Project target onto the XZ plane after A1 rotation
        # This effectively rotates the target so it's in the XZ plane of the arm
        # x_prime = dx * np.cos(A1) + dy * np.sin(A1)
        # For simplicity, we can consider the reach in the XY plane and Z height
        r_xy = np.hypot(dx, dy) # Radial distance in XY plane
        h_z = dz # Height along Z-axis

        # Target point relative to the shoulder joint for a 2-link planar arm
        # We consider a virtual 2-link arm (shoulder to wrist) for calculating A2 and A3
        # The distance to the end effector is the hypotenuse of r_xy and h_z
        target_dist = np.hypot(r_xy, h_z)

        # Check for reachability (sum of link lengths)
        max_reach = 3 * self.L
        if target_dist > max_reach:
            # Scale down the target if it's out of reach
            scale_factor = max_reach / target_dist
            r_xy *= scale_factor
            h_z *= scale_factor
            target_dist = max_reach

        # Solve for A2 and A3 using the Law of Cosines for the planar 2-link arm
        # Links are L, L, L. So, shoulder-elbow is L, elbow-wrist is L, wrist-endeffector is L
        # Consider the triangle formed by (0,0), (r_xy, h_z) and the elbow joint
        # Here, we treat it as a 2-link arm from origin to the point before the wrist
        # For a 3-link arm, the math is more involved, let's simplify for now

        # Simplified 2-link solution (from shoulder to a point before the wrist)
        # Let's say we have three segments of length L.
        # The first segment from A to B (shoulder). B to C (elbow). C to D (wrist).
        # We want D to be at (dx, dy, dz).

        # Consider the point P = (dx, dy, dz)
        # We are looking for joint angles A1, A2, A3, A4
        # Point B: (L*cos(A2)*cos(A1), L*cos(A2)*sin(A1), L*sin(A2))
        # Point C: ... (more complex)

        # Let's re-approach with common 3R robot IK
        # Given target (dx, dy, dz)

        # Wrist position (assuming it's the end of the 3rd link relative to base)
        # For a 3-link arm (L1, L2, L3) and target (Px, Py, Pz)
        # Let L1 = L2 = L3 = L

        # A1 (base rotation)
        A1 = np.arctan2(dy, dx)

        # Effective target for 2-link planar arm after rotating A1
        Px_eff = np.sqrt(dx**2 + dy**2)
        Pz_eff = dz

        # Use Law of Cosines to find A3 (elbow angle)
        # Cosine rule: c^2 = a^2 + b^2 - 2ab cos(C)
        # Here, a = L, b = L, c = distance between shoulder and end-of-second-link projected on a plane
        # distance from base (0,0) to target (Px_eff, Pz_eff)
        d_sq = Px_eff**2 + Pz_eff**2

        # Check for denominator in case d_sq is very small or links are too short
        cos_A3_num = d_sq - self.L**2 - self.L**2
        cos_A3_den = 2 * self.L * self.L

        # Ensure -1 <= cos_A3 <= 1
        if cos_A3_den == 0: # Avoid division by zero if L is 0
            A3 = 0.0 # Or raise an error
        else:
            cos_A3 = np.clip(cos_A3_num / cos_A3_den, -1.0, 1.0)
            A3 = np.arccos(cos_A3) # Elbow angle

        # Solve for A2 (shoulder angle)
        beta = np.arctan2(Pz_eff, Px_eff) # Angle of the target from the X-axis in the effective plane
        alpha_num = self.L * np.sin(A3)
        alpha_den = self.L + self.L * np.cos(A3)
        
        if alpha_den == 0:
            alpha = 0.0 # Avoid division by zero
        else:
            alpha = np.arctan2(alpha_num, alpha_den) # Angle of the second link relative to the first
        
        A2 = beta - alpha # Shoulder angle

        # A4 (wrist angle) - for simplicity, let the wrist align with the previous segment
        # or point towards the end effector. For now, let's make it such that A2+A3+A4 aligns with the target
        # This would require more advanced IK, let's assume A4 is relative to the elbow
        # A4 = -A3 # This would make the last link parallel to the first, good for visualization

        # For a simple visualization, we can make the wrist link point straight from the elbow
        # A4 = 0 # Relative to the C frame
        # Or, make it point towards the end effector
        # Let's keep A4 simple for now and set it to 0 relative to the elbow's direction
        A4 = 0.0 # Maintain a straight configuration after A3

        # Forward Kinematics to get joint positions
        # Joint A (Base)
        A = np.array([0.0, 0.0, 0.0])

        # Joint B (Shoulder)
        B = np.array([
            self.L * np.cos(A2) * np.cos(A1),
            self.L * np.cos(A2) * np.sin(A1),
            self.L * np.sin(A2)
        ])

        # Joint C (Elbow)
        C = B + np.array([
            self.L * np.cos(A2 + A3) * np.cos(A1),
            self.L * np.cos(A2 + A3) * np.sin(A1),
            self.L * np.sin(A2 + A3)
        ])

        # Joint D (Wrist)
        D = C + np.array([
            self.L * np.cos(A2 + A3 + A4) * np.cos(A1),
            self.L * np.cos(A2 + A3 + A4) * np.sin(A1),
            self.L * np.sin(A2 + A3 + A4)
        ])

        # Update quiver objects
        # End Vector quiver (from origin to target)
        self.quiver_object.set_segments([[[0, 0, 0], [dx, dy, dz]]])

        # Arm segment quivers
        self.quiver1.set_segments([[[A[0], A[1], A[2]], [B[0], B[1], B[2]]]])
        self.quiver2.set_segments([[[B[0], B[1], B[2]], [C[0], C[1], C[2]]]])
        self.quiver3.set_segments([[[C[0], C[1], C[2]], [D[0], D[1], D[2]]]])

        # Return the joint positions (optional, but good for debugging/further use)
        return A, B, C, D