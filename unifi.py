import logging
import os
import re
import sys
from time import sleep

import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ITEM_NAME = os.environ.get("ITEM_NAME")
ITEM_URL = os.environ.get("ITEM_URL")

pattern = re.compile('"inventory_quantity":[0-999999]')

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class BadResponseException(Exception):
    pass


def send_message(message):
    myobj = {
        'displayName': f"{ITEM_NAME} Inventory Check",
        'text': message
    }
    x = requests.post(WEBHOOK_URL, json=myobj)
    return x.status_code, x.reason


def check_inventory():
    resp = requests.get(ITEM_URL)
    if resp.status_code != 200:
        logger.info("Did not get a valid response from unifi, exiting")
        send_message(f"Cannot reach Unifi Website! {ITEM_URL}")
        raise BadResponseException

    script = BeautifulSoup(resp.text, "html.parser").find("script",
                                                          text=pattern)
    if script:
        match = pattern.search(str(script))
        if match:
            qty = match.group()[-1]
            if qty.strip() == "0":
                logger.info("No inventory, checking again in one minute")
                sleep(60)
                logging.info("exiting...")
                sys.exit()  # In Docker we can exit and it'll restart the container to prevent memory leaks
            else:
                logger.info(f"Quantity available: {qty}")
                send_message(
                    f"{ITEM_NAME} available! Quantity: {qty}. {ITEM_URL}")
                return


logger.info("Starting service")
logger.info(f"Webhook URL: {WEBHOOK_URL}")
logger.info(f"Item Name: {ITEM_NAME}")
logger.info(f"Item URL: {ITEM_URL}")
try:
    check_inventory()
except KeyboardInterrupt:
    # quit
    logger.info("Interrupt received, shutting down")
    sys.exit()
except BadResponseException:
    sys.exit()
