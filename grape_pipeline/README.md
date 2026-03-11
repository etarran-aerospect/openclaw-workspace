# Grape pipeline

Two-stage starter pipeline for vineyard RGB images:

1. Detect grape clusters with YOLOv8
2. Estimate grape count per detected cluster with a regression model

## Structure

- `train_detector.py` — trains the YOLOv8 cluster detector
- `train_counter.py` — trains the per-cluster grape count regressor
- `infer_grapes.py` — runs both models and writes an annotated output image
- `dataset_detector/` — YOLO-format cluster detection dataset
- `dataset_counter/` — cropped cluster images + manual count CSVs

## Install

```bash
pip install ultralytics torch torchvision opencv-python pandas pillow
```

## Train detector

```bash
python train_detector.py --data dataset_detector/data.yaml --model yolov8n.pt --epochs 100 --imgsz 1024
```

## Train counter

```bash
python train_counter.py \
  --train-images dataset_counter/train/images \
  --train-labels dataset_counter/train/labels.csv \
  --val-images dataset_counter/val/images \
  --val-labels dataset_counter/val/labels.csv \
  --epochs 30 \
  --out grape_counter.pt
```

## Inference

```bash
python infer_grapes.py your_image.jpg \
  --detector runs_detector/grape_cluster_detector/weights/best.pt \
  --counter grape_counter.pt \
  --output annotated_grapes.jpg \
  --conf 0.25
```

## Labeling guidance

### Detector dataset
- One box per visible grape cluster
- YOLO label format: `class x_center y_center width height`
- Only class is `0` = `grape_cluster`

### Counter dataset
- Each image should be a crop of one cluster
- `labels.csv` format:

```csv
image,count
cluster_001.jpg,84
cluster_002.jpg,97
```

## Notes
- This is the practical cluster-first approach, not per-berry detection.
- For operational use, calibrate estimated counts against real manual counts from field samples.
