import datetime as dt
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

timezone = pytz.timezone('Asia/Kolkata')  # IST timezone (you can replace with pytz.utc for UTC)

scheduler = AsyncIOScheduler(timezone=timezone)
scheduler.start()

time = dt.datetime.now(pytz.timezone('Asia/Kolkata'))

print(time)