import tkinter as tk
import cv2, json, os
from PIL import Image, ImageTk
from src.camera import Camera
from src.timer import countdown
from src.editor import add_sticker, create_photo_strip
from src.audio import add_music_to_video

# =========================
# 🎀 Cute Button
# =========================
def cute_button(parent, text, command, bg, fg="#ffffff"):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Comic Sans MS", 12, "bold"),
        bg=bg,
        fg=fg,
        activebackground="#FFC1DC",
        activeforeground="#6B2D5C",
        relief="flat",
        bd=0,
        padx=14,
        pady=6,
        cursor="hand2"
    )

# =========================
# 🌸 Main UI
# =========================
class SynellaPhotoUI:
    def __init__(self):
        self.settings = json.load(open("config/settings.json"))
        self.moods = self.settings["moods"]
        self.current_mood = "Cute"

        # Grid settings
        self.strip_count = 4

        # Window
        self.root = tk.Tk()
        self.root.title("🌸 SynellaPhoto 🌸")
        self.root.geometry("760x900")
        self.root.resizable(False, False)

        # Camera
        self.camera = Camera(self.settings["camera_index"])
        self.last_photo = None
        self.selected_sticker = None
        self.sticker_pos = (0, 0)

        # =========================
        # 📷 Camera Canvas
        # =========================
        self.canvas = tk.Canvas(
            self.root,
            width=520,
            height=390,
            bg="black",
            highlightthickness=4
        )
        self.canvas.pack(pady=10)

        # =========================
        # 💬 Info
        # =========================
        self.info = tk.Label(
            self.root,
            font=("Comic Sans MS", 15, "bold"),
            fg="#6B2D5C"
        )
        self.info.pack(pady=6)

        # =========================
        # 🎛️ Main Buttons
        # =========================
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(pady=6)

        cute_button(self.btn_frame, "📸 Foto", self.take_photo, "#FF8CC6").pack(side="left", padx=4)
        cute_button(self.btn_frame, "🎞️ Strip", self.take_strip, "#FFB6D9").pack(side="left", padx=4)
        cute_button(self.btn_frame, "🎥 Video", self.take_video, "#FFA6C9").pack(side="left", padx=4)

        # =========================
        # 🌈 Mood Selector
        # =========================
        self.mood_frame = tk.Frame(self.root)
        self.mood_frame.pack(pady=6)

        cute_button(self.mood_frame, "💖 Cute", lambda: self.set_mood("Cute"), "#FFB6D9").pack(side="left", padx=4)
        cute_button(self.mood_frame, "😎 Cool", lambda: self.set_mood("Cool"), "#AFCBFF").pack(side="left", padx=4)
        cute_button(self.mood_frame, "🤣 Funny", lambda: self.set_mood("Funny"), "#FFE082").pack(side="left", padx=4)

        # =========================
        # 🧮 Grid Selector
        # =========================
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=6)

        tk.Label(
            self.grid_frame,
            text="📐 Grid:",
            font=("Comic Sans MS", 12, "bold")
        ).pack(side="left", padx=4)

        cute_button(self.grid_frame, "2", lambda: self.set_grid(2), "#E1BEE7").pack(side="left", padx=3)
        cute_button(self.grid_frame, "4", lambda: self.set_grid(4), "#CE93D8").pack(side="left", padx=3)
        cute_button(self.grid_frame, "6", lambda: self.set_grid(6), "#BA68C8").pack(side="left", padx=3)

        self.custom_grid = tk.Entry(
            self.grid_frame,
            width=4,
            font=("Comic Sans MS", 12)
        )
        self.custom_grid.pack(side="left", padx=4)

        cute_button(
            self.grid_frame,
            "OK",
            self.apply_custom_grid,
            "#9575CD"
        ).pack(side="left", padx=4)

        # =========================
        # 🧸 Stickers
        # =========================
        self.sticker_frame = tk.Frame(self.root)
        self.sticker_frame.pack(pady=8)
        self.load_stickers()

        # Events
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.drop)

        # Default mood
        self.set_mood("Cute")

        # Start camera
        self.update_camera()

    # =========================
    # 🌈 Mood
    # =========================
    def set_mood(self, mood):
        cfg = self.moods[mood]
        self.current_mood = mood

        self.root.configure(bg=cfg["bg"])
        self.canvas.configure(highlightbackground=cfg["bg"])
        self.info.configure(text=cfg["text"], bg=cfg["bg"])

        for frame in [
            self.btn_frame, self.mood_frame,
            self.grid_frame, self.sticker_frame
        ]:
            frame.configure(bg=cfg["bg"])

    # =========================
    # 🧮 Grid
    # =========================
    def set_grid(self, count):
        self.strip_count = count
        self.info.config(text=f"📐 Grid {count} foto dipilih!")

    def apply_custom_grid(self):
        try:
            val = int(self.custom_grid.get())
            if val > 0:
                self.set_grid(val)
        except:
            pass

    # =========================
    # 🎥 Camera Preview
    # =========================
    def update_camera(self):
        if self.last_photo is None:
            frame = self.camera.get_frame()
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(
                    Image.fromarray(frame).resize((520, 390))
                )
                self.canvas.delete("all")
                self.canvas.image = img
                self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.root.after(30, self.update_camera)

    # =========================
    # 📸 Photo
    # =========================
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
        self.info.config(text="💖 Drag sticker ke foto!")

    # =========================
    # 🎞️ Strip
    # =========================
    def take_strip(self):
        paths = []

        def next_pose(i=0):
            if i == self.strip_count:
                strip = create_photo_strip(paths, self.settings["photo_save_path"])
                self.show_image(strip)
                self.info.config(text="🎉 Photo strip selesai!")
                return

            countdown(
                self.root,
                self.settings["countdown"],
                lambda c: self.info.config(text=f"Pose {i+1}/{self.strip_count} ⏳ {c}"),
                lambda: paths.append(
                    self.camera.take_photo(self.settings["photo_save_path"])
                ) or next_pose(i + 1)
            )

        next_pose()

    # =========================
    # 🎥 Video
    # =========================
    def take_video(self):
        self.info.config(text="🎬 Recording...")
        raw = self.camera.record_video(self.settings["video_save_path"])
        output = raw.replace(".avi", ".mp4")
        add_music_to_video(raw, "assets/music/bgm.mp3", output)
        self.info.config(text="🎉 Video selesai!")

    # =========================
    # 🧸 Stickers
    # =========================
    def load_stickers(self):
        for f in os.listdir("assets/stickers"):
            if f.endswith(".png"):
                cute_button(
                    self.sticker_frame,
                    f"🧸 {f.replace('.png','')}",
                    lambda s=f: self.select_sticker(s),
                    "#FFD1E8",
                    "#6B2D5C"
                ).pack(side="left", padx=4)

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
            self.info.config(text="✨ Sticker terpasang!")

    # =========================
    # 🖼️ Show Image
    # =========================
    def show_image(self, path):
        img = ImageTk.PhotoImage(
            Image.open(path).resize((520, 390))
        )
        self.canvas.delete("all")
        self.canvas.image = img
        self.canvas.create_image(0, 0, anchor="nw", image=img)

    # =========================
    # 🚀 Run
    # =========================
    def run(self):
        self.root.mainloop()
        self.camera.release()
