import os
import discord
from discord.ext.commands import Bot, Context
from dotenv import load_dotenv
import datetime

load_dotenv()
# Set this in .env
BOT_TOKEN = os.getenv("DEV_TOKEN")
# BOT_TOKEN = os.getenv("DEV_TOKEN")
assert type(BOT_TOKEN) is str

intents = discord.Intents().all()
bot = Bot(command_prefix="%", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def specs_of(ctx: Context, member: discord.Member):
    member_name = member.name
    member_tag = member.discriminator
    member_nick = member.nick or "No nick"

    if member.avatar:
        member_avatar = member.display_avatar
    else:
        # see lib.py for explanation of default avatar colours
        member_avatar = f"https://cdn.discordapp.com/embed/avatars/{int(member.discriminator) % 5}.png"

    member_status = member.status

    member_activity_name = "No activity"
    member_activity_type = "No activity type"
    member_activity_details = "No activity details"
    member_activity_state = "No activity state"
    member_activity_large_img = "No activity img"
    member_activity_small_img = "No small activity img"
    member_activity_end = None
    member_activity_start = None
    time_remaining = "No time remaining"
    time_elapsed = "No time elapsed"

    if activity := member.activity:
        member_activity_name = activity.name
        member_activity_type = activity.type.name

        if isinstance(activity, discord.Activity):
            member_activity_details = activity.details
            member_activity_state = activity.state
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

        if member_activity_start:
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

            time_elapsed = f"{days} days, {hours} hours, {mins} mins"

    await ctx.send(
        f"""
        {member_name}
        {member_tag}
        {member_nick}
        {member_status}
        {member_activity_name}
        {member_activity_type}
        {member_activity_details}
        {member_activity_state}
        Time remaining: {time_remaining}
        Time elapsed: {time_elapsed}
        {member_avatar}
        {member_activity_large_img}
        {member_activity_small_img}
        """.strip()
    )

    # await ctx.send(member_activity_name)

    # if member.activity.details:
    #     member_activity_details = member.activity.details
    # await ctx.send(member_activity_details)

    # if member.activity:
    #     member_activity_type = member.activity.type.name
    # else:
    #     member_activity_type = ""
    # await ctx.send(member_activity_type)

    # if member.activity:
    #     pass
    # if isinstance(member.activity, discord.):
    # member_activity_misc = [member.activity.state, member.activity.session_id]

    # start_time = member.activity.timestamps["start"]
    # end_time = member.activity.timestamps["end"]

    # # this is in milliseconds, but we can use a dating library to convert it nicely instead of writing by ourselves
    # now = time.time()
    # remaining = f"Time remaining (ms): {end_time - now}"
    # elapsed = f"Time elapsed (ms): {now - start_time}"

    # # Discord api has messaging rate limits so this should send everything in one chunk
    # # i split it up so i could comment out individual things during bug fixing
    # # for example aydan doesn't have activity details, so the entire thing breaks
    # # sine its in an f-string now, its just gonna show "None" instead of breaking... i think
    # await ctx.send(f"{member_name}\n{member_tag}\n{member_nick}\n{member_avatar}\n{member_status}\n{member_badges}\n{member_activity_name}\n{member_activity_details}\n{member_activity_type}\n{remaining}\n{elapsed}")

    # Dw about this chunk for now
    # for i in member_activity_misc:
    #     await ctx.send(i)

    # member_specs = [member_name, member_tag, member_nick, member_avatar, member_status, member_badges, member_activity, member_activity_type]
    # for spec in member_specs:
    #     print(spec)
    # await ctx.send(f"{member_name, member_tag, member_nick, member_avatar, member_status, member_badges, member_activity, member_activity_type}")


async def main():
    try:
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.close()
