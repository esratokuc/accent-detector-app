
from moviepy.editor import VideoFileClip

def extract_audio(video_path, output_audio="extracted_audio.wav"):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(output_audio)
    return output_audio
