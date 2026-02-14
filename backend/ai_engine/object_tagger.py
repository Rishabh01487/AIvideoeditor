"""Object tagging using YOLOv8"""
import logging
from typing import List, Dict
from pathlib import Path
import cv2
from ultralytics import YOLO

logger = logging.getLogger(__name__)

# Load YOLO model once (nano for speed)
_yolo_model = None


def get_yolo_model():
    """Get or load YOLO model"""
    global _yolo_model
    if _yolo_model is None:
        logger.info("Loading YOLOv8 nano model...")
        _yolo_model = YOLO('yolov8n.pt')
    return _yolo_model


def tag_video(video_path: str, sample_rate: int = 30) -> List[str]:
    """
    Tag objects detected in a video by sampling frames.

    Args:
        video_path: Path to the video file
        sample_rate: Sample every nth frame

    Returns:
        List of detected object tags
    """
    try:
        model = get_yolo_model()
        detected_tags = set()

        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Sample every nth frame
            if frame_count % sample_rate == 0:
                results = model(frame)
                for result in results:
                    if hasattr(result, 'names'):
                        for class_id in result.boxes.cls:
                            tag = result.names[int(class_id)]
                            detected_tags.add(tag)

            frame_count += 1

        cap.release()

        tags = list(detected_tags)
        logger.info(f"Detected {len(tags)} object types in video: {tags}")
        return tags

    except Exception as e:
        logger.error(f"Failed to tag video: {str(e)}")
        return []


def tag_image(image_path: str) -> List[str]:
    """
    Tag objects detected in an image.

    Args:
        image_path: Path to the image file

    Returns:
        List of detected object tags
    """
    try:
        model = get_yolo_model()
        detected_tags = set()

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        results = model(image)
        for result in results:
            if hasattr(result, 'names'):
                for class_id in result.boxes.cls:
                    tag = result.names[int(class_id)]
                    detected_tags.add(tag)

        tags = list(detected_tags)
        logger.info(f"Detected {len(tags)} object types in image: {tags}")
        return tags

    except Exception as e:
        logger.error(f"Failed to tag image: {str(e)}")
        return []
