from bitstring import BitArray
from work_with_bytes import return_type, return_hex_str_form_str, return_bytes_form_str
import time
import math
from hashlib import md5
from transform import domain_to_str_bytes, int_to_hex, return_hex


class CacheRecord:
    def __init__(self, name, _type, ttl, length, data):
        self.name = name
        self.type = _type
        self.ttl = ttl
        self.length = length
        self.time_added = time.time()
        self.data = data

    def is_not_alive(self):
        return time.time() - self.time_added > self.ttl

    def update_ttl(self):
        self.ttl = math.floor(self.time_added + self.ttl - time.time())

    def __str__(self):
        return f"{self.name} {self.type} {math.floor(self.ttl)}"

    def __hash__(self):
        return int(md5(self.name.encode() + self.type.encode()).hexdigest(), 16)


class Flag:
    def __init__(self, flags: BitArray):
        self.flags = flags
        self.is_request = flags[0]
        self.type = return_type(flags.bin[1:5])
        self.tc = flags[5]
        self.rd = flags[6]
        self.ra = flags[7]

    def to_bytes(self):
        return return_hex(self.flags.hex)

    def __str__(self):
        return f"Is request: {self.is_request}; type: {self.type}"


class Header:
    def __init__(self, request_id, flags, qdc, anc, nsc, arc):
        self.id = request_id
        self.flags = flags
        self.qd_count = qdc
        self.an_count = anc
        self.ns_count = nsc
        self.ar_count = arc

    def to_bytes(self):
        id_bytes = return_hex(self.id)
        flags_bytes = self.flags.to_bytes()
        return id_bytes + flags_bytes + int_to_hex(self.qd_count, 4) + int_to_hex(self.an_count, 4) + int_to_hex(self.ns_count, 4) + int_to_hex(self.ar_count, 4)

    def __str__(self):
        return f"Flags: {str(self.flags)}; req_id: {self.id}"


class Question:
    def __init__(self, domain, _type):
        self.domain = domain
        self.type = _type

    def to_bytes(self):
        return return_hex(domain_to_str_bytes(self.domain) + ' 00 ' +
                          return_hex_str_form_str(self.type)) + b'\x00\x01'

    def __str__(self):
        return f"Domain: {self.domain}; Type: {self.type}"


class Answer:
    def __init__(self, name, _type, ttl, length, data):
        self.name = name
        self.type = _type
        self.ttl = ttl
        self.length = length
        self.data = data

    def to_bytes(self):
        name_bytes = return_hex(domain_to_str_bytes(self.name))
        type_bytes = return_bytes_form_str(self.type)
        ttl_bytes = int_to_hex(self.ttl, 8)
        length_bytes = int_to_hex(self.length, 4)
        if self.type == 'NS':
            data_bytes = return_hex(domain_to_str_bytes(self.data))
        elif self.type == 'A':
            data_bytes = return_hex('{:02X}{:02X}{:02X}{:02X}'.format(*map(int, self.data.split("."))))
        else:
            if type(self.data) == str:
                data_bytes = return_hex(self.data)
            else:
                data_bytes = self.data
        return name_bytes + type_bytes + b'\x00\x01' + ttl_bytes + length_bytes + data_bytes

    def __str__(self):
        return f"Name: {self.name}, type: {self.type}, ttl: {self.ttl}, data: {self.data} \n"


def is_none(obj):
    if obj is None:
        return []
    else:
        return obj
    
    
class Response:
    def __init__(self, data, header, request, response, authority=None, additional=None):
        self.data_bytes = data
        self.header = header
        self.request = request
        self.response = response
        self.authority = is_none(authority)
        self.additional = is_none(additional)

    def get_all_info(self):
        return self.response + self.authority + self.additional

    def to_bytes(self):
        header_bytes = self.header.to_bytes()
        questions_bytes = b''
        for i in self.request:
            questions_bytes += i.to_bytes()
        answers_bytes = b''
        for i in self.response:
            answers_bytes += i.to_bytes()
        return header_bytes + questions_bytes + answers_bytes

    def __str__(self):
        return f"{self.header} \nREQUEST:" \
               f" {'; '.join(map(str, self.request))} \nRESPONSE: {''.join(map(str, self.response))}"


class Request:
    def __init__(self, header, request, byte_header=None):
        self.header = header
        self.byte_header = byte_header
        self.request = request

    def to_bytes(self):
        byte_questions = b''
        for i in self.request:
            byte_questions += i.to_bytes() + b'\x00\x01'
        return self.byte_header + byte_questions

    def __str__(self):
        return f"{self.header} \nREQUEST: {'; '.join(map(str, self.request))}"
