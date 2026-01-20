from ultralytics import YOLO

def main():
    model = YOLO('yolov8n.yaml')

    model.train(
        data="../model_config.yaml",
        epochs=65,
        imgsz=940,
        batch=16,
        device=0,
        project="runs",
        name="plate_detector"
    )

if __name__ == "__main__":
    main()