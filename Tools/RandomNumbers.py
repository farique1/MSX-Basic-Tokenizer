# Number generator test for MSXBatoken
# Generate integer, single, double and scientific notation

from random import randrange

lines = 1000
is_notation = True
file_save = 'DiskToken/notAut.asc'

signs = '#!%'
numbers_arr = []

for item in range(1, lines + 1):
    sign = ''
    integer = ''
    fractio = ''
    integer_size = randrange(10)
    fractio_size = randrange(10)
    dot_prob = randrange(2)
    sign_prob = randrange(4)

    for i in range(integer_size):
        digit = str(randrange(10))
        integer += digit

    dot = '.' if dot_prob == 0 else ''

    for i in range(fractio_size):
        digit = str(randrange(10))
        fractio += digit

    number = integer + dot + fractio
    if number == '' or number == '.':
        number = '0'
        integer = '0'
        fractio = '0'

    if is_notation:
        precision = 'e' if sign_prob < 2 else 'd'
        sign = '-' if randrange(2) < 1 else '+'
        number += precision + sign + str(randrange(10))
    else:
        if sign_prob < 3:
            if sign_prob == 2 and int(integer + fractio) <= 32767:
                number += signs[sign_prob]
            elif sign_prob < 2 and int(integer + fractio) <= 999999:
                number += signs[sign_prob]
            elif sign_prob < 1 and int(integer + fractio) <= (10 ** 63 - 1):
                number += signs[sign_prob]

    line = ' '.join([str(item * 10), 'print', number])
    print ' '.join([str(item * 10), 'print', number])
    numbers_arr.append(line)

with open(file_save, 'w') as f:
    for line in numbers_arr:
        f.write(line + '\r\n')
