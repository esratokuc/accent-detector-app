from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os

def extract_audio(video_path, output_audio="audio.wav"):
    clip = VideoFileClip(video_path)
    audio = clip.audio
    audio.write_audiofile(output_audio, logger=None)
    return output_audio
