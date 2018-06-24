from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Back, Style
from collections import OrderedDict
import sys
import operator
import zipfile
import os
import time


#Paths
URL_BASIC = 'http://titlovi.com/'
PAGE_ROOT_XPATH = "/html/body/div[@class='page-content-wrapper']/div[@class='contentWrapper']/div/main"
CURRENT_LINK_PATH = "/html/body/div[@class='page-content-wrapper']/div[@class='header']/nav/ul[@class='nav2']/li[a[contains(text(), 'Prijavi se')]]/a"
DOWNLOAD_BUTTON_PATH = "/html/body/div[@class='page-content-wrapper']/div[@class='contentWrapper']/div/main/section[@class='titl']/div/div[@class='bottom']/div[@class='download']/a"
DEFAULT_DOWNLOAD_PATH = os.path.join(os.environ.get("HOMEDRIVE"), os.environ.get("HOMEPATH"), 'Downloads', 'Titles')

#Global variables
driver = None
download_path = ''
season_path = ''
webbrowser = 0
title_info = {}


def sort_dict(input_dict: dict,) -> {}:
    sorted_array = sorted(input_dict.items(), key = operator.itemgetter(1), reverse = True)
    sorted_dict = OrderedDict()
    for sa in sorted_array:
        sorted_dict[sa[0]] = str(sa[1])
    return sorted_dict


def init_webdriver(input_: int,) -> webdriver:
    global download_path
    driver = None
    if input_ == 0:
        options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory" : download_path,
            "download.directory_upgrade": "true",
            "download.prompt_for_download": "false",
            "disable-popup-blocking": "true"
        }
        options.add_experimental_option("prefs", prefs)
        try:
            driver = webdriver.Chrome(chrome_options=options)
        except:
            print(Fore.RED + Style.BRIGHT + "Could not find Chrome webdriver!!")
            sys.exit(0)

    elif input_ == 1:
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.manager.showAlertOnComplete", False)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
        fp.set_preference("browser.download.dir", download_path)
        try:
            driver = webdriver.Firefox(firefox_profile=fp)
        except:
            print(Fore.RED + Style.BRIGHT + "Could not find Firefox webdriver!!")
            sys.exit(0)
    else:
        print(Fore.RED + Style.BRIGHT + "Wron input for webdriver init function.")
        sys.exit(0)

    return driver


def choose_webbrowser() -> int:
    menu_options = ["chrome", "firefox"]

    print()
    print('Choose webbrowser: ')
    for item in menu_options:
        print("[ " + str(menu_options.index(item)) + " ]\t" + item)
    while(True):
        choice = input("\nEnter choice number: ")
        if(choice.isdigit()):
            if(0 <= int(choice) < len(menu_options)):
                return int(choice)
            else:
                print("Number out range!")
        else:
            print("Not a valid input!")


def compare_description(description: str, description_input: list,) -> bool:
    for d in description_input:
        if d in description:
            return True
    return False


def requirement_satisfied(language: str,
                        author_input: list,
                        author: str,
                        description_input: list,
                        description: str,
                        compare_by_both: bool,) -> bool:
    return language in ['hr', 'rs', 'ba'] and \
        ((author in author_input and compare_description(description, description_input,) and compare_by_both) or \
        ((author in author_input or compare_description(description, description_input,)) and not compare_by_both))


def format_output(data: list, table_fores: list,) -> None:
    number_of_columns = len(data[0])
    col_width = [0] * number_of_columns
    for row in data:
        for i, word in enumerate(row):
            col_width[i] = max(col_width[i], len(word))

    fence = []
    small_fence = []
    padding = 2
    for i in range(0, number_of_columns):
        col_width[i] += padding
        fence.append("="*col_width[i])
        small_fence.append("-"*col_width[i])
    data = data[:1] + [fence] + data[1:]

    i = 0
    while i < len(data):
        try:
            if(i > 2 and data[i][0].split('EPIZOD')[1] != data[i - 1][0].split('EPIZOD')[1]):
                data = data[:i] + [small_fence] + data[i:]
                i += 1
            i += 1
        except:
            break

    for row in data:
        for i, word in enumerate(row):
            if '=' in word or '--' in word:
                print('|' + word.center(col_width[row.index(word)]), end = '|')
            else:
                print('|' + table_fores[i] + Style.BRIGHT + word.center(col_width[row.index(word)]), end = '|')
        print()


def episodes_info_table_output(table_header: list = [], 
                            table_content: dict = {}, 
                            table_fores: list = [],) -> None:
    data = [table_header]

    for episode_name, episode_infos in table_content.items():
        for episode_info in episode_infos:
            info = []
            for key, value in episode_info.items():
                info.append(value)
            data.append([episode_name] + info)

    format_output(data, table_fores)


def authors_with_number_of_subtitles_table_output(table_header: list = [], 
                table_content: dict = {}, 
                table_fores: list = [],) -> None:
    data = [table_header]

    for author_name, number_of_subtitles in table_content.items():
        data.append([author_name, number_of_subtitles])

    format_output(data, table_fores)


def get_episodes_info(episodes: list, season_path: str,) -> set:
    global title_info
    num_of_authors = {}
    num_of_descriptions = {}
    for i, t in enumerate(episodes, 1):
        t.click()
        episode_path = season_path + "/ul/li[%s]" %i
        episode_name = driver.find_element_by_xpath(episode_path + "/div/h3").text
        if episode_name not in title_info:
            title_info[episode_name] = []
        subtitles = driver.find_elements_by_xpath(episode_path + "/ul/*")
        this_episode_authors = OrderedDict()
        this_episode_descriptions = OrderedDict()
        for j, k in enumerate(subtitles, 1):
            languane_path = episode_path + "/ul/li[%s]/div[@class='icons']/img" %j
            language = driver.find_element_by_xpath(languane_path).get_attribute('src').split('/')[-1].split('.')[0][0:-1]
            if language in ['hr', 'rs', 'ba']:
                description_path = episode_path + "/ul/li[%s]/h4" %j
                description = driver.find_element_by_xpath(description_path).text.split('\n')[0]
                author_path = episode_path + "/ul/li[%s]/h5/span[@class='dodao']/a" %j
                author = driver.find_element_by_xpath(author_path).get_attribute('href').split("korisnik=")[1]
                title_info[episode_name].append(OrderedDict({'language': language, 'author': author, 'description': description,}))
                if author not in num_of_authors and author not in this_episode_authors:
                    num_of_authors[author] = 0
                    this_episode_authors[author] = 0
                if description not in num_of_descriptions and description not in this_episode_descriptions:
                    num_of_descriptions[description] = 0
                    this_episode_descriptions[description] = 0
                num_of_authors[author] += 1
                num_of_descriptions[description] += 1
    num_of_authors = sort_dict(num_of_authors)
    num_of_descriptions = sort_dict(num_of_descriptions)
    return(num_of_authors, num_of_descriptions)


def download_titles_by_author_description(author_input: list = [],
                    description_input: list = [],
                    compare_by_both: bool = False,) -> None:
    global title_info
    global season_path
    global download_path
    global driver
    current_url = driver.find_element_by_xpath(CURRENT_LINK_PATH).get_attribute('href').split('returnURL=')[1]

    for i in range(1, len(title_info) + 1):
        driver.get(current_url)
        season_number = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, season_path + "/div")));
        season_number.click()
        episode_path = season_path + "/ul/li[%s]" %i
        episode = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, episode_path,)));
        episode.click()
        subtitles = driver.find_elements_by_xpath(episode_path + "/ul/*")
        subtitle_not_found = True
        for j, k in enumerate(subtitles, 1):
            description_path = episode_path + "/ul/li[%s]/h4" %j
            description = driver.find_element_by_xpath(description_path).text.split('\n')[0]
            languane_path = episode_path + "/ul/li[%s]/div[@class='icons']/img" %j
            language = driver.find_element_by_xpath(languane_path).get_attribute('src').split('/')[-1].split('.')[0][0:-1]
            author_path = episode_path + "/ul/li[%s]/h5/span[@class='dodao']/a" %j
            author = driver.find_element_by_xpath(author_path).get_attribute('href').split("korisnik=")[1]
            if(requirement_satisfied(language = language,
                                    author_input = author_input,
                                    author = author,
                                    description_input = description_input,
                                    description = description,
                                    compare_by_both = compare_by_both,)):
                download_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, episode_path + "/ul/li[%s]/div[@class='download']/a" %j)));
                download_button.click()
                download_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, DOWNLOAD_BUTTON_PATH)));
                download_button.click()
                subtitle_not_found = False
                print(Fore.GREEN + "Subtitle for Episode %s downloaded." %i)
                break
        if(subtitle_not_found):
            print(Fore.RED + Style.BRIGHT + "There is no subtitle for Episode %s." %i)
    time.sleep(3)


def download_by_author() -> None:
    author_input = input('Insert author(s): ').split(' ')
    download_titles_by_author_description(author_input = author_input,
                                        compare_by_both = False)


def download_by_description() -> None:
    description_input = input('Insert description(s): ').split(' ')
    download_titles_by_author_description(description_input = description_input,
                                        compare_by_both = False,)


def download_by_author_or_description() -> None:
    author_input = input('Insert author(s): ').split(' ')
    description_input = input('Insert description(s): ').split(' ')
    download_titles_by_author_description(author_input = author_input,
                                        description_input = description_input,
                                        compare_by_both = False,)


def download_by_author_and_description() -> None:
    author_input = input('Insert author(s): ').split(' ')
    description_input = input('Insert description(s): ').split(' ')
    download_titles_by_author_description(author_input = author_input,
                                        description_input = description_input,
                                        compare_by_both = True,)


def unzip_files() -> None:
    print()
    print(Fore.YELLOW + Style.BRIGHT + 'Unziping files: ')
    try:
        for item in os.listdir(download_path):
            if item.endswith('.zip'):
                print(Fore.WHITE + Style.BRIGHT + 'Unziping file %s' %item)
                file_name = os.path.abspath(os.path.join(download_path, item))
                zip_ref = zipfile.ZipFile(file_name)
                zip_ref.extractall(download_path)
                zip_ref.close()
                os.remove(file_name)
    except:
        driver.close()
        print(Fore.RED + Style.BRIGHT + 'Could not unzip files, check the path.')
        print(Fore.RED + Style.BRIGHT + 'Closing.')
        sys.exit(0)


def exit() -> None:
    driver.close()
    sys.exit(0)


def main () -> None:
    global driver
    global season_path
    global download_path
    global webbrowser
    global title_info

    init(autoreset=True)
    
    print('If you leave the download path empty, titles will be downloaded in folder Download/Titles.')
    download_path = input('Insert download folder: ')
    if len(download_path) == 0:
        download_path = DEFAULT_DOWNLOAD_PATH
    movie_name_input = input('Insert movie name: ')
    while True:
        season_input = input('Insert season: ')
        try:
            int(season_input)
            break
        except:
            print('Season must be a number')

    webbrowser = choose_webbrowser()
    driver = init_webdriver(webbrowser)
    full_url = URL_BASIC + 'titlovi/?prijevod=' + '+'.join(movie_name_input.split(' ')).lower()
    driver.get(full_url)
    try:
        url = driver.find_element_by_xpath(PAGE_ROOT_XPATH + "/section/ul/li[1]/div[@class='download']/a").get_attribute('href')
    except:
        print(Fore.RED + Style.BRIGHT + "Can't find %s." %movie_name_input)
        driver.close()
        sys.exit(0)

    driver.get(url)

    try:
        season_path = PAGE_ROOT_XPATH + \
                    "/section[@class='lowerTabs']/div/div[@class='tabsContent']/div[@id='tabContent1']/div/ul/li[./div/h2[contains(text(), 'Sezona %s')]]" \
                    %season_input
        season_number = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, season_path + "/div/h2")));
    except:
        print('Season does not exist.')
        driver.close()
        sys.exit(0)

    season_number.click()
    episodes = driver.find_elements_by_xpath(season_path + "/ul/*")
    
    episodes_info = get_episodes_info(episodes, season_path)
    num_of_authors = episodes_info[0]
    num_of_descriptions = episodes_info[1]

    fores = [Fore.MAGENTA, Fore.RED, Fore.GREEN, Fore.CYAN]
    data_header = ['Episode', 'Subtitle', 'Author', 'Description',]
    episodes_info_table_output(data_header, title_info, fores)

    print()
    print("Number of subtitle per author: ")
    fores = [Fore.GREEN, Fore.RED,]
    data_header = ['Author', 'Number of subtitles',]
    authors_with_number_of_subtitles_table_output(data_header, num_of_authors, fores)

    print()
    print("Number of subtitle per description: ")
    fores = [Fore.CYAN, Fore.RED,]
    data_header = ['Author', 'Number of subtitles',]
    authors_with_number_of_subtitles_table_output(data_header, num_of_descriptions, fores)

    menu_options = [{'name': "exit",                        'function': exit},
                    {'name': "by author",                   'function': download_by_author},
                    {'name': "by desription",               'function': download_by_description},
                    {'name': "by author or description",    'function': download_by_author_or_description},
                    {'name': "by author and description",   'function': download_by_author_and_description}]

    print()
    print('Choose the search criteria: ')
    for item in menu_options:
        print("[ " + str(menu_options.index(item)) + " ]\t" + item["name"])
    while(True):
        choice = input("\nEnter choice number: ")
        if(choice.isdigit()):
            if(0 <= int(choice) < len(menu_options)):
                menu_options[int(choice)]['function']()
                break
            else:
                print("Number out range!")
        else:
            print("Not a valid input!")

    unzip_files()
    print(Fore.GREEN + Style.BRIGHT + "Completed.")
    driver.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
