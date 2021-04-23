import discord
from config import settings
import json
import requests
from discord.utils import get
import asyncio
import youtube_dl
import os
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from os import system
import ffmpeg
import urllib.parse, urllib.request, re
import random
import pymorphy2

joinrp = ['1.mpeg', '2.mpeg', '3.mpeg']
playrp = ['playrp.mpeg', 'playrp2.mpeg', 'playrp3.mpeg']

bot = commands.Bot(command_prefix = settings['prefix'])


@bot.command(name='fox')
async def fox(ctx):
    """Случайная лиса"""
    response = requests.get('https://some-random-api.ml/img/fox') # Get-запрос
    json_data = json.loads(response.text)

    embed = discord.Embed(color = 0xff9900, title = 'Random Fox')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)


@bot.command(name='dog')
async def dog(ctx):
    """Случайная собака"""
    response = requests.get('https://some-random-api.ml/img/dog')
    json_data = json.loads(response.text)

    embed = discord.Embed(color = 0xff9900, title = 'Random dog')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)


@bot.command(name='cat')
async def cat(ctx):
    """Случайная кошка"""
    response = requests.get('https://some-random-api.ml/img/cat')
    json_data = json.loads(response.text)
    embed = discord.Embed(color=0xff9900, title='Random cat')
    embed.set_image(url=json_data['link'])
    await ctx.send(embed=embed)


@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return
    if 'кот' in str(ctx.content).lower() or 'кош' in str(ctx.content).lower():
        response = requests.get('https://api.thecatapi.com/v1/images/search')
        json_data = json.loads(response.text)[0]
        await ctx.channel.send(json_data['url'])
    if 'соба' in str(ctx.content).lower():
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        json_data = json.loads(response.text)
        await ctx.channel.send(json_data['message'])
    if 'пудж' in str(ctx.content).lower():
        await ctx.channel.send(f'{ctx.author.mention}, меня звали?')
    await bot.process_commands(ctx)


@bot.command(name='meme')
async def meme(ctx):
    """Случайный мем"""
    response = requests.get('https://some-random-api.ml/meme')
    json_data = json.loads(response.text)

    embed = discord.Embed(color = 0xff9900, title = 'Random meme')
    embed.set_image(url = json_data['image'])
    await ctx.send(embed = embed)


@bot.command(name='hello')
async def hello(ctx):
    """Здоровается с пользователем"""
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}!')


@bot.command(pass_context=True, brief="Чтобы бот зашел в канал", aliases=['j', 'jo'])
async def join(ctx):
    if ctx.message.author.voice is None:
        await ctx.send("Чел, зайди в войс канал")
        return
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await ctx.send(f"Я в {channel}")
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.volume = 100
    voice.play(discord.FFmpegPCMAudio("replics/" + random.choice(joinrp)))


@bot.command(pass_context=True, brief="Чтобы начала играть музыка", aliases=['pl'])
async def play(ctx, *, url: str):
    ##
    if ctx.message.author.voice is None:
        await ctx.send("Чел, зайди в войс канал")
        return
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    ##
    voice.play(discord.FFmpegPCMAudio("replics/" + random.choice(playrp)))
    if 'www.' not in url:
        query_string = urllib.parse.urlencode({
            'search_query': url
        })
        htm_content = urllib.request.urlopen(
            'http://www.youtube.com/results?' + query_string
        )
        search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
        url = 'https://www.youtube.com/watch?v=' + search_results[0]
    params = {"format": "json", "url": url}
    urll = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    urll = urll + "?" + query_string
    with urllib.request.urlopen(urll) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        print(data['title'])
        title = data['title']


    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Дождись пока доиграет или используй 'p stop'")
        return

    voice = get(bot.voice_clients, guild=ctx.guild)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info['duration'] > 300:
            await ctx.send('Видео слишком долгое')
            return

    await ctx.send("Ща будет")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, 'song.mp3')
    voice.volume = 40 / 100
    voice.play(discord.FFmpegPCMAudio("song.mp3"))
    voice.is_playing()
    await ctx.send('Сейчас играет трек для настоящих пацанов :red_circle: ' + title)


@bot.command(name='leave')
async def leave(ctx):
    """Бот выходит из комнаты"""
    await ctx.voice_client.disconnect()


@bot.command(name='stop')
async def stop(ctx):
    '''Музыка перестаёт играть'''
    ctx.voice_client.stop()


@bot.command(name='search')
async def search(ctx, *, search):
    """"Поиск и выдача первых 5 запросов из ютуба"""
    query_string = urllib.parse.urlencode({
        'search_query': search
    })
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )
    search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
    embed = discord.Embed(color=0xff9900, title=search)
    embed.description = ''
    for i in range(5):
        params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % search_results[i]}
        urll = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        urll = urll + "?" + query_string
        with urllib.request.urlopen(urll) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            print(data['title'])
            title = data['title']
        embed.description += str(i + 1) + '. ' + title + '\n https://www.youtube.com/watch?v=' + search_results[i] + '\n'
    await ctx.send(embed=embed)


@bot.command(name='sp')
async def searchplay(ctx, *, search):
    """"Поиск и выдача первых 5 запросов из ютуба, а так же их воспроизведение"""
    query_string = urllib.parse.urlencode({
        'search_query': search
    })
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )
    search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
    embed = discord.Embed(color=0xff9900, title=search)
    embed.description = ''
    titles = []
    for i in range(5):
        params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % search_results[i]}
        urll = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        urll = urll + "?" + query_string
        with urllib.request.urlopen(urll) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            print(data['title'])
            title = data['title']
            titles.append('https://www.youtube.com/watch?v=' + search_results[i])
        embed.description += str(i + 1) + '. ' + title + '\n https://www.youtube.com/watch?v=' + search_results[i] + '\n'
    await ctx.send(embed=embed)

    author = ctx.author

    def check(author):
        def inner_check(message):
            if message.author != author:
                return False
            try:
                int(message.content)
                return True
            except ValueError:
                return False
        return inner_check

    msg = await bot.wait_for('message', check=check(author), timeout=30)
    if msg.content.isdigit() and 1 <= int(msg.content) <= 5:
        url = titles[int(msg.content) - 1]
        ##
        if ctx.message.author.voice is None:
            await ctx.send("Чел, зайди в войс канал")
            return
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
        ##
        voice.play(discord.FFmpegPCMAudio("replics/" + random.choice(playrp)))
        if 'www.' not in url:
            query_string = urllib.parse.urlencode({
                'search_query': url
            })
            htm_content = urllib.request.urlopen(
                'http://www.youtube.com/results?' + query_string
            )
            search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
            url = 'https://www.youtube.com/watch?v=' + search_results[0]
        params = {"format": "json", "url": url}
        urll = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        urll = urll + "?" + query_string
        with urllib.request.urlopen(urll) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            print(data['title'])
            title = data['title']

        song_there = os.path.isfile("song.mp3")
        try:
            if song_there:
                os.remove("song.mp3")
        except PermissionError:
            await ctx.send("Дождись пока доиграет или используй 'p stop'")
            return

        voice = get(bot.voice_clients, guild=ctx.guild)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info['duration'] > 300:
                await ctx.send('Видео слишком долгое')
                return
        await ctx.send("Ща будет")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, 'song.mp3')
        voice.volume = 40 / 100
        voice.play(discord.FFmpegPCMAudio("song.mp3"))
        voice.is_playing()
        await ctx.send('Сейчас играет трек для настоящих пацанов :red_circle: ' + title)


@bot.command(name='приветствие')
async def cs16(ctx):
    """Включить приветствие из кс16"""
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    voice.volume = 100
    voice.play(discord.FFmpegPCMAudio("replics/privet.mp3"))


@bot.command(name='helppymorph')
async def help(ctx):
    """Помощь с командами pymorphy2"""
    await ctx.send('Команды:\n'
                   '!numerals для согласовывания числительных с существительными\n'
                   '!alive для определения живой или нет\n'
                   '!noun изменения в числе и падеже\n'
                   '!inf начальная форма слова\n'
                   '!morph полный морфологический анализ слова')


@bot.command(name='numerals')
async def numerals(ctx, word, n):
    m = pymorphy2.MorphAnalyzer()
    c = m.parse(word)[0]
    c = c.make_agree_with_number(int(n)).word
    await ctx.send(f'{n} {c}')


@bot.command(name='alive')
async def alive(ctx, word):
    m = pymorphy2.MorphAnalyzer()
    p = m.parse(word)[0]
    if p.tag.POS == 'NOUN':
        if p.tag.animacy == 'anim':
            rod = p.tag.gender
            chis = p.tag.number
            if chis == 'sing':
                if rod == 'femn':
                    await ctx.send('Живая')
                elif rod == 'masc':
                    await ctx.send('Живой')
                elif rod == 'neut':
                    await ctx.send('Живое')
            else:
                await ctx.send('Живые')
        else:
            rod = p.tag.gender
            chis = p.tag.number
            if chis == 'sing':
                if rod == 'femn':
                    await ctx.send('Не живая')
                elif rod == 'masc':
                    await ctx.send('Не живой')
                elif rod == 'neut':
                    await ctx.send('Не живое')
            else:
                await ctx.send('Не живые')
    else:
        await ctx.send('Не существительное')


@bot.command(name='noun')
async def noun(ctx, word, padezh, chisl):
    m = pymorphy2.MorphAnalyzer()
    p = m.parse(word)[0]
    if p.tag.POS == 'NOUN':
        await ctx.send(f'{p.inflect({chisl, padezh}).word}')
    else:
        await ctx.send('Не существительное')


@bot.command(name='inf')
async def inf(ctx, word):
    m = pymorphy2.MorphAnalyzer()
    p = m.parse(word)[0].normal_form
    await ctx.send(p)


@bot.command(name='morph')
async def morph(ctx, word):
    m = pymorphy2.MorphAnalyzer()
    p = m.parse(word)[0]
    await ctx.send(p)


bot.run(settings['token'])
