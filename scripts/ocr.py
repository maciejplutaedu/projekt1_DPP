import cv2
import os

import easyocr
from matplotlib import pyplot as plt

reader = easyocr.Reader(['pl','en'], gpu=True)

def read_plate(plate_image, reader):
    DIGIT_TO_LETTER = {
        "1":"I","0": "O","2": "Z","3": "B","4": "A","5": "S",
        "6": "G","7": "T","8": "B","9": "P"
    }

    INVALID_FIRST = {"1","I","J","Q","U","V","X","Y"}

    results = reader.readtext(
        plate_image,
        allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    if not results:
        return "", ""

    # ===== WYBIERAMY NAJDŁUŻSZY SENSOWNY TEKST =====
    cleaned = []

    for r in results:
        txt = r[1].replace(" ", "").upper()
        if len(txt) >= 5:
            cleaned.append((txt, r[2]))

    if not cleaned:
        best = max(results, key=lambda x: x[2])
        raw_text = best[1].replace(" ", "").upper()
    else:
        raw_text = max(cleaned, key=lambda x: (len(x[0]), x[1]))[0]


    text = raw_text

    # ===== ZAMIANA CYFR NA LITERY W 2 PIERWSZYCH =====
    if len(text) >= 2:
        t = list(text)
        for i in range(2):
            if t[i] in DIGIT_TO_LETTER:
                t[i] = DIGIT_TO_LETTER[t[i]]
        text = "".join(t)

    # ===== USUWANIE PL =====
    if text.startswith("PL"):
        text = text[2:]

    # ===== USUWANIE ZŁEJ PIERWSZEJ LITERY =====
    if len(text) > 0 and text[0] in INVALID_FIRST:
        text = text[1:]

    # ===== SKRACANIE =====
    if len(text) > 8:
        text = text[:8]

    return raw_text, text


def yolo_detection(img_path, model):
    image = cv2.imread(img_path)
    if image is None:
        return None, None

    results = model(image, conf=0.1)[0]
    boxes = results.boxes

    if boxes is None or len(boxes) == 0:
        return None, None

    best_idx = boxes.conf.argmax()
    x1, y1, x2, y2 = map(int, boxes.xyxy[best_idx].cpu().numpy())

    plate = image[y1:y2, x1:x2]

    return plate, image


# PREPROCESS
def preproccess_plate(plate_image):
    crop = cv2.resize(plate_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    blur = cv2.bilateralFilter(gray, 9, 75, 75)

    _, thresh = cv2.threshold(
        blur, 64, 255, cv2.THRESH_BINARY_INV
    )

    return gray


def run_ocr_test(sample, gt_data, image_dir, model):
    total_acc = 0
    count = 0

    for filename in sample:
        IMAGE_PATH = os.path.join(image_dir, filename)
        true_plate = gt_data.get(filename)

        # ===== YOLO =====
        plate_image, full_image = yolo_detection(IMAGE_PATH, model)
        if plate_image is None:
            continue

        # ===== PREPROCESS =====
        plate_pre = preproccess_plate(plate_image)

        # ===== OCR =====
        raw_text, final_plate = read_plate(plate_pre, reader)

        # ===== ACCURACY =====
        acc = plate_accuracy_strict(final_plate, true_plate)

        total_acc += acc
        count += 1

        # ===== OUTPUT =====
        print("===== OCR RESULT =====")
        print(f"IMAGE       : {filename}")
        print(f"RAW OCR     : {raw_text}")
        print(f"FINAL OCR   : {final_plate}")
        print(f"GROUND TRUTH: {true_plate}")
        print(f"ACCURACY    : {acc:.2f}%")
        print("======================\n")


        if acc < 0:
            plt.figure(figsize=(6,2))
            plt.imshow(plate_pre, cmap="gray")
            plt.title(f"OCR: {final_plate} | GT: {true_plate} | {acc:.2f}%")
            plt.axis("off")
            plt.show()

    return total_acc, count


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


def plate_accuracy_strict(pred, gt):
    if not pred or not gt:
        return 0.0

    pred = pred.replace(" ", "").upper()
    gt = gt.replace(" ", "").upper()

    if pred == gt:
        return 100.0
    return 0.0
