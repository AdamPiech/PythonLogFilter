import sys
import re
import time
from os.path import os

log_file_lines = []
parse_log_file_path = os.path.join(time.strftime("%d.%m.%y_%H-%M-%S_")+'parse_')

settings_file = os.path.join('settings', 'extract')
ignore_file = os.path.join('settings', 'ignore')
keywords = set()
ignore_words = set()
write_mode = 'a'
read_mode = 'r'


class InvalidPathException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return `self.value`


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
            if any(key in line.lower() for key in keywords) and not (any(ignore in line for ignore in ignore_words)):
                log_collection.append("Line number: " + str(count_lines) + "   Message :   " + line)
    return log_collection


def write_parse_log(path, mode, collection, description):
    with open(path, mode) as write_log_file:
        write_log_file.write("\n" * 2 + "#" * 15 + "   LOG FROM: " + description + "   CURRENT SERVER TIME: " + time.strftime("%y/%m/%d %H:%M:%S") + "   " + "#" * 15 + "\n" * 3)
        write_log_file.writelines(collection)


def find_file(path, regexp, extension = "txt"):
    if os.path.isdir(path):
        return [path + os.sep + file for file in os.listdir(path) if re.search(".*(" + regexp + "){1}.*" + extension + "{1}", file)]
    else:
        raise InvalidPathException, "ERROR: Invalid path!"


read_options_file(settings_file, read_mode, keywords)
read_options_file(ignore_file, read_mode, ignore_words)

if len(sys.argv) >= 3:
    for file in find_file(sys.argv[1], sys.argv[2], sys.argv[3]) if len(sys.argv) == 4 else find_file(sys.argv[1], sys.argv[2]):
        try:
            log_file_lines = read_log(file, read_mode)
            write_parse_log(parse_log_file_path + sys.argv[2]+ ".log", write_mode, log_file_lines, file)
        except InvalidPathException, err:
            print "ERROR: Invalid path!"
elif len(sys.argv) == 2:
    for file in find_file(sys.argv[1], ""):
        try:
            log_file_lines = read_log(file, read_mode)
            write_parse_log(parse_log_file_path + "all.log", write_mode, log_file_lines, file)
        except InvalidPathException, err:
            print "ERROR: Invalid path!"
else:
    print "ERROR: Invalid number of arguments!"






