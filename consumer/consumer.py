import time
import pika
import json
import requests
import os
from producer.detector import init_model, count_people


os.makedirs("results", exist_ok=True)
os.makedirs("images", exist_ok=True)

def connect_with_retry():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host="rabbitmq",
                    credentials=pika.PlainCredentials("user", "pass")
                )
            )
            print("[CONSUMER] Connected to RabbitMQ!")
            return connection
        except Exception as e:
            print("[CONSUMER] RabbitMQ not ready, retrying in 1s...")
            time.sleep(1)


def callback(ch, method, properties, body):
    job = json.loads(body)
    job_id = job["id"]
    url = job["url"]

    print(f"[CONSUMER] Received: {job}")

    # --- analyze image ---
    people = count_people(url)

    # --- download and save analyzed image ---
    img_data = requests.get(url).content
    ext = url.split(".")[-1]
    filename = f"images/{job_id}-{people}.{ext}"

    with open(filename, "wb") as f:
        f.write(img_data)

    # --- save result ---
    result = {"job_id": job_id, "people": people, "file": filename}

    with open(f"results/{job_id}.json", "w") as f:
        json.dump(result, f)

    print(f"[CONSUMER] Job {job_id} done!")

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    print("[CONSUMER] Loading detection model...")
    init_model()
    print("[CONSUMER] Model loaded!")
    connection = connect_with_retry()
    channel = connection.channel()
    channel.queue_declare(queue="jobs")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="jobs", on_message_callback=callback)

    print("[CONSUMER] Waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
