from typing import TypedDict
from ..youtube import YouTube


class Resource(TypedDict):
    """A resource recommended to the user."""

    video_id: str
    title: str
    channel_title: str
    view_count: str


def related_resources_from_query(query: str, *, max_count=None) -> list[Resource]:
    """Get a list of related resources from a given query to search YouTube with.

    Return a series of youtube videos that are relevant to the query being given
    - Look at size of video (do not want to return another ocw lecture)
    - Shares
    - Audience watch ratio
    - relativeRetentionPerformance
    """
    youtube = YouTube()
    search_results = youtube.search(query, max_results=max_count)

    return [
        {
            "video_id": result["video_id"],
            "title": result["title"],
            "channel_title": result["stats"]["channel_title"]
            if result["stats"] is not None
            else None,
            "view_count": result["stats"]["view_count"]
            if result["stats"] is not None
            else None,
        }
        for result in search_results
    ]
