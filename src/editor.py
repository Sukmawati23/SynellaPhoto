from PIL import Image, ImageDraw
import os
from datetime import datetime

def add_sticker(photo_path, sticker_path, canvas_pos, output_path):
    photo = Image.open(photo_path).convert("RGBA")
    sticker = Image.open(sticker_path).convert("RGBA").resize((120, 120))

    scale_x = photo.width / 520
    scale_y = photo.height / 390

    x = int(canvas_pos[0] * scale_x)
    y = int(canvas_pos[1] * scale_y)

    photo.paste(sticker, (x - 60, y - 60), sticker)
    photo.save(output_path)

def create_photo_strip(photo_paths, output_dir):
    images = [Image.open(p).resize((500, 375)) for p in photo_paths]
    strip = Image.new("RGB", (500, 1600), "#FFF0F6")

    y = 20
    for img in images:
        strip.paste(img, (0, y))
        y += 390

    draw = ImageDraw.Draw(strip)
    draw.text((130, 1550), "🌸 SynellaPhoto 🌸", fill="#6B2D5C")

    os.makedirs(output_dir, exist_ok=True)
    filename = datetime.now().strftime("strip_%H%M%S.png")
    path = os.path.join(output_dir, filename)
    strip.save(path)
    return path
