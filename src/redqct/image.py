from pathlib import Path
from PIL import Image
from typing import Tuple


ROOT_DIR = Path(__file__).resolve().parents[2]


class Cache_:
    __slots__ = (
        "itemplate",
        "pfp_mask",
        "activity_mask",
        "status_mask",
        "status_underlay",
        "light_online",
        "light_idle",
        "light_dnd",
        "light_invis",
    )

    def __init__(self) -> None:
        self.itemplate = Image.open(f"{ROOT_DIR}/assets/redqct-empty-template-1100x600.png")
        self.pfp_mask = Image.open(f"{ROOT_DIR}/assets/mask_pfp.png")
        self.activity_mask = Image.open(f"{ROOT_DIR}/assets/mask_activity.png")
        self.status_mask = Image.open(f"{ROOT_DIR}/assets/mask_status_60.png")
        self.status_underlay = Image.open(f"{ROOT_DIR}/assets/status_underlay_69.png")

        self.light_online = Image.open(f"{ROOT_DIR}/assets/status_online.png").resize((48, 47))
        self.light_idle = Image.open(f"{ROOT_DIR}/assets/status_idle.png").resize((48, 47))
        self.light_dnd = Image.open(f"{ROOT_DIR}/assets/status_dnd.png").resize((48, 47))
        self.light_invis = Image.open(f"{ROOT_DIR}/assets/status_invis.png").resize((48, 47))


Cache = Cache_()


class Template:
    """
    An abstraction over Pillow to focus exclusively on editing the Redqct template image
    """

    def __init__(self) -> None:
        # Alpha composing the background with nothing allows support of alpha values when calling Image.paste
        self._background = Image.alpha_composite(
            Image.new("RGBA", Cache.itemplate.size), Cache.itemplate.convert("RGBA")
        )

    def draw(self, image: Image.Image, coords: Tuple[int, int]) -> None:
        self._background.paste(image, coords, image)

    def peek(self) -> None:
        self._background.show()


def masked(img: Image.Image, mask: Image.Image) -> Image.Image:
    """
    Returns a cropped image based off a mask

    img     | Original image
    mask    | Mask image
    """

    img = img.resize(mask.size)
    # Convert the mask to grayscale for better accuracy
    mask = mask.convert("L")
    assert img.size == mask.size
    return Image.composite(img, Image.new("RGBA", mask.size), mask).convert("RGBA")


def main():
    """
    For testing image manipulation code only. Run with:

    ```sh
    python src/redqct/image.py
    ```
    """
    # In production, these will be received from the discord bot
    iactivity_large = Image.open(f"{ROOT_DIR}/image-test/iactivity_large.jpg")
    iactivity_small = Image.open(f"{ROOT_DIR}/image-test/iactivity_small.png")
    pfp = Image.open(f"{ROOT_DIR}/image-test/pfp.png")

    template = Template()

    # Rich presence large/small image
    cropped_activity = masked(iactivity_large, Cache.activity_mask)
    cropped_activity_small = masked(iactivity_small, Cache.status_mask)
    template.draw(cropped_activity, (48, 356))
    template.draw(Cache.status_underlay, (177, 480))
    template.draw(cropped_activity_small, (177 + 4, 480 + 4))

    # Pfp
    cropped_pfp = masked(pfp, Cache.pfp_mask)
    template.draw(cropped_pfp, (30, 50))

    # Light
    template.draw(Cache.status_underlay, (164, 184))
    template.draw(Cache.light_dnd, (176, 196))

    template.peek()


if __name__ == "__main__":
    main()
