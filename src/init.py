import os
import xbmc
import shutil
import xbmcvfs
import xbmcaddon

def init_addon_data_dir():
    addon_dir = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo("path"))
    data_dir = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo("profile"))

    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)

    if not os.path.exists(os.path.join(data_dir, "channel_mappings.json")):
        shutil.copy(os.path.join(addon_dir, "resources/channel_mappings.json"), os.path.join(data_dir, "channel_mappings.json"))


if __name__ == "__main__":
    init_addon_data_dir()
