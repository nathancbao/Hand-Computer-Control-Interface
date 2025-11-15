import torch
import torch.nn as nn
import os

model_path = "model/keypoint_model.pth"

class KeyPointModel(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(42, 20), # First fully-connected layer
            nn.ReLU(), # Add non-linearity
            nn.Dropout(0.4),
            nn.Linear(20, 10), # Hidden Layer
            nn.ReLU(),
            nn.Linear(10, num_classes)
        )

    def forward(self, x):
        return self.net(x)

# Load the trained ML model and make it callable for classifying gestures
class KeyPointClassifier:
    def __init__(self, num_classes):
        if os.path.exists(model_path):
			# load model
            self.model = KeyPointModel(num_classes)
            state_dict = torch.load(model_path, map_location="cpu")
            self.model.load_state_dict(state_dict)
            self.model.eval()
        else:
            self.model = None

    def __call__(self, landmark_list):
        if self.model:
            x = torch.tensor(landmark_list, dtype=torch.float32).unsqueeze(0)
            logits = self.model(x)
            return torch.argmax(logits, dim=1).item()
        else:
            return 0
