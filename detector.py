from ultralytics import YOLO
from pydantic import BaseModel
from enum import Enum
from config import get_settings

SETTINGS = get_settings()

class PredictionType(str, Enum):
    classification = "CLS"
    object_detection = "OD"
    segmentation = "SEG"

class GeneralPrediction(BaseModel):
    pred_type: PredictionType

class Detection(GeneralPrediction):
    n_detections: int
    boxes: list[list[int]]
    labels: list[str]
    confidences: list[float]

class ObjectDetector:
    def __init__(self) -> None:
        self.model = YOLO(SETTINGS.yolo_version)

    def predict_image(self, image_array, threshold):
        results = self.model(image_array, conf=threshold)[0]
        labels = [results.names[i] for i in results.boxes.cls.tolist()]
        boxes = [[int(v) for v in box] for box in results.boxes.xyxy.tolist()]
        detection = Detection(
            pred_type=PredictionType.object_detection,
            n_detections=len(boxes),
            boxes=boxes,
            labels=labels,
            confidences=results.boxes.conf.tolist()
        )
        return detection