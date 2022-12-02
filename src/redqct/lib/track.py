import os
import shutil
import json
from PIL import Image
import discord
import datetime
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .singleton import singleton
from .image import generate_empty_graph, extend_legend, draw_legend_entry, draw_minute


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
    "osu!": (238, 109, 166), #ee6da6
    "Assassin's Creed Valhalla": (35, 153, 144), #239990
    "The Elder Scrolls V: Skyrim": (255, 255, 255), #ffffff
    "YouTube Music": (245, 2, 27), #f5021b
    "YouTube": (193, 45, 41), #c12d29
    "Visual Studio Code": (32, 160, 241), #20a0f1
    "Neovim": (26, 172, 77), #1aac4d
    "Crunchyroll": (246, 139, 30), #f68b1e
    "Twitch": (141, 68, 249), #8d44f9
    "TikTok": (240, 28, 82), #f01c52
}
# fmt: on

with open(f"{Path(__file__).resolve().parents[3]}/distincts.json", "r") as f:
    raw: List[List[int]] = json.load(f)
    DISTINCTS = [(a[0], a[1], a[2]) for a in raw]

    print(DISTINCTS)


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

                    with open(f"{data_dir}/{id}/legend.json", "r") as f:
                        legend_data = json.load(f)

                    self.track(str(id), offset_data["h_off"], offset_data["m_off"], legend_data)
                else:
                    # Member is not in the server - delete their data folder and its contents
                    shutil.rmtree(f"{data_dir}/{id}")

        print("Load existing succeeded")

    def exists(self, id: int) -> bool:
        """
        Checks if an user is being currently tracked
        """
        return any(user.id == str(id) for user in self.users)

    def track(
        self,
        user: str,
        h_off: int,
        m_off: int,
        legend_data: Optional[Dict[str, Tuple[int, int, int]]] = None,
    ) -> None:
        self.users.append(
            TrackedUser(
                bot=self.bot,
                id=str(user),
                utc_offset_h=h_off,
                utc_offset_m=m_off,
                legend=legend_data,
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
            await user.update_graph(ctx=self)


class TrackedUser:
    """
    Structure representing a member with their activity being tracked. Responsible for dealing with each member's graph IO
    """

    __slots__ = (
        "bot",
        "name",
        "tag",
        "id",
        "utc_offset_h",
        "utc_offset_m",
        "legend",
    )

    def __init__(
        self,
        bot: discord.Client,
        id: str,
        utc_offset_h: int,
        utc_offset_m: int,
        legend: Optional[Dict[str, Tuple[int, int, int]]] = None,
    ) -> None:
        user = bot.get_user(int(id))
        self.bot = bot
        self.name = user and user.name or "NULL"
        self.tag = user and user.discriminator or "NULL"
        self.id = id
        self.utc_offset_h = utc_offset_h
        self.utc_offset_m = utc_offset_m

        self.legend = legend or dict()
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

            with open(f"{data_dir}/legend.json", "w") as f:
                json.dump({}, f)

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

            # print(yesterday)
            # print(today)

            yesterday.save(f"{data_dir}/graph_yesterday.png")
            today.save(f"{data_dir}/graph_today.png")

    def check_new_entry(self, activity_name: str) -> None:
        print(activity_name)

        if activity_name in self.legend:
            return

        assigned = False

        # Check to assign a preset colour
        if activity_name in PRESETS:
            self.legend[activity_name] = PRESETS[activity_name]
            assigned = True

        # Assign a pastel colour that hasn't been already assigned
        if not assigned:
            for colour in DISTINCTS:
                if not (colour in self.legend.values()):
                    self.legend[activity_name] = colour
                    assigned = True
                    break

        # All the pastel colours have been taken... generate a random non taken colour
        if not assigned:
            while 1:
                r = random.randrange(0, 256)
                g = random.randrange(0, 256)
                b = random.randrange(0, 256)

                if not (rgb := (r, g, b)) in self.legend.values():
                    self.legend[activity_name] = rgb
                    assigned = True
                    break

        # By now, activity_name should have a unique colour entry in self.legend
        assert assigned

        graph_path = f"{Path(__file__).resolve().parents[3]}/data/{self.id}/graph_today.png"
        graph = Image.open(graph_path)

        if len(self.legend) % 13 == 0 and len(self.legend) != 0:
            # Stitch a new 430x1080 piece to the right of the current image
            graph = extend_legend(graph)
            print("Extended graph!")

        # Calculate coords of the new legend entry to be drawn
        base_x, base_y = 1538, 210
        dx, dy = 430, 60
        entries = len(self.legend)
        vertical_pos = entries % 13
        n_slice = entries // 13
        coords = (base_x + dx * n_slice, base_y + dy * (vertical_pos - 1))

        draw_legend_entry(
            graph=graph,
            colour=self.legend[activity_name],
            text=activity_name,
            coords=coords,
        )

        graph.save(graph_path)

        data_dir = f"{Path(__file__).resolve().parents[3]}/data/{self.id}"

        with open(f"{data_dir}/legend.json", "w") as f:
            json.dump(self.legend, f)

    async def check_clear(self) -> None:
        """
        Clears the member's graph if it's midnight according to their UTC offset. Stores the cleared graph for one day as `graph_yesterday.png, and resets the legend`
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

            # Reset legend
            with open(f"{data_dir}/legend.json", "w") as f:
                json.dump({}, f)

    async def update_graph(self, ctx: Users_) -> None:
        """ """
        # Get the current time relative to the user's desired utc offset
        # Get the user's current activities via the bot
        # Draw a 1px line at that specific time in a specific colour depending on the activities present now
        guild = self.bot.get_guild(911203235522543637)
        assert guild
        member = guild.get_member(int(self.id))

        if not member:
            ctx.untrack(int(self.id))
            return

        # Member exists
        activity_names: List[str] = []

        # Spotify doesn't have a .name, so this handles that edge case
        if any(isinstance(a, discord.Spotify) for a in member.activities):
            activity_names.append("Spotify")

        # For every activity, add the name to the activity_names list if it exists
        activity_names.extend(
            [
                a.name
                for a in member.activities
                if (isinstance(a, discord.Activity) or isinstance(a, discord.Game)) and a.name
            ]
        )

        for activity_name in activity_names:
            self.check_new_entry(activity_name)

        if len(activity_names) > 0:
            # Draw a line for every minute on the graph
            graph_path = f"{Path(__file__).resolve().parents[3]}/data/{self.id}/graph_today.png"
            graph = Image.open(graph_path)

            now: datetime.datetime = datetime.datetime.utcnow() + datetime.timedelta(
                hours=self.utc_offset_h, minutes=self.utc_offset_m
            )

            x_pos = 49 + (now.hour * 60 + now.minute)

            draw_minute(graph=graph, activities=activity_names, legend=self.legend, x=x_pos)
            print(f"Drew a line to {self.name}#{self.tag}'s graph")
            graph.save(graph_path)
