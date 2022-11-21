import os
import discord
from .lib import *
from discord.ext.commands import Bot, Context
from dotenv import load_dotenv
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


@bot.command()
async def specs_of(ctx: Context, member: discord.Member):
    member_name = member.name
    member_tag = member.discriminator
    member_nick = member.nick or "No nick"

    if member.avatar:
        member_avatar = str(member.display_avatar)
    else:
        # There are 5 default avatars, each with a different colour. The colour is determined by the member's discriminator
        member_avatar = f"https://cdn.discordapp.com/embed/avatars/{int(member.discriminator) % 5}.png"

    member_status = member.status

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

    if activity := member.activity:
        member_activity_name = activity.name or member_activity_name
        member_activity_type = activity.type.name

        if isinstance(activity, discord.Activity):
            member_activity_details = activity.details or member_activity_details
            member_activity_state = activity.state or member_activity_state
            # Handle None case with an or clause
            member_activity_large_img = activity.large_image_url or member_activity_large_img
            member_activity_small_img = activity.small_image_url or member_activity_small_img
            member_activity_end = activity.end
            member_activity_start = activity.start

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

            # time_elapsed = f"{days} days, {hours} hours, {mins} mins"
            if days != 0:
                line_4 = f"for {days} {days > 1 and 'days' or 'day'}"
            elif hours != 0:
                line_4 = f"for {hours} {hours > 1 and 'hours' or 'hour'}"
            else:
                line_4 = f"for {mins} {mins > 1 and 'minutes' or 'minute'}"

        line_1 = member_activity_name
        line_2 = member_activity_details
        line_3 = member_activity_state

    lines = [line_1, line_2, line_3, line_4]
    # Filter out the lines that are empty
    lines = [line for line in lines if line != ""]

    # Move those empty strings to the end of the list
    while len(lines) < 4:
        lines.append("")

    # Destruct the lines list back into four individual strings
    line_1, line_2, line_3, line_4 = lines

    # Debug within discord
    await ctx.send(
        # {member_activity_name}
        # {member_activity_details}
        # {member_activity_state}
        # Time remaining: {time_remaining}
        # Time elapsed: {time_elapsed}
        f"""
        {member_name}
        {member_avatar}
        {member_tag}
        {member_nick}
        {member_status}
        {member_activity_type}
        {line_1}
        {line_2}
        {line_3}
        {line_4}
        {member_activity_large_img}
        {member_activity_small_img}
        """.strip()
    )

    activity_attrs = ActivityAttrs(
        activity_type=member_activity_type,
        image_large=member_activity_large_img,
        image_small=member_activity_small_img,
        line1=line_1,
        line2=line_2,
        line3=line_3,
        line4=line_4,
    )

    attrs = MemberAttrs(
        name=member_name,
        tag=member_tag,
        nick=member_nick,
        status=member_status,
        avatar=member_avatar,
        activity=activity_attrs,
    )

    # return attrs


async def main():
    try:
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.close()
