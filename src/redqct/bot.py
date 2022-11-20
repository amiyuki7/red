import os
import discord
from discord.ext.commands import Bot, Context
from dotenv import load_dotenv
from time import time

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
async def kanye(ctx: Context):
    await ctx.send(f"{ctx.author.display_name} thinks that kanye is king :crown:")


@bot.command()
async def specs_of(ctx: Context, member: discord.Member):
    # await ctx.send("One Second")
    member_name = member.name
    await ctx.send(member_name)

    member_tag = member.discriminator
    await ctx.send(member_tag)

    if member.nick:
        member_nick = member.nick
    else:
        member_nick = "No nick"
    await ctx.send(member_nick)
    
    if member.avatar:
        member_avatar = member.display_avatar
    else:
        # see lib.py for explanation of default avatar colours
        # print("https://cdn.discordapp.com/embed/avatars/" str(member.discriminator%5) + ".png")
        print(str(int(member.discriminator)%5))
        member_avatar = "https://cdn.discordapp.com/embed/avatars/" + member.discriminator%5 + ".png"
        
    await ctx.send(member_avatar)
    
    member_status = member.status
    await ctx.send(member_status)
    
    if member.public_flags:
        member_badges = member.public_flags
    else:
        member_badges = "No badges"
    await ctx.send(member_badges)
    
    if member.activity:
        member_activity_name = member.activity.name
    else:
        member_activity_name = "No activity"
    await ctx.send(member_activity_name)

    if member.activity.details:
        member_activity_details = member.activity.details
    await ctx.send(member_activity_details)

    if member.activity:
        member_activity_type = member.activity.type.name
    else:
        member_activity_type = ""
    await ctx.send(member_activity_type)

    if member.activity:
        pass
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
