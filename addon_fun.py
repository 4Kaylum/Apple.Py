import discord
from discord.ext import commands
import requests
import os
import json
from cleverbot import Cleverbot
import random
from pyowm import OWM
import sys
from isAllowed import *
import re
import humanize
# from urllib.request import urlretrieve

cb = Cleverbot()
mashapeKey = {"X-Mashape-Key":
              tokens['Mashape']}
htmlHead = {'Accept-Endoding': 'identity'}
owm = OWM(tokens['OwmKey'])
owm = OWM(API_key=tokens['OwmKey'], version='2.5')
owm_en = OWM()
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

notallowed = "You are not allowed to use that command."
waitmessage = "Please wait..."


def txtFileToList(nameOfFile):
    nameOfFile = workingDirectory + nameOfFile + '.txt'
    file = open(nameOfFile, 'r', encoding="utf-8")
    fileContent = file.read()
    file.close()
    fileContent = fileContent.split("\n")
    return fileContent


def randFromList(listThing):
    return listThing[random.randint(0, len(listThing) - 1)]


class Fun():

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def aes(self):
        pass

    @aes.command(pass_context=True, description='Makes your string into a coolio thingmie.')
    async def sq(self, ctx):
        a = ctx.message.content.split(
            ' ', 2)[2].upper()  # knock off the ".as "
        for i in a:
            if i == '\n':
                return self.bot.say("Please have your word on one line.")
        ret = []
        length = len(a)
        temp = ''
        spa = ' ' * (((len(a) - 1) * 2) - 1)
        for i in a:
            temp = temp + i + ' '
        temp = temp[:-1]
        ret.append(temp)
        temp = ''
        for i in range(1, length - 1, 1):
            temp = a[i] + spa + a[length - i - 1]
            ret.append(temp)

        temp = ''
        for i in a[::-1]:
            temp = temp + i + ' '
        ret.append(temp)

        acRet = '```\n'
        for i in ret:
            acRet += i + '\n'
        acRet += '```'

        if len(acRet) > 2000:
            await self.bot.say("Please shorten your input string.")
            return

        print('Aes command :: %s' % a)

        await self.bot.say(acRet)

    @commands.command(pass_context=True, description='Gives you a random picture of a cat.')
    async def cat(self, ctx):
        edit = await self.bot.say(waitmessage)
        page = requests.get('http://thecatapi.com/api/images/get?format=src')
        print("Got a cat picture :: %s" % page.url)
        await self.bot.edit_message(edit, page.url)

    @commands.command(pass_context=True, description='Prints out some Skyrim guard text.')
    async def guard(self, ctx):
        msg = randFromList(txtFileToList("skyrimText"))
        print("Spat out guard dialogue :: %s" % msg)
        await self.bot.say(msg)

    @commands.command(pass_context=True, aliases=['complement', 'complements', 'compliments'], description='Prints out some Skyrim guard text.')
    async def compliment(self, ctx):
        with open(workingDirectory + "complements.txt") as a:
            es = a.read()
        es = es.split('\n')
        msg = randFromList(es)
        print("Spat out complement :: %s" % msg)
        await self.bot.say(msg)

    @commands.command(pass_context=True, description='Gives the lenny face.')
    async def lenny(self, ctx):
        await self.bot.say("( ͡° ͜ʖ ͡°)")

    @aes.command(pass_context=True)
    async def sp(self, ctx):
        ret = '```\n'
        if '\n' in ctx.message.content:
            await self.bot.say("Please only use one line in your input.")
            return
        toAlt = list(ctx.message.content.split(' ', 2)[2])
        for i in range(0, 4):
            for o in toAlt:
                ret = ret + o + ' ' * i
            ret = ret + '\n'
        for i in range(2, -1, -1):
            for o in toAlt:
                ret = ret + o + ' ' * i
            ret = ret + '\n'
        ret = ret + '```'
        if len(ret) > 2000:
            await self.bot.say("Please shorten your input string.")
            return
        await self.bot.say(ret)

    @commands.command(pass_context=True, description='Gives you love, gives you life.')
    async def love(self, ctx):
        a = ctx.message.content[len(ctx.message.content.split(' ')[0]) + 1:]
        if a == "":
            p = "What do you love?"
        else:
            a = "%s is love, %s is life." % (a, a)
            print("This guy is love :: %s" % a)
            p = a
        await self.bot.say(p)

    @commands.command(pass_context=True, aliases=['joke'], description='Gives a random pin from punoftheday.com.')
    async def pun(self, ctx):
        edit = await self.bot.say(waitmessage)
        page = requests.get('http://www.punoftheday.com/cgi-bin/randompun.pl',
                            headers=htmlHead)
        out = page.text.split('dropshadow1')[1][6:].split('<')[0]
        print("Said a pun :: %s" % out)
        await self.bot.edit_message(edit, out)

    @commands.command(pass_context=True, description='')
    async def weather(self, ctx):
        placeName = ctx.message.content[
            len(ctx.message.content.split(' ')[0]) + 1:]
        if placeName == '':
            await self.bot.say("Please provide a location to check the weather of.")
            return

        edit = await self.bot.say(waitmessage)
        weatherAtPlace = owm.weather_at_place(placeName)
        weath = weatherAtPlace.get_weather()
        wea_wind = weath.get_wind()['speed']  # mph
        wea_temp = weath.get_temperature(unit='celsius')['temp']
        wea_gene = weath.get_status()

        try:
            wea_gene = {'Clouds': 'Cloudy'}[wea_gene]
        except KeyError:
            pass

        ret = 'Weather in **%s**\n```\nWeather     :: %s\nTemperature :: %sC\nWindspeed   :: %smph```' % (
            weatherAtPlace.get_location().get_name(), wea_gene, wea_temp, wea_wind)

        await self.bot.edit_message(edit, ret)

    @commands.command(pass_context=True, description='Gives the look of disapproval.')
    async def disapprove(self, ctx):
        await self.bot.say("ಠ_ಠ")

    @commands.command(pass_context=True, description='Lets you talk to Cleverbot.')
    async def c(self, ctx):
        query = ctx.message.content.split(' ',1)[1]
        edit = await self.bot.say(waitmessage)
        x = cb.ask(query)
        print("Taling to Cleverbot :: \n    %s\n    %s" % (query, x))
        await self.bot.edit_message(edit, x.translate(non_bmp_map))

    @commands.command(pass_context=True, description='Evaluates the given codeset.')
    async def ev(self, ctx):
        toEx = ctx.message.content
        toEx = toEx[len(toEx.split(' ')[0]) + 1:]
        if 'sys' in toEx.lower() and 'exit' in toEx.lower():
            await self.bot.say("Nice try, asshole.")
            return
        try:
            out = eval(toEx)
        except Exception as e:
            out = str(repr(e))

        await self.bot.say(out)

    @commands.group(pass_context=True, description='Turns binary into ascii and vice versa')
    async def binary(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say("Please use `help binary` to see how to use this command properly.")

    @binary.command(pass_context=True, name='tobinary')
    async def toBinary(self, ctx):
        text = ctx.message.content
        text = text[len(text.split(' ')[0]) + len(text.split(' ')[1]) + 2:]
        letters = list(text)
        binary = []
        for i in letters:
            binary.append('{0:08b}'.format(ord(i)))
        out = 'That text in binary is \n```'
        for i in binary:
            out = out + i + ' '
        out = out[:-1] + '```'
        await self.bot.say(out)

    @binary.command(pass_context=True, name='totext')
    async def toAscii(self, ctx):
        text = ctx.message.content
        text = text[len(text.split(' ')[0]) + len(text.split(' ')[1]) + 2:]
        if len(text.split(' ')) > 1:
            binary = text.split(' ')
        else:
            binary = [text[i:i + 8] for i in range(0, len(text), 8)]

        out = 'That text in ASCII is \n```'
        for i in binary:
            out = out + chr(int(i, 2))
        out = out + '```'

        await self.bot.say(out)

    @commands.command(pass_context=True)
    async def mc(self, ctx):
        try:
            character = ctx.message.content.split(' ', 1)[1].replace(' ','_')
        except IndexError:
            await self.bot.say("Please provide a Minecraft username.")
            return

        returnString = "https://mcapi.ca/skin/2d/%s/85/false" % character
        await self.bot.say(returnString)

    @commands.command(pass_context=True)
    async def meme(self, ctx):
        spl = ctx.message.content.split('\n')

        url = spl[0].split(' ', 1)[1].replace(' ', '')
        try:
            topText = spl[1].replace(
                '-', '--').replace('_', '__').replace(' ', '-').replace('?', '~q')
        except IndexError:
            await self.bot.say("You can't leave the top or bottom blank.")
            return
        try:
            botText = spl[2].replace(
                '-', '--').replace('_', '__').replace(' ', '-').replace('?', '~q')
        except IndexError:
            await self.bot.say("You can't leave the top or bottom blank.")
            return

        cont = False
        for i in ['.png', '.jpg', '.jpeg']:
            if url.lower().endswith(i):
                cont = True
        if not cont:
            await self.bot.say("The URL provided for the meme was not retrieved successfully.")
            return

        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        # await self.bot.say(ctx.message.author.mention)
        # await self.bot.send_file(ctx.message.channel,
        #     requests.get("http://memegen.link/custom/{}/{}.jpg?alt={}".format(
        #     topText,
        #     botText,
        #     url)).content
        # )
        await self.bot.say("{} http://memegen.link/custom/{}/{}.jpg?alt={}".format(
            ctx.message.author.mention,
            topText,
            botText,
            url))

    @commands.command(pass_context=True)
    async def big(self, ctx):
        toReplace = ctx.message.content.split(' ',1)[1].lower()
        # qw = toReplace.replace(" ", )
        qw = ''
        # for i in 'abcdefghijklmnopqrstuvwxyz':
        #     qw = qw.replace(i, ":regional_indicator_{}: ".format(i))
        for o in toReplace:
            if o in 'abcdefghijklmnopqrstuvwxyz':
                o = ":regional_indicator_{}: ".format(o)
            if o == ' ':
                o = " ▫ "
            if o in '01236456789':
                o = ':' + humanize.apnumber(int(o)) + ': '
            qw = qw + o
        await self.bot.say(qw)


def setup(bot):
    bot.add_cog(Fun(bot))
