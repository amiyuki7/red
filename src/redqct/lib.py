from __future__ import annotations
from typing import List
import discord

Number = int | float


class Attrs:
    # Workflow of this would be:
    """
    1. The webserver requests for something, e.g. 127.0.0.1:8080/id/703204753743806585
    2. The route code in app.py  asks the bot to run a function that collects all the data for this specific user ID, and stores it into this Attrs class
    3. The instance of Attrs is then passed to code in image.py for an image to be generated, and that image is given back to the webserver
    4. The webserver sends that image back out to the user as well as a 200 OK code, and a 403 code if the ID cant be found
    i have started writing attrs below alr
    member_atributes
    """

    def __init__(self, name, tag, nick) -> None:
        self.name = name
        self.tag = tag
        self.nick = nick
        # etc


class member_atributes:
    def __init__(
        self,
        name: str,
        tag: str,
        nick: str | None,
        avatar: discord.Member.avatar,
        status: str,
        badges: List[discord.PublicUserFlags] | None,
        activity: activity_atributes | None,
    ) -> None:
        self.name = name
        self.status = status
        self.badges = badges
        self.nick = nick
        if avatar:
            self.avatar = avatar
        else:
            # There are 5 base avatars, each with a different background colour. The colour is determined based on the discriminant
            # For user name#1234 the discriminant would be 1234
            # This is explained at https://www.reddit.com/r/discordapp/comments/au6v4e/how_to_change_your_defualt_discord_avatars_colour/
            self.avatar = f"https://cdn.discordapp.com/embed/avatars/{tag % 5}.png"
        self.activity = activity


class activity_atributes:
    def __init__(
        self,
        name: str,
        activity_type: str,
        image_large: str,
        image_small: str,
        line1: str | None,
        line2: str | None,
        line3: str | None,
    ) -> None:
        self.name = name
        self.type = activity_type
        self.image_large = image_large
        self.image_small = image_small
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3


def cube(x: Number) -> Number:
    """
    Returns the cube of a number up to 3 decimal places
    """
    return round(x**3, 3)
