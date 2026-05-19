# Inverse Kinematics Solver for a 4-DOF Robotic Arm
# Copied over from desmos math and adapted for python

import numpy as np


class IKSolver:
    """
    Inverse Kinematics solver for a 4-DOF robotic arm.
    Calculates joint angles (A1, A2, A3, A4) for a given target position.
    
    The arm consists of:
    - A1: Base rotation (horizontal)
    - A2: Shoulder rotation
    - A3: Elbow rotation
    - A4: Wrist rotation
    
    Each link has length L (default 1.0).
    """

    def __init__(self, L=1.0):
        """
        Initialize the IK solver.
        
        Args:
            L (float): Length of each arm segment. Default 1.0
        """
        self.L = L

    def solve(self, dx, dy, dz):
        """
        Solves inverse kinematics for a target position.
        
        Args:
            dx (float): X displacement
            dy (float): Y displacement
            dz (float): Z displacement
            
        Returns:
            dict: Dictionary with keys 'A1', 'A2', 'A3', 'A4' (angles in degrees)
        """
        A2, A3, A4 = 0.0, 0.0, 0.0
        L = self.L

        # A1: Base rotation angle
        A1 = np.arctan2(dy, dx)

        # Horizontal and vertical distances
        r = np.hypot(dx, dy)
        s = dz

        # Check if target is reachable
        dist = np.hypot(r, s)
        max_reach = 3 * L - 1e-6
        if dist > max_reach:
            # Scale down to maximum reach
            scale = max_reach / dist
            r *= scale
            s *= scale

        # Special case: nearly vertical
        if r < 0.01:
            if abs(s) > 0.01:
                A2 = np.arctan2(s, 0)
                A3 = 0.0
                A4 = 0.0
        else:
            # IK for 3-link planar arm (A2, A3, A4)
            # Using law of cosines
            c2 = (r*r + s*s - 3*L*L) / (2*L*r)
            c2 = np.clip(c2, -1.0, 1.0)
            A2 = np.arctan2(s, r) - np.arctan2(np.sqrt(1 - c2*c2), c2)

            c23 = (r - L*np.cos(A2)) / (2*L)
            c23 = np.clip(c23, -1.0, 1.0)
            A3 = np.arccos(c23) - A2
            A4 = A3

        # Return angles in degrees
        return {
            'A1': float(np.degrees(A1)),
            'A2': float(np.degrees(A2)),
            'A3': float(np.degrees(A3)),
            'A4': float(np.degrees(A4)),
        }

    def solve_vect(self, dx, dy, dz):
        """
        Solves IK and returns displacement vectors for each arm segment.
        
        Uses forward kinematics to calculate joint positions:
        - A (base) at origin
        - B (shoulder) = A + first link
        - C (elbow) = B + second link
        - D (wrist) = C + third link
        
        Args:
            dx, dy, dz: Target position
            
        Returns:
            tuple: (v1, v2, v3) - displacement vectors for each link
        """
        L = self.L

        # Solve for angles first
        angles = self.solve(dx, dy, dz)
        A1 = np.radians(angles['A1'])
        A2 = np.radians(angles['A2'])
        A3 = np.radians(angles['A3'])
        A4 = np.radians(angles['A4'])

        # Forward kinematics: calculate joint positions
        A = np.array([0.0, 0.0, 0.0])

        # B (shoulder): first link
        B = np.array([
            L * np.cos(A2) * np.cos(A1),
            L * np.cos(A2) * np.sin(A1),
            L * np.sin(A2)
        ])

        # C (elbow): B + second link
        C = B + np.array([
            L * np.cos(A2 + A3) * np.cos(A1),
            L * np.cos(A2 + A3) * np.sin(A1),
            L * np.sin(A2 + A3)
        ])

        # D (wrist): C + third link
        D = C + np.array([
            L * np.cos(A2 + A3 + A4) * np.cos(A1),
            L * np.cos(A2 + A3 + A4) * np.sin(A1),
            L * np.sin(A2 + A3 + A4)
        ])

        
        v1 = B - A
        v2 = C - B
        v3 = D - C

        return v1, v2, v3

    def update(self, vector_str):
        """
        Solve from a space-separated string "dx dy dz".
        
        Args:
            vector_str (str): Space-separated target position like "0.5 0.5 0.5"
            
        Returns:
            dict: Angles in degrees {'A1': x, 'A2': y, 'A3': z, 'A4': w}
        """
        parts = vector_str.split()
        dx = float(parts[0])
        dy = float(parts[1])
        dz = float(parts[2])
        return self.solve(dx, dy, dz)

    def update_vect(self, vector_tuple):
        """
        Solve from a vector tuple (dx, dy, dz) and return displacement vectors.
        
        Args:
            vector_tuple (tuple): (dx, dy, dz) target position
            
        Returns:
            tuple: (v1, v2, v3) - displacement vectors for each link
        """
        dx, dy, dz = vector_tuple
        return self.solve_vect(float(dx), float(dy), float(dz))

    def get_joint_positions(self, dx, dy, dz):
        """
        Calculate all joint positions (A, B, C, D) for a target.
        
        Args:
            dx, dy, dz: Target position
            
        Returns:
            dict: Joint positions {'A': [x,y,z], 'B': [...], 'C': [...], 'D': [...]}
        """
        L = self.L
        angles = self.solve(dx, dy, dz)
        A1 = np.radians(angles['A1'])
        A2 = np.radians(angles['A2'])
        A3 = np.radians(angles['A3'])
        A4 = np.radians(angles['A4'])

        A = np.array([0.0, 0.0, 0.0])
        B = np.array([
            L * np.cos(A2) * np.cos(A1),
            L * np.cos(A2) * np.sin(A1),
            L * np.sin(A2)
        ])
        C = B + np.array([
            L * np.cos(A2 + A3) * np.cos(A1),
            L * np.cos(A2 + A3) * np.sin(A1),
            L * np.sin(A2 + A3)
        ])
        D = C + np.array([
            L * np.cos(A2 + A3 + A4) * np.cos(A1),
            L * np.cos(A2 + A3 + A4) * np.sin(A1),
            L * np.sin(A2 + A3 + A4)
        ])

        return {
            'A': A,
            'B': B,
            'C': C,
            'D': D,
            'angles': angles
        }