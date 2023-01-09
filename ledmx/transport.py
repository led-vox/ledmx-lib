import socket
from ledmx.matrix import Matrix
from ledmx.artnet.packet import art_dmx


def send(data: bytes, ip: str, port: int = 6454) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sck:
        if ip.endswith('.255'):
            sck.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sck.sendto(data, (ip, port))


def pub(mx: Matrix) -> None:
    for addr, data in mx.get_packets():
        packet = art_dmx(bytes(data), addr.net, addr.subnet, addr.universe)
        send(packet, addr.ip)

