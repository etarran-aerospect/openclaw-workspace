import argparse
from pathlib import Path

import pandas as pd
from PIL import Image
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models


class GrapeCountDataset(Dataset):
    def __init__(self, image_dir, labels_csv, transform=None):
        self.image_dir = Path(image_dir)
        self.df = pd.read_csv(labels_csv)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = self.image_dir / row["image"]
        count = float(row["count"])

        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)

        target = torch.tensor([count], dtype=torch.float32)
        return image, target


class CountRegressor(nn.Module):
    def __init__(self):
        super().__init__()
        backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        in_features = backbone.fc.in_features
        backbone.fc = nn.Linear(in_features, 1)
        self.model = backbone

    def forward(self, x):
        return self.model(x)


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0

    for images, targets in loader:
        images = images.to(device)
        targets = targets.to(device)

        optimizer.zero_grad()
        preds = model(images)
        loss = criterion(preds, targets)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)

    return total_loss / len(loader.dataset)


@torch.no_grad()
def eval_one_epoch(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    mae = 0.0

    for images, targets in loader:
        images = images.to(device)
        targets = targets.to(device)

        preds = model(images)
        loss = criterion(preds, targets)

        total_loss += loss.item() * images.size(0)
        mae += torch.abs(preds - targets).sum().item()

    avg_loss = total_loss / len(loader.dataset)
    avg_mae = mae / len(loader.dataset)
    return avg_loss, avg_mae


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-images", required=True)
    parser.add_argument("--train-labels", required=True)
    parser.add_argument("--val-images", required=True)
    parser.add_argument("--val-labels", required=True)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--out", default="grape_counter.pt")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    train_ds = GrapeCountDataset(args.train_images, args.train_labels, transform)
    val_ds = GrapeCountDataset(args.val_images, args.val_labels, transform)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False)

    model = CountRegressor().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.SmoothL1Loss()

    best_mae = float("inf")

    for epoch in range(args.epochs):
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_mae = eval_one_epoch(model, val_loader, criterion, device)

        print(
            f"Epoch {epoch+1}/{args.epochs} | "
            f"train_loss={train_loss:.4f} | val_loss={val_loss:.4f} | val_mae={val_mae:.2f}"
        )

        if val_mae < best_mae:
            best_mae = val_mae
            torch.save(model.state_dict(), args.out)
            print(f"Saved best model to {args.out}")


if __name__ == "__main__":
    main()
