import os
import onnxruntime as ort
import numpy as np
import cv2
import torch
import sys

# Add inference directory to path to import model definitions
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../inference"))
)
from train import build_model, CLASS_NAMES, DEVICE
from gradcam import GradCAM, generate_heatmap_overlay


class InferenceService:
    def __init__(self):
        self.onnx_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../../../inference/models/best_model.onnx"
            )
        )
        self.pth_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../../../inference/models/best_model.pth"
            )
        )

        self.ort_session = None
        self.pt_model = None

        # Load ONNX model for fast inference
        if os.path.exists(self.onnx_path):
            self.ort_session = ort.InferenceSession(
                self.onnx_path, providers=["CPUExecutionProvider"]
            )

    def load_pytorch_model(self):
        if self.pt_model is None and os.path.exists(self.pth_path):
            self.pt_model = build_model("efficientnet_b3")
            self.pt_model.load_state_dict(torch.load(self.pth_path, map_location="cpu"))
            self.pt_model.eval()
            self.pt_model.to("cpu")

    def preprocess_image(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))

        # Normalize
        img = img.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img = (img - mean) / std

        # Transpose to NCHW
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        return img

    def predict(self, image_path):
        if not self.ort_session:
            raise RuntimeError(
                "ONNX model not loaded. Run the training and export pipeline first."
            )

        input_data = self.preprocess_image(image_path)

        # ONNX Inference
        ort_inputs = {self.ort_session.get_inputs()[0].name: input_data}
        ort_outs = self.ort_session.run(None, ort_inputs)

        logits = ort_outs[0][0]
        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / exp_logits.sum()

        class_idx = np.argmax(probs)
        confidence = float(probs[class_idx])

        return {
            "condition": CLASS_NAMES[class_idx],
            "confidence": confidence,
            "severity": "Mild"
            if confidence < 0.8
            else "Moderate"
            if confidence < 0.95
            else "Severe",
            "class_idx": int(class_idx),
        }

    def generate_explainability(self, image_path, class_idx, output_dir):
        """Generates Grad-CAM heatmap and returns the path to the saved image."""
        self.load_pytorch_model()
        if not self.pt_model:
            raise RuntimeError("PyTorch model not loaded for Grad-CAM.")

        # For EfficientNet_b3, target the last convolutional layer in the features
        target_layer = self.pt_model.features[-1]

        grad_cam = GradCAM(self.pt_model, target_layer)

        # Prepare tensor
        img_np = self.preprocess_image(image_path)
        input_tensor = torch.from_numpy(img_np)
        input_tensor.requires_grad_(True)

        cam, _ = grad_cam(input_tensor, class_idx=class_idx)

        # Save visualization
        filename = os.path.basename(image_path)
        out_path = os.path.join(output_dir, f"heatmap_{filename}")

        generate_heatmap_overlay(image_path, cam, out_path)
        return out_path


inference_service = InferenceService()
