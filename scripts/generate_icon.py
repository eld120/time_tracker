from pathlib import Path

from PIL import Image, ImageDraw


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    assets = root / "assets"
    assets.mkdir(exist_ok=True)

    size = 512
    image = Image.new("RGBA", (size, size), (245, 239, 228, 255))
    draw = ImageDraw.Draw(image)

    draw.ellipse((56, 56, 456, 456), fill=(29, 78, 137, 255))
    draw.ellipse((96, 96, 416, 416), fill=(250, 248, 242, 255))

    draw.ellipse((244, 132, 268, 156), fill=(29, 78, 137, 255))
    draw.line((256, 144, 256, 256), fill=(29, 78, 137, 255), width=18)
    draw.line((256, 256, 334, 300), fill=(190, 88, 54, 255), width=18)

    image.save(assets / "icon.png")
    image.save(assets / "icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])


if __name__ == "__main__":
    main()
