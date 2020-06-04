def domain_to_str_bytes(domain):
    parts = domain.split('.')
    res = ''
    for i in parts:
        res += '{:02x} '.format(len(i)) + ' '.join('{:02x}'.format(ord(e)) for e in i) + ' '
    return res


def return_hex(data):
    return bytearray.fromhex(data)


def int_to_hex(value, size):
    number = f"{value:x}"
    zeros = size - len(number)
    return return_hex(('0' * zeros) + number)
