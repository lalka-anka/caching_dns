import socket
from bitstring import BitArray
from parsers import parse_request, parse_answers, cache_record_as_bytes
from transform import return_hex
from main_classes import Request, Question, Header, Flag
from cache import Cache

err = '80 01 00 00 00 00 00 00 00 00'
any = 'aa 1a 01 00 00 01 00 00 00 00 00 00'
a = 'aa aa 01 00 00 01 00 00 00 00 00 00'


def is_none(cache, request):
    data = cache.get_from_cache(request)
    if data is None:
        return None
    return data


def get_error_response(request):
    return return_hex(f'{request.header.id}' + err)


def find_any_record_on_ns(response, domain):
    req = Request(Header('aaaa', Flag(BitArray(b'\x01\x00')), 1, 0, 0, 0),
                  [Question(domain, 'ANY')], return_hex(any))
    req_bytes = req.to_bytes()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(req_bytes, (response.response[0].data, 53))
        data, sender = s.recvfrom(512)
        response = parse_answers(data)
    return response


class Server:
    def __init__(self):
        self.port = 53
        self.local_address = '127.0.0.1'
        self.yandex_dns = '77.88.8.8'
        # yandex resolver

    def begin(self):
        with Cache() as cache:
            data, sender = self.socket_listener.recvfrom(512)
            while data:
                if data:
                    request = parse_request(data)
                    records = is_none(cache, request)
                    if records:
                        res = cache_record_as_bytes(records, request)
                        self.socket_listener.sendto(res, sender)
                    else:
                        resp = self.get_from_ns(request)
                        cache.add_to_cache(resp)
                        records = is_none(cache, request)
                        if records:
                            res = cache_record_as_bytes(records, request)
                            self.socket_listener.sendto(res, sender)
                        else:
                            find_req = Request(request.header,
                                               [Question(request.request[0].domain, request.request.type)],
                                               request.byte_header)
                            byte_request = find_req.to_bytes()
                            self.socket_resolver.sendto(byte_request, (self.yandex_dns, self.port))
                            answer, s = self.socket_resolver.recvfrom(512)
                            cache.add_to_cache(parse_answers(answer))
                            self.socket_listener.sendto(answer, sender)
                data, sender = self.socket_listener.recvfrom(512)
                cache.delete_ttl()

    def get_from_ns(self, request: Request):
        answer = self.find_ns(request)
        answer = self.find_ip_for_ns(answer)
        return find_any_record_on_ns(answer, request.request[0].domain)

    def find_ns(self, request: Request):
        ns_request = Request(
            request.header,
            [Question(request.request[0].domain, 'NS')],
            request.byte_header)
        byte_request = ns_request.to_bytes()
        self.socket_resolver.sendto(byte_request, (self.yandex_dns, self.port))
        answer, sender = self.socket_resolver.recvfrom(512)
        answer = parse_answers(answer)
        return answer

    def find_ip_for_ns(self, response):
        domain = response.get_all_info()[0].data
        request = Request(Header('aaaa', Flag(BitArray(b'\x01\x00')), 1, 0, 0, 0), [Question(domain, 'A')],
                          return_hex(a))
        req_bytes = request.to_bytes()
        self.socket_resolver.sendto(req_bytes, (self.yandex_dns, self.port))
        data, sender = self.socket_resolver.recvfrom(512)
        data = parse_answers(data)
        return data

    def __enter__(self):
        self.socket_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_listener.bind((self.local_address, self.port))
        self.socket_resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('server works')
        print('port: ' + str(self.port))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket_listener.close()
        self.socket_resolver.close()


with Server() as server:
    server.begin()
