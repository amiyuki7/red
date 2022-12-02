import io
import os
import discord
from typing import Optional
from .lib import MemberAttrs, ActivityAttrs, NAMEMAP
from .lib.track import Users_
from .lib.image import generate_img
from discord.ext.commands import Bot, Context
from discord.ext import tasks
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image
import datetime

load_dotenv()
# Set this in .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
# BOT_TOKEN = os.getenv("DEV_TOKEN")
assert type(BOT_TOKEN) is str

intents = discord.Intents().all()
bot = Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    global Users
    Users = Users_(bot=bot)
    Users.load_existing()
    task_loop.start()


@tasks.loop(seconds=1)
async def task_loop():
    s = datetime.datetime.utcnow().second
    if s == 0:
        # A new minute
        await Users.update_graphs()


# command for just testing random stuff
@bot.command()
async def test(ctx: Context, member: discord.Member):
    for flag in member.public_flags.all():
        await ctx.send(flag.name)


@bot.command()
async def commands(ctx: Context):
    embed = discord.Embed(
        title="Public Commands",
        colour=0x5762EC,
    )

    # A bit of space
    embed.add_field(name=chr(173), value="___")

    embed.add_field(
        name="**`$specs <user>`**",
        value=f"""
        Generates a pretty image depicting what the pinged user is doing

        *Arguments*
        `user` | A pinged user

        *Examples*
        $specs <@703204753743806585>
        """.strip(),
        inline=False,
    )

    embed.add_field(name=chr(173), value="___")

    embed.add_field(
        name="**`$graph <user>`**",
        value=f"""
        Generates a pretty graph depicting what the pinged user has done today, relative to their timezone

        *Arguments*
        `user` | A pinged, tracked user

        *Examples*
        $graph <@703204753743806585>
        """.strip(),
        inline=False,
    )

    embed.add_field(name=chr(173), value="___")

    embed.add_field(
        name="**`$track <offset>`**",
        value=f"""
        Grants permission for the bot to track *YOUR* Discord activity (i.e. what game you're playing)

        *Arguments*
        `offset` | A special offset format that complies with:
        `[+/-][hours][minutes]`
        If this argument is omitted, you will be tracked in UTC time

        *Examples*
        $track
        $track +11
        $track -5:30
        """.strip(),
        inline=False,
    )

    embed.add_field(name=chr(173), value="___")

    embed.add_field(
        name="**`$untrack`**",
        value=f"""
        Revokes permission for the bot to track *YOUR* Discord activity (i.e. what game you're playing), and deletes any previously tracked graphs

        *Examples*
        $untrack
        """.strip(),
        inline=False,
    )

    await ctx.reply(embed=embed)


@bot.command()
async def track(ctx: Context, offset: Optional[str]):
    member = ctx.author

    if Users.exists(member.id):
        # Short circuit this entire function if the user is already being tracked
        embed = discord.Embed(
            title="Command failed",
            description=f"**Can't track**: {member.mention} is already being tracked",
            colour=0xFF0000,
        )
        await ctx.reply(embed=embed)
        return

    h_offset = 0
    m_offset = 0
    if offset:
        offset = offset.strip()
        # Everything after the sign
        parts = offset[1:].split(":")

        try:
            # A ton of rules the formatting of the offset must follow
            assert offset[0] == "+" or offset[0] == "-"
            assert all(x.isdigit() for x in parts)
            assert len(parts) == 1 or len(parts) == 2

            # Check that the hours and minutes offset is within reason
            assert 0 <= int(parts[0]) <= 23
            h_offset = int(parts[0])

            if len(parts) == 2:
                mins = parts[1]
                assert 0 <= int(mins) <= 59
                m_offset = int(mins)

        except AssertionError:
            # Something wrong happened with the offset formatting
            embed = discord.Embed(
                title="Command failed",
                description=f"**Invalid offset**: See `$commands` for the accepted offset format",
                colour=0xFF0000,
            )
            await ctx.reply(embed=embed)
            return

        fmt_h = len(str(h_offset)) == 1 and f"0{h_offset}" or str(h_offset)
        fmt_m = len(str(m_offset)) == 1 and f"0{m_offset}" or str(m_offset)

        Users.track(
            str(member.id),
            offset[0] == "+" and int(fmt_h) or -int(fmt_h),
            offset[0] == "+" and int(fmt_m) or -int(fmt_m),
        )

        embed = discord.Embed(
            title="Command successful",
            description=f"Successfully tracking {member.mention} @ `UTC{offset[0]}{fmt_h}:{fmt_m}`",
            colour=0x00FF00,
        )

        await ctx.reply(embed=embed)
    else:
        Users.track(
            str(member.id),
            0,
            0,
        )

        embed = discord.Embed(
            title="Command successful",
            description=f"Successfully tracking {member.mention} @ `UTC`",
            colour=0x00FF00,
        )

        await ctx.reply(embed=embed)


@bot.command()
async def untrack(ctx: Context):
    member = ctx.author

    if not Users.exists(member.id):
        embed = discord.Embed(
            title="Command failed",
            description=f"**Can't untrack**: {member.mention} was not already tracked",
            colour=0xFF0000,
        )
        await ctx.reply(embed=embed)

    Users.untrack(member.id)
    embed = discord.Embed(
        title="Command successful",
        description=f"Successfully untracked {member.mention} and reset their activity graph",
        colour=0x00FF00,
    )
    await ctx.reply(embed=embed)


@bot.command()
async def show_tracked(ctx: Context):
    # Only allow myself and @VladP1234 to use this command
    if not ctx.author.id in [565054806083895306, 703204753743806585]:
        return

    await ctx.send(str(Users.users))


@bot.command()
async def specs(ctx: Context, member: discord.Member):
    img = await specs_img(member)

    with io.BytesIO() as bin:
        img.save(bin, "png")
        bin.seek(0)
        await ctx.reply(file=discord.File(fp=bin, filename="out.png"))


@bot.command()
async def graph(ctx: Context, member: discord.Member):
    graph_path = f"{Path(__file__).resolve().parents[2]}/data/{member.id}/graph_today.png"

    await ctx.reply(file=discord.File(fp=graph_path, filename="out.png"))


async def specs_img(member: discord.Member) -> Image.Image:
    """
    Extracts current specs of a user and generates an image
    """
    member_name = member.name
    member_tag = member.discriminator
    member_nick = member.nick

    if member.avatar:
        member_avatar = str(member.display_avatar)
    else:
        # There are 5 default avatars, each with a different colour. The colour is determined by the member's discriminator
        member_avatar = f"https://cdn.discordapp.com/embed/avatars/{int(member.discriminator) % 5}.png"

    member_status = member.status
    user = await bot.fetch_user(member.id)
    member_banner_colour = user.accent_colour
    # CustomActivity is the custom status, which ofr this application, is not considered a "rich presence"
    without_custom = [actv for actv in member.activities if not isinstance(actv, discord.CustomActivity)]
    # Use the first non-custom activity
    # TODO: Use all the activites and track them into a graph
    activities = len(without_custom) > 0 and without_custom or None

    custom_activity = (
        # custom activity = (there is a cusom activity) and (the custom activity) or None
        len([actv for actv in member.activities if isinstance(actv, discord.CustomActivity)]) != 0
        and [actv for actv in member.activities if isinstance(actv, discord.CustomActivity)][0].name
        or None
    )

    activities_list = []

    if activities:
        # activities_list = []
        for activity in activities:
            member_activity_name = ""
            member_activity_type = ""
            member_activity_details = ""
            member_activity_state = ""
            member_activity_large_img = ""
            member_activity_small_img = ""
            member_activity_end = None
            member_activity_start = None
            time_remaining = "No time remaining"
            time_elapsed = "No time elapsed"
            line_1 = ""
            line_2 = ""
            line_3 = ""
            line_4 = ""
            member_activity_name = activity.name or member_activity_name
            member_activity_type = activity.type.name

            if isinstance(activity, discord.Activity) and not isinstance(activity, discord.Streaming):
                member_activity_details = activity.details or member_activity_details
                member_activity_state = activity.state or member_activity_state
                # Handle None case with an or clause
                member_activity_large_img = activity.large_image_url or member_activity_large_img
                member_activity_small_img = activity.small_image_url or member_activity_small_img
                member_activity_end = activity.end
                member_activity_start = activity.start

                line_1 = member_activity_name
                line_2 = member_activity_details
                line_3 = member_activity_state
            elif isinstance(activity, discord.Streaming):
                # This is completely untested
                # member_activity_large_img = activity.assets.get("large_image") or member_activity_large_img

                line_1 = member_activity_name
                line_2 = activity.game and f"playing {activity.game}" or ""
                line_3 = activity.url and activity.url or ""
            elif isinstance(activity, discord.Game):
                # This is completely untested
                member_activity_start = activity.start

                line_1 = member_activity_name
            elif isinstance(activity, discord.Spotify):
                now = datetime.datetime.now().timestamp()
                now = datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc)
                time_diff = now - activity.start
                s = time_diff.seconds
                mins = s // 60
                s %= 60
                duration = activity.duration
                ds = duration.seconds
                dmins = ds // 60
                ds %= 60
                fmt_elapsed = f"{mins}:{len(str(s)) > 1 and s or f'0{s}'}"
                fmt_duration = f"{dmins}:{len(str(ds)) > 1 and ds or f'0{ds}'}"
                artists = activity.artists
                fmt_artists = f"by {', '.join(artists)}"
                album = activity.album

                member_activity_large_img = activity.album_cover_url

                line_1 = activity.title
                line_2 = fmt_artists
                line_3 = f"on {album}"
                line_4 = f"{fmt_elapsed} / {fmt_duration}"

            # This if/elif block is only for discord.Activity
            if member_activity_end:
                now = datetime.datetime.now().timestamp()
                now = datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc)
                time_diff = member_activity_end - now
                raw_time_remaining = divmod(time_diff.days * (24 * 60 * 60) + time_diff.seconds, 60)
                minutes, seconds = raw_time_remaining
                minutes = len(str(minutes)) == 1 and f"0{minutes}" or minutes
                seconds = len(str(seconds)) == 1 and f"0{seconds}" or seconds
                time_remaining = f"{minutes}:{seconds} left"
                line_4 = time_remaining
            elif member_activity_start:
                now = datetime.datetime.now().timestamp()
                now = datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc)
                time_diff = now - member_activity_start
                s = time_diff.seconds

                days = s // (24 * 60 * 60)
                s %= 24 * 60 * 60
                hours = s // (60 * 60)
                s %= 60 * 60
                mins = s // 60

                if mins == 0:
                    mins = 1

                if days != 0:
                    line_4 = f"for {days} {days > 1 and 'days' or 'day'}"
                elif hours != 0:
                    line_4 = f"for {hours} {hours > 1 and 'hours' or 'hour'}"
                else:
                    line_4 = f"for {mins} {mins > 1 and 'minutes' or 'minute'}"

            lines = [line_1, line_2, line_3, line_4]
            # Filter out the lines that are empty
            lines = [line for line in lines if line != ""]

            # Move those empty strings to the end of the list
            while len(lines) < 4:
                lines.append("")

            # Destruct the lines list back into four individual strings
            line_1, line_2, line_3, line_4 = lines

            # # Debug within discord
            # await ctx.send(
            #     f"""{member_activity_name}
            # {member_activity_details}
            # {member_activity_state}
            # Time remaining: {time_remaining}
            # Time elapsed: {time_elapsed}
            # {member_name}
            # {member_avatar}
            # {member_tag}
            # {member_nick}
            # {member_status}
            # {member_activity_type}
            # {line_1}
            # {line_2}
            # {line_3}
            # {line_4}
            # {member_activity_large_img}
            # {member_activity_small_img}
            # """.strip()
            # )

            # # Handles the activities that are officially supported by discord

            if member_activity_large_img == "":
                # Check if the name of the game is in the data
                if obj := NAMEMAP.get(line_1):
                    # Check if a hash for the activity exists
                    if obj["icon_hash"]:
                        # Interpolate data into an endpoint
                        member_activity_large_img = f'https://cdn.discordapp.com/app-icons/{obj["application_id"]}/{obj["icon_hash"]}.png'

            activity_attrs = ActivityAttrs(
                activity_type=member_activity_type,
                image_large=member_activity_large_img,
                image_small=member_activity_small_img,
                line1=line_1,
                line2=line_2,
                line3=line_3,
                line4=line_4,
            )

            activities_list.append(activity_attrs)

    attrs = MemberAttrs(
        name=member_name,
        tag=member_tag,
        nick=member_nick,
        status=member_status,
        avatar=member_avatar,
        activities=activities_list,
        customActivity=custom_activity,
        banner_colour=member_banner_colour,
    )

    img = await generate_img(attrs)
    return img


async def main():
    try:
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.close()
