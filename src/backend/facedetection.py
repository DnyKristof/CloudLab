from fastapi import FastAPI, File, UploadFile, Form, WebSocket
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
import asyncio
import threading
from mongodb import MongoInit, MongoDB
from pymongo.results import InsertOneResult
import json
from kafka import KafkaProducer,KafkaConsumer
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
db : MongoDB = MongoInit()

producer = KafkaProducer(
    bootstrap_servers='kafka.facedetection.svc.cluster.local:9092',  #kafka.facedetection.svc.cluster.local
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

consumer = KafkaConsumer(
    "face-detections",
    bootstrap_servers='kafka.facedetection.svc.cluster.local:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id="face-detection-group"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

async def notify_clients(message: dict):
    for ws in clients:
        try:
            await ws.send_text(json.dumps(message))
        except:
            clients.remove(ws)

def start_kafka_loop():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for msg in consumer:
            loop.run_until_complete(notify_clients(msg.value))
    except Exception as e:
        print(f"[Kafka Loop Error] {e}")


@app.get("/health")
def health_check():
    mongodb_status = db.health_check()
    if "error" in mongodb_status:
        return {"status": "error", "mongodb": mongodb_status["error"]}
    return {"status": "ok"}


@app.post("/detect_faces")
async def detect_faces(file: UploadFile = File(...), description: str = Form(""), username: str = Form("")):

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return {"error": "Invalid image"}


    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )


    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    result : InsertOneResult = db.get_collection("images").insert_one(
        {
            "description": description,
            "username": username,
            "faces": len(faces)
        }
    )
    if result.acknowledged:
        print(f"Image data inserted with id: {result.inserted_id}")
    else:
        print("Failed to insert image data")

    producer.send("face-detections", {
        "username": username,
        "description": description,
        "faces_detected": len(faces)
    })




    _, img_encoded = cv2.imencode(".jpg", image)
    return StreamingResponse(io.BytesIO(img_encoded.tobytes()), media_type="image/jpeg")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    print(f"Client connected: {websocket.client}")

    images = list(db.get_collection("images").find({}, {"_id": 0}))
    for image in images:
        try:
            await websocket.send_text(json.dumps(image))
        except:
            clients.remove(websocket)
            return
        
    try:
        while True:
            await websocket.receive_text()  
    except:
        clients.remove(websocket)

@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_kafka_loop, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("facedetection:app", host="0.0.0.0", port=5000, reload=True)
