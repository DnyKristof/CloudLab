FROM python:3.11-slim


RUN pip install --no-cache-dir fastapi uvicorn opencv-python-headless python-multipart


RUN useradd -ms /bin/bash facedetector
USER facedetector


WORKDIR /home/facedetector/app


COPY src/facedetection.py .


CMD ["uvicorn", "facedetection:app", "--host", "0.0.0.0", "--port", "5000"]
