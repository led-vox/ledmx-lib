import asyncio
import contextlib
import time

import yaml

from ledmx.multiverse import Multiverse
from pathlib import Path


GREEN = 10, 0, 0
RED = 0, 10, 0
BLUE = 0, 0, 10


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


async def main(mvs: Multiverse):
    lock = asyncio.Lock()
    render = Render(mvs, lock, 60)
    render.start_loop()

    px_num = 0
    px_step = 1
    try:
        while True:
            print(px_num)
            await lock.acquire()
            mvs.off()
            mvs[px_num] = BLUE
            lock.release()
            px_num += px_step
            if px_num == 599:
                px_step = -1
            if px_num == 1:
                px_step = 1
            await asyncio.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        await lock.acquire()
        mvs.off()
        lock.release()
        await render.stop_loop()


if __name__ == '__main__':
    layout = yaml.safe_load(Path('layout.yaml').read_text())
    m_verse = Multiverse(layout)
    try:
        asyncio.run(main(m_verse))
    except KeyboardInterrupt:
        pass
    finally:
        m_verse.off()
        m_verse.pub()
