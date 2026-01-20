import xml.etree.ElementTree as ET
import os
import shutil
import random

# ========================
# PATHS
# ========================
XML_PATH = "../data/annotations.xml"
IMAGES_DIR = "../data/photos"
DATASET_DIR = "../dataset"

TRAIN_RATIO = 0.8   # 80% train, 20% val

# ========================
# OUTPUT DIRS
# ========================
IMG_TRAIN = os.path.join(DATASET_DIR, "images/train")
IMG_VAL   = os.path.join(DATASET_DIR, "images/val")
LBL_TRAIN = os.path.join(DATASET_DIR, "labels/train")
LBL_VAL   = os.path.join(DATASET_DIR, "labels/val")

for d in [IMG_TRAIN, IMG_VAL, LBL_TRAIN, LBL_VAL]:
    os.makedirs(d, exist_ok=True)

# ========================
# LOAD XML
# ========================
tree = ET.parse(XML_PATH)
root = tree.getroot()

images = root.findall("image")

print(f"Found {len(images)} images in XML")

# ========================
# SHUFFLE + SPLIT
# ========================
random.shuffle(images)
split_idx = int(len(images) * TRAIN_RATIO)

train_images = images[:split_idx]
val_images   = images[split_idx:]

# ========================
# CONVERT + SAVE
# ========================
def process_images(image_list, img_out_dir, lbl_out_dir):

    for img in image_list:
        name = img.get("name")
        width = float(img.get("width"))
        height = float(img.get("height"))

        src_img_path = os.path.join(IMAGES_DIR, name)
        if not os.path.exists(src_img_path):
            print("Missing image:", name)
            continue

        # copy image
        shutil.copy(src_img_path, os.path.join(img_out_dir, name))

        yolo_lines = []

        for box in img.findall("box"):
            # only one class: plate -> id 0
            class_id = 0

            xtl = float(box.get("xtl"))
            ytl = float(box.get("ytl"))
            xbr = float(box.get("xbr"))
            ybr = float(box.get("ybr"))

            x_center = ((xtl + xbr) / 2) / width
            y_center = ((ytl + ybr) / 2) / height
            w = (xbr - xtl) / width
            h = (ybr - ytl) / height

            yolo_lines.append(
                f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}"
            )

        # save label file
        txt_name = os.path.splitext(name)[0] + ".txt"
        with open(os.path.join(lbl_out_dir, txt_name), "w") as f:
            f.write("\n".join(yolo_lines))


# ========================
# RUN
# ========================
process_images(train_images, IMG_TRAIN, LBL_TRAIN)
process_images(val_images, IMG_VAL, LBL_VAL)

print("\nDataset prepared successfully!")
print(f"Train images: {len(train_images)}")
print(f"Val images  : {len(val_images)}")
