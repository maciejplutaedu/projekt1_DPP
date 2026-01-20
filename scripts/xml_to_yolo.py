import xml.etree.ElementTree as ET
import os

XML_FILE = "../data/annotations.xml"
LABELS_DIR = "../data/labels"

os.makedirs(LABELS_DIR, exist_ok=True)

tree = ET.parse(XML_FILE)
root = tree.getroot()

for image in root.findall("image"):
    img_name = image.get("name")
    img_w = float(image.get("width"))
    img_h = float(image.get("height"))

    if img_name is None:
        continue

    yolo_lines = []

    for box in image.findall("box"):
        class_id = 0

        xtl = float(box.get("xtl"))
        ytl = float(box.get("ytl"))
        xbr = float(box.get("xbr"))
        ybr = float(box.get("ybr"))

        x_center = ((xtl + xbr) / 2) / img_w
        y_center = ((ytl + ybr) / 2) / img_h
        width = (xbr - xtl) / img_w
        height = (ybr - ytl) / img_h

        yolo_lines.append(
            f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
        )

    txt_name = os.path.splitext(img_name)[0] + ".txt"
    txt_path = os.path.join(LABELS_DIR, txt_name)

    with open(txt_path, "w") as f:
        f.write("\n".join(yolo_lines))

