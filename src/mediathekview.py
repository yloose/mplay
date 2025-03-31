import re
import os
import json
import xbmc
import urllib3
import xbmcvfs
import xbmcaddon
from datetime import datetime

API_URL = "https://mediathekviewweb.de/api/query" 

http = urllib3.PoolManager()

def get_channel_mappings():
    with open(os.path.join(xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo("profile")), "channel_mappings.json")) as f:
        try:
            return json.loads(f.read())
        except Exception as e:
            xbmc.log(f"Could not read channel mappings file: {str(e)}", 2)
            return {}


def build_query(title, channel=None, description=None):
    return json.dumps({
        "queries": 
            ([{"fields": ["title", "topic"], "query": title}] if title else []) +
            ([{"fields": ["channel"], "query": channel}] if channel else []) +
            ([{"fields": ["description"], "query": description}] if description else []),
        "sortBy": "timestamp",
        "sortOrder": "desc",
        "future": True
    })

def perform_request(query):
    res = http.request(
        "POST",
        API_URL,
        body=query,
        headers={"Content-Type": "text/plain"}
    )
    if res.status == 200:
        try:
            data = json.loads(res.data.decode("utf-8"))
            return data["result"]["results"]
        except json.JSONDecodeError:
            raise Exception(xbmcaddon.Addon().getLocalizedString(32104))
    else:
        raise Exception(xbmcaddon.Addon().getLocalizedString(32105))

def find_program(title, channel_name, description=None, date=None):
    # First search with title and channel
    channel = get_channel_mappings().get(channel_name, None) 
    xbmc.log(f"Searching for program with title {title} and date {date}", xbmc.LOGDEBUG)
    query = build_query(title, channel=channel)
    pgms = perform_request(query)

    # No results for first search => search again only with title
    if not pgms:
        query = build_query(title)
        pgms = perform_request(query)

    # Too many results => search again with description
    if len(pgms) > 10 and description:
        # Filter description for first eight words
        sanitized_description = " ".join(re.sub("[.,]", "", description).split(" ")[:8])
        query = build_query(title, channel=channel, description=sanitized_description)
        pgmsDescriptionFilter = perform_request(query)
        if pgmsDescriptionFilter:
            pgms = pgmsDescriptionFilter

    # Check if there is a program with exact matching date
    if len(pgms) > 10 and date:
        for pgm in pgms:
            if datetime.fromtimestamp(pgm["timestamp"]) == date:
                pgms = [pgm]
                break

    # Remove programs that are audio descriptions
    pgmsAudioDescriptionFilter = [pgm for pgm in pgms if "Audiodeskription" not in pgm["title"]]
    if len(pgmsAudioDescriptionFilter) != 0:
        pgms = pgmsAudioDescriptionFilter

    return pgms[:10]
