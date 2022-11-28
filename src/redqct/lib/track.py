import os
import shutil
import json
import discord
import datetime
from pathlib import Path
from typing import List
from .singleton import singleton
from .image import generate_empty_graph


# fmt: off
PRESETS = {
    "Spotify": (101, 213, 109), #65d56d
    "VALORANT": (253, 83, 98), #fd5362
    "Rocket League": (0, 143, 226), #008fe2
    "Overwatch 2": (242, 105, 28), #f2691c
    "Tom Clancy's Rainbow Six Siege": (255, 216, 0), #ffd800
    "Grand Theft Auto V": (86, 136, 53), #568835
    "Minecraft": (116, 81, 57), #745139
    "Roblox": (143, 159, 173), #8f9fad
    "Genshin Impact": (254, 232, 208), #fee8d0
    "Assassin's Creed Valhalla": (35, 153, 144), #239990
    "The Elder Scrolls V: Skyrim": (255, 255, 255), #ffffff
    "YouTube Music": (245, 2, 27), #f5021b
    "YouTube": (193, 45, 41), #c12d29
} 

PASTELS = [
    (255, 171, 171), #FFABAB
    (133, 227, 255), #85E3FF
    (255, 245, 186), #FFF5BA
    (191, 252, 198), #BFFCC6
    (197, 163, 255), #C5A3FF
    (252, 194, 255), #FCC2FF
]
# fmt: on


@singleton
class Users_:
    """
    Singleton structure that acts on a List[TrackedUser]
    """

    def __init__(self, bot: discord.Client) -> None:
        self.users: List[TrackedUser] = []
        self.bot = bot

    def load_existing(self) -> None:
        """
        Checks through `data/`, loading any currently tracked members into `self.users`
        """
        data_dir = f"{Path(__file__).resolve().parents[3]}/data"
        guild = self.bot.get_guild(911203235522543637)
        assert guild

        ids = os.listdir(data_dir)
        for id in ids:
            if os.path.isdir(f"{data_dir}/{id}"):
                # E Dorm guild ID
                if guild.get_member(int(id)):
                    # Load the member into self.users
                    with open(f"{data_dir}/{id}/utc_offset.json", "r") as f:
                        offset_data = json.load(f)

                    self.track(str(id), offset_data["h_off"], offset_data["m_off"])
                else:
                    # Member is not in the server - delete their data folder and its contents
                    shutil.rmtree(f"{data_dir}/{id}")

    def exists(self, id: int) -> bool:
        """
        Checks if an user is being currently tracked
        """
        return any(user.id == str(id) for user in self.users)

    def track(self, user: str, h_off: int, m_off: int) -> None:
        self.users.append(
            TrackedUser(
                bot=self.bot,
                id=str(user),
                utc_offset_h=h_off,
                utc_offset_m=m_off,
            )
        )

    def untrack(self, user: int) -> None:
        target_user = [u for u in self.users if u.id == str(user)][0]
        self.users.remove(target_user)
        # Delete the member's data folder and its contents
        if os.path.isdir(dir := f"{Path(__file__).resolve().parents[3]}/data/{user}"):
            shutil.rmtree(dir)

    async def update_graphs(self) -> None:
        """
        Should be called every minute by a discord bot loop
        """
        for user in self.users:
            await user.check_clear()
            await user.update_graph()


class TrackedUser:
    """
    Structure representing a member with their activity being tracked. Responsible for dealing with each member's graph IO
    """

    __slots__ = (
        "name",
        "tag",
        "id",
        "utc_offset_h",
        "utc_offset_m",
        "legend",
    )

    def __init__(self, bot: discord.Client, id: str, utc_offset_h: int, utc_offset_m: int) -> None:
        user = bot.get_user(int(id))
        self.name = user and user.name or "NULL"
        self.tag = user and user.discriminator or "NULL"
        self.id = id
        self.utc_offset_h: int = utc_offset_h
        self.utc_offset_m: int = utc_offset_m
        self.legend: List[str] = []

        print(self.utc_offset_h, self.utc_offset_m)
        self.setup_dir()

    def setup_dir(self) -> None:
        """
        Creates a new directory entry in `data/` and populates it if it doesn't already exist
        """
        root_dir = Path(__file__).resolve().parents[3]
        data_dir = f"{root_dir}/data/{self.id}"

        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)

            with open(f"{data_dir}/utc_offset.json", "w") as f:
                json.dump(
                    {
                        "h_off": self.utc_offset_h,
                        "m_off": self.utc_offset_m,
                    },
                    f,
                )

            yesterday = generate_empty_graph(
                self.name,
                self.tag,
                datetime.datetime.utcnow()
                + datetime.timedelta(hours=self.utc_offset_h - 24, minutes=self.utc_offset_m),
                self.utc_offset_h,
                self.utc_offset_m,
            )
            today = generate_empty_graph(
                self.name,
                self.tag,
                datetime.datetime.utcnow()
                + datetime.timedelta(hours=self.utc_offset_h, minutes=self.utc_offset_m),
                self.utc_offset_h,
                self.utc_offset_m,
            )

            print(yesterday)
            print(today)

            yesterday.save(f"{data_dir}/graph_yesterday.png")
            today.save(f"{data_dir}/graph_today.png")

    async def check_clear(self) -> None:
        """
        Clears the member's graph if it's midnight according to their UTC offset. Stores the cleared graph for one day as `graph_yesterday.png`
        """
        now = datetime.datetime.utcnow() + datetime.timedelta(
            hours=self.utc_offset_h, minutes=self.utc_offset_m
        )

        root_dir = Path(__file__).resolve().parents[3]
        data_dir = f"{root_dir}/data/{self.id}"

        if now.hour == 0 and now.minute == 0:
            # It's Midnight - store the graph and then reset it
            shutil.copy(f"{data_dir}/graph_today.png", f"{data_dir}/graph_yesterday.png")
            shutil.copy(
                f"{root_dir}/assets/redqct-graph-empty-template-1920x1080.png",
                f"{data_dir}/graph_today.png",
            )

    async def update_graph(self) -> None:
        """ """
        # Get the current time relative to the user's desired utc offset
        # Get the user's current activities via the bot
        # Draw a 1px line at that specific time in a specific colour depending on the activities present now
        pass
