from youtubesearchpython import VideosSearch, Playlist, ResultMode
from yt_dlp import YoutubeDL
import pprint as pp

def DownloadPlaylist(query):
    playlist = Playlist(query)
    playlist = playlist.videos
    return playlist[0]
    # return [{'source':item["link"], 'title':item["title"]} for item in playlist]

PlaylistTest = DownloadPlaylist("https://www.youtube.com/playlist?list=PLZuZrScKjWOMAEEBEGTmAGtmmlg6QY7bC")


def SearchYT(video):
    videoTitle = video["title"]
    channelName = video["channel"]['name']
    query = f"{videoTitle} {channelName}"
    return VideosSearch(query).result()['result'][0]['link']

pp.pprint(SearchYT(PlaylistTest))