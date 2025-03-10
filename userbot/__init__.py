# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot initialization. """

import os

from sys import version_info
from logging import basicConfig, getLogger, INFO, DEBUG
from distutils.util import strtobool as sb

from dotenv import load_dotenv
from requests import get
from telethon import TelegramClient
from pymongo import MongoClient
import redis


load_dotenv("config.env")

# Bot Logs setup:
CONSOLE_LOGGER_VERBOSE = sb(os.environ.get("CONSOLE_LOGGER_VERBOSE", "False"))


if CONSOLE_LOGGER_VERBOSE:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=DEBUG,
    )
else:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=INFO
    )
LOGS = getLogger(__name__)

if version_info[0] < 3 or version_info[1] < 6:
    LOGS.error(
        "You MUST have a python version of at least 3.6."
        " Multiple features depend on this. Bot quitting."
    )
    quit(1)

# Check if the config was edited by using the already used variable
CONFIG_CHECK = os.environ.get("___________PLOX_______REMOVE_____THIS_____LINE__________", None)

if CONFIG_CHECK:
    LOGS.error("Please remove the line mentioned in the first hashtag from the config.env file")
    quit(1)

API_KEY = os.environ.get("API_KEY", None)

API_HASH = os.environ.get("API_HASH", None)

BOTLOG_CHATID = int(os.environ.get("BOTLOG_CHATID", "0"))

BOTLOG = sb(os.environ.get(
    "BOTLOG", "False"
))

PM_AUTO_BAN = sb(os.environ.get("PM_AUTO_BAN", "False"))

CONSOLE_LOGGER_VERBOSE = sb(
    os.environ.get("CONSOLE_LOGGER_VERBOSE", "False")
    )

MONGO_DB_URI = os.environ.get("MONGO_DB_URI", None)

SCREENSHOT_LAYER_ACCESS_KEY = os.environ.get(
    "SCREENSHOT_LAYER_ACCESS_KEY", None
    )

OPEN_WEATHER_MAP_APPID = os.environ.get("OPEN_WEATHER_MAP_APPID", None)

WELCOME_MUTE = sb(os.environ.get(
    "WELCOME_MUTE", "False"
))

YOUTUBE_API_KEY = os.environ.get(
    "YOUTUBE_API_KEY", None
    )

SPOTIFY_USERNAME = os.environ.get("SPOTIFY_USERNAME", None)
SPOTIFY_PASS = os.environ.get("SPOTIFY_PASS", None)
SPOTIFY_BIO_PREFIX = os.environ.get("SPOTIFY_BIO_PREFIX", None)
DEFAULT_BIO = os.environ.get("DEFAULT_BIO", None)

# pylint: disable=invalid-name
bot = TelegramClient("userbot", API_KEY, API_HASH)

if os.path.exists("learning-data-root.check"):
    os.remove("learning-data-root.check")
else:
    LOGS.info("Braincheck file does not exist, fetching...")

URL = 'https://raw.githubusercontent.com/dracarys18/userbot/master/learning-data-root.check'

with open('learning-data-root.check', 'wb') as load:
    load.write(get(URL).content)

# Init Mongo
MONGOCLIENT = MongoClient(MONGO_DB_URI, 27017, serverSelectionTimeoutMS=1)
MONGO = MONGOCLIENT.userbot

def is_mongo_alive():
    try:
        MONGOCLIENT.server_info()
    except:
        return False
    return True
# Init Redis
####### Redis will be hosted inside the docker container that hosts the bot
####### We need redis for just caching, so we just leave it to non-persistent

REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)

def is_redis_alive():
    try:
        REDIS.ping()
        return True
    except:
        return False

# Global Variables
COUNT_MSG = 0
BRAIN_CHECKER = []
USERS = {}
WIDE_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
WIDE_MAP[0x20] = 0x3000
COUNT_PM = {}
LASTMSG = {}
ENABLE_KILLME = True
CMD_HELP = {}
AFKREASON = "no reason"
DISABLE_RUN = False
