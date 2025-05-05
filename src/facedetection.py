from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
from mongodb import MongoInit

app = FastAPI()
db = MongoInit()


@app.get("/health")
def health_check():
    mongodb_status = db.health_check()
    if "error" in mongodb_status:
        return {"status": "error", "mongodb": mongodb_status["error"]}
    return {"status": "ok"}


@app.post("/detect_faces")
async def detect_faces(file: UploadFile = File(...)):

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


    _, img_encoded = cv2.imencode(".jpg", image)
    return StreamingResponse(io.BytesIO(img_encoded.tobytes()), media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("facedetection:app", host="0.0.0.0", port=5000, reload=False)