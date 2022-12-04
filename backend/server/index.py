import os
import logging
from typing import TypedDict
from flask import Flask, request
from backend.models.query_predictor.index import predict_query_from_transcript
from backend.models.youtube_recommender import Resource, related_resources_from_query
from backend.models.transcribe_video import transcribe_youtube_video, Transcription

# Set Up Logging

log_level = os.environ.get("LOGLEVEL", "WARNING").upper()
logging.basicConfig(level=log_level)

app = Flask(__name__)

# Response Types
class Recommendation(TypedDict):
    """A recommendation with query and related resources. Returned from the `recommend` endpoint."""

    transcript_segment: str
    query: str
    resources: list[Resource]


# Helper Methods


def trivial_extract_confusion_timestamps(comprehension_points):
    """The most trivial extraction for confusing timestamps from comprehension points.
    Filters by points with comprehension less than -0.5."""
    return [
        point["timestamp"]
        for point in comprehension_points
        if point["comprehension"] < -0.5
    ]


def get_transcript_sections(transcript: Transcription, timestamps) -> list[str]:
    """Get the transcript sections from a transcript object and a list of timestamps."""
    timestamp_buffer = 5  # seconds

    for timestamp in timestamps:
        start = timestamp - timestamp_buffer
        end = timestamp + timestamp_buffer
        yield transcript.text_from(start, end)


# API Routes
@app.route("/recommend", methods=["POST"])
def recommend_resources():
    """API Route to access recommendations from a video ID and a list of comprehension points."""
    data = request.json

    video_id: str = data["videoId"]
    comprehension_points: list[float] = data["comprehensionPoints"]

    confusing_timestamps = trivial_extract_confusion_timestamps(comprehension_points)
    transcript = transcribe_youtube_video(video_id)
    logging.debug("Video title: %s", transcript.video_title)
    transcript_segments = get_transcript_sections(transcript, confusing_timestamps)

    recommendations: list[Recommendation] = []

    logging.debug("Starting to predict queries from transcript segments")

    for transcript_segment in transcript_segments:
        logging.debug("Transcript segment: %s", transcript_segment)
        query_options = predict_query_from_transcript(
            transcript.video_title, transcript_segment
        )
        logging.debug("Query options: %s", query_options)
        query = query_options[0]
        related_resources = related_resources_from_query(query, max_count=3)

        recommendation: Recommendation = {
            "transcript_segment": transcript_segment,
            "query": query,
            "resources": related_resources,
        }

        recommendations.append(recommendation)

    logging.debug("Finished predicting queries from transcript segments")

    return recommendations


if __name__ == "__main__":
    from dotenv import load_dotenv
    import openai

    load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
    openai.api_key = os.getenv("OPENAI_API_KEY")

    app.run()
