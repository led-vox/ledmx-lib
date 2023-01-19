"""
Основные классы - модели в мультивёрсе
"""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True, unsafe_hash=True)
class UniAddr:
    """
    Адрес вселенной
    """
    node: str  # имя узла
    host: str  # адрес узла
    net: int  # номер сети
    subnet: int  # номер подсети
    out_idx: int  # индекс выхода на узле
    uni_idx: int  # индекс вселенной на узле

    def __repr__(self) -> str:
        """ текстовый вывод адреса """
        return f'{self.node}[{self.host}]n:{self.net}|s:{self.subnet}|o:{self.out_idx}|u:{self.uni_idx}'


@dataclass
class Universe:
    """
    Вселенная
    """
    addr: UniAddr  # адрес
    data: np.ndarray  # данные (массив байт)


@dataclass(frozen=True)
class PixInfo:
    """
    Пиксель
    """
    data: np.ndarray  # указатель на данные пикселя в матрице
    uni: Universe  # указатель на вселенную, в которой находится пиксель
    offset: int  # значение смещения относительно начала вселенной для данных пикселя
