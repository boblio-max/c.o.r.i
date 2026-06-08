import matplotlib.pyplot as plt
# Demo plotting 3D vectors for testing and visualization.
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for i in range(10):
    v1 = np.array([1, 2, 3])
    v2 = np.array([-i, i, i])

    #VECTOR 1
    ax.quiver(0, 0, 0, v1[0], v1[1], v1[2], color='r', arrow_length_ratio=0.1)
    #VECTOR 2
    ax.quiver(0, 0, 0, v2[0], v2[1], v2[2], color='b', arrow_length_ratio=0.1)

    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    ax.set_zlim([-3, 3])

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title('3D Vector Plot')

    # Display the plot window
    plt.show()