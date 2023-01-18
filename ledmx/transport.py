import socket


def send(data: bytes, host: str, port: int = 6454) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sck:
        if host.endswith('.255'):
            sck.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sck.sendto(data, (host, port))
