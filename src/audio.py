from moviepy.editor import VideoFileClip, AudioFileClip
import os

def add_music_to_video(video_path, music_path, output_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(music_path).subclip(0, video.duration)
    final = video.set_audio(audio)

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )
