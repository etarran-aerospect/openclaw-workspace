import argparse

from pathlib import Path

import cv2
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models
from ultralytics import YOLO


class CountRegressor(nn.Module):
    def __init__(self):
        super().__init__()
        backbone = models.resnet18(weights=None)
        in_features = backbone.fc.in_features
        backbone.fc = nn.Linear(in_features, 1)
        self.model = backbone

    def forward(self, x):
        return self.model(x)


def load_counter_model(weights_path, device):
    model = CountRegressor().to(device)
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()
    return model


def crop_bgr(image, box):
    x1, y1, x2, y2 = box
    h, w = image.shape[:2]
    x1 = max(0, min(x1, w - 1))
    y1 = max(0, min(y1, h - 1))
    x2 = max(0, min(x2, w - 1))
    y2 = max(0, min(y2, h - 1))
    return image[y1:y2, x1:x2]


@torch.no_grad()
def estimate_count(counter_model, crop, device, tfm):
    rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    x = tfm(pil).unsqueeze(0).to(device)
    pred = counter_model(x).item()
    return max(0, round(pred))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Input image path")
    parser.add_argument("--detector", required=True, help="YOLO cluster detector weights")
    parser.add_argument("--counter", required=True, help="Count regressor weights (.pt)")
    parser.add_argument("--output", default="annotated_grapes.jpg")
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    detector = YOLO(args.detector)
    counter = load_counter_model(args.counter, device)

    tfm = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    image = cv2.imread(args.image)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {args.image}")

    results = detector.predict(
        source=args.image,
        conf=args.conf,
        save=False,
        verbose=False,
    )

    annotated = image.copy()
    total_estimated = 0
    cluster_idx = 0

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0]) if box.conf is not None else 0.0

            crop = crop_bgr(image, (x1, y1, x2, y2))
            if crop.size == 0:
                continue

            est_count = estimate_count(counter, crop, device, tfm)
            total_estimated += est_count
            cluster_idx += 1

            label = f"cluster_{cluster_idx}: ~{est_count} grapes ({conf:.2f})"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

    cv2.putText(
        annotated,
        f"Total estimated grapes: {total_estimated}",
        (10, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.imwrite(args.output, annotated)
    print(f"Saved: {args.output}")
    print(f"Total estimated grapes: {total_estimated}")


if __name__ == "__main__":
    main()
