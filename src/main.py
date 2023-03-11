import inspect  # call stack inspection
import os  # environment variables
import random  # dumb random number generator

import discord  # base discord module
import yt_dlp  # we be getting stuff from youtube
from discord.ext import commands  # Bot class and utils

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

ytdl_opts = {
        'format':         'bestaudio/best',
        'outtmpl':        'temp',
        'postprocessors': [{
                'key':              'FFmpegExtractAudio',
                'preferredcodec':   'mp3',
                'preferredquality': '192',
        }],
}


# print error message in console
def throw_error(msg):
    print(msg)


# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
    # user selectable display config (prompt symbol, color)
    dsp_sel = {
            'debug':   ('\033[34m', '-'),
            'info':    ('\033[32m', '*'),
            'warning': ('\033[33m', '?'),
            'error':   ('\033[31m', '!'),
    }

    # internal ansi codes
    _extra_ansi = {
            'critical': '\033[35m',
            'bold':     '\033[1m',
            'unbold':   '\033[2m',
            'clear':    '\033[0m',
    }

    # get information about call site
    caller = inspect.stack()[1]

    # input sanity check
    if level not in dsp_sel:
        print(
                '%s%s[@] %s:%d %sBad log level: "%s"%s' % \
                (_extra_ansi['critical'], _extra_ansi['bold'],
                 caller.function, caller.lineno,
                 _extra_ansi['unbold'], level, _extra_ansi['clear'])
        )
        return

    # print the damn message already
    print(
            '%s%s[%s] %s:%d %s%s%s' % \
            (_extra_ansi['bold'], *dsp_sel[level],
             caller.function, caller.lineno,
             _extra_ansi['unbold'], msg, _extra_ansi['clear'])
    )


################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################

# bot instantiation
bot = commands.Bot(command_prefix = '!')


# on_ready - called after connection to server is established
@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')


# on_message - called when a new message is posted to the server
#   @msg : discord.message.Message
@bot.event
async def on_message(msg):
    # filter out our own messages
    if msg.author == bot.user:
        return

    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')

    # overriding the default on_message handler blocks commands from executing
    # manually call the bot's command processor on given message
    await bot.process_commands(msg)


# code.interact(local=dict(bot = bot, msg = msg))

# bot disconnects automatically when left alone in a voice channel
# if the bot is turned on after someone joined the voice channel, it will
# still trigger this and disconnect (user is not seen as connected)
@bot.event
async def on_voice_state_update(member, before, after):
    # Check if the bot is the only member in the voice channel
    voice_channel = before.channel or after.channel
    if voice_channel is not None \
            and voice_channel.guild.voice_client is not None:
        vc = voice_channel.guild.voice_client
        members = vc.channel.members

        if len(members) == 1 and members[0].id == bot.user.id:
            # Disconnect from the voice channel
            text_channel = discord.utils.get(
                    voice_channel.guild.text_channels,
                    name = 'bot-commands'
            )

            await text_channel.send("I'm leaving, I'm lonely :(")
            await vc.disconnect()


# roll - rng chat command
#   @ctx     : command invocation context
#   @max_val : upper bound for number generation (must be at least 1)
@bot.command(brief = 'Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    # argument sanity check
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')

    await ctx.send(random.randint(1, max_val))


@bot.command(brief = 'Bot joins the voice channel')
async def join(ctx):
    # check if the author is in a voice channel
    if ctx.author.voice is None:
        await ctx.send(
                'enter a voice channel if you want to summon the bot, peasant'
        )
        raise Exception('author is not in a voice channel')

    # save the channel where the author is connected
    voice_channel = ctx.author.voice.channel

    # check whether bot is connected elsewhere or not
    if ctx.voice_client is not None:
        await ctx.send('i am already here')
        raise Exception('bot is already connected')

    await voice_channel.connect()
    await ctx.send('bot is in the house')


@bot.command(brief = 'Bot leaves the voice channel')
async def scram(ctx):
    is_connected = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    # check if bot is connected at all
    if is_connected is None:
        raise Exception('bot is not in a voice channel')

    # make him go away
    await ctx.voice_client.disconnect()
    await ctx.send('bye bitches')


@bot.command(brief = 'Bot changes voice channels')
async def cmere(ctx):
    author_state = ctx.author.voice

    # check if author is connected
    if author_state is None:
        raise Exception('author is not already in a voice channel')

    voice_client = discord.utils.get(bot.voice_clients, guild = ctx.guild)

    # check if bot is connected
    if voice_client is None:
        raise Exception('bot is not in a voice channel')

    # check if author is not in the same channel as bot
    if ctx.author.voice.channel is ctx.voice_client.channel:
        await ctx.send('already here, boss')
        return

    if ctx.voice_client.is_playing():
        await ctx.send('i am already playing something, somewhere else')
        raise Exception('bot is already playing a song somewhere else')

    # bot swtiches channels
    voice_channel = ctx.author.voice.channel
    await ctx.voice_client.disconnect()
    await voice_channel.connect()


@bot.command(brief = 'Bot plays a song')
async def play(ctx, song: str):
    # check if the song exists locally
    if ("%s.mp3" % song) in os.listdir('../music/'):
        # check if the bot is connected
        if ctx.voice_client is None:
            # make the bot join
            await ctx.invoke(bot.get_command('join'))
        elif ctx.voice_client.channel is not ctx.author.voice.channel:
            # check if the bot is playing a song on another voice channel
            if ctx.voice_client.is_playing():
                # move the bot to the master's channel
                await ctx.send('i am already playing something, somewhere else')
                log_msg('bot is already playing a song somewhere else', 'error')
                return

            await ctx.invoke(bot.get_command('cmere'))
        else:
            # throw error if the bot is already playing a song somewhere else
            if ctx.voice_client.is_playing():
                await ctx.send(
                        'i am already playing something, wait until i am done'
                )
                log_msg('bot is already playing a song', 'error')
                return

        ctx.voice_client.play(
                discord.FFmpegPCMAudio("./music/%s.mp3" % song)
        )
    else:
        # await ctx.send('i do not have that song locally, una momento')

        if "temp.mp3" in os.listdir('..'):
            os.remove("../temp.mp3")

        yt_dlp.YoutubeDL(ytdl_opts).download([song])
        ctx.voice_client.play(discord.FFmpegPCMAudio("./temp.mp3"))


@bot.command(brief = 'List all songs in ./music/ ')
async def list(ctx):
    if len(os.listdir('../music/')) == 0:
        await ctx.send('you do not have any songs locally')
        raise Exception('no songs in folder')
    else:
        for song in os.listdir('../music/'):
            if song != "temp.mp3":
                await ctx.send(song)


@bot.command(brief = 'Bot pauses')
async def pause(ctx):
    if ctx.author.voice is None:
        await ctx.send('you are not here to stop me, bastard')
        raise Exception('author not connected')

    if ctx.voice_client is None:
        await ctx.send('not even here, boss')
        raise Exception('bot is not already in a voice channel')

    if ctx.voice_client.channel is not ctx.author.voice.channel:
        await ctx.send("you are not the boss of me, %s" % ctx.author)
        raise Exception('author is not in the same channel as bot')

    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
    else:
        await ctx.send('nothing to pause here')
        raise Exception('bot is not playing anything')


@bot.command(brief = 'Bot resumes playing')
async def resume(ctx):
    if ctx.author.voice is None:
        await ctx.send('you are not here to make me work, bastard')
        raise Exception('author not connected')

    if ctx.voice_client is None:
        await ctx.send('not even here, boss')
        raise Exception('bot is not in a voice channel')

    if ctx.voice_client.channel is not ctx.author.voice.channel:
        await ctx.send("you are not the boss of me, %s" % ctx.author)
        raise Exception('author is not in the same channel as bot')

    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
    else:
        await ctx.send('nothing to resume here')
        raise Exception('bot is not paused anything')


@bot.command(brief = 'Bot stops playing')
async def stop(ctx):
    if ctx.author.voice is None:
        await ctx.send('you are not here to make me work, bastard')
        raise Exception('author not connected')

    if ctx.voice_client is None:
        await ctx.send('not even here, boss')
        raise Exception('bot is not in a voice channel')

    if ctx.voice_client.channel is not ctx.author.voice.channel:
        await ctx.send("you are not the boss of me, %s" % ctx.author)
        raise Exception('author is not in the same channel as bot')

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    else:
        await ctx.send('i am not playing anything')
        raise Exception('bot is not playing anything')


@bot.command(brief = 'Bot tells you a secret in private')
async def secret(ctx):
    await ctx.author.send('i am not telling you anything, %s' % ctx.author.nick)

@bot.command(brief = 'Tell bot a secret in private (he will remember it)')
async def tell_secret(ctx, *, message):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send('you should tell me in private, %s' % ctx.author.nick)
        return

    await ctx.send('i will remember that')
    log_msg('secret: %s' % message, 'info')


# roll_error - error handler for the <roll> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))


################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################

if __name__ == '__main__':
    # check that token exists in environment
    if 'BOT_TOKEN' not in os.environ:
        log_msg('save your token in the BOT_TOKEN env variable!', 'error')
        exit(-1)

    # launch bot (blocking operation)
    bot.run(os.environ['BOT_TOKEN'])
