from moviepy.editor import VideoFileClip
import os

def extract_audio(video_path, output_audio="audio.wav"):
    audio_path = os.path.splitext(video_path)[0] + ".wav"
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec='pcm_s16le')
    return audio_path
