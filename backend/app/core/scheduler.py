import asyncio
import logging

logger = logging.getLogger("v-suitcase.scheduler")


async def periodic_cleanup(cleanup_fn, interval_seconds: int = 600):
    while True:
        try:
            await cleanup_fn()
        except Exception as e:
            logger.error("Cleanup task failed: %s", e)
        await asyncio.sleep(interval_seconds)
