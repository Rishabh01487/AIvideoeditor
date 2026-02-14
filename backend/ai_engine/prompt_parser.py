"""Prompt parsing using LLM (Ollama with Llama 3)"""
import json
import logging
import re
from typing import Dict, Optional, List
import requests
from app.config import settings

logger = logging.getLogger(__name__)


def parse_prompt_with_ollama(prompt: str) -> Dict:
    """
    Parse a natural language prompt using Ollama with Llama 3.

    Args:
        prompt: User's natural language prompt

    Returns:
        Structured JSON with editing parameters
    """
    system_prompt = """You are an expert video editor AI. Parse the user's video editing request and return a JSON object with the following fields:
    - duration: Target video duration in seconds (or null for auto)
    - filter: Visual filter to apply ('vintage', 'b&w', 'sepia', 'none')
    - speed: Playback speed ('slow', 'normal', 'fast')
    - music_mood: Background music mood ('upbeat', 'calm', 'cinematic', 'none')
    - include_tags: List of object types to include (e.g., ['person', 'car'])
    - exclude_tags: List of object types to exclude
    - transition: Transition effect ('fade', 'dissolve', 'glitch', 'none')
    - pacing: Editing pacing ('fast', 'medium', 'slow')
    - text_overlays: List of {"text": "...", "position": "top|center|bottom"}

    Return ONLY valid JSON, no other text."""

    try:
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": f"{system_prompt}\n\nUser request: {prompt}",
                "stream": False,
                "temperature": 0.7
            },
            timeout=30
        )

        if response.status_code == 200:
            response_text = response.json().get('response', '')
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                logger.info(f"Prompt parsed successfully: {parsed}")
                return _validate_parsed_prompt(parsed)
    except Exception as e:
        logger.warning(f"Ollama parsing failed: {str(e)}")

    # Fallback to rule-based parsing
    return parse_prompt_rule_based(prompt)


def parse_prompt_rule_based(prompt: str) -> Dict:
    """
    Fallback rule-based prompt parsing.

    Args:
        prompt: User's natural language prompt

    Returns:
        Structured JSON with editing parameters
    """
    prompt_lower = prompt.lower()

    # Duration detection
    duration = None
    if '30 second' in prompt_lower:
        duration = 30
    elif '1 minute' in prompt_lower:
        duration = 60
    elif '2 minute' in prompt_lower:
        duration = 120
    elif match := re.search(r'(\d+)\s*(?:second|sec|s)', prompt_lower):
        duration = int(match.group(1))

    # Filter detection
    filter_type = 'none'
    if 'vintage' in prompt_lower or 'retro' in prompt_lower:
        filter_type = 'vintage'
    elif 'black and white' in prompt_lower or 'b&w' in prompt_lower or 'monochrome' in prompt_lower:
        filter_type = 'b&w'
    elif 'sepia' in prompt_lower or 'brown' in prompt_lower:
        filter_type = 'sepia'

    # Speed detection
    speed = 'normal'
    if 'slow' in prompt_lower or 'slow motion' in prompt_lower:
        speed = 'slow'
    elif 'fast' in prompt_lower or 'speed up' in prompt_lower or '2x' in prompt_lower:
        speed = 'fast'

    # Music mood detection
    music_mood = 'none'
    if 'upbeat' in prompt_lower or 'energetic' in prompt_lower or 'fun' in prompt_lower:
        music_mood = 'upbeat'
    elif 'calm' in prompt_lower or 'relaxing' in prompt_lower or 'peaceful' in prompt_lower:
        music_mood = 'calm'
    elif 'cinematic' in prompt_lower or 'epic' in prompt_lower or 'dramatic' in prompt_lower:
        music_mood = 'cinematic'

    # Transition detection
    transition = 'none'
    if 'fade' in prompt_lower:
        transition = 'fade'
    elif 'dissolve' in prompt_lower:
        transition = 'dissolve'
    elif 'glitch' in prompt_lower:
        transition = 'glitch'

    # Pacing detection
    pacing = 'medium'
    if 'fast' in prompt_lower and 'pacing' in prompt_lower:
        pacing = 'fast'
    elif 'slow' in prompt_lower and 'pacing' in prompt_lower:
        pacing = 'slow'

    parsed = {
        'duration': duration,
        'filter': filter_type,
        'speed': speed,
        'music_mood': music_mood,
        'include_tags': [],
        'exclude_tags': [],
        'transition': transition,
        'pacing': pacing,
        'text_overlays': []
    }

    logger.info(f"Prompt parsed using rule-based engine: {parsed}")
    return parsed


def _validate_parsed_prompt(parsed: Dict) -> Dict:
    """Validate and normalize parsed prompt"""
    defaults = {
        'duration': None,
        'filter': 'none',
        'speed': 'normal',
        'music_mood': 'none',
        'include_tags': [],
        'exclude_tags': [],
        'transition': 'none',
        'pacing': 'medium',
        'text_overlays': []
    }

    # Validate each field
    if 'duration' in parsed and parsed['duration'] is not None:
        try:
            parsed['duration'] = int(parsed['duration'])
        except (ValueError, TypeError):
            parsed['duration'] = None

    for key in ['filter', 'speed', 'music_mood', 'transition', 'pacing']:
        if key in parsed:
            parsed[key] = str(parsed[key]).lower()
        else:
            parsed[key] = defaults[key]

    for key in ['include_tags', 'exclude_tags', 'text_overlays']:
        if key not in parsed or parsed[key] is None:
            parsed[key] = defaults[key]

    return parsed
