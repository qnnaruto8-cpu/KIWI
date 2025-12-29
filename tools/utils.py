import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor

# Ye executor background threads manage karega
executor = ThreadPoolExecutor(max_workers=10)

async def run_sync(func, *args, **kwargs):
    """
    Magic Function: 
    Ye kisi bhi blocking function (Search/Download) ko 
    background thread me run karta hai taaki Bot Freeze na ho.
    """
    loop = asyncio.get_running_loop()
    # Function aur arguments ko pack karke thread me bhejo
    pfunc = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(executor, pfunc)
  
