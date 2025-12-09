FROM python:3.7-slim

WORKDIR /app

COPY consumer/ .

COPY producer/ ./producer

COPY ssd_mobilenet_v2_coco_2018_03_29 ./ssd_mobilenet_v2_coco_2018_03_29

RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python","-u", "consumer.py"]
