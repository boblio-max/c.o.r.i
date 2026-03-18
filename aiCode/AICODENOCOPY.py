import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Setup 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([0, 1])
ax.set_ylim([0, 1])
ax.set_zlim([0, 1])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title('3D Vector Visualization')

# Initialize vector storage
vector_data = []

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert to grayscale and detect features (simple AI-like processing)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray, 100, 0.01, 10)
    
    # Calculate centroid of detected features
    if corners is not None:
        centroid = np.mean(corners, axis=0)[0]
        centroid = [centroid[0]/frame.shape[1], centroid[1]/frame.shape[0]]
    else:
        centroid = [0.5, 0.5]
    
    # Create 3D vector (X,Y from centroid, Z from motion detection)
    motion_score = cv2.absdiff(gray, np.uint8(np.mean(gray)))
    motion = np.mean(motion_score) / 255.0
    vector = [centroid[0], centroid[1], motion]
    
    # Update plot
    ax.clear()
    ax.quiver(0.5, 0.5, 0.5, 
              vector[0]-0.5, 
              vector[1]-0.5, 
              vector[2], 
              color='red', 
              lw=2)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_zlim([0, 1])
    plt.draw()
    plt.pause(0.05)
    
    # Break loop with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
plt.show()
