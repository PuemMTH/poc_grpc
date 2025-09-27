import torch
import clip
from PIL import Image, ImageDraw
from rich.console import Console

print = Console().print

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load(
        name="ViT-B/32",
        device=device,
        download_root="./models",
    )
    print("Model components:")
    for name, module in model.named_children():
        print(f"- {name}: {type(module).__name__}")

    # text = clip.tokenize(["anime", "cute", "cat"]).to(device)
    # image = preprocess(Image.open("image.png")).unsqueeze(0).to(device)
    
    # with torch.no_grad():
    #     logits_per_image, logits_per_text = model(image, text)
    #     probs = logits_per_image.softmax(dim=-1).cpu().numpy()

    # print("Label probs:", probs)  # prints: [[0.9927937  0.00421068 0.00299572]]

    # draw = ImageDraw.Draw(Image.open("image.png"))
    # draw.rectangle([0, 0, 100, 100], outline="red")
    # Image.open("image.png").show()

if __name__ == "__main__":
    main()
