import sys
import json
import xbmc
import xbmcgui
from datetime import datetime, timedelta
from kodi import get_program_by_channel_number_and_date

from mediathekview import find_program

def play_program(program):
    player = xbmc.Player()
    player.play(program["url_video_hd"])

if __name__ == "__main__":
    labelTitle = xbmc.getInfoLabel("Listitem.Title")
    labelDate = xbmc.getInfoLabel("Listitem.Date")
    labelChName = xbmc.getInfoLabel("Listitem.ChannelName")
    labelChNum = xbmc.getInfoLabel('Listitem.ChannelNumberLabel')

    title = labelTitle
    channel = labelChName.split(" ")[0]
    channelNum = int(labelChNum)
    date = datetime.strptime(labelDate, "%d-%m-%Y %H:%M")

    program = get_program_by_channel_number_and_date(channelNum, date - timedelta(hours=1))

    try:
        if program is None:
            raise Exception("Internal error")

        pgms = find_program(f"{program["title"]} {program["episodename"]}", channel, description=program["plot"], date=date)
        if len(pgms) == 0:
            xbmcgui.Dialog().notification("Mediathek Play", "No programs found.")
        elif len(pgms) == 1:
            play_program(pgms[0]) 
        else:
            selection = xbmcgui.Dialog().select("Please select a program", [f"{pgm["channel"]} | {pgm["topic"]} {pgm["title"]}" for pgm in pgms], preselect=0)
            if selection >= 0:
                play_program(pgms[selection])

    except Exception as e:
        xbmcgui.Dialog().ok("Failed to find/play program.", f"The error encountered was:\n{repr(e)}")
