#!/usr/bin/env python3
"""
openMSX Basic (de)Tokenizer
v1.3
Uses openMSX to tokenize ASCII MSX Basic or vice-versa.

Copyright (C) 2019-2020 - Fred Rique (farique)
https://github.com/farique1/MSX-Basic-Tokenizer

See also:
MSX Sublime Tools at
https://github.com/farique1/MSX-Sublime-Tools
Syntax Highlight, Theme, Build System, Comment Preference and Auto Completion.

MSX Basic Dignified at
https://github.com/farique1/msx-basic-dignified
Convert modern MSX Basic Dignified to traditional MSX Basic format.

openmsxbatoken.py <source> <destination> [args...]
openmsxbatoken.py -h for help.

New: 1.3 14-02-2020
    Python 3.8.
    Better subprocess call and IO handling.
    Improved verbose output.
    Changed -fb to -frb.
    Warning issued if didn' delete original.
    Fixed bug and better handling when trying to load or save files with spaces and more than 8 characters.
        Files opened on openMSX now are internally cropped to 8 char and have spaces replaced with _
        Error if conflicting file names due to disk format limitations.
"""

# for i in *.bas; do python openmsxbatoken.py "$i" -asc; done
# *** CAUTION *** An autoexec.bas on the mounted folder will crash the script

import os.path
import argparse
import subprocess
import configparser
from os import remove as osremove

file_load = ''              # Source file
file_save = ''              # Destination file
machine_name = ''           # openMSX machine to open, eg: 'Sharp_HB-8000_1.2' 'Sharp_HB-8000_1.2_Disk' 'Philips_NMS_8250'
disk_ext_name = ''          # openMSX extension to open, eg: 'Microsol_Disk:SlotB'
show_output = True          # Show the openMSX stderr output
output_format = 't'         # Tokenized or ASCII output: t-tokenized a-ASCII
delete_original = False     # Delete the original file
verbose_level = 3           # Show processing status: 0-silent 1-+erros 2-+warnings 3-+steps 4-+details
is_from_build = False       # Tell if it is being called from a build system (show file name on error messages and other stuff)
openmsx_filepath = ''       # Path to openMSX ('' = local path)


def show_log(line, text, level, **kwargs):
    bullets = ['', '*** ', '  * ', '--- ', '  - ', '    ']

    try:
        bullet = kwargs['bullet']
    except KeyError:
        bullet = level

    display_file_name = ''
    if is_from_build and (bullet == 1 or bullet == 2):
        display_file_name = os.path.basename(file_load) + ': '

    line_number = line

    if verbose_level >= level:
        print(bullets[bullet] + display_file_name + line_number + text)
        # print bullets[bullet] + text

    if bullet == 1:
        if proc:
            proc.stdin.write('<command>type_via_keybuf poke-2,0\\r</command>')
        if is_from_build:
            print('    Tokenizing_aborted')
        else:
            print('    Execution_stoped')
            print()
        raise SystemExit(0)


local_path = os.path.split(os.path.abspath(__file__))[0] + '/'
if os.path.isfile(local_path + 'openMSXBatoken.ini'):
    config = configparser.ConfigParser()
    config.sections()
    try:
        config.read(local_path + 'openMSXBatoken.ini')
        file_load = config.get('DEFAULT', 'file_load') if config.get('DEFAULT', 'file_load') else file_load
        file_save = config.get('DEFAULT', 'file_save') if config.get('DEFAULT', 'file_save') else file_save
        machine_name = config.get('DEFAULT', 'machine_name') if config.get('DEFAULT', 'machine_name') else machine_name
        disk_ext_name = config.get('DEFAULT', 'disk_ext_name') if config.get('DEFAULT', 'disk_ext_name').strip() else disk_ext_name
        output_format = config.get('DEFAULT', 'Output_format') if config.get('DEFAULT', 'Output_format') else output_format
        delete_original = config.getboolean('DEFAULT', 'delete_original') if config.get('DEFAULT', 'delete_original') else delete_original
        verbose_level = config.getint('DEFAULT', 'verbose_level') if config.get('DEFAULT', 'verbose_level') else verbose_level
        openmsx_filepath = config.get('DEFAULT', 'openmsx_filepath') if config.get('DEFAULT', 'openmsx_filepath') else openmsx_filepath
    except (ValueError, configparser.NoOptionError) as e:
        show_log('', 'openMSXBatoken.ini: ' + str(e), 1)

parser = argparse.ArgumentParser(description='Use openMSX to convert between ASCII and tokenized MSX Basic.')
parser.add_argument("file_load", nargs='?', default=file_load, help='The file to be converted.')
parser.add_argument("file_save", nargs='?', default=file_save, help='The file to convert to.')
parser.add_argument("-of", default=output_format, choices=['t', 'T', 'a', 'A'], help="Tokenized or ASCII output: t-tokenized(def) a-ASCII")
parser.add_argument("-do", default=delete_original, action='store_true', help="Delete original file after conversion")
parser.add_argument("-vb", default=verbose_level, type=int, help="Verbosity level: 0 silent, 1 errors, 2 +warnings, 3 +steps(def), 4 +detalis")
parser.add_argument("-frb", default=is_from_build, action='store_true', help="Tell it is running from a build system")
args = parser.parse_args()

file_load = args.file_load
file_save = args.file_save
output_format = args.of.upper()
delete_original = args.do
verbose_level = args.vb
is_from_build = args.frb

show_log('', '', 3, bullet=0)

file_load_full = file_load
file_name = os.path.basename(file_save)
save_rest = file_save.replace(file_name, '')
file_save = file_name
save_extension = '.bas'
save_argument = ''
using_machine = 'default machine'
disk_ext_slot = 'ext'
proc = ''
if openmsx_filepath == '':
    openmsx_filepath = local_path + 'openMSX.app'
if machine_name != '':
    using_machine = machine_name
    machine_name = ['-machine', machine_name]
disk_ext = disk_ext_name.split(':')
disk_ext_name = disk_ext[0].strip()
if len(disk_ext) > 1:
    disk_ext_slot = 'extb' if disk_ext[1].lower().strip() == 'slotb' else disk_ext_slot
if file_load:
    if not os.path.isfile(file_load):
        show_log('', ' '.join(['source_not_found', file_load]), 1)  # Exit
else:
    show_log('', 'source_not_given', 1)  # Exit
if output_format == 'A':
    save_extension = '.asc'
    save_argument = '",a'
if file_save == '':
    file_save = os.path.basename(file_load)
    file_save = os.path.splitext(file_save)[0] + save_extension
disk_path = os.path.dirname(file_load)
disk_path = local_path if disk_path == '' else disk_path
file_load = os.path.basename(file_load)

crop_load = os.path.splitext(file_load)[0][0:8] + os.path.splitext(file_load)[1]
crop_save = os.path.splitext(file_save)[0][0:8] + os.path.splitext(file_save)[1]

if save_rest:
    show_log('', ' '.join(['destination_path_removed', save_rest]), 2)

if crop_save == file_load:
    show_log('', ' '.join(['destination_same_as_source', crop_save]), 1)  # Exit

list_dir = os.listdir(disk_path)
list_load = [x for x in list_dir if
             x.lower() != file_load.lower() and
             os.path.splitext(x)[0][0:8].replace(' ', '_').lower() +
             os.path.splitext(x)[1].replace(' ', '_').lower() ==
             crop_load.lower()]

list_save = [x for x in list_dir if
             x.lower() != file_load.lower() and
             os.path.splitext(x)[0][0:8].replace(' ', '_').lower() +
             os.path.splitext(x)[1].replace(' ', '_').lower() ==
             crop_load.lower() and
             len(os.path.splitext(x)[0][0:8]) > 8]

list_all = list_load.extend(list_save)

if list_all:
    show_log('', ' '.join(['MSX_disk_name_format_conflict', ', '.join(list_all)]), 1)  # Exit

disk_path = disk_path.replace(' ', r'\ ')
crop_load = crop_load.replace(' ', '_')
crop_save = crop_save.replace(' ', '_')


def output(show_output, has_input, step):
    if show_output:
        log_out = proc.stdout.readline().rstrip() if has_input else ''
        log_out = log_out.replace('&quot;', '"')
        log_out = log_out.replace('&apos;', "'")
        if '"nok"' in log_out or ' error: ' in log_out:
            log_out = log_out.replace('<reply result="nok">', '')
            proc.stdin.write('<command>quit</command>')
            show_log('', ''.join([step]), 3)
            if 'invalid command name "ext' in log_out:
                show_log('', ''.join(['Machine probably missing a slot']), 2)
            show_log('', ''.join([log_out]), 1)  # Exit
        elif '<log level="warning">' in log_out:
            log_warning = log_out.replace('<log level="warning">', '')
            log_warning = log_warning.replace('</log>', '')
            log_out = log_out.split('<log')[0]
            log_comma = '' if log_out == '' else ': '
            if step + log_comma + log_out != '':
                show_log('', ''.join([step, log_comma, log_out]), 3)
            show_log('', ''.join([log_warning]), 2)
            output(show_output, True, '')
        else:
            log_out = log_out.replace('<openmsx-output>', '')
            log_out = log_out.replace('</openmsx-output>', '')
            log_out = log_out.replace('<reply result="ok">', '')
            log_out = log_out.replace('</reply>', '')
            log_comma = '' if log_out == '' else ': '
            if step + log_comma + log_out != '':
                show_log('', ''.join([step, log_comma, log_out]), 3)


cmd = [openmsx_filepath + '/contents/macos/openmsx', '-control', 'stdio']
if machine_name != '':
    cmd.extend(machine_name)

proc = subprocess.Popen(cmd, bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')

endline = '\r\n'

output(show_output, True, 'openMSX initialized as ' + using_machine)

# proc.stdin.write('<command>set renderer SDL</command>' + endline)
# output(show_output, True, 'Show screen')

proc.stdin.write('<command>set throttle off</command>' + endline)
output(show_output, True, 'Set throttle off')

proc.stdin.write('<command>debug set_watchpoint write_mem 0xfffe {[debug read "memory" 0xfffe] == 0} {quit}</command>' + endline)
output(show_output, True, 'Set quit watchpoint')

if disk_ext_name != '':
    proc.stdin.write('<command>' + disk_ext_slot + ' ' + disk_ext_name + '</command>' + endline)
    output(show_output, True, 'Insert disk drive extension: ' + disk_ext_name + ' at ' + disk_ext_slot)

proc.stdin.write('<command>diska insert ' + disk_path + '</command>' + endline)
output(show_output, True, 'insert folder as disk: ' + disk_path)

proc.stdin.write('<command>set power on</command>' + endline)
output(show_output, True, 'Power on')

proc.stdin.write('<command>type_via_keybuf \\r\\r</command>' + endline)  # Disk ROM ask for date, enter twice to skip
output(show_output, True, 'Press return twice')

proc.stdin.write('<command>type_via_keybuf load"' + crop_load + '\\r</command>' + endline)
output(show_output, True, 'type load"' + crop_load)

proc.stdin.write('<command>type_via_keybuf save"' + crop_save + save_argument + '\\r</command>' + endline)
output(show_output, True, 'type save"' + crop_save + save_argument)

proc.stdin.write('<command>type_via_keybuf poke-2,0\\r</command>' + endline)
output(show_output, True, 'Quit')

proc.wait()

file_save_full = disk_path + '/' + crop_save
if delete_original:
    if os.path.isfile(file_save_full):
        show_log('', 'Deleting source', 3)
        show_log('', ' '.join(['delete_file:', file_load_full]), 4)
        osremove(file_load_full)
    else:
        show_log('', ' '.join(['source_not_deleted', file_load_full]), 2)
        show_log('', ' '.join(['converted_not_found', crop_save]), 2)

show_log('', '', 3, bullet=0)
