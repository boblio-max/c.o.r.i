import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.animation as animation
from IPython.display import HTML

# Set up the figure and 3D axes
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Set axis limits initially
ax.set_xlim([-5, 5])
ax.set_ylim([-5, 5])
ax.set_zlim([-5, 5])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Animated 3D Vector')
L = 1
Lm = 1.57079
A1 = 0
A2 = 0
A3 = 0
A4 = 0
# Initialize the vector using quiver. The components (U, V, W) will be updated.
# We set initial components to (0,0,0) as they will be immediately updated.

A = (0,0,0)
B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))
C = np.add(B, (L*np.cos(A2 + A3)*np.cos(A1), L*np.cos(A2 + A3)*np.sin(A3), L*np.sin(A2 + A3)))
D = np.add(C, (L*np.cos(A2 + A3 + A4)*np.cos(A1), L*np.cos(A2 + A3 + A4)*np.sin(A1), L* np.sin(A2 + A3 + A4)))

N = (0,0,0)
quiver_object = ax.quiver(A[0], A[1], A[2], N[0], N[1], N[2], color='r', label='Moving Vector')
quiver1 = ax.quiver(A[0], A[1], A[2], B[0], B[1], B[2])
quiver2 = ax.quiver(B[0], B[1], B[2], C[0], C[1], C[2])
quiver2 = ax.quiver(C[0], C[1], C[2], D[0], D[1], D[2])

ax.legend()

# Animation update function: This function is called for each frame
def update(frame):
    # Calculate new vector components based on the frame number
    # The vector tip moves in a circle in the XY plane and oscillates in Z
    t = frame * 0.05  # Time parameter to control speed of animation
    dx = 4 * np.cos(t)
    dy = 4 * np.sin(t)
    dz = 2 * np.sin(t * 2)  # Oscillate faster in Z

    B1 = np.arctan(dy,dx)
    # Update the quiver object's direction components (U, V, W)
    # The set_segments method expects a list of [start_point, end_point] lists
    N = (dx,dy,dz)
    quiver_object.set_segments([[[0, 0, 0], [dx, dy, dz]]])
    A1 = B1
    B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))
    quiver1.set_segments([[0,0,0], [B[0],B[1],B[2]]])


    # You can also update other properties, e.g., the starting point if needed
    # quiver_object.set_offsets(np.array([[start_x, start_y, start_z]]))
    return np.linalg.norm(np.array(D) - np.array(N))
    return quiver_object, # Return the updated artist(s)

# Create the animation
# frames: The number of frames to generate
# interval: Delay between frames in milliseconds
# blit: Whether to use blitting for optimization (can be tricky with 3D, so set to False)
anim = animation.FuncAnimation(fig, update, frames=100, interval=50, blit=False)

# Display the animation in the Colab notebook
# Note: This might take a moment to render depending on the animation length.
HTML(anim.to_jshtml())