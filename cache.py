from transform import return_hex
from main_classes import Request, Response, CacheRecord


class Cache:
    def __init__(self):
        self.info = {}

    def get_from_cache(self, request: Request):
        res = {}
        for i in request.request:
            data = self.info.get((i.domain, i.type))
            if data is not None:
                res[i] = []
                for j in data:
                    if not j.is_not_alive():
                        j.update_ttl()
                        res[i].append(j)
        if res == '':
            return None
        return res

    def add_to_cache(self, response: Response):
        for i in response.get_all_info():
            record = CacheRecord(i.name, i.type, i.ttl, i.length, i.data)
            if (i.name, i.type) in self.info:
                self.info[(i.name, i.type)].append(record)
            else:
                self.info[(i.name, i.type)] = [record]

    def delete_ttl(self):
        new = {}
        for i in self.info:
            temp = []
            for j in self.info[i]:
                if not j.is_not_alive():
                    temp.append(j)
            if len(temp) != 0:
                new[(i[0], i[1])] = temp
        self.info.clear()
        self.info = new

    def store_cache(self):
        lines = []
        self.delete_ttl()
        with open('cache.txt', 'w') as f:
            for i in self.info:
                for j in self.info[i]:
                    parse_data = ''
                    if type(j.data) == bytes or type(j.data) == bytearray:
                        for t in j.data:
                            parse_data += str(int(t)) + ' '
                    else:
                        parse_data = j.data
                    lines.append(f"{str(i[0])}&{str(i[1])}&{j.name}&{j.type}&"
                                 f"{str(j.ttl)}&{str(j.length)}&{parse_data}\n")
            f.writelines(lines)

    def restore_cache(self):
        with open('cache.txt', 'r') as f:
            for i in f.readlines():
                if i == "\n":
                    continue
                spl = i.split('&')
                if len(spl[6].split(' ')) > 1:
                    normal_data = Cache.parse_int_to_bytes(spl[6])
                else:
                    normal_data = spl[6]

                if self.info.get((spl[0], spl[1])) is None:
                    self.info[(spl[0], spl[1])] = []
                    self.info[(spl[0], spl[1])].append(
                        CacheRecord(
                            spl[2], spl[3], int(spl[4]), int(spl[5]), normal_data
                        )
                    )
                else:
                    self.info[(spl[0], spl[1])].append(CacheRecord(
                            spl[2], spl[3], int(spl[4]), int(spl[5]), normal_data
                        ))
        self.delete_ttl()

    @staticmethod
    def parse_int_to_bytes(ints):
        normal_data = ''
        for j in ints.split(' '):
            if j == '\n':
                continue
            hex_char = hex(int(j))[2:]
            if len(hex_char) == 1:
                hex_char = '0' + hex_char
            normal_data += hex_char + ' '
        return return_hex(normal_data)

    def __enter__(self):
        self.restore_cache()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.store_cache()
