import sys
import re
import time
from os.path import os
import getopt

settings_file = os.path.join('settings', 'extract')
ignore_file = os.path.join('settings', 'ignore')
log_file_lines = []
keywords = set()
ignore_words = set()
write_mode = 'a'
read_mode = 'r'

path_arg = '..'
regexp_arg = ('dx', 'trx', 're', 'ec')
extension_arg = 'txt'

try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:r:e:', ['path=', 'regexp=', 'extension='])
except getopt.GetoptError:
    print "ERROR: Invalid arguments!"
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-p', '--path'):
        path_arg = arg
    elif (opt in ('-r', '--regexp')):
        if arg.lower() != 'all':
            regexp_arg = arg.lower()
    elif opt in ('-e', '--extension'):
        extension_arg = arg.lower()
    else:
        sys.exit(2)

parse_log_file_path = path_arg + os.sep + time.strftime("%d-%m-%y_%H-%M-%S") + '_parse_'


def read_options_file(path, mode, collection):
    with open(path, mode) as read_settings:
        for settings in read_settings:
            collection.add(settings.replace('\n', ''))


def read_log(path, mode):
    count_lines = 0
    log_collection = []
    with open(path, mode) as read_log_file:
        for line in read_log_file:
            count_lines += 1
            if any(key in line.lower() for key in keywords) and not (any(ignore in line.lower() for ignore in ignore_words)):
                log_collection.append("Line number: " + str(count_lines) + "   Message :   " + line)
    return log_collection


def write_parse_log(path, mode, collection, description):
    with open(path, mode) as write_log_file:
        write_log_file.write("\n" * 2 + "#" * 15 + "   TYPE OF LOG: " + type_of_log(description) + "   LOG FROM: " + description +
                             "   CURRENT SERVER TIME: " + time.strftime("%y/%m/%d %H:%M:%S") + "   " + "#" * 15 + "\n" * 3)
        write_log_file.writelines(collection)


def type_of_log(filename):
    if isinstance(regexp_arg, tuple):
        for log_type in regexp_arg:
            if re.search(log_type, filename.lower()):
                return log_type
    else:
        if re.search(regexp_arg, filename.lower()):
            return regexp_arg


def find_file(path = '.', regexp = '.*', extension = 'txt'):
    if os.path.isdir(path):
        if isinstance(regexp_arg, tuple):
            files = []
            for reg in regexp:
                for file in os.listdir(path):
                    if re.search(".*(" + reg + "){1}.*" + extension + "{1}", file):
                        files.append(path + os.sep + file)
            return files
        else:
            return [path + os.sep + file for file in os.listdir(path) if re.search(".*(" + regexp + "){1}.*" + extension + "{1}", file)]
    else:
        print "ERROR: Invalid path!"
        sys.exit(2)


read_options_file(settings_file, read_mode, keywords)
read_options_file(ignore_file, read_mode, ignore_words)

for file in find_file(path_arg, regexp_arg, extension_arg):
    log_file_lines = read_log(file, read_mode)
    write_parse_log(parse_log_file_path + ("all" if isinstance(regexp_arg, tuple) else regexp_arg) + ".log", write_mode, log_file_lines, file)
