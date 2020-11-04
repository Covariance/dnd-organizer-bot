import random


def parse_expr(expr):
    return DiceParser(expr).parse()


class DiceParser:
    __signs = {'+': 1, '-': -1}

    def __init__(self, expr):
        self.__source = expr
        self.__pos = 0
        self.__entities = []

    def __empty(self):
        return self.__pos >= len(self.__source)

    def __next(self):
        if self.__empty():
            self.__pos += 1
            return self.__source[self.__pos - 1]
        return '\0'

    def __test(self, ch):
        return self.__source[self.__pos] == ch

    def __skip_ws(self):
        while not self.__empty() and self.__source[self.__pos].isspace():
            self.__pos += 1

    @staticmethod
    def __process_entity(entity, sign):
        if len(entity) == 0:
            raise RuntimeError('missing dice or const')
        dig = 0
        while dig < len(entity) and entity[dig].isdigit():
            dig += 1
        if dig == len(entity):
            return DiceParser.__signs[sign] * int(entity), sign + entity
        count = 1 if dig == 0 else int(entity[:dig])
        if entity[dig] != 'd' or not entity[dig + 1:].isdigit():
            raise Exception('invalid dice format: ' + entity)
        value = int(entity[dig + 1:])

        results = [random.randint(1, value) for i in range(count)]
        return \
            DiceParser.__signs[sign] * sum(results), \
            sign + '(' + ' + '.join(map(str, results)) + ')'

    def __parse_entity(self, sign):
        if self.__empty():
            raise Exception('unexpected expression end at ' + str(self.__pos))
        end = self.__pos
        while end < len(self.__source) and not self.__source[end].isspace():
            end += 1

        self.__entities.append(DiceParser.__process_entity(self.__source[self.__pos:end], sign))
        self.__pos = end

    def __parse_pool(self, sign):
        self.__skip_ws()
        self.__parse_entity(sign)
        self.__skip_ws()
        if not self.__empty():
            if self.__source[self.__pos] not in DiceParser.__signs.keys():
                raise Exception('unexpected character ' + self.__source[self.__pos]
                                + ' at ' + str(self.__pos))
            self.__pos += 1
            self.__parse_pool(self.__source[self.__pos - 1])

    def __parse_seq(self):
        self.__skip_ws()
        if self.__empty():
            raise Exception('expression is empty')
        if self.__source[self.__pos] in DiceParser.__signs.keys():
            self.__skip_ws()
            self.__pos += 1
            self.__parse_pool(self.__source[self.__pos - 1])
        else:
            self.__parse_pool('+')

    def parse(self):
        self.__parse_seq()
        sm = 0
        log = ''
        for entity in self.__entities:
            sm += entity[0]
            log += entity[1]
        return str(sm) + ': ' + log
