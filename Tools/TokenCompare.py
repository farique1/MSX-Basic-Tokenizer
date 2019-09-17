# Convert ASCII listings with MSXBatoken and compares it
# with a conversion from openMSXBatoken (using the MSX)
# cmp may be exchanged for fc on Windows (I guess)

import os
import time
import glob
import subprocess

report_arr = []

error_tolerance = 15
save_list_report = True
save_file_report = False
base_path = 'basictests/'
file_list = []
save_file = ''
make_formated_viz = True
make_token_list_file = True
delete_files_if_ok = True
# Put a single entry ['name'] to do a single file
# An empty file_list [] will get the whole base_path folder

if save_file == '':
    if len(file_list) == 1:
        save_file = file_list[0]
    elif base_path != '':
        save_file = os.path.basename(os.path.normpath(base_path))
    else:
        print '*** No save file given'
        raise SystemExit(0)

token_list_file = ' -sl' if make_token_list_file else ''

if file_list == []:
    for files in glob.glob(base_path + '*.asc'):
        file = os.path.basename(files)
        file = os.path.splitext(file)[0]
        file_list.append(file)

file_list.sort()


def report(text):
    text = ' '.join(text)
    report_arr.append(text)
    print text


report([save_file])
report([])

for file in file_list:
    base_name = file  # os.path.splitext(file)[0]
    file_load = base_path + base_name + '.asc'
    file_msx = base_path + base_name + '.bas'
    file_bto = base_path + base_name + '.bto'
    file_btc = base_path + base_name + '.btc'

    wait_time = 1
    file_size = os.path.getsize(file_load), file_load
    if file_size > 10000:
        wait_time = 4

    report(['---', base_name + '.asc'])
    os.system('python MSXBatoken20.py ' + file_load + ' ' + file_bto + token_list_file)
    os.system('python openMSXBatoken.py ' + file_load + ' ' + file_msx)
    time.sleep(wait_time)

    cmd = ('cmp --verbose ' + file_msx + ' ' + file_bto)
    proc = subprocess.Popen([cmd], shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    error_num = 0
    log_out = '*'
    while log_out:
        log_out = proc.stdout.readline().strip()
        if not log_out.replace(' ', '').isdigit():
            if log_out.replace(' ', '') != '':
                report(['  *', log_out])
                error_num = 1
            break
        output = log_out.split()
        if log_out:
            address = '{0:04x}'.format(int(output[0]))
            source = '{0:02x}'.format(int(output[1]))
            destin = '{0:02x}'.format(int(output[2]))
            line, col = divmod(int(output[0]), 16)
            report(['***', address, source, destin, '-', str(line + 1), str(col)])
            error_num += 1
            if error_num >= error_tolerance:
                report(['  - More than'])
                break

    if error_num == 0:
        if delete_files_if_ok:
            os.remove(file_msx)
            os.remove(file_bto)
            if os.path.isfile(base_path + base_name + '.mlt'):
                os.remove(base_path + base_name + '.mlt')
            if os.path.isfile(file_btc):
                os.remove(file_btc)
        report(['--- No errors'])
    else:
        report(['  -', str(error_num), 'error(s)'])
        if make_formated_viz:
            os.system('python TokenFormatViz.py -lb ' + file_msx + ' -lc ' + file_bto + ' -sa ' + file_btc)

    report([''])

if (save_file_report and len(file_list) == 1) or \
        (save_list_report and len(file_list) > 1):
    with open(base_path + save_file + '.log', 'w') as f:
        for line in report_arr:
            f.write(line + '\n')
