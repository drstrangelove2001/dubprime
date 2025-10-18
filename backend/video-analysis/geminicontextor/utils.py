import cv2
from dataclasses import dataclass
from typing import List

@dataclass
class FrameChunk:
    t_starts: List[float]
    t_ends: List[float]
    images_bgr: List  # list of np.ndarray

def sample_frames(video_path: str, fps: float):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")
    native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = int(max(1, round(native_fps / fps)))
    i = 0
    while True:
        ret = cap.grab()
        if not ret:
            break
        if i % frame_interval == 0:
            ok, frame = cap.retrieve()
            if not ok:
                break
            ts = i / native_fps
            yield ts, frame
        i += 1
    cap.release()

def chunk_frames(frames_iter, batch_size: int):
    batch_ts = []
    batch_images = []
    for ts, frame in frames_iter:
        batch_ts.append((ts, ts))
        batch_images.append(frame)
        if len(batch_images) == batch_size:
            yield FrameChunk(
                t_starts=[s for s,_ in batch_ts],
                t_ends=[e for _,e in batch_ts],
                images_bgr=batch_images
            )
            batch_ts, batch_images = [], []
    if batch_images:
        yield FrameChunk(
            t_starts=[s for s,_ in batch_ts],
            t_ends=[e for _,e in batch_ts],
            images_bgr=batch_images
        )
