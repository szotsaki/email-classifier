import os
import shutil
import sys
from functools import partial
from socketserver import ThreadingUnixStreamServer

from .SocketConnectionHandler import SocketConnectionHandler


class SocketListener:
    def __init__(self, timeout: int, max_email_size: int, processing_callback):
        self._timeout = timeout
        self._max_email_size = max_email_size
        self._callback = processing_callback


class UnixSocketListener(SocketListener):
    def __init__(self, socket: str, uid: int | str, gid: int | str, timeout: int, max_email_size: int,
                 processing_callback):
        super().__init__(timeout, max_email_size, processing_callback)

        if isinstance(uid, str) and uid.isdigit():
            uid = int(uid)
        if isinstance(gid, str) and gid.isdigit():
            gid = int(gid)

        self._socket = socket
        self._uid = uid
        self._gid = gid

        try:
            socket_dir = os.path.dirname(self._socket)
            os.makedirs(socket_dir, exist_ok=True)
        except PermissionError as e:
            print(f"Could not create socket directory. {e}", file=sys.stderr)
            exit(1)

        if os.path.exists(self._socket):
            os.unlink(self._socket)

    def listen(self):
        try:
            handler = partial(SocketConnectionHandler, self._timeout, self._max_email_size, self._callback)
            with ThreadingUnixStreamServer(self._socket, handler) as server:
                try:
                    try:
                        shutil.chown(self._socket, self._uid, self._gid)
                    except (PermissionError, LookupError, OverflowError) as e:
                        print(f'Could not set the permission of the socket "{self._socket}". {e}', file=sys.stderr)
                        exit(1)

                    print(f"Listening on {self._socket}")
                    server.serve_forever()
                except KeyboardInterrupt:
                    print("Shutting down")
                    if os.path.exists(self._socket):
                        os.unlink(self._socket)
                    pass

                server.server_close()
        except PermissionError as e:
            print(f'Could not create socket "{self._socket}". {e}', file=sys.stderr)
            exit(1)
