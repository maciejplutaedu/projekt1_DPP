import urllib.request
import numpy as np
import tensorflow as tf
import cv2 as cv

graph = None
sess = None

def init_model():
    global graph, sess
    graph = load_graph()
    sess = tf.compat.v1.Session(graph=graph)
# --------------------------------------------------------------------
# Load frozen TensorFlow 1.x graph
# --------------------------------------------------------------------
def load_graph():
    graph = tf.Graph()
    with graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile("ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb", "rb") as f:
            serialized_graph = f.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name="")
    return graph


graph = load_graph()
sess = tf.compat.v1.Session(graph=graph)


# --------------------------------------------------------------------
# Download image
# --------------------------------------------------------------------
def download_image(url: str):
    resp = urllib.request.urlopen(url)
    data = resp.read()
    img_array = np.asarray(bytearray(data), dtype=np.uint8)
    img = cv.imdecode(img_array, cv.IMREAD_COLOR)
    return img


# --------------------------------------------------------------------
# Count people
# --------------------------------------------------------------------
def count_people(url: str) -> int:
    img = download_image(url)
    if img is None:
        return 0

    # convert BGR to RGB
    rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    # expand dims to match model input
    input_tensor = np.expand_dims(rgb, axis=0)

    # run TF session
    boxes, scores, classes, num = sess.run(
        [
            graph.get_tensor_by_name("detection_boxes:0"),
            graph.get_tensor_by_name("detection_scores:0"),
            graph.get_tensor_by_name("detection_classes:0"),
            graph.get_tensor_by_name("num_detections:0")
        ],
        feed_dict={"image_tensor:0": input_tensor}
    )

    # COCO class 1 = person
    count = sum(
        1 for i in range(int(num[0]))
        if scores[0][i] > 0.5 and int(classes[0][i]) == 1
    )

    return count
