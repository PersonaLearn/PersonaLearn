import os
import logging

# import torch
from appdirs import AppDirs
from pytube import YouTube as PyTube
from stable_whisper import load_model, results_to_sentence_srt


def convert_timestamp_str_to_float(timestamp: str) -> float:
    """Convert a timestamp string of the form 00:00:00,000 to a float."""
    hours, minutes, seconds = timestamp.split(":")
    seconds, milliseconds = seconds.split(",")

    return (
        int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
    )


class Phrase:  # pylint: disable=too-few-public-methods
    """A transcription phrase."""

    def __init__(self, start: float, end: float, text: str):
        self.start = start
        self.end = end
        self.text = text

    @staticmethod
    def from_string_bounds(start: str, end: str, text: str):
        """Create a Phrase from string bounds."""
        return Phrase(
            convert_timestamp_str_to_float(start),
            convert_timestamp_str_to_float(end),
            text,
        )


class Transcription:  # pylint: disable=too-few-public-methods
    """A transcription of a video made up of a list of phrases."""

    def __init__(self, video_title: str, phrases: list[Phrase]):
        self.video_title = video_title
        # PHRASES MUST BE ORDERED
        self.phrases = phrases

    def __binary_search(self, time: float) -> int:
        """Binary search for the index of a phrase given a time."""
        left = 0
        right = len(self.phrases) - 1

        while left <= right:
            mid = (left + right) // 2

            if self.phrases[mid].start <= time < self.phrases[mid].end:
                return mid

            if self.phrases[mid].start > time:
                right = mid - 1
            else:
                left = mid + 1

        return -1

    def text_from(self, start: float, end: float) -> str:
        """Extract the text from a given start and end time with binary search."""
        if start > end:
            raise ValueError("Start time must be before end time.")

        start_index = self.__binary_search(start)
        end_index = self.__binary_search(end)

        if start_index == -1 and end_index == -1:
            raise ValueError("Start and end time are not in the transcription")
        if start_index == -1:
            start_index = 0
        if end_index == -1:
            end_index = len(self.phrases)

        return " ".join(
            [phrase.text for phrase in self.phrases[start_index : end_index + 1]]
        )


# Define cache directories
dirs = AppDirs("PersonaLearn", "PersonaLearn")
cache_dir = dirs.user_cache_dir
VIDEOS_DIR = os.path.join(cache_dir, "videos")
TRANSCRIPTIONS_DIR = os.path.join(cache_dir, "transcriptions")


def audio_file_from_video_id(video_id: str):
    """Get the audio file from a video ID."""
    return os.path.join(VIDEOS_DIR, f"{video_id}.mp3")


def download_video_mp3(yt_video: PyTube, video_id: str):
    """Download a YouTube video mp3 from PyTube instance."""
    audio_file = audio_file_from_video_id(video_id)

    # Extract audio
    video = yt_video.streams.filter(only_audio=True).first()

    # Download video to videos directory
    logging.debug("Downloading video with ID %s to %s", video_id, VIDEOS_DIR)
    out_file = video.download(output_path=VIDEOS_DIR)

    # Rename to `[video_id].mp3`
    os.rename(out_file, audio_file)
    return audio_file


def transcribe_mp3_to_srt(video_id: str):
    """Transcribe an mp3 to an SRT file."""
    audio_file = audio_file_from_video_id(video_id)
    transcription_file = os.path.join(TRANSCRIPTIONS_DIR, f"{video_id}.srt")
    if os.path.exists(transcription_file):
        logging.debug(
            "Transcription with ID %s already exists in %s",
            video_id,
            TRANSCRIPTIONS_DIR,
        )
        return transcription_file

    # Load whisper model
    # device_identifier = "mps" if torch.has_mps else "cuda" if torch.has_cuda else "cpu"
    # logging.debug("Loading whisper model with device: %s", device_identifier)
    logging.debug("Loading whisper model")
    model = load_model("base")
    results = model.transcribe(audio_file, pbar=True)

    # Make transcriptions directory if it does not exist
    if not os.path.exists(TRANSCRIPTIONS_DIR):
        os.makedirs(TRANSCRIPTIONS_DIR)

    # Use stable whisper to transcribe at a sentence/phrase-level
    logging.debug("Transcribing video with ID %s to %s", video_id, TRANSCRIPTIONS_DIR)
    results_to_sentence_srt(results, transcription_file)
    return transcription_file


def load_srt(srt_file: str, video_title: str) -> Transcription:
    """Load an SRT file into a Transcription object."""
    phrases = []
    with open(srt_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().isdigit():
                start, end = f.readline().strip().split(" --> ")
                text = f.readline().strip()
                phrases.append(Phrase.from_string_bounds(start, end, text))

    return Transcription(video_title, phrases)


def transcribe_youtube_video(video_id: str) -> Transcription:
    """Generate a transcription from a YouTube video."""

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    yt_video = PyTube(video_url)

    transcription_file = os.path.join(TRANSCRIPTIONS_DIR, f"{video_id}.srt")
    if not os.path.exists(transcription_file):
        logging.debug(
            "Transcription with ID %s does not exist in %s. Downloading and transcribing it now.",
            video_id,
            TRANSCRIPTIONS_DIR,
        )
        audio_file = download_video_mp3(yt_video, video_id)
        transcription_file = transcribe_mp3_to_srt(video_id)

        # Delete audio file to save on space
        logging.debug("Transcription complete. Deleting audio file %s", audio_file)
        os.remove(audio_file)

    return load_srt(transcription_file, yt_video.title)
