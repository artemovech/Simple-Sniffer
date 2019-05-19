import argparse
import os
import socket
import struct
import time


class Ethernet:
    def __init__(self, raw_data):
        dest, src, prototype = struct.unpack('! 6s 6s H', raw_data[:14])
        self.dest_mac = self.get_mac_address(dest)
        self.src_mac = self.get_mac_address(src)
        self.proto = socket.htons(prototype)
        self.data = raw_data[14:]

    @staticmethod
    def get_mac_address(mac_raw):
        byte_str = map('{:02x}'.format, mac_raw)
        mac_address = ':'.join(byte_str).upper()
        return mac_address


def parsing(filename):
    with open(filename, "w+") as f:
        f.write("TIME,IP,DESTINATION,SOURCE,PROTOCOL,\n")
        while True:
            try:
                raw_data, addr = s.recvfrom(16384)
                eth = Ethernet(raw_data)
                t = time.strftime('%d/%m %H:%M:%S')
                f.write(f"{t},{addr[0]},{eth.dest_mac},{eth.src_mac},{eth.proto}\n")
                f.flush()
                os.fsync(f.fileno())
                print(f"{t} | {addr[0]} | {eth.dest_mac} | {eth.src_mac} | {eth.proto}")
            except Exception as e:
                print(f">>> Error >>> {e}")


def setup(HOST, PORT):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        s.bind((HOST, PORT))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    except Exception as e:
        print(f"SETUP ERROR >>> {e}")
        quit(1)
    return s


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--h', required=False)
    parser.add_argument('--p', required=False)
    args = parser.parse_args()
    HOST = vars(args)['h']
    PORT = vars(args)['p']
    if not PORT:
        PORT = 0
    if not HOST:
        HOST = socket.gethostbyname(socket.gethostname())
    s = setup(HOST, PORT)
    filename = f"{time.strftime('%H%M%S')}_log.csv"
    parsing(filename)
