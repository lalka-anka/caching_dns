def return_type(data):
    if data == "0000":
        return 'standard'
    if data == "0001":
        return 'inverse'
    if data == "0010":
        return 'status'
    return 'unknown'


def return_byte_type(data: str):
    if data == 'standard':
        return b'\x00\x00'
    if data == 'inverse':
        return b'\x00\x01'
    if data == 'status':
        return b'\x00\x10'
    return b'\x00\x00'


def return_hex_str_form_str(data):
    if data == 'A':
        return '00 01'
    if data == 'AAAA':
        return '00 1c'
    if data == 'MX':
        return '00 0f'
    if data == 'NS':
        return '00 02'
    if data == 'CNAME':
        return '00 05'
    if data == 'PTR':
        return '00 0c'
    if data == 'ANY':
        return '00 ff'
    if data == 'TXT':
        return '00 10'
    if data == 'SOA':
        return '00 06'


def return_type_from_bytes(data):
    if data == b'\x00\x01':
        return 'A'
    if data == b'\x00\x1c':
        return 'AAAA'
    if data == b'\x00\x0f':
        return 'MX'
    if data == b'\x00\x02':
        return 'NS'
    if data == b'\x00\x05':
        return 'CNAME'
    if data == b'\x00\x0c':
        return 'PTR'
    if data == b'\x00\xff':
        return 'ANY'
    if data == b'\x00\x10':
        return 'TXT'
    if data == b'\x00\x06':
        return 'SOA'


def return_bytes_form_str(data):
    if data == 'A':
        return b'\x00\x01'
    if data == 'AAAA':
        return b'\x00\x1c'
    if data == 'MX':
        return b'\x00\x0f'
    if data == 'NS':
        return b'\x00\x02'
    if data == 'CNAME':
        return b'\x00\x05'
    if data == 'PTR':
        return b'\x00\x0c'
    if data == 'ANY':
        return b'\x00\xff'
    if data == 'TXT':
        return b'\x00\x10'
    if data == 'SOA':
        return b'\x00\x06'
