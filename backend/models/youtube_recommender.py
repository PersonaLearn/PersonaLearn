from typing import TypedDict


class Resource(TypedDict):
    """A resource recommended to the user."""

    video_id: str


def related_resources_from_query(query: str):
    """Get a list of related resources from a given query to search YouTube with."""
    return []  # TODO: implement this
