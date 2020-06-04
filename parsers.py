from work_with_bytes import return_type_from_bytes
from main_classes import Question, Request, Answer, Response, Header, Flag
from bitstring import BitArray


def parse_queries(data, count):
    questions = []
    position = 12
    for i in range(count):
        domain, position = parse_domain(data, position)
        _type = return_type_from_bytes(data[position: position + 2])
        questions.append(Question(domain, _type))
        position += 4
    return questions, position


def parse_answer(data, position, count):
    answers = []
    start = position
    for i in range(count):
        domain, position = parse_domain(data, start)
        start = position - 1
        _type = return_type_from_bytes(data[start:start + 2])
        start += 4
        ttl = int.from_bytes(data[start: start + 4], 'big')
        start += 4
        length = int.from_bytes(data[start: start + 2], 'big')
        start += 2
        if _type is None:
            start += length
            continue
        if _type == 'NS':
            answer_data, position = parse_domain(data, start, start + length)
            answers.append(Answer(domain, _type, ttl, length, answer_data))
        elif _type == 'A':
            ip = parse_ip(data[start:start + 4])
            answers.append(Answer(domain, _type, ttl, length, ip))
        else:
            answers.append(Answer(domain, _type, ttl, length, data[start: start + length]))
        start += length
    return answers, start


def parse_request(data):
    header = parse_headers(data)
    queries, position = parse_queries(data, header.qd_count)
    return Request(header, queries, data[:12])


def parse_answers(data):
    header = parse_headers(data)
    queries, position = parse_queries(data, header.qd_count)
    answers, position = parse_answer(data, position, header.an_count)
    authority, position = parse_answer(data, position, header.ns_count)
    additional, position = parse_answer(data, position, header.ar_count)
    return Response(data, header, queries, answers, authority, additional)


def cache_record_as_bytes(records, request):
    record_info = []
    answers = []
    anc = 0
    for i in records:
        anc += len(records[i])
        record_info += records[i]
    for i in record_info:
        answers.append(
            Answer(i.name, i.type, i.ttl, i.length, i.data))
    res = Response(
        b'\x00',
        Header(request.header.id, Flag(BitArray(b'\x80\x80')), request.header.qd_count, anc, 0, 0), request.request, answers
    )
    return res.to_bytes()


def parse_headers(data):
    bit_data = BitArray(data)
    request_id = bit_data.hex[0:4]
    flags = Flag(BitArray(bit_data.bytes[4:6]))
    qdc = int(bit_data.hex[8:12], 16)
    anc = int(bit_data.hex[12:16], 16)
    nsc = int(bit_data.hex[16:20], 16)
    rdc = int(bit_data.hex[20:24], 16)
    return Header(request_id, flags, qdc, anc, nsc, rdc)


def parse_domain(data, s_position, end=None):
    def get_part(part_data):
        part_domain = BitArray(part_data)
        start = 0
        if part_domain.hex[start: start + 2] == 'c0' or part_domain.hex[start: start + 2] == 'c1':
            return parse_domain_link(data, part_data[0: 2])
        else:
            count = int(part_domain.hex[start: start + 2], 16)
            name = bytes.fromhex(part_domain.hex[2:count * 2 + 2]).decode('ascii')
            return count, name
    position = s_position
    names = []
    if end is None:
        end = -1
    while True:
        if position == int(end) + 1:
            position += 1
            break
        new_count, part_name = get_part(data[position:])
        if new_count == 0:
            break
        names.append(part_name)
        position += new_count + 1
        if new_count == 1:
            break
    return '.'.join(names), position + 1


def parse_ip(data):
    res = []
    for i in data:
        res.append(str(int(i)))
    return '.'.join(res)


def parse_domain_link(data, position):
    length = int(BitArray(position).bin[2:], 2)
    domain, count = parse_domain(data, length)
    return 1, domain


def parse_type(data):
    return_type_from_bytes(data)
