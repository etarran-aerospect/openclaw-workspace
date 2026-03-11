import argparse
import csv
import shutil
from pathlib import Path

import cv2
import numpy as np


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def detect_cluster_boxes(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, w = image.shape[:2]

    red_mask = cv2.inRange(hsv, np.array([0, 40, 10]), np.array([20, 255, 150]))
    purple_mask = cv2.inRange(hsv, np.array([100, 25, 10]), np.array([179, 255, 170]))
    mask = cv2.bitwise_or(red_mask, purple_mask)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    boxes = []
    for i in range(1, num_labels):
        x, y, bw, bh, area = stats[i]
        touches_border = x <= 1 or y <= 1 or x + bw >= w - 1 or y + bh >= h - 1
        if touches_border:
            continue
        if area < 1500:
            continue
        if bw < 40 or bh < 40:
            continue
        aspect = bw / max(1, bh)
        if aspect < 0.2 or aspect > 4.0:
            continue
        pad_x = max(8, int(bw * 0.08))
        pad_y = max(8, int(bh * 0.08))
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(w, x + bw + pad_x)
        y2 = min(h, y + bh + pad_y)
        boxes.append((x1, y1, x2, y2))

    boxes = sorted(boxes, key=lambda b: (b[0], b[1]))
    return boxes, mask


def count_visible_berries(crop):
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=9,
        param1=70,
        param2=15,
        minRadius=4,
        maxRadius=18,
    )
    if circles is None:
        return 0
    return int(len(circles[0]))


def yolo_line(box, width, height, class_id=0):
    x1, y1, x2, y2 = box
    x_center = ((x1 + x2) / 2) / width
    y_center = ((y1 + y2) / 2) / height
    w = (x2 - x1) / width
    h = (y2 - y1) / height
    return f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="source image")
    parser.add_argument("--root", default=".", help="grape_pipeline root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    src = Path(args.image).resolve()
    image = cv2.imread(str(src))
    if image is None:
        raise FileNotFoundError(src)

    h, w = image.shape[:2]
    boxes, mask = detect_cluster_boxes(image)

    det_train_img = root / "dataset_detector/images/train/grape_seed_001.jpg"
    det_val_img = root / "dataset_detector/images/val/grape_seed_001.jpg"
    det_train_lbl = root / "dataset_detector/labels/train/grape_seed_001.txt"
    det_val_lbl = root / "dataset_detector/labels/val/grape_seed_001.txt"

    ensure_dir(det_train_img.parent)
    ensure_dir(det_val_img.parent)
    ensure_dir(det_train_lbl.parent)
    ensure_dir(det_val_lbl.parent)

    shutil.copy2(src, det_train_img)
    shutil.copy2(src, det_val_img)

    label_text = "\n".join(yolo_line(b, w, h) for b in boxes) + ("\n" if boxes else "")
    det_train_lbl.write_text(label_text)
    det_val_lbl.write_text(label_text)

    train_csv = root / "dataset_counter/train/labels.csv"
    val_csv = root / "dataset_counter/val/labels.csv"
    ensure_dir((root / "dataset_counter/train/images"))
    ensure_dir((root / "dataset_counter/val/images"))

    rows = []
    annotated = image.copy()
    for idx, (x1, y1, x2, y2) in enumerate(boxes, start=1):
        crop = image[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        est = max(1, count_visible_berries(crop))
        filename = f"cluster_{idx:03d}.jpg"
        out_train = root / "dataset_counter/train/images" / filename
        out_val = root / "dataset_counter/val/images" / filename
        cv2.imwrite(str(out_train), crop)
        cv2.imwrite(str(out_val), crop)
        rows.append((filename, est))
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(annotated, f"c{idx}~{est}", (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    with train_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "count"])
        writer.writerows(rows)

    with val_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "count"])
        writer.writerows(rows)

    cv2.imwrite(str(root / "seed_annotation_preview.jpg"), annotated)
    cv2.imwrite(str(root / "seed_mask_preview.jpg"), mask)

    print(f"Detected clusters: {len(rows)}")
    print(f"Wrote detector labels and counter crops under: {root}")


if __name__ == "__main__":
    main()
