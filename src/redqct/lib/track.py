from typing import List


# fmt: off
PRESETS = {
    "Spotify": (101, 213, 109), #65d56d
    "VALORANT": (253, 83, 98), #fd5362
    "Rocket League": (0, 143, 226), #008fe2
    "Overwatch 2": (242, 105, 28), #f2691c
    "Tom Clancy's Rainbow Six Siege": (255, 216, 0),  #ffd800
    "Grand Theft Auto V": (86, 136, 53), #568835
    "Minecraft": (171, 161, 159), #aba19f
    "Roblox": (219, 33, 25), #db2119
    "Genshin Impact": (254, 232, 208), #fee8d0
    "Assassin's Creed Valhalla": (35, 153, 144), #239990
    "The Elder Scrolls V: Skyrim": (255, 255, 255), #ffffff
}
# fmt: on


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
