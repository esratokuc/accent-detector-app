from moviepy.editor import VideoFileClip
import os

def extract_audio(video_path, output_audio="audio.wav"):
    try:
        clip = VideoFileClip(video_path)
        if not clip.audio:
            raise ValueError("No audio track found in video.")
        clip.audio.write_audiofile(output_audio, codec='pcm_s16le')
        return output_audio
    except Exception as e:
        print("Error extracting audio:", e)
        raise FileNotFoundError("Audio extraction failed.")
