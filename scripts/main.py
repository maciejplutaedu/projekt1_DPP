import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ultralytics import YOLO
import easyocr
import xml.etree.ElementTree as ET
import random
import time
from paddleocr import PaddleOCR
from paddle_OCR import run_ocr_test

#from ocr import run_ocr_test

IMAGE_DIR = "../data/photos"
XML_PATH = "../data/annotations.xml"

# ========================
# OCENA
# ========================
def calculate_final_grade(accuracy_percent: float, processing_time_sec: float) -> float:
    if accuracy_percent < 60 or processing_time_sec > 60:
        return 2.0

    accuracy_norm = (accuracy_percent - 60) / 40
    time_norm = (60 - processing_time_sec) / 50

    score = 0.7 * accuracy_norm + 0.3 * time_norm
    grade = 2.0 + 3.0 * score

    return round(grade * 2) / 2


# ========================
# POPRAWNA REJESTRACJA
# ========================
def load_gt():
    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    gt = {}
    for image in root.findall("image"):
        name = image.attrib["name"]
        box = image.find("box")
        if box is not None:
            attr = box.find("attribute")
            if attr is not None:
                gt[name] = attr.text.strip().upper()
    return gt


# ========================
# PORÓWNANIE
# ========================
def plate_accuracy(pred, gt):
    if not pred or not gt:
        return 0.0

    pred = pred.replace(" ", "").upper()
    gt = gt.replace(" ", "").upper()

    correct = 0
    for p, t in zip(pred, gt):
        if p == t:
            correct += 1

    return correct / max(len(gt), 1) * 100


# ========================
# MODELE
# ========================
model = YOLO("runs/plate_detector2/weights/best.pt")




# ========================
# DANE
# ========================
gt_data = load_gt()
images = list(gt_data.keys())
sample = random.sample(images, min(100, len(images)))

print("\n===== OCR =====\n")

start_time = time.time()


total_acc, count = run_ocr_test(
    sample=sample,
    gt_data=gt_data,
    image_dir=IMAGE_DIR,
    model=model,
)

end_time = time.time()
processing_time = end_time - start_time


# PODSUMOWANIE
mean_acc = total_acc / count if count else 0
grade = calculate_final_grade(mean_acc, processing_time)

print("========= SUMMARY =========")
print(f"TESTED IMAGES : {count}")
print(f"MEAN ACCURACY : {mean_acc:.2f}%")
print(f"TIME         : {processing_time:.2f}s")
print(f"FINAL GRADE  : {grade}")
print("===========================")
