import sys
from os.path import os

log_file_lines = []
log_file_path = "../../RXOTG-513_trx0_log_fault_1.txt"
parse_log_file_path = "../../parse_log"
settings_file = "../settings/settings"
ignore_file = "../settings/ignore"

keywords = set()
ignore_words = set()
write_mode = 'w'
read_mode = 'r'

def read_options_file(path, mode, collection):
    with open(path, mode) as read_settings:
        for settings in read_settings:
            collection.add(settings.replace('\n', ''))

def read_log(path, mode, collection):
    count_lines = 0
    with open(path, mode) as read_log_file:
        for line in read_log_file:
            count_lines = count_lines + 1
            if any(key in line.lower() for key in keywords) and not (any(ignore in line for ignore in ignore_words)):
                collection.append("Line number: " + str(count_lines) + "   Message :   " + line)

def write_parse_log(path, mode, collection, description):
    with open(path, mode) as write_log_file:
        write_log_file.write("\n" * 3 + "#" * 25 + "   LOG FROM: " + description + "   " + "#" * 25 + "\n" * 3)
        write_log_file.writelines(collection)

def find_file(path, extension):
    print path
    print extension
    file_list = [path + "/" + file for file in os.listdir(path)] # if splitext(file)[1].lower() == "." + "extension"]
    print file_list

read_options_file(settings_file, read_mode, keywords)
read_options_file(ignore_file, read_mode, ignore_words)
read_log(log_file_path, read_mode, log_file_lines)
write_parse_log(parse_log_file_path + ".log", write_mode, log_file_lines, log_file_path)

find_file("/afs/ericpol.int/home/p/6/p660/home/workspace/Python_Git/PythonLogFilter/parser","") # zmianiec na argument

if sys.argv.__len__() > 2:
    find_file(str(sys.argv[1]),str(sys.argv[2]))
