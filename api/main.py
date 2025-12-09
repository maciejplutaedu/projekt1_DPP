import uuid
import pika
import json
from fastapi import FastAPI, Query

app = FastAPI()

def publish_job(job):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq", credentials=pika.PlainCredentials("user","pass"))
    )
    channel = connection.channel()
    channel.queue_declare(queue="jobs")

    channel.basic_publish(
        exchange="",
        routing_key="jobs",
        body=json.dumps(job)
    )
    connection.close()


@app.get("/analyze_img")
def analyze_img(url: str = Query(...)):
    job_id = str(uuid.uuid4())

    publish_job({"id": job_id, "url": url})

    return {"job_id": job_id, "status": "queued"}


@app.get("/check")
def check(job_id: str):
    try:
        with open(f"results/{job_id}.json", "r") as f:
            return json.load(f)
    except:
        return {"job_id": job_id, "status": "pending"}
