from typing import List


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
