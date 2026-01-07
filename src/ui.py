import tkinter as tk
import cv2, json, os
from PIL import Image, ImageTk
from src.camera import Camera
from src.timer import countdown
from src.editor import add_sticker, create_photo_strip
from src.audio import add_music_to_video

class SynellaPhotoUI:
    def __init__(self):
        self.settings = json.load(open("config/settings.json"))
        self.root = tk.Tk()
        self.root.title("🌸 SynellaPhoto 🌸")
        self.root.geometry("740x800")
        self.root.configure(bg=self.settings["theme"]["bg_color"])

        self.camera = Camera(self.settings["camera_index"])
        self.last_photo = None
        self.selected_sticker = None
        self.sticker_pos = (0, 0)

        self.canvas = tk.Canvas(self.root, width=520, height=390, bg="black")
        self.canvas.pack(pady=10)

        self.info = tk.Label(
            self.root,
            text="✨ Welcome to SynellaPhoto ✨",
            font=(self.settings["theme"]["font"], 16),
            bg=self.settings["theme"]["bg_color"]
        )
        self.info.pack()

        btn = tk.Frame(self.root, bg=self.settings["theme"]["bg_color"])
        btn.pack(pady=5)

        tk.Button(btn, text="📸 Foto", command=self.take_photo).pack(side="left", padx=5)
        tk.Button(btn, text="🎞️ Strip", command=self.take_strip).pack(side="left", padx=5)
        tk.Button(btn, text="🎥 Video", command=self.take_video).pack(side="left", padx=5)

        self.sticker_frame = tk.Frame(self.root)
        self.sticker_frame.pack(pady=5)
        self.load_stickers()

        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.drop)

        self.update_camera()

    def update_camera(self):
        if self.last_photo is None:
            frame = self.camera.get_frame()
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(frame).resize((520, 390)))
                self.canvas.delete("all")
                self.canvas.image = img
                self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.root.after(15, self.update_camera)

    def take_photo(self):
        self.last_photo = None
        countdown(
            self.root,
            self.settings["countdown"],
            lambda c: self.info.config(text=f"⏳ {c}"),
            self._photo_done
        )

    def _photo_done(self):
        self.last_photo = self.camera.take_photo(self.settings["photo_save_path"])
        self.show_image(self.last_photo)
        self.info.config(text="🐰 Pilih & drag stiker!")

    def take_strip(self):
        paths = []

        def next_pose(i=0):
            if i == 4:
                strip = create_photo_strip(paths, self.settings["photo_save_path"])
                self.show_image(strip)
                return

            countdown(
                self.root,
                self.settings["countdown"],
                lambda c: self.info.config(text=f"Pose {i+1} ⏳ {c}"),
                lambda: paths.append(self.camera.take_photo(self.settings["photo_save_path"])) or next_pose(i+1)
            )

        next_pose()

    def take_video(self):
        raw = self.camera.record_video(self.settings["video_save_path"])
        output = raw.replace(".avi", ".mp4")
        add_music_to_video(raw, "assets/music/bgm.mp3", output)
        self.info.config(text="🎉 Video booth selesai!")

    def load_stickers(self):
        for f in os.listdir("assets/stickers"):
            if f.endswith(".png"):
                tk.Button(
                    self.sticker_frame,
                    text=f.replace(".png", ""),
                    command=lambda s=f: self.select_sticker(s)
                ).pack(side="left", padx=3)

    def select_sticker(self, sticker):
        self.selected_sticker = sticker
        self.info.config(text="🖱️ Drag stikernya!")

    def drag(self, e):
        if self.selected_sticker:
            self.sticker_pos = (e.x, e.y)
            img = ImageTk.PhotoImage(
                Image.open(f"assets/stickers/{self.selected_sticker}").resize((120, 120))
            )
            self.canvas.delete("sticker")
            self.canvas.sticker_img = img
            self.canvas.create_image(e.x, e.y, image=img, tags="sticker")

    def drop(self, e):
        if self.selected_sticker and self.last_photo:
            output = self.last_photo.replace(".png", "_final.png")
            add_sticker(
                self.last_photo,
                f"assets/stickers/{self.selected_sticker}",
                self.sticker_pos,
                output
            )
            self.show_image(output)
            self.selected_sticker = None

    def show_image(self, path):
        img = ImageTk.PhotoImage(Image.open(path).resize((520, 390)))
        self.canvas.delete("all")
        self.canvas.image = img
        self.canvas.create_image(0, 0, anchor="nw", image=img)

    def run(self):
        self.root.mainloop()
        self.camera.release()
