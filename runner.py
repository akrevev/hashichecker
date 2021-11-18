# -*- coding: utf-8 -*-
import logging
from pythonjsonlogger import jsonlogger
import requests
import os
from os.path import exists
import json
import time
from shutil import copyfile

logger = logging.getLogger()

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

json_directory = "./json/"
current_quote_file = json_directory + "current_quote.json"
current_overview_file = json_directory + "current_overview.json"

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',  # No support for brolti in python requests yet.
    'Accept-Language': 'en-GB,en-US;q=0.9,en;'
}

def has_difference(previous_details, details):
    logging.debug("Checking difference")

    changes = {}
    for key in details:
        if key in previous_details:
            if details[key] != previous_details[key]:
                logging.debug("Details have changed", extra={'old': previous_details[key], 'new': details[key]})
                changes[key] = {
                    'old': previous_details[key],
                    'new': details[key]
                }
        else:
            changes[key] = {
                'old': '',
                'new': details[key]
            }
    return changes

def load_previous_details(file_name):
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("File Not Found")
        return {"data": {}}

def post_message_to_slack(filename, changes):
    slack_token = os.environ.get('SLACK_TOKEN')
    slack_channel = os.environ.get('SLACK_CHANNEL')
    logging.debug("Posting message to slack", extra={'changes': changes})

    blocks = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"There were changes to the HashiCorp IPO {filename}."
        }
    }]

    logging.debug(blocks)

    for change in changes:
        fieldchanged = change[0].upper() + change[1:]
        oldvalue = changes[change]["old"]
        newvalue = changes[change]["new"]
        blocks.append(
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{fieldchanged}* changed from `{oldvalue}` to `{newvalue}`"
            }
        }
        )

    logging.debug(blocks)
    logging.debug("Sending request to Slack")
    response = requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': slack_channel,
        'text': "NASDAQ Alert",
        'icon_emoji': ':hashi-celebrate:',
        'username': "NASDAQ",
        'blocks': json.dumps(blocks) if blocks else None
    }).json()

    if response['ok'] == False:
        logging.error(f"There was an error - {response['error']}")
        logging.error(response)
        return False

    logging.debug("Slack notified")
    return True

if __name__ == '__main__':
    previous_quote = load_previous_details(current_quote_file)
    quote = requests.get("https://api.nasdaq.com/api/quote/HCP/info?assetclass=ipo", headers=headers).json()

    quote_changes = has_difference(previous_quote["data"], quote["data"])
    if quote_changes != {}:
        if exists(current_quote_file):
            change_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
            change_file = json_directory + "/quote_" + change_time + "_changes.json"
            f = open(change_file, "w")
            f.write(str(json.dumps(quote_changes, indent=4, sort_keys=True)))
            f.close()
            newfile = json_directory + "/quote_" + change_time + ".json"
            copyfile(current_quote_file, newfile)

        data = json.dumps(quote, indent=4, sort_keys=True)
        f = open(current_quote_file, "w")
        f.write(data)
        post_message_to_slack("quote", quote_changes)


    previous_overview = load_previous_details(current_overview_file)
    overview = requests.get('https://api.nasdaq.com/api/ipo/overview/?dealId=1035813-101007', headers=headers).json()

    overview_changes = has_difference(previous_overview["data"], overview["data"])
    if overview_changes != {}:
        if exists(current_overview_file):
            change_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
            change_file = json_directory + "/overview_" + change_time + "_changes.json"
            f = open(change_file, "w")
            f.write(str(json.dumps(overview_changes, indent=4, sort_keys=True)))
            f.close()
            newfile = json_directory + "/overview_" + change_time + ".json"
            copyfile(current_overview_file, newfile)


        data = json.dumps(overview, indent=4, sort_keys=True)
        f = open(current_overview_file, "w")
        f.write(data)
        post_message_to_slack("overview", quote_changes)