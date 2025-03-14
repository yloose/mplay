import re
import json
import xbmc
import urllib3
from datetime import datetime

API_URL = "https://mediathekviewweb.de/api/query" 

http = urllib3.PoolManager()

channel_mappings = {
    "Das Erste HD": "ARD",
    "ZDF HD": "ZDF",
    "3sat": "3Sat",
    "ZDFneo HD": "ZDF",
    "one HD": "ARD",
    "ZDFinfo HD": "ZDF",
    "ARD-alpha": "ARD-alpha",
    "phoenix": "PHOENIX",
    "ARTE HD": "ARTE.DE",
    "KiKA": "KiKA",
    "WDR HD": "WDR",
    "NDR Niedersachen HD": "NDR",
    "BR Fernsehen Süd HD": "BR",
    "SWR Baden-Württemberg HD": "SWR",
    "SR Fernsehen HD": "SR",
    "hr-fernsehen": "HR",
    "MDR Sachsen-Anhalt HD": "MDR",
    "rbb Berlin HD": "RBB",
    "Radio Bremen TV HD": "Radio Bremen TV",
}

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
            raise Exception("Failed to decode response.")
    else:
        raise Exception("MediathekView request failed.")

def find_program(title, channel_name, description=None, date=None):
    channel = channel_mappings.get(channel_name, None) 
    query = build_query(title, channel=channel)
    pgms = perform_request(query)

    xbmc.log(str(len(pgms)), 2)

    if not pgms:
        query = build_query(title)
        pgms = perform_request(query)

    # Search again to reduce results
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
