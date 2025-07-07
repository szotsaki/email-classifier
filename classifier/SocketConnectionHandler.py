import sys
from socketserver import BaseRequestHandler


class SocketConnectionHandler(BaseRequestHandler):
    def __init__(self, timeout: int, max_email_size: int, processing_callback, *args, **kwargs):
        self._timeout = timeout
        self._max_email_size = max_email_size
        self._callback = processing_callback

        super().__init__(*args, **kwargs)

    def handle(self):
        self.request.settimeout(self._timeout)

        data = bytearray()
        try:
            while len(data) < self._max_email_size:
                packet: bytes = self.request.recv(self._max_email_size - len(data))
                if packet:
                    # If EOT (End of Transmission) is found, process the response up until that point, then return
                    eot_pos = packet.find(b'\x04')
                    if eot_pos != -1:
                        data.extend(packet[:eot_pos])
                        break
                    else:
                        data.extend(packet)
                else:
                    # Empty response means the client has disconnected
                    print("The client has disconnected without waiting for the response", file=sys.stderr)
                    return
        except TimeoutError:
            print("Timed out while receiving data from the client", file=sys.stderr)

        if data:
            response = self._callback(data)
            try:
                self.request.sendall(response)
            except BrokenPipeError:
                print("The client closed the connection before the response was sent", file=sys.stderr)
