import asyncio
import contextlib
import time

import yaml

from ledmx.multiverse import Multiverse
from pathlib import Path


GREEN = 100, 0, 0
RED = 0, 100, 0
BLUE = 0, 0, 100


class Render:
    def __init__(self, mv: Multiverse, lock: asyncio.Lock, fps: int = 60):
        self.__task = None
        self.__lock = lock
        self.__mv = mv
        self.__timeout = 1 / fps

    async def __render(self):
        t0 = time.time()
        try:
            while True:
                await asyncio.sleep(10e-6)
                t1 = time.time()
                td = t1 - t0
                if td < self.__timeout:
                    continue
                t0 = t1

                await self.__lock.acquire()
                self.__mv.pub()
                self.__lock.release()
        except KeyboardInterrupt:
            return

    def start_loop(self):
        if self.__task is not None:
            return None
        self.__task = asyncio.create_task(self.__render())

    async def stop_loop(self):
        if self.__task is None:
            return
        self.__task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await self.__task

        self.__task = None


async def main(layout_filename: str):
    layout = yaml.safe_load(Path(layout_filename).read_text())
    lock = asyncio.Lock()
    mvs = Multiverse(layout)
    render = Render(mvs, lock, 60)
    render.start_loop()

    px_num = 0
    try:
        while True:
            print(px_num)
            await lock.acquire()
            mvs.off()
            mvs[px_num] = BLUE
            lock.release()
            px_num += 1
            await asyncio.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        await lock.acquire()
        mvs.off()
        lock.release()
        await render.stop_loop()


if __name__ == '__main__':
    asyncio.run(main('layout.yaml'))

