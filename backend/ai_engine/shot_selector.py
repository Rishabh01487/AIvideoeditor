"""Shot selection using dynamic programming"""
import logging
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)


class Scene:
    """Represents a scene for selection"""

    def __init__(self, start: float, end: float, tags: List[str], score: float = 5.0):
        self.start = start
        self.end = end
        self.duration = end - start
        self.tags = set(tags) if tags else set()
        self.score = score


def select_shots(
    scenes: List[Scene],
    target_duration: int = 60,
    include_tags: List[str] = None,
    exclude_tags: List[str] = None
) -> List[Tuple[float, float]]:
    """
    Select optimal shots using dynamic programming.

    Args:
        scenes: List of Scene objects with timing and tags
        target_duration: Target video duration in seconds
        include_tags: Only include scenes containing these tags
        exclude_tags: Exclude scenes containing these tags

    Returns:
        List of selected (start_sec, end_sec) tuples
    """
    include_tags = set(include_tags) if include_tags else set()
    exclude_tags = set(exclude_tags) if exclude_tags else set()

    # Filter scenes
    filtered_scenes = []
    for scene in scenes:
        # Check exclude tags
        if exclude_tags and scene.tags & exclude_tags:
            continue

        # Check include tags
        if include_tags and not (scene.tags & include_tags):
            continue

        filtered_scenes.append(scene)

    if not filtered_scenes:
        logger.warning("No scenes match the tag filters, using all scenes")
        filtered_scenes = scenes

    # If no target duration, use all filtered scenes (capped at 60 seconds)
    if target_duration is None or target_duration == 0:
        total_duration = sum(s.duration for s in filtered_scenes)
        target_duration = min(int(total_duration), 60)

    logger.info(f"Selecting from {len(filtered_scenes)} scenes, target duration: {target_duration}s")

    # Knapsack dynamic programming
    selected_indices = _knapsack_select(filtered_scenes, target_duration)

    # Build result
    result = []
    for idx in sorted(selected_indices):
        scene = filtered_scenes[idx]
        result.append((scene.start, scene.end))

    total_sec = sum(s.end - s.start for s in [filtered_scenes[i] for i in selected_indices])
    logger.info(f"Selected {len(result)} shots, total duration: {total_sec:.1f}s")

    return result


def _knapsack_select(scenes: List[Scene], capacity: int) -> List[int]:
    """
    0/1 knapsack algorithm to maximize score within time constraint.

    Args:
        scenes: List of Scene objects
        capacity: Maximum total duration

    Returns:
        List of selected scene indices
    """
    n = len(scenes)
    durations = [int(s.duration) for s in scenes]
    scores = [s.score for s in scenes]

    # DP table
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    # Fill DP table
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if durations[i - 1] <= w:
                dp[i][w] = max(
                    scores[i - 1] + dp[i - 1][w - durations[i - 1]],
                    dp[i - 1][w]
                )
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtrack to find selected items
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(i - 1)
            w -= durations[i - 1]

    return selected
