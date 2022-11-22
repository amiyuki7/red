from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
from typing import Tuple, List
from io import BytesIO
from fontTools.ttLib import TTFont

from discord import Status

from .lib import MemberAttrs, fetch_all


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
        "bold_30",
        "bold_25",
        "bold_20",
        "heavy_25",
        "reg_25",
        "noto_25",
        "unisans",
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

        self.bold_30 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans Bold.ttf", 30)
        self.bold_25 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans Bold.ttf", 25)
        self.bold_20 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans Bold.ttf", 20)
        self.heavy_25 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans Heavy.ttf", 25)
        self.reg_25 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans.ttf", 25)
        self.noto_25 = ImageFont.truetype(f"{ROOT_DIR}/fonts/NotoSansMonoCJK-VF.ttf", 25)

        self.unisans = TTFont(f"{ROOT_DIR}/fonts/Uni Sans.ttf")


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

    def to_editable(self) -> ImageDraw.ImageDraw:
        return ImageDraw.Draw(self._background)


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


def contains_glyph(font: TTFont, char: str) -> bool:
    """
    Checks if `font` contains (i.e. supports) a singular charcter `char`
    """
    for table in font["cmap"].tables:  # type: ignore
        if ord(char) in table.cmap.keys():
            return True
    return False


def supported_font(wanted_font: ImageFont.FreeTypeFont, line: str) -> ImageFont.FreeTypeFont:
    """
    Checks if `line` is supported by UniSans. If it is supported, return the `wanted_font`. Else, return Noto
    """
    unisans_support = all(contains_glyph(Cache.unisans, c) for c in line)
    return unisans_support and wanted_font or Cache.noto_25


async def generate_img(attrs: MemberAttrs) -> Image.Image:
    """
    Generates an image and returns it, based off a MemberAttrs instance
    """
    template = Template()
    urls: List[Tuple[str, str]] = [(attrs.avatar, "avatar")]
    avatar = None
    iactivity_large = None
    iactivity_small = None

    if attrs.activity:
        if attrs.activity.image_large != "":

            tmp = attrs.activity.image_large
            # For some reason, you get a 401 when GET-ing from here, but we can find the original URL of the asset
            if tmp.startswith("https://media.discordapp.net/external/"):
                buf = tmp.split("https")
                # This is the original url
                url = f"https:/{buf[2]}"
                urls.append((url, "image_large"))
            else:
                urls.append((attrs.activity.image_large, "image_large"))
        if attrs.activity.image_small != "":
            # Might need to recycle above code for this, but usually the small image is in the CDN. Will fix if there
            # is an issue open regarding this
            urls.append((attrs.activity.image_small, "image_small"))

    # Fetch all the images required (i.e. avatar, image_large?, image_small?)
    results: List[Tuple[bytes, str]] = await fetch_all(urls)

    # Use an identifier to check which image it really is, because an asynchronous fetch_all() doesn't return
    # everything in the same order
    for result in results:
        match result[1]:
            case "avatar":
                avatar = Image.open(BytesIO(result[0]))
            case "image_large":
                iactivity_large = Image.open(BytesIO(result[0]))
            case "image_small":
                iactivity_small = Image.open(BytesIO(result[0]))

        # Debug: Show them as they are collected
        # avatar and avatar.show()
        # iactivity_large and iactivity_large.show()
        # iactivity_small and iactivity_small.show()

    # Render avatar and light
    if avatar:
        cropped_pfp = masked(avatar, Cache.pfp_mask)
        template.draw(cropped_pfp, (30, 50))
        template.draw(Cache.status_underlay, (164, 184))

        match attrs.status:
            case Status.online:
                light = Cache.light_online
            case Status.idle:
                light = Cache.light_idle
            case Status.dnd | Status.do_not_disturb:
                light = Cache.light_dnd
            case Status.offline | Status.invisible:
                light = Cache.light_invis

        template.draw(light, (176, 196))

    # Render activity image
    if iactivity_large:
        cropped_activity = masked(iactivity_large, Cache.activity_mask)
        template.draw(cropped_activity, (48, 356))

    # Render small activity image (if it exists)
    if iactivity_small:
        cropped_activity_small = masked(iactivity_small, Cache.status_mask)
        template.draw(Cache.status_underlay, (177, 480))
        template.draw(cropped_activity_small, (177 + 4, 480 + 4))

    edit = template.to_editable()

    has_nick = bool(attrs.nick)
    username = attrs.name
    tag = attrs.tag
    # Top left coordinate of the username if there is no nickname
    username_xy = (266, 113)
    # Top left coordinate of the username if there is a nickname
    username_xy2 = (266, 73)
    nickname_xy = (266, 109)

    if has_nick:
        # Renders the name#tag and the nickname underneath
        # Render name#tag
        edit.text(username_xy2, username, fill=(255, 255, 255), font=Cache.bold_30)
        left_margin = edit.textsize(username, font=Cache.bold_30)[0]

        edit.text(
            (username_xy2[0] + left_margin, username_xy2[1]),
            f"#{tag}",
            fill=(167, 169, 172),
            font=Cache.bold_30,
        )

        # Render nickname
        edit.text(nickname_xy, f"(aka {attrs.nick})", fill=(255, 255, 255), font=Cache.bold_20)
    else:
        # Only renders the name#tag
        # Render name#tag
        edit.text(username_xy, username, fill=(255, 255, 255), font=Cache.bold_30)
        left_margin = edit.textsize(username, font=Cache.bold_30)[0]

        edit.text(
            (username_xy[0] + left_margin, username_xy[1]),
            f"#{tag}",
            fill=(167, 169, 172),
            font=Cache.bold_30,
        )

    if attrs.activity:
        # Render all the activity text
        actv = attrs.activity
        actv_type = actv.type

        match actv_type:
            case "playing":
                activity_ = "PLAYING A GAME"
            case "streaming":
                activity_ = "STREAMING SOMETHING"
            case "listening":
                activity_ = "LISTENING TO SPOTIFY"
            case "watching":
                activity_ = "WATCHING SOMETHING"
            case "custom":
                activity_ = "CUSTOM ACTIVITY"
            case "competing":
                activity_ = "COMPETING IN A GAME"
            case _:
                activity_ = "UNKNOWN ACTIVITY (BUG?)"

        edit.text((51, 317), activity_, fill=(255, 255, 255), font=Cache.heavy_25)

        edit.text(
            (253, 384),
            actv.line1,
            fill=(255, 255, 255),
            # Check if Uni Sans supports the line. If it does, use Cache.bold_25. Else, Noto will be returned
            font=supported_font(Cache.bold_25, actv.line1),
        )

        edit.text(
            (253, 414),
            actv.line2,
            fill=(255, 255, 255),
            font=supported_font(Cache.reg_25, actv.line2),
        )

        edit.text(
            (253, 444),
            actv.line3,
            fill=(255, 255, 255),
            font=supported_font(Cache.reg_25, actv.line3),
        )

        edit.text(
            (253, 474),
            actv.line4,
            fill=(255, 255, 255),
            font=supported_font(Cache.reg_25, actv.line4),
        )
    else:
        # There is no user activity
        edit.text((51, 317), "CURRENTLY NOT DOING ANYTHING", fill=(255, 255, 255), font=Cache.heavy_25)

    return template._background
