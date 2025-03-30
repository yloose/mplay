import json
import xbmc
from datetime import datetime, timezone

def get_all_channel_groups():
    query = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "PVR.GetChannelGroups",
        "params": {
            "channeltype": "tv"
        }
    }
    return json.loads(xbmc.executeJSONRPC(json.dumps(query)))["result"]["channelgroups"]

def get_channels_by_channel_group(channel_group_id):
    query = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "PVR.GetChannels",
        "params": {
            "channelgroupid": channel_group_id,
            "properties": ["channel", "channelnumber" ]
        }
    }
    return json.loads(xbmc.executeJSONRPC(json.dumps(query)))["result"]["channels"]

def get_all_channels():
    channels = []
    
    channel_groups = get_all_channel_groups()
    for cg in channel_groups:
        channels = channels + (get_channels_by_channel_group(cg["channelgroupid"]))

    return channels

def get_channel_id_by_channel_number(channel_number):
    channels = get_all_channels()
    channel = [chnl for chnl in channels if chnl["channelnumber"] == channel_number][0]
    return channel["channelid"]

def get_broadcast_details_by_broadcast_id(broadcast_id):
    query = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "PVR.GetBroadcastDetails",
        "params": {
            "broadcastid": broadcast_id,
            "properties": ["plot"]
        }
    }

    return json.loads(xbmc.executeJSONRPC(json.dumps(query)))["result"]["broadcastdetails"]

def get_broadcasts_by_channel_id(channel_id):
    query = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "PVR.GetBroadcasts",
        "params": {
            "channelid": channel_id,
            "properties": ["title", "starttime", "episodename"]
        }
    }

    return json.loads(xbmc.executeJSONRPC(json.dumps(query)))["result"]["broadcasts"]

def get_program_by_channel_number_and_date(channel_number, date):
    channel_id = get_channel_id_by_channel_number(channel_number)
    broadcasts = get_broadcasts_by_channel_id(channel_id)
    
    for bc in broadcasts:
        if datetime.fromisoformat(bc["starttime"]).replace(tzinfo=timezone.utc) == date.astimezone(timezone.utc):
            bc_details = get_broadcast_details_by_broadcast_id(bc["broadcastid"])
            return bc | bc_details
