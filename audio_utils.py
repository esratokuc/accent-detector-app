from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os

def extract_audio(video_path, output_audio="audio.wav"):
    video = VideoFileClip(video_path)
    audio_path = "temp_audio.mp3"
    video.audio.write_audiofile(audio_path)

    # Convert to WAV using pydub
    sound = AudioSegment.from_file(audio_path)
    wav_path = "converted_audio.wav"
    sound.export(wav_path, format="wav")

    os.remove(audio_path)
    return wav_path
