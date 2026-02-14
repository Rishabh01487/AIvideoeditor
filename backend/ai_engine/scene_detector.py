"""Scene detection using PySceneDetect"""
import logging
from typing import List, Tuple
from scenedetect import detect, AdaptiveDetector

logger = logging.getLogger(__name__)


def detect_scenes(video_path: str) -> List[Tuple[float, float]]:
    """
    Detect scene boundaries in a video.

    Args:
        video_path: Path to the video file

    Returns:
        List of (start_sec, end_sec) tuples
    """
    try:
        # Detect scenes using adaptive detector
        scenes = detect(video_path, AdaptiveDetector())

        # Convert FrameTimecode objects to seconds
        scene_intervals = []
        for i in range(len(scenes)):
            start_sec = float(scenes[i][0].get_seconds())
            end_sec = float(scenes[i][1].get_seconds()) if i + 1 < len(scenes) else start_sec

            scene_intervals.append((start_sec, end_sec))

        logger.info(f"Detected {len(scene_intervals)} scenes in {video_path}")
        return scene_intervals

    except Exception as e:
        logger.error(f"Failed to detect scenes: {str(e)}")
        # Return single full-video scene on failure
        return [(0.0, float('inf'))]
