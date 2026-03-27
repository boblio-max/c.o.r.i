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
L = 1
Lm = 1.57079
A1 = 0
A2 = 0
A3 = 0
A4 = 0

n = "1 1 1"

ns = n.split(" ")


A = (0,0,0)
B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))
C = np.add(B, (L*np.cos(A2 + A3)*np.cos(A1), L*np.cos(A2 + A3)*np.sin(A3), L*np.sin(A2 + A3)))
D = np.add(C, (L*np.cos(A2 + A3 + A4)*np.cos(A1), L*np.cos(A2 + A3 + A4)*np.sin(A1), L* np.sin(A2 + A3 + A4)))

N = (ns[0], ns[1], ns[2])
quiver_object = ax.quiver(A[0], A[1], A[2], N[0], N[1], N[2], color='r', label='End Vector')
quiver1 = ax.quiver(A[0], A[1], A[2], B[0], B[1], B[2], color='b', label='Shoulder Vector')
quiver2 = ax.quiver(B[0], B[1], B[2], C[0], C[1], C[2], color='y', label='Elbow Vector')
quiver3 = ax.quiver(C[0], C[1], C[2], D[0], D[1], D[2], color='r', label='Wrist Vector')

ax.legend()

class vector:
    def __init__(self):
        
        self.quiver_object = quiver_object
        self.quiver1 = quiver1
        self.quiver2 = quiver2
        self.quiver3 = quiver3

    def update(self, vector): 
        n = vector
        ns = n.split(" ")
        dx = float(ns[0]) 
        dy = float(ns[1])
        dz = float(ns[2])
        A2, A3, A4 = 0,0,0
        A1 = np.arctan2(dy,dx)
        B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))

        r = np.hypot(dx, dy)            
        s = dz                         
        
        try:
            c2 = (r*r + s*s - 3*L*L) / (2*L*r)      
            if abs(c2) > 1.0:                    
                raise ValueError('point out of reach')
            A2 = np.arctan2(s, r) - np.arctan2(np.sqrt(1 - c2*c2), c2)

            c23 = (r - L*np.cos(A2)) / (2*L)
            c23 = np.clip(c23, -1.0, 1.0)  
            A3 = np.arccos(c23) - A2              
            A4 = A3                              
        except ValueError:
            A2, A3, A4 = 0.0, 0.0, 0.0

        B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))
        C = B + np.array([L*np.cos(A2+A3)*np.cos(A1),
                            L*np.cos(A2+A3)*np.sin(A1),
                            L*np.sin(A2+A3)])
        D = C + np.array([L*np.cos(A2+A3+A4)*np.cos(A1),
                            L*np.cos(A2+A3+A4)*np.sin(A1),
                            L*np.sin(A2+A3+A4)])
        
        
        self.quiver_object.set_segments([[[0, 0, 0], [dx, dy, dz]]])
        self.quiver1.set_segments([[[0,0,0], B]])
        self.quiver2.set_segments([[B, C]])
        self.quiver3.set_segments([[C, D]])  

        angles_deg = {
            'A1': np.degrees(A1) % 180,
            'A2': np.degrees(A2) % 180,
            'A3': np.degrees(A3) % 180,
            'A4': np.degrees(A4) % 180,
        }
        
        return angles_deg