"""
Реализация асинхронного изменения и рендеринга матрицы,
изменения значений байт в матрице и её отправка в сеть
производятся асинхронно, в разных корутинах
"""

import asyncio
import contextlib
import time
from itertools import cycle

from ledmx.multiverse import Multiverse
from ledmx.layout import parse_file


GREEN = 100, 0, 0
RED = 0, 100, 0
BLUE = 0, 0, 100


class Render:
    """
    класс рендера, в теле корутины периодически отправляет
    всю матрицу в сеть с заданными интервалом
    """
    def __init__(self, mv: Multiverse, lock: asyncio.Lock, fps: int = 60):
        """
        конструктор рендера

        :param mv:Multiverse: указатель на мультивёрс
        :param lock:asyncio.Lock: локер для блокировки доступа к данным
        :param fps:int=60: желаемая частота отсылки данных
        """
        self.__task = None
        self.__lock = lock
        self.__mv = mv
        self.__timeout = 1 / fps

    async def __render(self):
        """
        воркер - корутина, периодически проверяет
        сколько времени прошло после предыдущей отправки данных,
        если время вышло - данные в матрице блокируются и рассылаются
        """
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
        """
        запуск воркера
        """
        if self.__task is not None:
            return None
        self.__task = asyncio.create_task(self.__render())

    async def stop_loop(self):
        """
        остановка воркера
        """
        if self.__task is None:
            return
        self.__task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await self.__task

        self.__task = None


async def main(mvs: Multiverse):
    """
    корутина обновления данных в матрице

    :param mvs: Multiverse - указатель на мультивёрс
    """

    # локер для блокировки данных
    lock = asyncio.Lock()

    # экземпляр рендера
    render = Render(mvs, lock, 60)

    # запуск рендера
    render.start_loop()

    # цикличный итератор по цветам
    colors = cycle([BLUE, RED, GREEN])

    # текущий активный цвет
    active_color = next(colors)

    # текущий активный пиксел
    px_num = 0

    # направление движения
    px_step = 1
    try:
        # бесконечный цикл
        while True:
            # захват локера
            await lock.acquire()

            # очистка матрицы (забивка нулями)
            mvs.off()

            # текущему пикселу задаётся текущий цвет
            mvs[px_num] = active_color

            # высвобождение локера
            lock.release()

            # инкремент счётчика циклов в заданном направлении
            px_num += px_step

            # если насчитали 599 циклов
            if px_num == 599:

                # шаг - в обратную сторону
                px_step = -1

                # меняем текущий активный цвет на следующий
                active_color = next(colors)

            # если на первом пикеселе
            if px_num == 1:

                # направление - "вперёд"
                px_step = 1

                # меняем текущий активный цвет на следующий
                active_color = next(colors)

            # таймаут
            await asyncio.sleep(0.02)

    # обработка прерывания Ctrl-C
    except KeyboardInterrupt:
        pass
    finally:
        # захват локера
        await lock.acquire()

        # очистка матрицы
        mvs.off()

        # высвобождение локера
        lock.release()

        # ожидание завершения цикла рендера
        await render.stop_loop()


if __name__ == '__main__':

    # парсим конфиг
    layout = parse_file('layout.yaml')

    # строим мультивёрс
    m_verse = Multiverse(layout)

    try:
        # запускаем основную корутину
        asyncio.run(main(m_verse))
    # обработка прерывания Ctrl-C
    except KeyboardInterrupt:
        pass
    finally:
        # очищаем матрицу
        m_verse.off()

        # рендерим
        m_verse.pub()
