from os import environ
from typing import TypedDict, Optional
from googleapiclient.discovery import build


class Resource(TypedDict):
    """A resource recommended to the user."""

    video_id: str
    title: str
    channel_title: str
    view_count: str


class YouTubeStats(TypedDict):
    """YouTube statistics for a given video."""

    channel_id: str
    channel_title: str
    category_id: str
    favorite_count: int
    view_count: int
    tags: str


class YouTubeResult(TypedDict):
    """A typed YouTube result dict."""

    title: str
    video_id: str
    stats: Optional[YouTubeStats]


class YouTube:
    """YouTube class to handle the YouTube v3 API instance."""

    def __init__(self, api_key: str):
        self.youtube = build("youtube", "V3", developerKey=api_key)

    def search(
        self,
        query,
        max_results=50,
        order="relevance",
    ) -> list[YouTubeResult]:
        """Search YouTube for a query with search options."""
        response = (
            self.youtube.search()  # pylint: disable=no-member
            .list(
                q=query,
                type="video",
                order=order,
                part="id,snippet",
                maxResults=max_results,
            )
            .execute()
        )

        return self.__parse_response(response)

    def get_stats(self, video_id: str) -> Optional[YouTubeStats]:
        """Get statistics for a given video ID."""
        stats_response = (
            self.youtube.videos()  # pylint: disable=no-member
            .list(part="statistics, snippet", id=video_id)
            .execute()
        )

        items = stats_response.get("items", [])
        if len(items) == 0:
            return None
        video_stats = items[0]

        return {
            "channel_id": video_stats["snippet"]["channelId"],
            "channel_title": video_stats["snippet"]["channelTitle"],
            "category_id": video_stats["snippet"]["categoryId"],
            "favorite_count": video_stats["statistics"]["favoriteCount"],
            "view_count": video_stats["statistics"]["view_count"],
        }

    def __parse_response(self, response):
        """Parse the response received from searching YouTube."""
        items = response.get("items", [])
        results: list[YouTubeResult] = []

        for item in items:
            # Filter non-video content
            if item["id"]["kind"] != "youtube#video":
                continue

            video_id: str = item["id"]["videoId"]
            title: str = item["snippet"]["title"]

            # Get stats
            stats = self.get_stats(video_id)
            if stats is None:
                print(f"Could not get statistics for video with ID: {video_id}")

            results.append(
                {
                    "title": title,
                    "video_id": video_id,
                    "stats": stats,
                }
            )

        return results


def related_resources_from_query(query: str) -> list[Resource]:
    """Get a list of related resources from a given query to search YouTube with.

    Return a series of youtube videos that are relevant to the query being given
    - Look at size of video (do not want to return another ocw lecture)
    - Shares
    - Audience watch ratio
    - relativeRetentionPerformance
    """
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube = YouTube(api_key)
    search_results = youtube.search(query)

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
