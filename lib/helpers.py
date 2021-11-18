import json
import logging
import os
from pythonjsonlogger import jsonlogger
import requests

logger = logging.getLogger('ipochecker')

class Helpers:
  @classmethod
  def headers(cls):
    return {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'Accept-Encoding': 'gzip, deflate',  # No support for brolti in python requests yet.
      'Accept-Language': 'en-GB,en-US;q=0.9,en;'
   }

  @classmethod
  def load_json(cls, url):
    return requests.get(url, headers=Helpers.headers()).json()

  @classmethod
  def json_directory(cls):
    return "./json/"

  @classmethod
  def load_previous_details(cls):
      file_name = Helpers.json_directory() + "ipo_details.json"
      try:
          with open(file_name, "r") as f:
              return json.load(f)
      except FileNotFoundError:
          logging.error("File Not Found")
          return {}

  @classmethod
  def send_error_to_slack(cls, msg):
    blocks = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "There were errors checking the HashiCorp IPO."
        }
    },
    {
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": f"Error: {msg}"
        }
    }]
    return Helpers.post_blocks_to_slack(blocks, "#bingobingo")


  @classmethod
  def post_message_to_slack(cls, filename, changes):
    blocks = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"There were changes to the HashiCorp IPO {filename}."
        }
    }]

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
    return Helpers.post_blocks_to_slack(blocks)

  @classmethod
  def post_blocks_to_slack(cls, blocks, slack_channel=os.environ.get('SLACK_CHANNEL')):
      slack_token = os.environ.get('SLACK_TOKEN')
      logging.debug(blocks)
      logging.debug(f"Sending request to Slack (channel {slack_channel}")
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