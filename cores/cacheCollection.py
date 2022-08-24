import shutil
from pathlib import Path
from loguru import logger
from graia.scheduler.timers import crontabify
from graia.saya import Channel
from graia.scheduler.saya.schema import SchedulerSchema

channel = Channel.current()


@channel.use(SchedulerSchema(crontabify("0 0 */2 * *")))
async def cacheCollection():
    cachePath = Path('./cache')
    for path in cachePath.iterdir():
        if 'log' not in str(path):
            print(path)
            try:
                shutil.rmtree(path)
            except OSError as e:
                logger.error("Error: %s : %s" % (path, e.strerror))
