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
    def __init__(self, num_classes, model_path=model_path, load_weights=True):
        # always create a model
        self.model = KeyPointModel(num_classes)

        if load_weights and os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location="cpu")
            try:
                self.model.load_state_dict(state_dict)
            except RuntimeError as e:
                # Shape mismatch (e.g., old 5-class checkpoint with new 6-class model)
                print(
                    "WARNING: could not load pretrained weights from "
                    f"{model_path} (probably class-count mismatch):\n", e
                )
                print("Continuing with randomly initialized weights.")
        else:
            if not os.path.exists(model_path):
                print(f"WARNING: model file {model_path} not found. "
                      "Using randomly initialized weights.")
            # if load_weights is False we also just keep random weights

        self.model.eval()

    def __call__(self, landmark_list):
        # landmark_list: normalized 42-dim vector from data.py
        x = torch.tensor(landmark_list, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(x)
            pred = torch.argmax(logits, dim=1).item()
        return pred
