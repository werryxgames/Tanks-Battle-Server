from network import stop_server, is_active
from sys import exit


def stop(*args, **kwargs):
    if is_active():
        stop_server()

    exit(*args, **kwargs)
