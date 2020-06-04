import socket
from work_with_bytes import return_hex_str_form_str
from parsers import parse_answers
from transform import return_hex, domain_to_str_bytes
import argparse


class User:
    def __init__(self, q_name, q_type):
        if q_type not in ['A', 'MX', 'TXT']:
            raise ValueError("Invalid type value")
        self.data = return_hex(insert_info_into_request(q_name, q_type))
        self.address = '127.0.0.1'
        self.port = 53
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(self.data, (self.address, self.port))
            data, sender = s.recvfrom(256)
            answer = parse_answers(data)
            print(answer)


def insert_info_into_request(domain, _type):
    return "4a 4a 01 00 00 01 00 00 00 00 00 00 {} 00 {} 00 01".format(domain_to_str_bytes(domain), return_hex_str_form_str(_type))


def main():
    parser = argparse.ArgumentParser(description='Program for working with a user who uses a caching DNS')
    parser.add_argument('domain', help="The domain you are looking for")
    parser.add_argument('type', default='A', help='The type of record you are looking for; available: A, AAAA, NS, TXT, MX')
    args = parser.parse_args()
    User(args.domain, args.type)


if __name__ == "__main__":
    main()


