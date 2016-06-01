import sys
import re
import time
from os.path import os
import getopt

settings_file = os.path.join('settings', 'extract')
# path to extract patterns on Jenkins
#settings_file = os.path.join(os.sep, 'proj', 'bscautodata', 'bts_ci', 'rbslog_parser', 'settings', 'extract')
ignore_file = os.path.join('settings', 'ignore')
# path to ignore patterns on Jenkins
#ignore_file = os.path.join(os.sep, 'proj', 'bscautodata', 'bts_ci', 'rbslog_parser', 'settings', 'ignore')

# collection of all extracted lines from log
log_file_lines = []
# collection of regular expressions to extract from log
keywords = set()
# collection of words or lines to ignore from parsed line
ignore_words = set()
write_mode = 'a'
read_mode = 'r'


# default parser settings when no parameters passed
path_arg = '..'
regexp_arg = ('dx', 'trx', 're', 'ec')
extension_arg = 'txt'

# getting arguments from command line
try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:r:e:', ['path=', 'regexp=', 'extension='])
except getopt.GetoptError:
    print "ERROR: Invalid arguments!"
    sys.exit(2)

# if argument is passed, it is set to the variable
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

# path to parsed result
parse_log_file_path = path_arg + os.sep + time.strftime("%d-%m-%y_%H-%M-%S") + '_parse_'


# function used to read settings from keywords and ignore_words collections
def read_options_file(path, mode, collection):
    with open(path, mode) as read_settings:
        for settings in read_settings:
            collection.add(settings.replace('\n', ''))


# Function used to read specified logs. It walks line by line through log file, checks if line contains pattern from
# keywords and then checks if there is pattern from ignored_words. In case it contains pattern from ignored_words,
# the line is not appended to log_collection, otherwise it is appended to log_collection.
# There is also a message about number of line, where the pattern was.
def read_log(path, mode):
    count_lines = 0
    log_collection = []
    with open(path, mode) as read_log_file:
        for line in read_log_file:
            count_lines += 1
            if any(key in line.lower() for key in keywords) and not (any(ignore in line.lower() for ignore in ignore_words)):
                log_collection.append("Line number: " + str(count_lines) + "   Message :   " + line)
    return log_collection


#Function is similar to upper one, if OSE DUMP occurs it appends it to resulting log.
def ose_dump_occur(path,mode):
    count_lines = 0
    log_lines = []
    ose_keyword = "OSE DUMP"
    ose_end_keyword = "END OF OSE DUMP"
    with open(path,mode) as read_log_file:
        parsing = False
        for line in read_log_file:
            count_lines += 1
            if ose_keyword in line:
                parsing = True
            if ose_end_keyword in line:
                log_lines.append("Line number: " + str(count_lines) + "   Message :   " + 23*"=" + " END OF OSE DUMP " + 30*"="+"\n")
                parsing = False
            if parsing:
                log_lines.append("Line number: " + str(count_lines) + "   Message :   " + line)
    return log_lines


# This function is used to write a resulting collection (from read_log) with description about log file.
def write_parse_log(path, mode, collection, description):
    with open(path, mode) as write_log_file:
        if not collection:
            write_log_file.write("THERE IS NO OSE DUMP IN:" + "#" * 15 + "   TYPE OF LOG: " + type_of_log(description) + "   LOG FROM: " + description +
                                 "   CURRENT SERVER TIME: " + time.strftime("%y/%m/%d %H:%M:%S") + "   " + "#" * 15 + "\n")
            write_log_file.writelines(collection)
        else:
            write_log_file.write("\n" + "#" * 15 + "   TYPE OF LOG: " + type_of_log(description) + "   LOG FROM: " + description +
                                 "   CURRENT SERVER TIME: " + time.strftime("%y/%m/%d %H:%M:%S") + "   " + "#" * 15 + "\n")
            write_log_file.writelines(collection)


# This function checks the type of log. It gets a filename of current log file and returns a type of log.
def type_of_log(filename):
    if isinstance(regexp_arg, tuple):
        for log_type in regexp_arg:
            if re.search(log_type, filename.lower()):
                return log_type
    else:
        if re.search(regexp_arg, filename.lower()):
            return regexp_arg


# This function return postfix from the name of file which is took from the file path
def type_of_postfix(filename):
    result = []
    for part_of_filename in  os.path.basename(os.path.splitext(filename)[0]).split('_')[::-1]:
        # TEMPORARY CODE TO DELETE AFTER DAREK's LOG NAMES CHANGE
        if part_of_filename.__eq__("INCOMPLETE") or part_of_filename.__eq__("EMPTY"):
            continue
        # THIS CODE SHOULD REMAIN UNCHANGED
        if part_of_filename.isdigit():
            result.append(part_of_filename)
            continue
        result.append(part_of_filename)
        return '_' + '_'.join(result[::-1])


# This function is used to get all files from selected directory, which contains specified regexp and/or extension in
# its name. It retuns a list of path to file.
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


# Read settings
read_options_file(settings_file, read_mode, keywords)
read_options_file(ignore_file, read_mode, ignore_words)

# This loop is used to parse selected log files. Name of the resulting parsed file is created by a name
# of pattern which was used to choose files to parse. The resulting log file is written in directory
# where the logs files were found.
for file in find_file(path_arg, regexp_arg, extension_arg):
    log_lines = ose_dump_occur(file, read_mode)
    write_parse_log(parse_log_file_path + ("all" if isinstance(regexp_arg, tuple) else regexp_arg) + type_of_postfix(file) + ".log", write_mode, log_lines, file)
for file in find_file(path_arg, regexp_arg, extension_arg):
    log_file_lines = read_log(file, read_mode)
    write_parse_log(parse_log_file_path + ("all" if isinstance(regexp_arg, tuple) else regexp_arg) + type_of_postfix(file) + ".log", write_mode, log_file_lines, file)


