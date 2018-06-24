import os
import sys
import re
from colorama import init, Fore, Back, Style

print(sys.version)

init(autoreset=True)

words = raw_input("Please type movie name or part of movie name using character '_' instead of space: ")

movieFiles = [f for f in os.listdir('.') if os.path.isfile(f) and (f.endswith(".mkv") or f.endswith(".mp4"))]
subtitleFiles = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(".srt")]
unwantedFiles = []

print "Searching for files that contain: " + Fore.GREEN + Style.BRIGHT + ' '.join(words)

for f in subtitleFiles:
    for w in words:
        if w.lower() not in f.lower():
            unwantedFiles.append(f)
            break

for uf in unwantedFiles:
    subtitleFiles.remove(uf)

unwantedFiles = []

for f in movieFiles:
    for w in words:
        if w.lower() not in f.lower():
            unwantedFiles.append(f)
            break

for uf in unwantedFiles:
    movieFiles.remove(uf)

print "Files found: " + Fore.GREEN + Style.BRIGHT + '\n'.join(subtitleFiles + movieFiles)

for mf in movieFiles:
    if re.search("[Ss]\d{2}", mf) is not None and re.search("[Ee]\d{2}", mf).group(0) is not None:
        directory = re.search("[Ss]\d{2}", mf).group(0).upper() + re.search("[Ee]\d{2}", mf).group(0).upper()
        if not os.path.exists(directory):
            print "Creating folder " + Fore.GREEN + Style.BRIGHT + directory
            os.makedirs(directory)
        print "Moving " + Fore.GREEN + Style.BRIGHT + mf + Style.RESET_ALL + " to folder " + Fore.GREEN + Style.BRIGHT + directory
        destination = os.path.join(directory, mf)
        try:
            os.rename(mf, destination)
        except:
            print Fore.RED + Style.BRIGHT + "Could not move " + mf + " to folder " + directory

for sf in subtitleFiles:
    if re.search("[Ss]\d{2}", sf) is not None and re.search("[Ee]\d{2}", sf).group(0) is not None:
        directory = re.search("[Ss]\d{2}", sf).group(0).upper() + re.search("[Ee]\d{2}", sf).group(0).upper()
        if os.path.exists(directory):
            print sf, directory
            file = [f for f in os.listdir(os.path.join(os.getcwd(), directory)) if f.endswith(".mkv") or f.endswith(".mp4")]
            if len(file) != 0:
                file = file[0]
                if re.search(directory[:3].lower(), sf.lower()) is not None and re.search(directory[3:].lower(), sf.lower()) is not None:
                    destination = os.path.join(directory, file)
                    print  sf + "   " + destination[:-4] + ".srt"
                    print "Moving " + Fore.GREEN + Style.BRIGHT + sf + Style.RESET_ALL +\
                    " to folder " + Fore.GREEN + Style.BRIGHT + directory
                    try:
                        os.rename(sf, destination[:-4] + ".srt")
                    except:
                        print Fore.RED + Style.BRIGHT + "Could not move " + sf + " to folder " + directory
        else:
            print "Creating folder " + Fore.GREEN + Style.BRIGHT + directory
            os.makedirs(directory)
            print "Moving " + Fore.GREEN + Style.BRIGHT + sf + Style.RESET_ALL + " to folder " + Fore.GREEN + Style.BRIGHT + directory
            destination = os.path.join(directory, sf)
            os.rename(sf, destination)

sys.exit()
