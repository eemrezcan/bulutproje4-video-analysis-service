import subprocess
from pathlib import Path

import imageio_ffmpeg


def main() -> None:
    media_dir = Path("/app/app/media")
    media_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    variants = [
        ("cam_meydan_01", 12, "0x1d4ed8", "0x38bdf8", 44),
        ("cam_otogar_01", 42, "0x9a3412", "0xfb923c", 32),
        ("cam_kampus_01", 92, "0x166534", "0x86efac", 36),
        ("cam_hastane_01", 176, "0x0f766e", "0x67e8f9", 24),
        ("cam_sanayi_01", 268, "0x6b21a8", "0xc084fc", 20),
    ]

    for camera_id, hue, header_color, accent_color, crowd_size in variants:
        output = media_dir / f"synthetic_{camera_id}.webm"
        filtergraph = (
            f"hue=h={hue},"
            f"drawbox=x=0:y=0:w=iw:h=70:color={header_color}@0.95:t=fill,"
            f"drawbox=x=40:y=120:w=220:h=90:color={accent_color}@0.65:t=fill,"
            f"drawbox=x=700:y=300:w=120:h=70:color={accent_color}@0.80:t=fill,"
            f"drawbox=x=120:y=430:w={crowd_size * 6}:h=32:color=white@0.55:t=fill"
        )
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "testsrc2=duration=12:size=960x540:rate=24",
                "-vf",
                filtergraph,
                "-c:v",
                "libvpx",
                "-b:v",
                "850k",
                "-an",
                str(output),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


if __name__ == "__main__":
    main()
