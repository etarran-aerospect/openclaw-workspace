import argparse
import csv
import random
import shutil
from pathlib import Path

import cv2
import numpy as np


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def clear_dir(path: Path):
    ensure_dir(path)
    for p in path.iterdir():
        if p.is_file() or p.is_symlink():
            p.unlink()


def detect_cluster_boxes(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, w = image.shape[:2]

    red_mask = cv2.inRange(hsv, np.array([0, 40, 10]), np.array([20, 255, 150]))
    purple_mask = cv2.inRange(hsv, np.array([100, 25, 10]), np.array([179, 255, 170]))
    dark_mask = cv2.inRange(hsv, np.array([0, 30, 0]), np.array([179, 255, 95]))
    mask = cv2.bitwise_or(cv2.bitwise_or(red_mask, purple_mask), dark_mask)

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
        if area < 1500 or bw < 40 or bh < 40:
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

    return sorted(boxes, key=lambda b: (b[0], b[1]))


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
    return 0 if circles is None else int(len(circles[0]))


def yolo_line(box, width, height, class_id=0):
    x1, y1, x2, y2 = box
    x_center = ((x1 + x2) / 2) / width
    y_center = ((y1 + y2) / 2) / height
    bw = (x2 - x1) / width
    bh = (y2 - y1) / height
    return f"{class_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--incoming", default="incoming_images")
    parser.add_argument("--root", default=".")
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    incoming = (root / args.incoming).resolve()
    files = sorted([p for p in incoming.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}])
    if not files:
        raise SystemExit('No input images found')

    det_img_train = root / 'dataset_detector/images/train'
    det_img_val = root / 'dataset_detector/images/val'
    det_lbl_train = root / 'dataset_detector/labels/train'
    det_lbl_val = root / 'dataset_detector/labels/val'
    count_img_train = root / 'dataset_counter/train/images'
    count_img_val = root / 'dataset_counter/val/images'

    for d in [det_img_train, det_img_val, det_lbl_train, det_lbl_val, count_img_train, count_img_val]:
        clear_dir(d)

    random.seed(args.seed)
    shuffled = files[:]
    random.shuffle(shuffled)
    val_count = max(1, int(len(shuffled) * args.val_ratio)) if len(shuffled) > 1 else 0
    val_set = {p.name for p in shuffled[:val_count]}

    train_rows = []
    val_rows = []
    preview_dir = root / 'seed_previews'
    clear_dir(preview_dir)

    total_boxes = 0
    cluster_serial = 1
    usable_images = 0

    for idx, src in enumerate(files, start=1):
        image = cv2.imread(str(src))
        if image is None:
            continue
        h, w = image.shape[:2]
        boxes = detect_cluster_boxes(image)
        if not boxes:
            continue
        usable_images += 1
        split = 'val' if src.name in val_set else 'train'
        stem = f'grape_seed_{idx:03d}'

        img_out = root / f'dataset_detector/images/{split}/{stem}.jpg'
        lbl_out = root / f'dataset_detector/labels/{split}/{stem}.txt'
        cv2.imwrite(str(img_out), image)
        lbl_out.write_text('\n'.join(yolo_line(b, w, h) for b in boxes) + '\n')

        preview = image.copy()
        for box in boxes:
            x1, y1, x2, y2 = box
            crop = image[y1:y2, x1:x2]
            if crop.size == 0:
                continue
            est = max(1, count_visible_berries(crop))
            crop_name = f'cluster_{cluster_serial:04d}.jpg'
            crop_out = root / f'dataset_counter/{split}/images/{crop_name}'
            cv2.imwrite(str(crop_out), crop)
            row = (crop_name, est)
            if split == 'train':
                train_rows.append(row)
            else:
                val_rows.append(row)
            cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(preview, f'c{cluster_serial}~{est}', (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
            cluster_serial += 1
            total_boxes += 1
        cv2.imwrite(str(preview_dir / f'{stem}_{split}.jpg'), preview)

    for csv_path, rows in [
        (root / 'dataset_counter/train/labels.csv', train_rows),
        (root / 'dataset_counter/val/labels.csv', val_rows),
    ]:
        with csv_path.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['image', 'count'])
            writer.writerows(rows)

    print(f'Total source images: {len(files)}')
    print(f'Usable images with seeded boxes: {usable_images}')
    print(f'Total seeded cluster crops: {total_boxes}')
    print(f'Train crops: {len(train_rows)} | Val crops: {len(val_rows)}')


if __name__ == '__main__':
    main()
