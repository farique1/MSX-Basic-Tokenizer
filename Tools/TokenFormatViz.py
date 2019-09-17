# Format a tokenized MSX Basic program to display a line of basic per line of tokens
# Also can interleave another tokenized file to compare them line by line

import argparse

file_load = ['BasicOthers/expert.bas',
             'BasicOthers/expert.bto']
file_save = 'BasicOthers/expert.btc'

parser = argparse.ArgumentParser(description='Format MSX tokenized binary.')
parser.add_argument("-lb", default=file_load[0], help='The file to format.')
parser.add_argument("-lc", default=file_load[1], help='A second file to compare.')
parser.add_argument("-sa", default=file_save, help='The formatted output file.')
args = parser.parse_args()

file_load[0] = args.lb
file_load[1] = args.lc
file_save = args.sa

file_load = [file_load[0]] if file_load[1] == '' else file_load
file_save = file_load if file_save == '' else file_save


def bytes_from_file(filename, chunksize=8192):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                for b in chunk:
                    yield b
            else:
                break


def get_next_addrs(pos):
    return int(bin_file[pos + 1] + bin_file[pos], 16) - int('8000', 16) - 1


for file in file_load:
    bin_file = []
    for b in bytes_from_file(file):
        bin_file.append('{0:02x}'.format(ord(b)))

    bin_file.remove('ff')
    bin_form = []
    byte_line = ''
    next_addrs = get_next_addrs(0)
    prev_addrs = 0
    for n, byte in enumerate(bin_file):
        byte_line += byte
        if n != prev_addrs + 0 and n != prev_addrs + 2:
            byte_line += ' '
        if n == next_addrs - 1:
            line_num = str(int(byte_line[7:9] + byte_line[5:7], 16))
            bin_form.append(line_num + ': ' + byte_line + '\n')
            byte_line = ''
            prev_addrs = next_addrs
            next_addrs = get_next_addrs(n + 1)
    bin_form.insert(0, '"' + file + '"' + '\n')
    if file == file_load[0]:
        comp_form = bin_form
        blnk_form = ['\n'] * len(comp_form)

if len(file_load) > 1:
    lists = [comp_form, bin_form, blnk_form]
    bin_form = [val for pair in zip(*lists) for val in pair]

with open(file_save, 'w') as f:
    for line in bin_form:
        f.write(line)
