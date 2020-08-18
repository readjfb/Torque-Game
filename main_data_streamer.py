from multiprocessing.connection import Client
from data_streamer import streamer

"""
Very simple script! Just connects to the multiprocessing socket,
creates a data streamer object, then calls whichever data strem method
is desired.

Multiprocessing sockets make the data streaming really easy, as there's
built in pickling/ unpickling of the data, so we can just throw the whole
data sequence from data_streamer into a tuple, and just send that on

Tuple format is being used for consistency wth the admin_control, and for
potential future enhancements to program that could result in this script
sending multiple types of message
"""


def cast_data(data):
    try:
        conn.send(("DATA", data))
        # conn.send(("DATA", (leftT, rightT, time)))
    except BrokenPipeError:
        # Pipe is one way, so there's an error when the main program is
        # terminated, and the pipe is cut. Therefore quit
        quit()


if __name__ == '__main__':
    port = 6007
    address = ('localhost', port)
    conn = Client(address)

    stream = streamer()

    print("sending data")

    # uncomment the type of stream desired
    stream.arduino_stream(cast_data, 1000, usb_port='/dev/cu.usbserial-DA011ECL')
    # stream.fake_stream(cast_data, 1000)

    conn.close()
