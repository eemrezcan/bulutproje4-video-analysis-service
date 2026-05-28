from pathlib import Path

import cv2
import numpy as np


def ensure_synthetic_video(path: Path) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return True

    width, height = 960, 540
    fps = 24
    frame_count = fps * 12
    suffix = path.suffix.lower()
    fourcc = "VP80" if suffix == ".webm" else "mp4v"
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*fourcc),
        fps,
        (width, height),
    )

    if not writer.isOpened():
        return False

    for frame_no in range(frame_count):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (33, 42, 47)

        cv2.rectangle(frame, (0, 340), (width, height), (48, 54, 58), -1)
        cv2.line(frame, (0, 405), (width, 350), (90, 96, 98), 4)
        cv2.line(frame, (0, 455), (width, 395), (90, 96, 98), 4)

        sun_x = 80 + (frame_no * 2) % width
        cv2.circle(frame, (sun_x, 75), 34, (70, 170, 230), -1)

        for idx, x in enumerate(range(90, width, 145)):
            building_height = 145 + (idx % 3) * 38
            cv2.rectangle(
                frame,
                (x, 330 - building_height),
                (x + 74, 330),
                (67, 83, 91),
                -1,
            )
            for window_y in range(330 - building_height + 18, 320, 32):
                cv2.rectangle(frame, (x + 16, window_y), (x + 30, window_y + 14), (230, 185, 85), -1)
                cv2.rectangle(frame, (x + 44, window_y), (x + 58, window_y + 14), (96, 180, 210), -1)

        for idx in range(9):
            x = int((frame_no * (4 + idx % 3) + idx * 120) % (width + 90)) - 70
            y = 388 + (idx % 3) * 34
            color = [(50, 130, 210), (210, 110, 70), (90, 175, 110)][idx % 3]
            cv2.rectangle(frame, (x, y), (x + 58, y + 24), color, -1)
            cv2.circle(frame, (x + 12, y + 25), 7, (20, 22, 24), -1)
            cv2.circle(frame, (x + 46, y + 25), 7, (20, 22, 24), -1)

        for idx in range(38):
            x = int((frame_no * (1 + idx % 4) + idx * 37) % width)
            y = 300 + ((idx * 23) % 180)
            cv2.circle(frame, (x, y), 5, (210, 220, 220), -1)
            cv2.line(frame, (x, y + 5), (x, y + 20), (185, 205, 210), 2)

        cv2.putText(
            frame,
            "Smart City Live Camera",
            (28, 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (245, 245, 245),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            f"Frame {frame_no + 1:03d}",
            (28, 84),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (190, 225, 230),
            2,
            cv2.LINE_AA,
        )
        writer.write(frame)

    writer.release()
    return path.exists() and path.stat().st_size > 0
