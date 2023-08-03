"""Module for server stop."""
from sys import exit as exit_

from network import is_active
from network import stop_server


def stop(*args, **kwargs):
    """Stops server."""
    if is_active():
        stop_server()

    exit_(*args, **kwargs)
