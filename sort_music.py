##=============================================================================
#
# @file     sort_music.py
# @brief    Music sorter script. This script sorts music by the first letter
#           in the file name.
#
#=============================================================================


from os import listdir
from os.path import isfile, join
import os
from string import ascii_uppercase
from colorama import init
from colorama import Fore, Back, Style

DEFAULT_DIRECTORY = '$'
NUMBER_DIRECTORY = '0-9'
EXTENSION = ['mp3', 'wav']
SOURCE_DIRECTORY = os.path.join('D:\\', 'Program Files (x86)')
DESTINATION_DIRECTORY = os.path.join('D:\\', 'Projekte', 'home_skripts', 'music')


##============================================================================
#
# @brief    This function creates directories on the path given 
#           as second parameter.
#
# @param[in]  directory_names   The names of the directories needed 
#                               for sorting.
#
# @param[in]  dest_dir          The destination directory name.
#
#=============================================================================
def create_directory(directory_names: list, dest_dir: str) -> None:
    for c in directory_names:
        tmp_dir = os.path.join(dest_dir, c)
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)


##============================================================================
#
# @brief    This function copies all files from source directory and sorts
#           them in the destination directories.
#
# @param[in]  src_dir       The source directory name.
#
# @param[in]  dest_dir      The destination directory name.
#
# @param[in]  rekursive     Boolean value, if True, all subdirectories will
#                           be searched for files, otherwise only the src_dir.
#
#=============================================================================
def move_file_to_one_of_the_directories(src_dir: str, dest_dir: str, rekursive: bool) -> None:
    only_files = [f for f in listdir(src_dir) if isfile(join(src_dir, f))]
    only_directory = [os.path.join(src_dir, f) for f in listdir(src_dir) if not isfile(join(src_dir, f))]

    for f in only_files:
        copied = False
        src_file = os.path.join(src_dir, f)
        if f[0].isdigit():
            tmp_dir = os.path.join(dest_dir, NUMBER_DIRECTORY)
            if os.path.exists(os.path.join(tmp_dir, f)):
                print ('file ' + Fore.RED + src_file + Fore.RESET + ' exists already in folder ' + Fore.RED + tmp_dir)
                copied = True
                continue
            os.rename(src_file, os.path.join(tmp_dir, f))
            print ('file ' + Fore.GREEN + src_file + Fore.RESET + ' copied to folder ' + Fore.GREEN + tmp_dir)
            continue
        for c in ascii_uppercase:
            tmp_dir = os.path.join(dest_dir, c)
            if os.path.exists(os.path.join(tmp_dir, f)):
                print ('file ' + Fore.RED + src_file + Fore.RESET + ' exists already in folder ' + Fore.RED + tmp_dir)
                copied = True
                break
            if c == f[0].upper():
                os.rename(src_file, os.path.join(tmp_dir, f))
                print ('file ' + Fore.GREEN + src_file + Fore.RESET + ' copied to folder ' + Fore.GREEN + tmp_dir)
                copied = True
                break
        if not copied:
            tmp_dir = os.path.join(dest_dir, DEFAULT_DIRECTORY)
            if os.path.exists(os.path.join(tmp_dir, f)):
                print ('file ' + Fore.RED + src_file + Fore.RESET + ' exists already in folder ' + Fore.RED + tmp_dir)
                continue
            os.rename(src_file, os.path.join(tmp_dir, f))
            print ('file ' + Fore.GREEN + src_file + Fore.RESET + ' copied to folder ' + Fore.GREEN + tmp_dir)
    if rekursive is True:
        for od in only_directory:
            move_file_to_one_of_the_directories(od, dest_dir, rekursive)


if __name__ == "__main__":
    init(autoreset=True)

    print ('destination_directory: %s' %DESTINATION_DIRECTORY)
    if not os.path.exists(DESTINATION_DIRECTORY):
        os.makedirs(DESTINATION_DIRECTORY)
    print ('source_directory: %s' %SOURCE_DIRECTORY)
    
    create_directory(ascii_uppercase, DESTINATION_DIRECTORY)
    special_folder_names = [DEFAULT_DIRECTORY, NUMBER_DIRECTORY]
    create_directory(special_folder_names, DESTINATION_DIRECTORY)
    move_file_to_one_of_the_directories(SOURCE_DIRECTORY, DESTINATION_DIRECTORY, True)
    