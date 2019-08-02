'''
MSX Basic Tokenizer
v0.1
Copyright (c) 2019 - Fred Rique.
https://github.com/farique1/MSX-Basic-Tokenizer

Save an MSX Basic program in tokenized format
Program starts with FF
Then the lines (starting at 8001)
  First 2 bytes point to the begining of the next ilne: last - first
  Next 2 bytes are the line number: last - first
  Then the tokenized code
  Line ends with 00
The program ends with 0000

TODO: Check the order of the instructions on the list.
        If a smaller has the same chars of the start of a larger one it will be picked first. Larger should come first
      Whatever else. There should be thousands of fringe cases not covered here o.O !

NOTE: MSX &b tokenizes anything after it as characters except when a command is reched (but not '=' for instance)
        The implementation here only looks for 0 and 1, reverting back to the normal parsing on other characters
      Different behaviour from MSX while encoding overflowed lines on jump instructions
        MSX seems to split the number (with 0e) in legal parts, here it throw an error
      Line number too high throw an error
      Line number out of order throw an error
'''

import re
import binascii
import argparse
import os.path

tokens = [('>', 'ee'), ('PAINT', 'bf'), ('=', 'ef'), ('ERROR', 'a6'), ('ERR', 'e2'), ('<', 'f0'), ('+', 'f1'),
          ('FIELD', 'b1'), ('PLAY', 'c1'), ('-', 'f2'), ('FILES', 'b7'), ('POINT', 'ed'), ('*', 'f3'), ('POKE', '98'),
          ('/', 'f4'), ('FN', 'de'), ('^', 'f5'), ('FOR', '82'), ('PRESET', 'c3'), ('\\', 'fc'), ('PRINT', '91'), ('?', '91'),
          ('PSET', 'c2'), ('AND', 'f6'), ('GET', 'b2'), ('PUT', 'b3'), ('GOSUB', '8d'), ('READ', '87'), ('GOTO', '89'),
          ('ATTR$', 'e9'), ('RENUM', 'aa'), ('AUTO', 'a9'), ('IF', '8b'), ('RESTORE', '8c'), ('BASE', 'c9'), ('IMP', 'fa'),
          ('RESUME', 'a7'), ('BEEP', 'c0'), ('INKEY$', 'ec'), ('RETURN', '8e'), ('BLOAD', 'cf'), ('INPUT', '85'),
          ('BSAVE', 'd0'), ('INSTR', 'e5'), ('RSET', 'b9'), ('CALL', 'ca'), ('_', '5f'), ('RUN', '8a'), ('IPL', 'd5'), ('SAVE', 'ba'),
          ('KEY', 'cc'), ('SCREEN', 'c5'), ('KILL', 'd4'), ('SET', 'd2'), ('CIRCLE', 'bc'), ('CLEAR', '92'), ('CLOAD', '9b'),
          ('LET', '88'), ('SOUND', 'c4'), ('CLOSE', 'b4'), ('LFILES', 'bb'), ('CLS', '9f'), ('LINE', 'af'), ('SPC(', 'df'),
          ('CMD', 'd7'), ('LIST', '93'), ('SPRITE', 'c7'), ('COLOR', 'bd'), ('LLIST', '9e'), ('CONT', '99'), ('LOAD', 'b5'),
          ('STEP', 'dc'), ('COPY', 'd6'), ('LOCATE', 'd8'), ('STOP', '90'), ('CSAVE', '9a'), ('CSRLIN', 'e8'),
          ('STRING$', 'e3'), ('LPRINT', '9d'), ('SWAP', 'a4'), ('LSET', 'b8'), ('TAB(', 'db'), ('MAX', 'cd'), ('DATA', '84'),
          ('MERGE', 'b6'), ('THEN', 'da'), ('TIME', 'cb'), ('DEFDBL', 'ae'), ('TO', 'd9'), ('DEFINT', 'ac'), ('DEF', '97'),
          ('TROFF', 'a3'), ('DEFSNG', 'ad'), ('TRON', 'a2'), ('DEFSTR', 'ab'), ('MOD', 'fb'), ('USING', 'e4'),
          ('DELETE', 'a8'), ('MOTOR', 'ce'), ('USR', 'dd'), ('DIM', '86'), ('NAME', 'd3'), ('DRAW', 'be'), ('NEW', '94'),
          ('VARPTR', 'e7'), ('NEXT', '83'), ('VDP', 'c8'), ('DSKI$', 'ea'), ('NOT', 'e0'), ('DSKO$', 'd1'), ('VPOKE', 'c6'),
          ('OFF', 'eb'), ('WAIT', '96'), ('END', '81'), ('ON', '95'), ('WIDTH', 'a0'), ('OPEN', 'b0'), ('XOR', 'f8'),
          ('EQV', 'f9'), ('OR', 'f7'), ('ERASE', 'a5'), ('OUT', '9c'), ('ERL', 'e1'), ('REM', '8f'),

          ("'", '3a8fe6'), ('ELSE', '3aa1'),

          ('PDL', 'ffa4'), ('EXP', 'ff8b'), ('PEEK', 'ff97'), ('FIX', 'ffa1'), ('POS', 'ff91'), ('FPOS', 'ffa7'),
          ('ABS', 'ff86'), ('FRE', 'ff8f'), ('ASC', 'ff95'), ('ATN', 'ff8e'), ('HEX$', 'ff9b'), ('BIN$', 'ff9d'),
          ('INP', 'ff90'), ('RIGHT$', 'ff82'), ('RND', 'ff88'), ('INT', 'ff85'), ('CDBL', 'ffa0'), ('CHR$', 'ff96'),
          ('CINT', 'ff9e'), ('LEFT$', 'ff81'), ('SGN', 'ff84'), ('LEN', 'ff92'), ('SIN', 'ff89'), ('SPACE$', 'ff99'),
          ('SQR', 'ff87'), ('LOC(', 'ffac28'), ('STICK', 'ffa2'), ('COS', 'ff8c'), ('LOF', 'ffad'), ('STR$', 'ff93'),
          ('CSNG', 'ff9f'), ('LOG', 'ff8a'), ('STRIG', 'ffa3'), ('LPOS', 'ff9c'), ('CVD', 'ffaa'), ('CVI', 'ffa8'),
          ('CVS', 'ffa9'), ('TAN', 'ff8d'), ('MID$', 'ff83'), ('MKD$', 'ffb0'), ('MKI$', 'ffae'), ('MKS$', 'ffaf'),
          ('VAL', 'ff94'), ('DSKF', 'ffa6'), ('VPEEK', 'ff98'), ('OCT$', 'ff9a'), ('EOF', 'ffab'), ('PAD', 'ffa5')]

jumps = ['RESTORE', 'AUTO', 'RENUM', 'DELETE', 'RESUME', 'ERL', 'ELSE', 'RUN', 'LIST', 'LLIST',
         'GOTO', 'RETURN', 'THEN', 'GOSUB']

file_load = ''  # Source file
file_save = ''  # Destination file
verbose_level = 1
is_from_build = False

parser = argparse.ArgumentParser(description='Tokenize ASCII MSX Basic')
parser.add_argument("input", nargs='?', default=file_load, help='Source file (preferible .asc)')
parser.add_argument("output", nargs='?', default=file_save, help='Destination file ([source].bas) if missing')
parser.add_argument("-vb", default=verbose_level, type=int, choices=[0, 1, 2, 3], help="Verbosity level: 0 silent, 1 erros, 2 +warnings(def), 3 +details")
parser.add_argument("-fb", default=is_from_build, action='store_true', help="Tell it is running from a build system")
args = parser.parse_args()

file_load = args.input
file_save = args.output
if args.output == '':
    save_path = os.path.dirname(file_load)
    save_path = '' if save_path == '' else save_path + '/'
    save_file = os.path.basename(file_load)
    save_file = os.path.splitext(save_file)[0][0:8] + '.bas'
    file_save = save_path + save_file
verbose_level = args.vb
is_from_build = args.fb


def show_log(line_number, text, level, **kwargs):
    global is_from_build
    global file_load
    bullets = ['    ', '--- ', '*** ', '  - ', '  * ']

    try:
        bullet = kwargs['bullet']
    except KeyError:
        bullet = level

    display_file_name = ''
    if is_from_build and bullet == 2:
        display_file_name = os.path.basename(file_load) + ': '
    line_number = str(line_number) if line_number == '' else '(' + str(line_number) + '): '

    if verbose_level >= level:
        print bullets[bullet] + display_file_name + line_number + text


def update_lines(source, compiled):
    global line_compiled
    global line_source
    if len(line_source) > 2:
        line_source = line_source[source:]
        line_compiled = line_compiled + compiled
        show_log('', ' '.join([line_compiled + '|' + line_source.rstrip()]), 3)


def parse_numeric_bases(nugget_comp, token, base):
    global line_number
    if not nugget_comp:
        nugget_comp = ''
        hexa = '0000'
    else:
        if int(nugget_comp, base) > 65535:
            show_log('', ''.join(['overflow', str(line_number)]), 1, bullet=2)
            show_log('', 'Execution_stoped\n', 1, bullet=0)
            raise SystemExit(0)
        hexa = '{0:04x}'.format(int(nugget_comp, base))
    return token + hexa[2:] + hexa[:-2]


ascii_code = []
if file_load:
    try:
        with open(file_load, 'r') as f:
            for line in f:
                if line.strip() == "" or line.strip().isdigit():
                    continue
                ascii_code.append(line.strip() + '\r\n')
    except IOError:
        show_log('', ' '.join(['source_not_found', file_load]), 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)
else:
    show_log('', 'source_not_given', 1, bullet=2)
    show_log('', 'Execution_stoped\n', 1, bullet=0)
    raise SystemExit(0)

show_log('', '', 3, bullet=0)

base = 0x8001
line_order = 0
tokenized_code = ['ff']
for line_source in ascii_code:
    line_compiled = ''

    show_log('', ' '.join([line_compiled + '|' + line_source.rstrip()]), 3)

    # Get line number
    nugget = re.match(r'\s*\d+\s?', line_source).group()
    line_number = nugget.strip()
    if int(line_number) <= line_order:
        show_log(line_number, ' '.join(['line_number_out_of_order', str(line_number)]), 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)
    if int(line_number) > 65529:
        show_log(line_number, ' '.join(['line_number_too_high', str(line_number)]), 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)
    line_order = int(line_number)
    line_source = line_source[len(nugget):]
    hexa = '{0:04x}'.format(int(nugget))
    line_compiled += hexa[2:] + hexa[:-2]

    show_log('', ' '.join([line_compiled + '|' + line_source.rstrip()]), 3)

    # Look for instructions
    while len(line_source) > 2:
        for command, token in tokens:
            if line_source.upper().startswith(command):
                compiled = token
                source = len(command)
                update_lines(source, compiled)

                # Is a jumping instructions
                if command in jumps:
                    while True:
                        nugget = re.match(r'(\s*)(\d+)', line_source)
                        if nugget:
                            nugget_spaces = nugget.group(1)
                            nugget_line = nugget.group(2)

                            if int(nugget_line) > 65529:
                                show_log(line_number, ' '.join(['line_number_jump_too_high', str(nugget_line)]), 1, bullet=2)
                                show_log('', 'Execution_stoped\n', 1, bullet=0)
                                raise SystemExit(0)
                            hex_spaces = '20' * len(nugget_spaces)
                            hexa = '{0:04x}'.format(int(nugget_line))
                            compiled = hex_spaces + '0e' + hexa[2:] + hexa[:-2]
                            source = len(nugget_spaces) + len(nugget_line)
                            update_lines(source, compiled)

                            # Has several jumps (on goto/gosub)
                            has_comma = re.match(r'(\s*)(,)', line_source)
                            if has_comma:
                                has_comma_spaces = has_comma.group(1)
                                has_comma_comma = has_comma.group(2)
                                hex_spaces = '20' * len(has_comma_spaces)
                                hexa = '{0:02x}'.format(ord(has_comma_comma))
                                compiled = hex_spaces + hexa
                                source = len(has_comma_spaces) + len(has_comma_comma)
                                update_lines(source, compiled)
                        else:
                            break

                # Instruction with literal data after it
                if command == 'DATA' or command == 'REM' or command == "'" or command == 'CALL' or command == '_':
                    while True:
                        character = line_source[0]
                        if command == 'CALL' or command == '_':
                            character = character.upper()
                        hexa = '{0:02x}'.format(ord(character))
                        compiled = hexa
                        source = 1
                        update_lines(source, compiled)

                        if len(line_source) <= 2 \
                                or (command == 'DATA' and line_source[0] == ':') \
                                or (command == '_' and (line_source[0] == ':' or line_source[0] == '('))\
                                or (command == 'CALL' and (line_source[0] == ':' or line_source[0] == '(')):
                            break
                break

        # Look each character
        else:
            nugget = line_source[0].upper()

            # Is a number
            if nugget.isdigit() or nugget == '.':
                nugget = re.match(r'(\d*)\s*(.)', line_source)
                nugget_number = nugget.group(1)
                nugget_integer = nugget.group(1)
                nugget_fractional = ''
                nugget_signal = nugget.group(2)

                # Is floating point
                if nugget_signal == '.':
                    nugget = re.match(r'(\d*)\s*(.)\s*(\d*)\s*(.)', line_source)
                    nugget_number = nugget.group(1) + nugget.group(3)
                    nugget_number = '0' if nugget_number == '' else nugget_number
                    nugget_integer = nugget.group(1)
                    nugget_fractional = '.' + nugget.group(3)
                    nugget_signal = nugget.group(4)

                # Has integer signal
                if nugget_signal == '%':
                    nugget_number = nugget_integer
                    print nugget_number
                    if int(nugget_number) >= 32768:
                        show_log(line_number, ' '.join(['overflow', str(nugget_number)]), 1, bullet=2)
                        show_log('', 'Execution_stoped\n', 1, bullet=0)
                        raise SystemExit(0)
                elif nugget_signal != '%' and nugget_signal != '!' and nugget_signal != '#':
                    nugget_signal = ''

                # Is single precision
                if (int(nugget_number) >= 32768 and int(nugget_number) <= 999999) \
                        or (nugget_signal == '!' and int(nugget_number) <= (10 ** 63 - 1)) \
                        or (nugget_fractional != '' and int(nugget_number) <= 999999):

                    nugget_stripped = nugget_integer.lstrip('0')
                    if nugget_stripped == '':
                        nugget_stripped = '0'
                        hexa_precision = '00'
                    else:
                        hexa_precision = '{0:02x}'.format(len(nugget_stripped) + 64)

                    hexa = '1d' + hexa_precision
                    nugget_cropped = float(nugget_number[0:6] + '.' + nugget_number[6:])
                    nugget_cropped = str(int(round(nugget_cropped)))

                    for character in nugget_cropped:
                        hexa += character
                    hexa += '0' * (10 - len(hexa))

                # Is double precision
                elif (int(nugget_number) >= 1000000 and int(nugget_number) <= (10 ** 63 - 1)) \
                        or (nugget_signal == '#' and int(nugget_number) <= (10 ** 63 - 1)) \
                        or (nugget_fractional != '' and int(nugget_number) <= (10 ** 63 - 1)):

                    nugget_stripped = nugget_integer.lstrip('0')
                    if nugget_stripped == '':
                        nugget_stripped = '0'
                        hexa_precision = '00'
                    else:
                        hexa_precision = '{0:02x}'.format(len(nugget_stripped) + 64)

                    hexa = '1f' + hexa_precision
                    nugget_cropped = float(nugget_number[0:14] + '.' + nugget_number[14:])
                    nugget_cropped = str(int(round(nugget_cropped)))  # THEN crop to single precision

                    for character in nugget_cropped:
                        hexa += character
                    hexa += '0' * (18 - len(hexa))
                    hexa = hexa[0:18]

                # Is normal integer
                elif int(nugget_number) >= 0 and int(nugget_number) <= 9:
                    nugget_add = str(int(nugget_number) + 17)
                    hexa = '{0:02x}'.format(int(nugget_add))

                elif int(nugget_number) >= 10 and int(nugget_number) <= 255:
                    hexa = '0f' + '{0:02x}'.format(int(nugget_number))

                elif int(nugget_number) >= 256 and int(nugget_number) <= 32767:
                    hexa = '{0:04x}'.format(int(nugget_number))
                    hexa = '1c' + hexa[2:] + hexa[:-2]

                else:
                    show_log(line_number, ' '.join(['number_too_high', str(nugget_number.lstrip('0'))]), 1, bullet=2)
                    show_log('', 'Execution_stoped\n', 1, bullet=0)
                    raise SystemExit(0)

                compiled = hexa
                source = len(nugget_integer) + len(nugget_fractional) + len(nugget_signal)
                update_lines(source, compiled)

            # Other bases
            elif nugget == '&':
                nugget = line_source[0:2].upper()
                if nugget == '&H':
                    nugget_comp = re.match(r'[0-9a-f]*', line_source[2:].lower()).group()
                    hexa = parse_numeric_bases(nugget_comp, '0c', 16)
                elif nugget == '&O':
                    nugget_comp = re.match(r'[0-7]*', line_source[2:]).group()
                    hexa = parse_numeric_bases(nugget_comp, '0b', 8)
                elif nugget == '&B':
                    nugget_comp = re.match(r'[01]*', line_source[2:]).group()
                    hexa = '2642'
                    if nugget_comp:
                        for character in nugget_comp:
                            hexa += '{0:02x}'.format(ord(character))
                    else:
                        nugget_comp = ''
                else:
                    nugget = '&'
                    hexa = '{0:02x}'.format(ord(nugget))
                    nugget_comp = ''
                compiled = hexa
                source = len(nugget) + len(nugget_comp)
                update_lines(source, compiled)

            # Quotes
            else:
                nugget = line_source[0]
                if nugget == '"':
                    num_quotes = 0
                    while True:
                        if line_source[0] == '"':
                            num_quotes += 1
                        hexa = '{0:02x}'.format(ord(line_source[0]))
                        compiled = hexa
                        source = 1
                        update_lines(source, compiled)
                        if num_quotes > 1 or len(line_source) <= 2:
                            break
                else:
                    compiled = '{0:02x}'.format(ord(nugget.upper()))
                    source = 1
                    update_lines(source, compiled)

    base += (len(line_compiled) + 6) / 2
    hexa = '{0:04x}'.format(base)
    line_compiled = hexa[2:] + hexa[:-2] + line_compiled
    line_compiled += '00'
    tokenized_code.append(line_compiled)

tokenized_code.append('0000')

# show_log('', ' '.join([str(tokenized_code)]), 3)
show_log('', '', 3, bullet=0)

with open(file_save, 'wb') as f:
    for line in tokenized_code:
        f.write(binascii.unhexlify(line))
