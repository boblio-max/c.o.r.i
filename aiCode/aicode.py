import cv2
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights

# Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = resnet50(weights=ResNet50_Weights.DEFAULT).to(device).eval()

preprocess = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

cap = cv2.VideoCapture(0)  # 0 = default webcam

with torch.no_grad():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # BGR (OpenCV) → RGB → tensor → batch dim
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor = preprocess(rgb).unsqueeze(0).to(device)  # [1, 3, 224, 224]

        output = model(tensor)  # raw logits
        probs = torch.softmax(output, dim=1)
        top_prob, top_class = probs.topk(1, dim=1)

        label = f"Class {top_class.item()} ({top_prob.item():.2%})"
        cv2.putText(frame, label, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Live AI", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()