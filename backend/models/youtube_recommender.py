from typing import TypedDict
from ..youtube import YouTube


class Resource(TypedDict):
    """A resource recommended to the user."""

    video_id: str
    title: str
    thumbnail_url: str
    channel_title: str
    view_count: str


def related_resources_from_query(
    query: str, *, max_count=None, filter_video_id=None
) -> list[Resource]:
    """Get a list of related resources from a given query to search YouTube with.

    Return a series of youtube videos that are relevant to the query being given
    - Look at size of video (do not want to return another ocw lecture)
    - Shares
    - Audience watch ratio
    - relativeRetentionPerformance
    """
    youtube = YouTube()

    # If asked to filter out a video ID, increase max count and filter after
    if filter_video_id is not None:
        max_count += 1

    search_results = youtube.search(query, max_results=max_count)

    if filter_video_id is not None:
        search_results = [
            result for result in search_results if result["video_id"] != filter_video_id
        ][: max_count - 1]

    return [
        {
            "video_id": result["video_id"],
            "title": result["title"],
            "thumbnail_url": result["thumbnail_url"],
            "channel_title": result["stats"]["channel_title"]
            if result["stats"] is not None
            else None,
            "view_count": result["stats"]["view_count"]
            if result["stats"] is not None
            else None,
        }
        for result in search_results
    ]
