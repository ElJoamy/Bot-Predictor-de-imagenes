import io
import cv2
import os
import telegram_bot
import numpy as np
import csv
from fastapi import (
    FastAPI, 
    UploadFile, 
    File, 
    HTTPException, 
    status,
    Depends
)
from fastapi.responses import Response
from datetime import datetime
from PIL import Image
from detector import ObjectDetector, Detection
from config import get_settings
from functools import cache
from fastapi.responses import FileResponse
from threading import Thread
from typing import List


SETTINGS = get_settings()

app = FastAPI(title=SETTINGS.api_name, version=SETTINGS.revision)

object_detector = ObjectDetector()

log_file = "predictions_log.csv"

def start_telegram_bot():
    telegram_bot.bot.polling(none_stop=True)

@cache
def get_object_detector():
    print("Creating object detector...")
    return ObjectDetector()

def predict_uploadfile(predictor, file, threshold):
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No file uploaded"
        )
    file_content = file.file.read()
    if file.content_type is None or file.content_type.split("/")[0] != "image":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail="Not an image"
        )
    img_stream = io.BytesIO(file_content)
    img_obj = Image.open(img_stream)
    img_array = np.array(img_obj)

    return predictor.predict_image(img_array, threshold), img_array

def annotate_image(image_array, prediction: Detection):
    ann_color = (255, 255, 0)
    annotated_img = image_array.copy()
    for box, label, conf in zip(prediction.boxes, prediction.labels, prediction.confidences):
        cv2.rectangle(annotated_img, (box[0], box[1]), (box[2], box[3]), ann_color, 3)
        cv2.putText(
            annotated_img, 
            label, 
            (box[0], box[1] - 10), 
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            ann_color,
            2,
        )
        cv2.putText(
            annotated_img, 
            f"{conf:.1f}", 
            (box[0], box[3] - 10), 
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            ann_color,
            2,
        )
    img_pil = Image.fromarray(annotated_img)
    image_stream = io.BytesIO()
    img_pil.save(image_stream, format="JPEG")
    image_stream.seek(0)

    return image_stream

def filter_predictions(prediction: Detection, labels_to_find: List[str]) -> Detection:
    filtered_boxes = []
    filtered_labels = []
    filtered_confidences = []
    
    for box, label, confidence in zip(prediction.boxes, prediction.labels, prediction.confidences):
        if label in labels_to_find:
            filtered_boxes.append(box)
            filtered_labels.append(label)
            filtered_confidences.append(confidence)

    return Detection(
        pred_type=prediction.pred_type,
        n_detections=len(filtered_boxes),
        boxes=filtered_boxes, 
        labels=filtered_labels, 
        confidences=filtered_confidences
    )


def log_prediction_to_csv(image_name, prediction, timestamp):
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Image Name", "Timestamp", "Label", "Confidence", "Box (x1, y1, x2, y2)"])

        for box, label, confidence in zip(prediction.boxes, prediction.labels, prediction.confidences):
            writer.writerow([image_name, timestamp, label, confidence, *box])

@app.get("/status")
def get_status():
    return {"message": "Endpoint de status del servicio de detección de objetos",
            "status": "OK", 
            "api_name": SETTINGS.api_name,
            "revision": SETTINGS.revision,
            "model_version": SETTINGS.yolo_version,
            "log_level": SETTINGS.log_level
            }

@app.post("/objects")
def detect_objects(
    threshold: float = 0.5,
    file: UploadFile = File(...), 
    predictor: ObjectDetector = Depends(get_object_detector)
) -> Detection:
    results, _ = predict_uploadfile(predictor, file, threshold)
    
    return results

@app.post("/predict")
async def predict(
    file: UploadFile = File(...), 
    threshold: float = 0.5,
    predictor: ObjectDetector = Depends(get_object_detector)
) -> Response:
    results, img = predict_uploadfile(predictor, file, threshold)
    annotated_img_stream = annotate_image(img, results)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_prediction_to_csv(file.filename, results, timestamp)
    return Response(content=annotated_img_stream.read(), media_type="image/jpeg")

@app.get("/reports", responses={200: {"content": {"text/csv": {}}}})
def download_report() -> Response:
    csv_stream = io.StringIO()
    
    with open(log_file, mode='r') as file:
        content = file.read()

    csv_stream.write(content)
    csv_stream.seek(0) 

    return Response(content=csv_stream.getvalue(), media_type="text/csv")

@app.post("/choose_predict")
async def choose_predict(
    file: UploadFile = File(...), 
    threshold: float = 0.5,
    labels: List[str] = [],
    predictor: ObjectDetector = Depends(get_object_detector)
) -> Response:
    results, img = predict_uploadfile(predictor, file, threshold)
    filtered_results = filter_predictions(results, labels)

    if not filtered_results.boxes:
        return Response(content="No se ha encontrado tu petición", media_type="text/plain")

    annotated_img_stream = annotate_image(img, filtered_results)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_prediction_to_csv(file.filename, filtered_results, timestamp)
    return Response(content=annotated_img_stream.read(), media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    Thread(target=start_telegram_bot).start()
    uvicorn.run("app:app", reload=True)