from ast import alias
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch, Playlist
from yt_dlp import YoutubeDL
import asyncio
import concurrent.futures


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS =   { 'options': '-vn',
                                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                                }

        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

    #searching the item on youtube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return{'source':item, 'title':title}
        search = VideosSearch(item, limit=1)
        return{'source':search.result()["result"][0]["link"], 'title':search.result()["result"][0]["title"]}

    def search_playlist(self, query):
        items = Playlist(query).videos
        search_results = []
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            
            try:
                for item in items:
                    future = executor.submit(self.search_yt, f"{item['title']} {item['channel']['name']}")
                    futures.append(future)
            
                search_results.extend([future.result() for future in concurrent.futures.as_completed(futures)])
                futures = []
                
                search_results.extend([future.result() for future in concurrent.futures.as_completed(futures)])
                search_results = [{'source': result["result"][0]["link"], 'title': result["result"][0]["title"]} for result in search_results]
            
            except Exception as e:
                #Debbuing purposes
                print(f"An error occurred: {e}")
        
        return search_results

    ##Nah, this shit to slow bitch
    # def search_playlist(self, query):
    #     
    #     items = Playlist(query).videos
    #     return [{'source': VideosSearch(f"{item['title']} {item['channel']['name']}", limit=1).result()["result"][0]["link"], 'title': item["title"]} for item in items]

    def PlaylistName(self, query):
        return Playlist(query).info['info']['title']

    # async def play_next(self, ctx):
    #     if len(self.music_queue) > 0:
    #         self.is_playing = True
    #         # get the first url
    #         m_url = self.music_queue[0][0]['source']
    #         await ctx.send(f"**'{self.music_queue[0][0]['title']}'** is now playing")

    #         # remove the first element as you are currently playing it
    #         self.music_queue.pop(0)
    #         loop = asyncio.get_event_loop()
    #         data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
    #         song = data['url']
    #         self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda _: self.bot.loop.create_task(self.play_next(ctx)))
    #         self.music_queue.append([{'source': m_url, 'title': data['title']}, self.music_queue[0][1]])  # Add the song back to the queue
    #     else:
    #         self.is_playing = False

    # infinite loop checking 
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            #TODO: Check Implementation later
            NotPlaying = False
            # if NotPlaying:
            await ctx.send(f"**'{self.music_queue[0][0]['title']}'** is now playing")
                # NotPlaying = True

            #try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await ctx.send("```Could not connect to the voice channel```")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            #remove the first element as you are currently playing it
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable= "ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda _: self.bot.loop.create_task(self.play_music(ctx)))

        else:
            self.is_playing = False

    @commands.command(name="PlaySong", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def PlaySong(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("```Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue)+2} -'{song['title']}'** added to the queue")  
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")
                self.music_queue.append([song, voice_channel])
                if self.is_playing == False:
                    await self.play_music(ctx)
    
    @commands.command(name="PPlaylist", aliases=["pp"], help="Plays a selected playlist from youtube")
    async def PPlaylist(self, ctx, *args):
        query  = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            playlist = self.search_playlist(query)
            if type(playlist) == type(True):
                await ctx.send("```Could not download the playlist. Incorrect format try another keyword. This could be due to playlist or a livestream format.```")
            else:
                await ctx.send(f"**'{self.PlaylistName(query)}'** added to the queue")
                for song in playlist:
                    self.music_queue.append([song, voice_channel])
                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music(ctx)


    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"#{i+1} -" + self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("```Music queue cleared```")

    @commands.command(name="stop", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
    
    @commands.command(name="remove", help="Removes last song added to queue")
    async def re(self, ctx):
        self.music_queue.pop()
        await ctx.send("```last song removed```")
    