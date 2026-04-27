import numpy as np

class IKSolver:
    """
    Headless Inverse Kinematics solver for the robotic arm.
    Calculates the joint angles (A1, A2, A3, A4) for a given target vector.
    """
    def __init__(self, L=1.0):
        self.L = L

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
        
    def solve_from_string(self, vector_str):
        """
        Helper method to solve from a space-separated string "dx dy dz".
        """
        ns = vector_str.split(" ")
        dx = float(ns[0]) 
        dy = float(ns[1])
        dz = float(ns[2])
        return self.solve(dx, dy, dz)

# Example usage:
# solver = IKSolver()
# angles = solver.solve_from_string("1 1 1")
# print(angles)
