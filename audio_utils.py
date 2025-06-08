from moviepy.editor import VideoFileClip
import os

def extract_audio(video_path, output_audio="audio.wav"):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(output_audio, codec='pcm_s16le')
    return output_audio
