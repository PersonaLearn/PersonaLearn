from typing import TypedDict
from flask import Flask, request
from backend.models.query_predictor.index import predict_query_from_transcript
from backend.models.youtube_recommender import Resource, related_resources_from_query

app = Flask(__name__)

# Response Types
class Recommendation(TypedDict):
    """A recommendation containing the query and related resources. Returned from the `recommend` endpoint."""

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


def get_transcript_sections(transcript, timestamps):
    """Get the transcript sections from a transcript object and a list of timestamps."""
    return []  # TODO: implement this


# API Routes
@app.route("/recommend", method=["POST"])
def recommend_resources():
    """API Route to access recommendations from a video ID and a list of comprehension points."""
    data = request.json

    video_id: str = data["videoId"]
    comprehension_points: list[float] = data["comprehensionPoints"]

    confusing_timestamps = trivial_extract_confusion_timestamps(comprehension_points)
    video_title, transcript = None, None  # Get youtube title and transcript
    transcript_segments = get_transcript_sections(transcript, confusing_timestamps)

    recommendations: list[Recommendation] = []

    for transcript_segment in transcript_segments:
        query = predict_query_from_transcript(video_title, transcript_segment)
        related_resources = related_resources_from_query(query)

        recommendation: Recommendation = {
            "query": query,
            "resources": related_resources,
        }

        recommendations.append(recommendation)

    return recommendations
