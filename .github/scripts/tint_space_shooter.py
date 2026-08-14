from __future__ import annotations

from pathlib import Path
from sys import argv

from PIL import Image, ImageOps, ImageSequence


def tint_frame(frame: Image.Image) -> Image.Image:
    rgba_frame = frame.convert("RGBA")
    grayscale_frame = ImageOps.grayscale(rgba_frame)
    pink_frame = ImageOps.colorize(
        grayscale_frame,
        black="#0D1117",
        white="#F8BBD0",
        mid="#FF69B4",
        blackpoint=0,
        midpoint=150,
        whitepoint=255,
    )
    pink_frame.putalpha(rgba_frame.getchannel("A"))
    return pink_frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)


def tint_animation(source_path: Path) -> None:
    if not source_path.is_file():
        raise FileNotFoundError(f"Space Shooter GIF not found: {source_path}")

    with Image.open(source_path) as source_image:
        frames = [tint_frame(frame) for frame in ImageSequence.Iterator(source_image)]
        durations = [frame.info.get("duration", 40) for frame in ImageSequence.Iterator(source_image)]

    if not frames:
        raise ValueError(f"Space Shooter GIF has no frames: {source_path}")

    frames[0].save(
        source_path,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def main(arguments: list[str]) -> None:
    if len(arguments) != 2:
        raise ValueError("Usage: tint_space_shooter.py <space-shooter.gif>")

    tint_animation(Path(arguments[1]))


if __name__ == "__main__":
    main(argv)
