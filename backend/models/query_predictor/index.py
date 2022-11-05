from openai import Completion
from backend.models.query_predictor import query_template

QUERY_TEMPLATER = query_template.QueryTemplate()


def predict_query_from_transcript(video_title: str, transcript: str) -> list[str]:
    """
    Predict several search queries using GPT-3 from a video title
    and a transcript of a section which was confusing.
    """
    prompt = QUERY_TEMPLATER.generate_query(video_title, transcript)
    response = Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.3,
        max_tokens=400,
        top_p=0.98,
        frequency_penalty=0.7,
        presence_penalty=0.0,
    )
    return [choice["text"].strip() for choice in response["choices"]]
