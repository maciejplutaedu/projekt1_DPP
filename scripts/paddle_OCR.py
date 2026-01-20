import cv2
import os
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
import re


reader = PaddleOCR(use_textline_orientation=False,
                   lang='en',
                   use_gpu=False,
                   det_db_thesh=0.2,
                   det_db_box_thresh=0.3,
                   det_db_unclip_ratio=2.0,
                   )


def read_plate(plate_image, reader):
    DIGIT_TO_LETTER = {
        "1":"I","0": "O","2": "Z","3": "B","4": "A","5": "S",
        "6": "G","7": "T","8": "B","9": "P"
    }

    INVALID_FIRST = {"1","A","H","I","J","M","Q","U","V","X","Y"}

    result = reader.ocr(plate_image)

    if not result or not result[0]:
        return "", ""

    cleaned = []
    h = plate_image.shape[0]

    for line in result[0]:
        box = line[0]
        txt = line[1][0].replace(" ", "").upper()
        txt = re.sub(r"[^A-Z0-9]", "", txt)
        conf = line[1][1]

        y_center = sum([p[1] for p in box]) / 4

        if y_center > h * 0.75:
            continue

        if len(txt) >= 2:
            cleaned.append((txt, conf))

    if not cleaned:
        return "", ""

    raw_text = max(cleaned, key=lambda x: (len(x[0]), x[1]))[0]
    text = raw_text



    # USUWANIE PL
    if text.startswith("PL"):
        text = text[2:]

    # USUWANIE ZŁEJ PIERWSZEJ LITERY
    if len(text) > 0 and text[0] in INVALID_FIRST:
        text = text[1:]

    #SKRACANIE
    if len(text) > 8:
        text = text[:8]

    # ZAMIANA CYFR NA LITERY
    t = list(text)

    if len(text) < 7:
        if len(t) >= 1 and t[0] in DIGIT_TO_LETTER:
            t[0] = DIGIT_TO_LETTER[t[0]]
    elif len(text) < 8:
        for i in range(min(2, len(t))):
            if t[i] in DIGIT_TO_LETTER:
                t[i] = DIGIT_TO_LETTER[t[i]]
    else:
        for i in range(min(3, len(t))):
            if t[i] in DIGIT_TO_LETTER:
                t[i] = DIGIT_TO_LETTER[t[i]]

    text = "".join(t)

    return raw_text, text


def yolo_detection(img_path, model):
    image = cv2.imread(img_path)
    if image is None:
        return None, None

    results = model(image, conf=0.01, imgsz=640)[0]
    boxes = results.boxes

    if boxes is None or len(boxes) == 0:
        return None, None

    best_idx = boxes.conf.argmax()
    x1, y1, x2, y2 = map(int, boxes.xyxy[best_idx].cpu().numpy())

    plate = image[y1:y2, x1:x2]

    return plate, image


def preproccess_plate(plate_image):
    gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)

    blur = cv2.bilateralFilter(gray, 9, 75, 75)

    _, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY_INV)

    return gray, thresh


# ========================
# TEST
# ========================
def run_ocr_test(sample, gt_data, image_dir, model):
    total_acc = 0
    count = 0

    for filename in sample:
        IMAGE_PATH = os.path.join(image_dir, filename)
        true_plate = gt_data.get(filename)

        plate_image, _ = yolo_detection(IMAGE_PATH, model)
        if plate_image is None:
            continue

        plate_pre_gray, plate_pre_thresh = preproccess_plate(plate_image)

        raw_text, final_plate = read_plate(plate_pre_gray, reader)

        if not final_plate or len(final_plate) < 5:
            raw_text, final_plate = read_plate(plate_pre_thresh, reader)

        acc = plate_accuracy_strict(final_plate, true_plate)

        total_acc += acc
        count += 1

        print("===== OCR RESULT =====")
        print(f"IMAGE       : {filename}")
        print(f"RAW OCR     : {raw_text}")
        print(f"FINAL OCR   : {final_plate}")
        print(f"GROUND TRUTH: {true_plate}")
        print(f"ACCURACY    : {acc:.2f}%")
        print("======================\n")

        if acc < 0:
            plt.figure(figsize=(6,2))
            plt.imshow(plate_pre_gray, cmap="gray")
            plt.title(f"OCR: {final_plate} | GT: {true_plate}")
            plt.axis("off")
            plt.show()

    return total_acc, count


# ========================
# ACCURACY
# ========================
def plate_accuracy_strict(pred, gt):
    if not pred or not gt:
        return 0.0
    return 100.0 if pred.replace(" ","") == gt.replace(" ","") else 0.0
