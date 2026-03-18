import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation
from IPython.display import HTML


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')


ax.set_xlim([-5, 5])
ax.set_ylim([-5, 5])
ax.set_zlim([-5, 5])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D vector regression code')
L = 1
Lm = 1.57079
A1 = 0
A2 = 0
A3 = 0
A4 = 0


A = (0,0,0)
B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))
C = np.add(B, (L*np.cos(A2 + A3)*np.cos(A1), L*np.cos(A2 + A3)*np.sin(A3), L*np.sin(A2 + A3)))
D = np.add(C, (L*np.cos(A2 + A3 + A4)*np.cos(A1), L*np.cos(A2 + A3 + A4)*np.sin(A1), L* np.sin(A2 + A3 + A4)))

N = (0,0,0)
quiver_object = ax.quiver(A[0], A[1], A[2], N[0], N[1], N[2], color='r', label='Moving Vector')
quiver1 = ax.quiver(A[0], A[1], A[2], B[0], B[1], B[2])
quiver2 = ax.quiver(B[0], B[1], B[2], C[0], C[1], C[2])
quiver3 = ax.quiver(C[0], C[1], C[2], D[0], D[1], D[2])

ax.legend()


def update(frame):

    t = frame * 0.05  
    dx = 4 * np.cos(t)
    dy = 4 * np.sin(t)
    dz = 2 * np.sin(t * 2)  

    # solve for A1
    # B1 = np.arctan2(dy,dx)
    N = (dx,dy,dz)
    
    A1 = np.arctan2(dy,dx)
    B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))
    quiver1.set_segments([[0,0,0], [B[0],B[1],B[2]]])

    # Find A2, A3, A4 from the N vector                   
    r = np.hypot(dx, dy)            
    s = dz                         

    try:
        c2 = (r*r + s*s - 3*L*L) / (2*L*r)      
        if abs(c2) > 1.0:                    
            raise ValueError('point out of reach')
        A2 = np.arctan2(s, r) - np.arctan2(np.sqrt(1 - c2*c2), c2)

        c23 = (r - L*np.cos(A2)) / (2*L)       
        A3 = np.arccos(c23) - A2              
        A4 = A3                              
    except ValueError:
        A2, A3, A4 = 0.0, 0.0, 0.0

    # Recompute B, C, and D vector lengths
    B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))
    C = B + np.array([L*np.cos(A2+A3)*np.cos(A1),
                        L*np.cos(A2+A3)*np.sin(A1),
                        L*np.sin(A2+A3)])
    D = C + np.array([L*np.cos(A2+A3+A4)*np.cos(A1),
                        L*np.cos(A2+A3+A4)*np.sin(A1),
                        L*np.sin(A2+A3+A4)])
    
    # Redraw the vectors 
    quiver_object.set_segments([[[0, 0, 0], [dx, dy, dz]]])
    quiver1.set_segments([[[0,0,0], B]])
    quiver2.set_segments([[B, C]])
    quiver3.set_segments([[C, D]])  
    
    return quiver_object,quiver1, quiver2, quiver3
anim = animation.FuncAnimation(fig, update, frames=100, interval=50, blit=False)


HTML(anim.to_jshtml())