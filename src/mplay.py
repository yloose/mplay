import time
import xbmc
import xbmcgui
import xbmcaddon
from datetime import datetime
from kodi import get_program_by_channel_number_and_date

from mediathekview import find_program

def play_program(program):
    # Not all programs have hd videos avaiable
    # so we try all possible streaming urls here
    url = ""
    for key in ["url_video_hd", "urL_video", "url_video_low"]:
        if key in program and program[key] != "":
            url = program[key]
            break

    if url == "":
        raise Exception(xbmcaddon.Addon().getLocalizedString(32106))

    player = xbmc.Player()
    player.play(url)

if __name__ == "__main__":
    labelTitle = xbmc.getInfoLabel("Listitem.Title")
    labelDate = xbmc.getInfoLabel("Listitem.Date")
    labelChName = xbmc.getInfoLabel("Listitem.ChannelName")
    labelChNum = xbmc.getInfoLabel('Listitem.ChannelNumberLabel')
    
    title = labelTitle
    channel = labelChName.split(" ")[0]
    channelNum = int(labelChNum)

    # Get correct time format
    date_format = xbmc.getRegion("dateshort")
    date = datetime(*(time.strptime(labelDate, f"{date_format} %H:%M")[0:6]))

    program = get_program_by_channel_number_and_date(channelNum, date)

    try:
        if program is None:
            raise Exception(xbmcaddon.Addon().getLocalizedString(32101))

        pgms = find_program(f'{program["title"]} {program["episodename"]}', channel, description=program["plot"], date=date)

        if len(pgms) == 0:
            xbmcgui.Dialog().notification("Mediathek Play", xbmcaddon.Addon().getLocalizedString(32002))
        elif len(pgms) == 1:
            play_program(pgms[0]) 
        else:
            selection = xbmcgui.Dialog().select(xbmcaddon.Addon().getLocalizedString(32003), [f'{pgm["channel"]} | {pgm["topic"]} {pgm["title"]}' for pgm in pgms], preselect=0)
            if selection >= 0:
                play_program(pgms[selection])

    except Exception as e:
        xbmcgui.Dialog().ok(xbmcaddon.Addon().getLocalizedString(32102), f"{xbmc.Addon().getLocalizedString(32103)}:\n{repr(e)}")
