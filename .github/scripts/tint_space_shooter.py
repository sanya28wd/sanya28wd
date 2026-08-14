from __future__ import annotations

from pathlib import Path
from sys import argv

from PIL import Image, ImageSequence


def interpolate_channel(start: int, end: int, amount: float) -> int:
    return round(start + (end - start) * amount)


def pink_tint(red: int, green: int, blue: int, alpha: int) -> tuple[int, int, int, int]:
    luminance = (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255
    shadow = (13, 17, 23)
    highlight = (255, 105, 180)
    glow = (248, 187, 208)

    if luminance < 0.1:
        return shadow[0], shadow[1], shadow[2], alpha

    blend = min(1, luminance * 1.45)
    base = tuple(
        interpolate_channel(shadow[index], highlight[index], blend)
        for index in range(3)
    )
    glow_blend = max(0, (luminance - 0.65) / 0.35)
    return (
        interpolate_channel(base[0], glow[0], glow_blend),
        interpolate_channel(base[1], glow[1], glow_blend),
        interpolate_channel(base[2], glow[2], glow_blend),
        alpha,
    )


def tint_frame(frame: Image.Image) -> Image.Image:
    rgba_frame = frame.convert("RGBA")
    tinted_pixels = [pink_tint(*pixel) for pixel in rgba_frame.getdata()]
    tinted_frame = Image.new("RGBA", rgba_frame.size)
    tinted_frame.putdata(tinted_pixels)
    return tinted_frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)


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
