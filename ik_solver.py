import numpy as np

class IKSolver:
    """
    Headless Inverse Kinematics solver for the robotic arm.
    Calculates the joint angles (A1, A2, A3, A4) for a given target vector.
    """
    def __init__(self, L=1.0):
        self.L = L

    def solve_vect(self, dx, dy, dz):
        """
        Solves IK and returns three displacement vectors for the arm links.
        Uses the forward kinematics:
        B = (L*cos(a1)*cos(a2), L*sin(a1)*cos(a2), L*sin(a2))
        C = B + (L*cos(a1-a3)*cos(a2+a3), L*sin(a1-a3)*cos(a2+a3), L*sin(a2+a3))
        D = C + (L*cos(a1-a2-a3)*cos(a2+a3+a4), L*sin(a1-a2-a3)*cos(a2+a3+a4), L*sin(a2+a3+a4))
        """
        L = self.L
        target = np.array([dx, dy, dz])

        # Base rotation angle
        a1 = np.arctan2(dy, dx)

        # For now, use a simple heuristic to solve for a2, a3, a4
        # This is a placeholder IK solution
        # TODO: Implement proper 3-link IK solver
        r = np.hypot(dx, dy)
        s = dz

        # Simple angle estimates
        a2 = np.arctan2(s, r)
        a3 = 0.0
        a4 = 0.0

        # Calculate joint positions using forward kinematics
        # A is at origin
        A = np.array([0.0, 0.0, 0.0])

        # B = (L*cos(a1)*cos(a2), L*sin(a1)*cos(a2), L*sin(a2))
        B = np.array([
            L * np.cos(a1) * np.cos(a2),
            L * np.sin(a1) * np.cos(a2),
            L * np.sin(a2)
        ])

        # C = B + (L*cos(a1-a3)*cos(a2+a3), L*sin(a1-a3)*cos(a2+a3), L*sin(a2+a3))
        C = B + np.array([
            L * np.cos(a1 - a3) * np.cos(a2 + a3),
            L * np.sin(a1 - a3) * np.cos(a2 + a3),
            L * np.sin(a2 + a3)
        ])

        # D = C + (L*cos(a1-a2-a3)*cos(a2+a3+a4), L*sin(a1-a2-a3)*cos(a2+a3+a4), L*sin(a2+a3+a4))
        D = C + np.array([
            L * np.cos(a1 - a2 - a3) * np.cos(a2 + a3 + a4),
            L * np.sin(a1 - a2 - a3) * np.cos(a2 + a3 + a4),
            L * np.sin(a2 + a3 + a4)
        ])

        # Return displacement vectors
        v1 = B - A
        v2 = C - B
        v3 = D - C

        return v1, v2, v3


    def solve(self, dx, dy, dz):
        """
        Solves the IK for given target coordinates dx, dy, dz.
        Returns a dictionary of angles in degrees.
        """
        A2, A3, A4 = 0.0, 0.0, 0.0
        L = self.L

        # Angle of base rotation
        A1 = np.arctan2(dy, dx)

        r = np.hypot(dx, dy)
        s = dz

        dist = np.hypot(r, s)
        max_reach = 3 * L - 1e-6
        if dist > max_reach:
            scale = max_reach / dist
            r *= scale
            s *= scale

        if r < 0.01:
            if abs(s) > 0.01:
                A2 = np.arctan2(s, 0)
                A3 = 0.0
                A4 = 0.0
        else:
            # IK math for 3-link planar arm (ignoring base rotation which is handled by A1)
            c2 = (r*r + s*s - 3*L*L) / (2*L*r)
            c2 = np.clip(c2, -1.0, 1.0)
            A2 = np.arctan2(s, r) - np.arctan2(np.sqrt(1 - c2*c2), c2)

            c23 = (r - L*np.cos(A2)) / (2*L)
            c23 = np.clip(c23, -1.0, 1.0)
            A3 = np.arccos(c23) - A2
            A4 = A3

        angles_deg = {
            'A1': float(np.degrees(A1)),
            'A2': float(np.degrees(A2)),
            'A3': float(np.degrees(A3)),
            'A4': float(np.degrees(A4)),
        }

        return angles_deg

    def update(self, vector):
        """
        Helper method to solve from a space-separated string "dx dy dz".
        Returns angles in degrees.
        """
        parts = vector.split(" ") # Split the string into parts
        dx = float(parts[0])
        dy = float(parts[1])
        dz = float(parts[2])
        return self.solve(dx, dy, dz)

    def update_vect(self, vector):
        """
        Solves IK from a vector tuple (dx, dy, dz) and returns 3 displacement vectors.
        """
        dx, dy, dz = vector
        dx = float(dx)
        dy = float(dy)
        dz = float(dz)
        return self.solve_vect(dx, dy, dz)

    def solve_from_string(self, vector_str):
        """
        Helper method to solve from a space-separated string "dx dy dz".
        """
        parts = vector_str.split(" ")
        dx = float(parts[0])
        dy = float(parts[1])
        dz = float(parts[2])
        return self.solve(dx, dy, dz)

solve = IKSolver()
print(solve.solve_vect(0.5, 0.5, 0.5))