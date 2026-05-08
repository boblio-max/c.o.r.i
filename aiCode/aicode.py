import cv2
import torch
import torch.nn as nn # Import for the new linear layer
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights

# Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load ResNet50 with default weights, then modify its final layer
model = resnet50(weights=ResNet50_Weights.DEFAULT)

# Replace the final classification layer with a new linear layer
# that outputs a 3D vector. The original ResNet50.fc.in_features is 2048.
num_output_features = 3
model.fc = nn.Linear(model.fc.in_features, num_output_features)

# Move the modified model to the device and set to evaluation mode.
# For a meaningful 3D vector, this new 'model.fc' layer would need training
# on a dataset specific to the desired 3D output.
model = model.to(device).eval()

preprocess = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

cap = cv2.VideoCapture(0)

with torch.no_grad():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame or camera not available. Exiting.")
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor = preprocess(rgb).unsqueeze(0).to(device)

        # Get the 3D vector output from the modified model
        output_vector = model(tensor).squeeze(0) # Remove batch dimension

        # Convert the tensor to a numpy array for display
        vector_np = output_vector.cpu().numpy()

        # Format the 3D vector for display
        label = f"Vector: [{vector_np[0]:.2f}, {vector_np[1]:.2f}, {vector_np[2]:.2f}]"
        cv2.putText(frame, label, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Live AI Output (Untrained 3D Vector)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
