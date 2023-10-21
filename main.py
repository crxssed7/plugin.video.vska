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

from resources.lib.vidsrc import movie, episode

if sys.version_info >= (3,0,0):
    from urllib.parse import urlencode, parse_qsl
else:
    from urllib import urlencode
    from urlparse import parse_qsl

URL = sys.argv[0]
HANDLE = int(sys.argv[1])
ADDON = xbmcaddon.Addon(id="plugin.video.vska")

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

    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_SIZE)
    xbmcplugin.endOfDirectory(HANDLE)

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    """
    params = dict(parse_qsl(paramstring))

    if not params:
        main()
    else:
        raise NotImplementedError("Not yet implemented.")

if __name__ == '__main__':
    router(sys.argv[2][1:])
