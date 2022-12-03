from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
from typing import Tuple, List, Optional, Dict
from io import BytesIO
from fontTools.ttLib import TTFont

from discord import Status, Colour

from . import MemberAttrs
from .http import fetch_all


ROOT_DIR = Path(__file__).resolve().parents[3]


class Cache_:
    __slots__ = (
        # "itemplate",
        "member_template",
        "banner_template",
        "custom_activity_template",
        "dummy_activity_template",
        "activity_template",
        "graph_template",
        "pfp_mask",
        "activity_mask",
        "status_mask",
        "status_underlay",
        "light_online",
        "light_idle",
        "light_dnd",
        "light_invis",
        "bold_40",
        "bold_30",
        "bold_25",
        "bold_20",
        "heavy_25",
        "reg_25",
        "noto_40",
        "noto_30",
        "noto_20",
        "noto_25",
        "noto_30",
        "unisans",
    )

    def __init__(self) -> None:
        # self.itemplate = Image.open(f"{ROOT_DIR}/assets/redqct-empty-template-1100x600.png")
        # fmt: off
        self.member_template = Image.open(f"{ROOT_DIR}/assets/redqct-empty-template-member-1100x600.png")
        self.banner_template = Image.open(f"{ROOT_DIR}/assets/redqct-empty-template-banner-1100x150.png")
        self.custom_activity_template = Image.open(f"{ROOT_DIR}/assets/redqct-empty-template-custom-status-1100x100.png")
        self.dummy_activity_template = Image.open(f"{ROOT_DIR}/assets/redqct-empty-template-dummy-1100x335.png")
        self.activity_template = Image.open(f"{ROOT_DIR}/assets/redqct-empty-template-activity-1100x335.png")
        self.graph_template = Image.open(f"{ROOT_DIR}/assets/redqct-graph-empty-template-1920x1080.png")
        # fmt: on
        self.pfp_mask = Image.open(f"{ROOT_DIR}/assets/mask_pfp.png")
        self.activity_mask = Image.open(f"{ROOT_DIR}/assets/mask_activity.png")
        self.status_mask = Image.open(f"{ROOT_DIR}/assets/mask_status_60.png")
        self.status_underlay = Image.open(f"{ROOT_DIR}/assets/status_underlay_69.png")

        self.light_online = Image.open(f"{ROOT_DIR}/assets/status_online.png").resize((48, 47))
        self.light_idle = Image.open(f"{ROOT_DIR}/assets/status_idle.png").resize((48, 47))
        self.light_dnd = Image.open(f"{ROOT_DIR}/assets/status_dnd.png").resize((48, 47))
        self.light_invis = Image.open(f"{ROOT_DIR}/assets/status_invis.png").resize((48, 47))

        self.bold_40 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans Bold.ttf", 40)
        self.bold_30 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans Bold.ttf", 30)
        self.bold_25 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans Bold.ttf", 25)
        self.bold_20 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans Bold.ttf", 20)
        self.heavy_25 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans Heavy.ttf", 25)
        self.reg_25 = ImageFont.truetype(f"{ROOT_DIR}/fonts/Uni Sans.ttf", 25)
        self.noto_40 = ImageFont.truetype(f"{ROOT_DIR}/fonts/NotoSansMonoCJK-VF.ttf", 40)
        self.noto_30 = ImageFont.truetype(f"{ROOT_DIR}/fonts/NotoSansMonoCJK-VF.ttf", 30)
        self.noto_20 = ImageFont.truetype(f"{ROOT_DIR}/fonts/NotoSansMonoCJK-VF.ttf", 20)
        self.noto_25 = ImageFont.truetype(f"{ROOT_DIR}/fonts/NotoSansMonoCJK-VF.ttf", 25)
        self.noto_30 = ImageFont.truetype(f"{ROOT_DIR}/fonts/NotoSansMonoCJK-VF.ttf", 30)

        self.unisans = TTFont(f"{ROOT_DIR}/fonts/Uni Sans.ttf")


Cache = Cache_()


class Template:
    """
    An abstraction over Pillow to focus exclusively on editing the Redqct template image
    """

    def __init__(self, template: Image.Image) -> None:
        # Alpha composing the background with nothing allows support of alpha values when calling Image.paste
        self._background = Image.alpha_composite(Image.new("RGBA", template.size), template.convert("RGBA"))

    def draw(self, image: Image.Image, coords: Tuple[int, int]) -> None:
        self._background.paste(image, coords, image)

    def peek(self) -> None:
        self._background.show()

    def to_editable(self) -> ImageDraw.ImageDraw:
        return ImageDraw.Draw(self._background)


class MemberTemplate(Template):
    def __init__(self) -> None:
        super().__init__(Cache.member_template)


class CustomActivityTemplate(Template):
    def __init__(self) -> None:
        super().__init__(Cache.custom_activity_template)


class ActivityTemplate(Template):
    def __init__(self, dummy: bool) -> None:
        if dummy:
            super().__init__(Cache.dummy_activity_template)
        else:
            super().__init__(Cache.activity_template)


class GraphTemplate(Template):
    def __init__(self) -> None:
        super().__init__(Cache.graph_template)


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


def draw_text(
    interface: ImageDraw.ImageDraw,
    line: str,
    colour: Tuple[int, int, int],
    start: Tuple[int, int],
    wanted_font: ImageFont.FreeTypeFont,
    fallback: ImageFont.FreeTypeFont,
) -> int:
    """
    Renders a line of text, in different fonts if necessary

    interface   | a pillow `ImageDraw` object pointing to a pillow `Image`
    line        | line of text to be rendered
    start       | top left corner of the text (x, y)
    wanted_font | desired font for each character to be rendered in
    fallback    | Preferably a type of "Noto" font to use if Uni Sans doesn't work

    Returns the total width of the rendered text
    """
    can_unisans: List[bool] = [contains_glyph(Cache.unisans, char) for char in line]
    x, y = start
    net_offset: int = 0

    for i, char in enumerate(line):
        # If the character is supported by Unisans, use the wanted font. Else, use Noto
        font = [fallback, wanted_font][can_unisans[i]]
        # Render the individual character. If the font is a fallback Noto font, translate the y value up 4px for alignment
        interface.text(
            (x + net_offset, font == fallback and y - 4 or y),
            char,
            fill=colour,
            font=font,
        )
        # Calculate the width of the character, add to offset
        net_offset += interface.textsize(char, font=font)[0]

    return net_offset


def generate_member(
    name: str,
    tag: str,
    nick: Optional[str],
    status: Status,
    avatar: Image.Image,
    banner_colour: Optional[Colour],
) -> Image.Image:
    """
    Generates the member piece of the overall image using a template
    """
    template = MemberTemplate()
    if banner_colour:
        rgb_banner_template = Cache.banner_template.convert("RGBA")
        for y in range(rgb_banner_template.height):
            for x in range(rgb_banner_template.width):
                if rgb_banner_template.getpixel((x, y)) != (0, 0, 0, 0):
                    rgb_banner_template.putpixel(
                        (x, y), (banner_colour.r, banner_colour.g, banner_colour.b, 255)
                    )
        template.draw(rgb_banner_template, (0, 0))
    # Render avatar and light
    cropped_pfp = masked(avatar, Cache.pfp_mask)
    template.draw(cropped_pfp, (30, 50))
    template.draw(Cache.status_underlay, (164, 184))

    match status:
        case Status.online:
            light = Cache.light_online
        case Status.idle:
            light = Cache.light_idle
        case Status.dnd | Status.do_not_disturb:
            light = Cache.light_dnd
        case Status.offline | Status.invisible:
            light = Cache.light_invis

    template.draw(light, (176, 196))

    edit = template.to_editable()
    username_xy = (266, 113)
    username_xy2 = (266, 73)
    nickname_xy = (266, 109)

    if nick:
        # Render name#tag
        offset = draw_text(
            edit,
            name,
            (255, 255, 255),
            username_xy2,
            Cache.bold_30,
            Cache.noto_30,
        )

        draw_text(
            edit,
            f"#{tag}",
            (167, 169, 172),
            (username_xy2[0] + offset, username_xy2[1]),
            Cache.bold_30,
            Cache.noto_30,
        )

        # Render nickname
        draw_text(
            edit,
            f"(aka {nick})",
            (255, 255, 255),
            nickname_xy,
            Cache.bold_20,
            Cache.noto_20,
        )
    else:
        # Render only the name#tag

        offset = draw_text(
            edit,
            name,
            (255, 255, 255),
            username_xy,
            Cache.bold_30,
            Cache.noto_30,
        )

        draw_text(
            edit,
            f"#{tag}",
            (167, 169, 172),
            (username_xy[0] + offset, username_xy[1]),
            Cache.bold_30,
            Cache.noto_30,
        )

    return template._background


def generate_custom_status(line: Optional[str]) -> Image.Image:
    """
    Generates the custom status piece of the overall image using a template
    """
    template = CustomActivityTemplate()

    edit = template.to_editable()

    if line:
        draw_text(
            edit,
            line,
            (255, 255, 255),
            (50, 38),
            Cache.heavy_25,
            Cache.noto_25,
        )

    return template._background


def generate_activity(
    image_large: Optional[Image.Image],
    image_small: Optional[Image.Image],
    atype: str,
    line1: str,
    line2: str,
    line3: str,
    line4: str,
    **kwargs,
) -> Image.Image:
    """
    Generates an activity piece of the overall image using a template

    kwargs:
    `dummy`: bool   | When set to `True`, returns an empty activity piece
    """
    if kwargs.get("dummy"):
        template = ActivityTemplate(dummy=True)
        edit = template.to_editable()
        edit.text(
            (51, 55),
            "CURRENTLY NOT DOING ANYTHING",
            fill=(255, 255, 255),
            font=Cache.heavy_25,
        )
        return template._background
    else:
        template = ActivityTemplate(dummy=False)

    # Render activity image
    if image_large:
        cropped_image = masked(image_large, Cache.activity_mask)
        template.draw(cropped_image, (48, 91))

    if image_small:
        cropped_image_small = masked(image_small, Cache.status_mask)
        template.draw(Cache.status_underlay, (177, 215))
        template.draw(cropped_image_small, (177 + 4, 215 + 4))

    edit = template.to_editable()

    # Render all the activity text

    match atype:
        case "playing":
            activity = "PLAYING A GAME"
        case "streaming":
            activity = "STREAMING SOMETHING"
        case "listening":
            activity = "LISTENING TO SPOTIFY"
        case "watching":
            activity = "WATCHING SOMETHING"
        case "custom":
            activity = "CUSTOM ACTIVITY"
        case "competing":
            activity = "COMPETING IN A GAME"
        case _:
            activity = "UNKNOWN ACTIVITY (BUG?)"

    edit.text((51, 55), activity, fill=(255, 255, 255), font=Cache.heavy_25)

    draw_text(edit, line1, (255, 255, 255), (253, 128), Cache.bold_25, Cache.noto_25)
    draw_text(edit, line2, (255, 255, 255), (253, 158), Cache.reg_25, Cache.noto_25)
    draw_text(edit, line3, (255, 255, 255), (253, 188), Cache.reg_25, Cache.noto_25)
    draw_text(edit, line4, (255, 255, 255), (253, 218), Cache.reg_25, Cache.noto_25)

    return template._background


def stitch(pieces: List[Image.Image]) -> Image.Image:
    """
    Takes a list of pieces and "stitches" them together in order vertically, returning the composed image
    """
    total_height = sum([piece.height for piece in pieces])
    background = Image.new("RGBA", (1100, total_height), (255, 255, 255, 255))
    y_offset = 0
    for piece in pieces:
        background.paste(piece, (0, y_offset))
        y_offset += piece.height

    return background


async def generate_img(attrs: MemberAttrs) -> Image.Image:
    """
    Generates an image and returns it, based off a MemberAttrs instance
    """
    urls: List[Tuple[str, str]] = [(attrs.avatar, "avatar")]

    for idx, activity in enumerate(attrs.activities):
        if activity.image_large != "":
            tmp = activity.image_large
            # For some reason, a 401 is returned when rawly fetching from this endpoint
            # Instead, find the original URL and fetch from there
            if tmp.startswith("https://media.discordapp.net/external/"):
                buf = tmp.split("https")
                url = f"https:/{buf[2]}"
                urls.append((url, f"image_large{idx}"))
            else:
                urls.append((activity.image_large, f"image_large{idx}"))

        if activity.image_small != "":
            tmp = activity.image_small
            if tmp.startswith("https://media.discordapp.net/external/"):
                buf = tmp.split("https")
                url = f"https:/{buf[2]}"
                urls.append((url, f"image_small{idx}"))
            else:
                urls.append((activity.image_small, f"image_small{idx}"))

    results: List[Tuple[bytes, str]] = await fetch_all(urls)

    # Goes through all the results and finds the avatar image by locating its corresponding identifier "avatar"
    avatar_bytes = [result[0] for result in results if result[1] == "avatar"][0]
    avatar_png = Image.open(BytesIO(avatar_bytes))

    image_groups: List[List[Optional[Image.Image]]] = [[None, None] for _ in range(len(attrs.activities))]

    # Pairs all the activity images so that this structure is formed:
    # [(large0, small0), (large1, small1), (large2, small2), ... (largen, smalln)]
    for result in results:
        img_id = result[1]
        idx = img_id[-1]
        img_type = img_id[:-1]

        if img_type == "image_large":
            image_groups[int(idx)][0] = Image.open(BytesIO(result[0]))
        elif img_type == "image_small":
            image_groups[int(idx)][1] = Image.open(BytesIO(result[0]))

    member_piece = generate_member(
        attrs.name, attrs.tag, attrs.nick, attrs.status, avatar_png, attrs.banner_colour
    )

    activity_pieces = [
        generate_activity(
            image_groups[idx][0],
            image_groups[idx][1],
            activity.type,
            activity.line1,
            activity.line2,
            activity.line3,
            activity.line4,
        )
        for idx, activity in enumerate(attrs.activities)
    ]

    # Create a dummy piece if no activity pieces were generated
    if len(activity_pieces) == 0:
        activity_pieces.append(generate_activity(None, None, "", "", "", "", "", dummy=True))

    return (
        attrs.customActivity is not None
        and stitch(
            [
                member_piece,
                generate_custom_status(attrs.customActivity),
                *activity_pieces,
            ]
        )
        or stitch([member_piece, *activity_pieces])
    )


def generate_empty_graph(name: str, tag: str, date: datetime, h_off: int, m_off: int) -> Image.Image:
    """
    Fills out a graph template with the user's name, tag, day and timezone
    """
    template = GraphTemplate()
    edit = template.to_editable()

    match date.month:
        case 1:
            mo = "January"
        case 2:
            mo = "February"
        case 3:
            mo = "March"
        case 4:
            mo = "April"
        case 5:
            mo = "May"
        case 6:
            mo = "June"
        case 7:
            mo = "July"
        case 8:
            mo = "August"
        case 9:
            mo = "September"
        case 10:
            mo = "October"
        case 11:
            mo = "November"
        case 12:
            mo = "December"
        case _:
            # Won't reach this exhaustive case but pyright wants it
            mo = ""

    match (h_off, m_off):
        case (0, 0):
            timezone = "UTC"
        case (h, m) if h == 0 and m > 0:
            timezone = f"UTC + 0:{m < 10 and f'0{m}' or m}"
        case (h, m) if h == 0 and m < 0:
            timezone = f"UTC - 0:{(m := abs(m)) < 10 and f'0{m}' or m}"
        case (h, m) if h < 0 and m < 0:
            timezone = f"UTC - {abs(h)}:{(m := abs(m)) < 10 and f'0{m}' or m}"
        case (h, m) if h < 0 and m == 0:
            timezone = f"UTC - {abs(h)}"
        case (h, m) if h > 0 and m > 0:
            timezone = f"UTC + {h}:{m < 10 and f'0{m}' or m}"
        case (h, m) if h > 0 and m == 0:
            timezone = f"UTC + {h}"
        case _:
            # Won't reach this exhaustive case but pyright wants it
            timezone = ""

    name_offset = draw_text(edit, name, (255, 255, 255), (46, 45), Cache.bold_40, Cache.noto_40)
    tag_offset = draw_text(
        edit, f"#{tag}", (167, 169, 172), (46 + name_offset, 45), Cache.bold_40, Cache.noto_40
    )
    draw_text(edit, "'s", (255, 255, 255), (46 + name_offset + tag_offset, 45), Cache.bold_40, Cache.noto_40)
    draw_text(
        edit,
        f"Activity Graph ({date.day} {mo} {date.year} / {timezone})",
        (255, 255, 255),
        (46, 105),
        Cache.bold_40,
        Cache.noto_40,
    )

    return template._background


def extend_legend(graph: Image.Image) -> Image.Image:
    """
    Stitches a 430x1080 piece to the right of the graph, providing space for a larger legend
    """
    extension = Image.new("RGBA", (430, 1080), (41, 43, 47))

    assert graph.height == extension.height == 1080

    result = Image.new(
        "RGBA",
        (graph.width + extension.width, 1080),
        (255, 255, 255, 255),
    )

    result.paste(graph, (0, 0))
    result.paste(extension, (graph.width, 0))

    return result


def draw_legend_entry(
    graph: Image.Image, colour: Tuple[int, int, int], text: str, coords: Tuple[int, int]
) -> None:
    """
    Draws a new legend entry to an existing graph by mutating it
    """
    dummy = Image.new("RGBA", (0, 0))
    dummy_interface = ImageDraw.Draw(dummy)
    cut = False

    while 1:
        # Cuts down the text until its 335px in width or less
        # TODO: Make this more efficient and smart by cutting down more or less characters at a time
        width = draw_text(dummy_interface, text, (255, 255, 255), (0, 0), Cache.bold_30, Cache.noto_30)

        if width > 335 and not cut:
            # Replace the last character with a Unicode ellipses. This can only be done once.
            text = text[:-1] + "…"
            cut = True
            continue
        elif width > 335 and cut:
            # Remove letters before the ellipses
            text = text[:-2] + text[-1]
        elif width <= 335:
            break

    square = Image.new("RGBA", (30, 30), colour)
    graph.paste(square, coords)
    interface = ImageDraw.Draw(graph)
    x, y = coords
    draw_text(interface, text, (255, 255, 255), (x + 44, y - 3), Cache.bold_30, Cache.noto_30)


def draw_minute(
    graph: Image.Image, activities: List[str], legend: Dict[str, Tuple[int, int, int]], x: int
) -> None:
    """
    Draws a 1px line representing a minute of activity to an existing graph by mutating it
    """
    activities.sort()

    n = len(activities)

    part_height = 800 // n

    chunks = []

    # Divide into "equal groups", splitting the remainder if there is one
    while (s := sum(chunks)) != 800:
        if s + part_height > 800:
            remainder = 800 - s
            for idx, _ in enumerate(chunks):
                if remainder == 0:
                    break
                chunks[idx] += 1
                remainder -= 1
        else:
            chunks.append(part_height)

    line = Image.new("RGBA", (1, 800), (255, 255, 255, 255))

    for i in range(len(activities)):
        segment = Image.new("RGBA", (1, chunks[i]), legend[activities[i]])
        line.paste(segment, (0, sum(chunks[:i])))

    graph.paste(line, (x, 174))
