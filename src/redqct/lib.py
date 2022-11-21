from __future__ import annotations
from typing import Optional
from discord import Status

Number = int | float


class MemberAttrs:
    def __init__(
        self,
        name: str,
        tag: str,
        nick: Optional[str],
        status: Status,
        avatar: str,
        # badges: List[discord.PublicUserFlags] | None,
        activity: Optional[ActivityAttrs],
    ) -> None:
        self.name = name
        self.tag = tag
        self.nick = nick
        self.status = status
        self.avatar = avatar
        # self.badges = badges
        self.activity = activity


class ActivityAttrs:
    def __init__(
        self,
        # name: str,
        activity_type: str,
        image_large: str,
        image_small: str,
        line1: str,
        line2: str,
        line3: str,
        line4: str,
    ) -> None:
        # self.name = name
        self.type = activity_type
        self.image_large = image_large
        self.image_small = image_small
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        self.line4 = line4


def cube(x: Number) -> Number:
    """
    Returns the cube of a number up to 3 decimal places
    """
    return round(x**3, 3)
