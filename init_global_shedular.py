import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

global_scheduler = AsyncIOScheduler()
