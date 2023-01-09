import asyncio
import contextlib
import time

from ledmx.matrix import Matrix
from pathlib import Path

from ledmx.transport import pub


GREEN = 100, 0, 0
RED = 0, 100, 0
BLUE = 0, 0, 100


class Render:
    def __init__(self, matrix: Matrix, lock: asyncio.Lock, fps: int = 60):
        self.__task = None
        self.__lock = lock
        self.__matrix = matrix
        self.__timeout = 1 / fps

    async def __render(self):
        t0 = time.time()
        try:
            while True:
                await asyncio.sleep(10e-9)
                t1 = time.time()
                td = t1 - t0
                if td < self.__timeout:
                    continue
                t0 = t1

                await self.__lock.acquire()
                pub(self.__matrix)
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


async def main():
    lock = asyncio.Lock()
    mtx = Matrix(Path('layout.yaml').read_text())
    render = Render(mtx, lock, 60)
    render.start_loop()

    px_num = 0
    try:
        while True:
            await lock.acquire()
            mtx.off()
            mtx[px_num] = BLUE
            lock.release()
            px_num += 1
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await lock.acquire()
        mtx.off()
        lock.release()
        await render.stop_loop()


if __name__ == '__main__':
    asyncio.run(main())
