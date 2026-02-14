"""Video rendering using MoviePy and FFmpeg"""
import os
import logging
from typing import List, Tuple, Optional
import numpy as np
from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip,
    concatenate_videoclips, TextClip
)
from moviepy.audio.AudioFileClip import AudioFileClip
import cv2

logger = logging.getLogger(__name__)


def apply_filter(clip, filter_type: str):
    """Apply visual filter to a clip"""
    if filter_type == 'b&w':
        # Black and white
        return clip.fx(lambda gf: 0.299 * gf[:, :, 0] + 0.587 * gf[:, :, 1] + 0.114 * gf[:, :, 2])
    elif filter_type == 'sepia':
        # Sepia tone
        def sepia_filter(gf):
            img = gf.astype(float)
            sepia = np.zeros_like(img)
            sepia[:, :, 0] = 0.272 * img[:, :, 0] + 0.534 * img[:, :, 1] + 0.131 * img[:, :, 2]
            sepia[:, :, 1] = 0.349 * img[:, :, 0] + 0.686 * img[:, :, 1] + 0.168 * img[:, :, 2]
            sepia[:, :, 2] = 0.393 * img[:, :, 0] + 0.769 * img[:, :, 1] + 0.189 * img[:, :, 2]
            return np.clip(sepia, 0, 255).astype(np.uint8)
        return clip.fx(sepia_filter)
    elif filter_type == 'vintage':
        # Vintage effect (slight color shift and reduced saturation)
        def vintage_filter(gf):
            img = gf.astype(float)
            # Add yellow tint
            img[:, :, 0] *= 0.8
            img[:, :, 2] *= 1.1
            return np.clip(img, 0, 255).astype(np.uint8)
        return clip.fx(vintage_filter)
    else:
        return clip


def render_video(
    clips_info: List[Tuple[str, float, float]],  # [(file_path, start, end), ...]
    output_path: str,
    filter_type: str = 'none',
    speed: str = 'normal',
    transition_type: str = 'none',
    music_mood: str = 'none',
    text_overlays: List[dict] = None,
    duration: Optional[int] = None
) -> bool:
    """
    Render a video from selected clips.

    Args:
        clips_info: List of (file_path, start_sec, end_sec) tuples
        output_path: Path to save output video
        filter_type: Visual filter ('vintage', 'b&w', 'sepia', 'none')
        speed: Playback speed ('slow', 'normal', 'fast')
        transition_type: Transition effect ('fade', 'dissolve', 'glitch', 'none')
        music_mood: Background music mood
        text_overlays: List of text overlay specifications
        duration: Target duration in seconds

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Rendering video with {len(clips_info)} clips to {output_path}")

        # Extract clips
        clips = []
        for file_path, start, end in clips_info:
            try:
                clip = VideoFileClip(file_path).subclip(start, end)
                clips.append(clip)
            except Exception as e:
                logger.error(f"Failed to load clip {file_path}: {str(e)}")
                continue

        if not clips:
            logger.error("No clips could be loaded")
            return False

        # Apply speed
        speed_factor = {'slow': 0.5, 'normal': 1.0, 'fast': 2.0}.get(speed, 1.0)
        if speed_factor != 1.0:
            clips = [clip.speedx(speed_factor) for clip in clips]

        # Apply filters
        if filter_type != 'none':
            clips = [apply_filter(clip, filter_type) for clip in clips]

        # Concatenate with transitions
        if transition_type == 'fade':
            video = concatenate_videoclips(clips, method='chain')
        else:
            video = concatenate_videoclips(clips, method='chain')

        # Add text overlays
        if text_overlays:
            video = _add_text_overlays(video, text_overlays)

        # Handle duration adjustment
        if duration:
            current_duration = video.duration
            if current_duration < duration:
                # Loop last clip to reach target
                loops_needed = int((duration / current_duration) + 1)
                last_clip = VideoFileClip(clips_info[-1][0]).subclip(
                    clips_info[-1][1], clips_info[-1][2]
                )
                extended_clips = list(clips) + [last_clip] * (loops_needed - 1)
                video = concatenate_videoclips(extended_clips, method='chain')
                video = video.subclip(0, duration)
            elif current_duration > duration:
                video = video.subclip(0, duration)

        # Add music
        if music_mood != 'none':
            music_path = _get_music_path(music_mood)
            if music_path and os.path.exists(music_path):
                try:
                    audio = AudioFileClip(music_path)
                    # Loop music to match video duration
                    if audio.duration < video.duration:
                        loops = int(video.duration / audio.duration) + 1
                        audio = concatenate_videoclips([audio] * loops).subclip(0, video.duration)
                    else:
                        audio = audio.subclip(0, video.duration)

                    # Mix with original audio
                    if video.audio:
                        final_audio = CompositeAudioClip([video.audio.volumex(0.3), audio.volumex(0.7)])
                        video = video.set_audio(final_audio)
                    else:
                        video = video.set_audio(audio)
                except Exception as e:
                    logger.warning(f"Failed to add music: {str(e)}")

        # Write video
        video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=24,
            verbose=False,
            logger=None
        )

        logger.info(f"Video rendered successfully to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Rendering failed: {str(e)}")
        return False


def _add_text_overlays(video, overlays: List[dict]):
    """Add text overlays to video"""
    clips = [video]

    for overlay in overlays:
        text = overlay.get('text', '')
        position = overlay.get('position', 'center')
        duration = overlay.get('duration', video.duration)
        start = overlay.get('start', 0)

        txt_clip = TextClip(
            text,
            fontsize=40,
            color='white',
            font='Arial',
            method='caption',
            size=(video.w - 40, None)
        )

        # Position mapping
        pos_map = {
            'top': ('center', video.h * 0.1),
            'center': ('center', 'center'),
            'bottom': ('center', video.h * 0.9)
        }

        txt_clip = txt_clip.set_position(pos_map.get(position, 'center'))
        txt_clip = txt_clip.set_duration(duration).set_start(start)

        clips.append(txt_clip)

    return CompositeVideoClip(clips)


def _get_music_path(mood: str) -> Optional[str]:
    """Get music file path for given mood"""
    base_dir = os.path.dirname(__file__)
    music_dir = os.path.join(base_dir, 'assets')

    mood_files = {
        'upbeat': 'upbeat.mp3',
        'calm': 'calm.mp3',
        'cinematic': 'cinematic.mp3'
    }

    filename = mood_files.get(mood)
    if filename:
        filepath = os.path.join(music_dir, filename)
        if os.path.exists(filepath):
            return filepath

    return None
