from __future__ import annotations
from typing import Optional, List, Tuple
from discord import Status, Colour
import asyncio
import aiohttp

Number = int | float


class Users:
    def __init__(self) -> None:
        self.users: List[TrackedUser] = []

    def track(self, user: str) -> None:
        self.users.append(
            TrackedUser(
                id=user,
            )
        )

    def update_graphs(self) -> None:
        """
        Should be called every minute by a discord bot loop
        """
        for user in self.users:
            user.check_clear()
            user.update_graph()


class TrackedUser:
    def __init__(self, id: str) -> None:
        self.id = id
        self.utc_offset: int = 0
        self.img_path: str = ""

    def check_clear(self) -> None:
        """ """
        # If it's exactly midnight for the user (relative to their utc offset), clear their graph
        pass

    def update_graph(self) -> None:
        """ """
        # Get the current time relative to the user's desired utc offset
        # Get the user's current activities via the bot
        # Draw a 1px line at that specific time in a specific colour depending on the activities present now
        pass


class MemberAttrs:
    def __init__(
        self,
        name: str,
        tag: str,
        nick: Optional[str],
        status: Status,
        avatar: str,
        banner_colour: Optional[Colour],
        # badges: List[discord.PublicUserFlags] | None,
        activities: List[ActivityAttrs],
        customActivity: Optional[str],
    ) -> None:
        self.name = name
        self.tag = tag
        self.nick = nick
        self.status = status
        self.avatar = avatar
        self.banner_colour = banner_colour
        # self.badges = badges
        self.activities = activities
        self.customActivity = customActivity


class ActivityAttrs:
    def __init__(
        self,
        activity_type: str,
        image_large: str,
        image_small: str,
        line1: str,
        line2: str,
        line3: str,
        line4: str,
    ) -> None:
        self.type = activity_type
        self.image_large = image_large
        self.image_small = image_small
        self.line1 = len(line1) > 35 and line1[:50] + "..." or line1
        self.line2 = len(line2) > 35 and line2[:50] + "..." or line2
        self.line3 = len(line3) > 35 and line3[:50] + "..." or line3
        self.line4 = len(line4) > 35 and line4[:50] + "..." or line4


async def fetch_bytes(session: aiohttp.ClientSession, url: str, id: str) -> Tuple[bytes, str]:
    async with session.get(url) as response:
        # Debug
        print(response.status, response.content_type)
        bytes = await response.read()
        return (bytes, id)


async def fetch_all(pairs: List[Tuple[str, str]]) -> List[Tuple[bytes, str]]:
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[fetch_bytes(session, *pair) for pair in pairs])
        return results


def cube(x: Number) -> Number:
    """
    Returns the cube of a number up to 3 decimal places
    """
    return round(x**3, 3)
