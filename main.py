"""
vska
"""
import os
import sys

# pylint: disable=import-error
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
# pylint: enable=import-error

from resources.lib.tmdb import search_movie, search_tv, get_seasons, get_episodes
from resources.lib.vidsrc import movie, episode

if sys.version_info >= (3,0,0):
    from urllib.parse import urlencode, parse_qsl
else:
    from urllib import urlencode
    from urlparse import parse_qsl

URL = sys.argv[0]
HANDLE = int(sys.argv[1])
ADDON = xbmcaddon.Addon(id="plugin.video.vska")
TMDB_KEY = ADDON.getSetting("tmdb_key")

# pylint: disable=bare-except
try:
    ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo("path"))
except:
    ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo("path")).decode("utf-8")
# pylint: enable=bare-except

ICONS_DIR = os.path.join(ADDON_PATH, "resources", "images", "icons")

def _build_url(**kwargs):
    """
    Creates a URL for the addon, e.g.
    plugin://plugin.video.vska/mode=searchtv
    """
    return URL + "?" + urlencode(kwargs)

def main():
    """
    Addon entry point. Displays 'Movie' and 'TV' buttons
    """
    xbmcplugin.setPluginCategory(HANDLE, "vska")
    xbmcplugin.setContent(HANDLE, "videos")

    movie_item = xbmcgui.ListItem(label="Movies")
    movie_item.setInfo("video", {
        "title": "Movies",
        "mediatype": "video"
    })
    movie_item.setArt({"icon": os.path.join(ICONS_DIR, "movie.png")})
    url = _build_url(mode="searchmovie")
    xbmcplugin.addDirectoryItem(HANDLE, url, movie_item, True)

    tv_item = xbmcgui.ListItem(label="TV")
    tv_item.setInfo("video", {
        "title": "TV",
        "mediatype": "video"
    })
    tv_item.setArt({"icon": os.path.join(ICONS_DIR, "tv.png")})
    url = _build_url(mode="searchtv")
    xbmcplugin.addDirectoryItem(HANDLE, url, tv_item, True)

    key_item = xbmcgui.ListItem(label="TMDb API Key")
    key_item.setInfo("video", {
        "title": "TV",
        "mediatype": "video"
    })
    key_item.setArt({"icon": os.path.join(ICONS_DIR, "key.png")})
    url = _build_url(mode="setkey")
    xbmcplugin.addDirectoryItem(HANDLE, url, key_item, True)

    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(HANDLE)

def _listing(itms):
    """
    Creates a virtual Kodi directory with list items
    """
    xbmcplugin.setPluginCategory(HANDLE, "vska - listing")
    xbmcplugin.setContent(HANDLE, "videos")
    for itm in itms:
        list_item = xbmcgui.ListItem(label=itm["title"])
        title = itm["title"]
        tmdb_id = itm["id"]
        plot = itm["plot"]
        poster = itm["poster"]
        fanart = itm["fanart"]
        _type = itm["type"]
        season = itm.get("season", None)
        episode_number = itm.get("episode", None)
        list_item.setInfo("video", {
            "title": title,
            "plot": plot,
            "mediatype": "video"
        })
        list_item.setArt({
            "icon": poster,
            "fanart": fanart
        })
        if _type == "movie":
            urlparams = {
                "mode": "play",
                "external_id": tmdb_id
            }
            is_folder = False
            list_item.setProperty('IsPlayable', 'true')
        elif _type == "tv":
            urlparams = {
                "mode": "listing",
                "listingtype": "seasons",
                "external_id": tmdb_id
            }
            is_folder = True
        elif _type == "season":
            urlparams = {
                "mode": "listing",
                "listingtype": "episodes",
                "external_id": tmdb_id,
                "season": season
            }
            is_folder = True
        elif _type == "episode":
            urlparams = {
                "mode": "play",
                "external_id": tmdb_id,
                "season": season,
                "episode": episode_number
            }
            is_folder = False
            list_item.setProperty('IsPlayable', 'true')
        url = _build_url(**urlparams)
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)

    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(HANDLE)

def list_movies(query):
    """
    Searches for movies with given query and displays them in a Kodi directory
    """
    results = search_movie(query, TMDB_KEY)
    _listing(results)

def list_tv(query):
    """
    Searches for tv shows with given query and displays them in a Kodi directory
    """
    results = search_tv(query, TMDB_KEY)
    _listing(results)

def list_seasons(external_id):
    """
    Lists all seasons in a given show
    """
    seasons = get_seasons(external_id, TMDB_KEY)
    _listing(seasons)

def list_episodes(external_id, season_number):
    """
    Lists all episodes in a given season
    """
    episodes = get_episodes(external_id, season_number, TMDB_KEY)
    _listing(episodes)

def play(external_id, season_number, episode_number):
    """
    Plays a movie or episode
    """
    if season_number and episode_number:
        url = episode(external_id, season_number, episode_number)
    else:
        url = movie(external_id)
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)

def validate_id(external_id):
    if not external_id:
        raise ValueError("You must provide an external id")

def validate_listingtype(listingtype):
    if not listingtype:
        raise ValueError("You must provide a listing type")

    listingtypes = ["seasons", "episodes"]
    if listingtype not in listingtypes:
        raise ValueError("You must provide a valid listing type: " + listingtype)

def validate_season(season):
    if not season:
        raise ValueError("You must specify a season")

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    """
    params = dict(parse_qsl(paramstring))

    if not params:
        main()
    else:
        mode = params.get("mode", None)
        external_id = params.get("external_id", None)
        season_number = params.get("season", None)
        episode_number = params.get("episode", None)
        listingtype = params.get("listingtype", None)
        if mode == "searchmovie":
            query = xbmcgui.Dialog().input('Search movie...', type=xbmcgui.INPUT_ALPHANUM)
            if query:
                list_movies(query)
            else:
                quit()
        elif mode == "searchtv":
            query = xbmcgui.Dialog().input('Search tv...', type=xbmcgui.INPUT_ALPHANUM)
            if query:
                list_tv(query)
            else:
                quit()
        elif mode == "listing":
            validate_listingtype(listingtype)
            validate_id(external_id)
            if listingtype == "seasons":
                list_seasons(external_id)
            else:
                validate_season(season_number)
                list_episodes(external_id, season_number)
        elif mode == "play":
            validate_id(external_id)
            play(external_id, season_number, episode_number)
        elif mode == "setkey":
            apikey = xbmcgui.Dialog().input('Enter your TMDb API key', type=xbmcgui.INPUT_ALPHANUM)
            if apikey:
                ADDON.setSetting('tmdb_key', apikey)
                xbmc.executebuiltin('Container.Refresh')
            else:
                quit()
        else:
            raise ValueError("Specify a valid mode.")

if __name__ == '__main__':
    router(sys.argv[2][1:])
