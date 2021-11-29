from lib.ipo_details import *
from os.path import exists
import json
import time
from shutil import copyfile
import logging

class IPOChecker:
  logger = logging.getLogger('ipochecker')

  @classmethod
  def run(cls):
    # load up cached details
    previous_ipo_details = IPODetails().from_cache()
    # get latest details
    current_ipo_details = IPODetails().from_api()
    # compare and get changes
    changes = previous_ipo_details.diff(current_ipo_details)

    if changes != {}:
        logger.info(f'Changes detected: {changes}')

        ipo_details_file = Helpers.json_directory() + "ipo_details.json"

        if exists(ipo_details_file):
            change_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
            change_file = Helpers.json_directory() + "ipo_details_" + change_time + "_changes.json"
            logger.info(f"Backing up previous details to {change_file}")
            f = open(change_file, "w")
            f.write(str(json.dumps(changes, indent=4, sort_keys=True)))
            f.close()

            backup_file = Helpers.json_directory() + "/ipo_details_" + change_time + ".json"
            copyfile(ipo_details_file, backup_file)

        f = open(ipo_details_file, "w")
        f.write(current_ipo_details.to_json())
        f.close()
        Helpers.post_message_to_slack("quote", changes)

    else:
        logger.info("No IPO details changes")