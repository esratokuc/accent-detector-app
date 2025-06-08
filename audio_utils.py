from moviepy.editor import VideoFileClip
import os

def extract_audio(video_path, output_audio="audio.wav"):
    clip = VideoFileClip(video_path)
    if not clip.audio:
        raise ValueError("No audio track found in video.")

    output_path = os.path.join("/tmp", output_audio)
    clip.audio.write_audiofile(output_path, codec="pcm_s16le")
    return output_path
