import torch
import os
from train import build_model, DEVICE

def export_to_onnx(arch="efficientnet_b3", weights_path="models/best_model.pth", out_path="models/best_model.onnx"):
    print(f"Loading {arch} from {weights_path}...")
    model = build_model(arch)
    
    if os.path.exists(weights_path):
        model.load_state_dict(torch.load(weights_path, map_location=DEVICE))
        print("Weights loaded successfully.")
    else:
        print("Warning: Weights file not found. Exporting model with random initialization.")
        
    model.eval()
    model.to("cpu") # Export on CPU for broader ONNX runtime compatibility
    
    # Dummy input for tracing (batch_size=1, channels=3, height=224, width=224)
    dummy_input = torch.randn(1, 3, 224, 224, device="cpu")
    
    # Export the model
    print(f"Exporting to {out_path}...")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    torch.onnx.export(
        model,               
        dummy_input,                         
        out_path,   
        export_params=True,        
        opset_version=14,          
        do_constant_folding=True,  
        input_names=['input'],   
        output_names=['output'], 
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"Successfully exported ONNX model to {out_path}")

if __name__ == "__main__":
    export_to_onnx()
