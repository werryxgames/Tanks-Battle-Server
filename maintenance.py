import socket
import json


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 7490))
    PREPARED_BYTES = json.dumps([-1, ["login_fail", 8, 0, "Сервер на техобслуживании"]]).encode("UTF-8")
    print("Server started")

    while True:
        try:
            adrdata = sock.recvfrom(1024)
        except (ConnectionResetError,  ConnectionAbortedError):
            continue

        sock.sendto(PREPARED_BYTES, adrdata[1])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Server stopped")
