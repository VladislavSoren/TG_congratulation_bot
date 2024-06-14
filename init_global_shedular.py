import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# jobstores = {
# 'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
# }
# Schedule = AsyncIOScheduler(jobstores=jobstores)

global_scheduler = AsyncIOScheduler()

print(f"init crud id - {id(global_scheduler)}")
