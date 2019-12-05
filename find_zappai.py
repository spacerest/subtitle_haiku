import string
from nltk.corpus import cmudict
import re
import os
import codecs
import srt
from shutil import copyfile

PATH_FOR_RESULTS = './results/'

class TerminalUi():

    def run(self):
        subtitle_path = input("What is the name of the directory with the srt file(s)?\n")
        self.zappai_collector = ZappaiCollector(subtitle_path)
        self.storage = StorageFactory()
        self.storage.set_subtitle_path(subtitle_path)
        tv_or_movie = input("Is it a TV show or a movie? (tv / movie)\n")
        if tv_or_movie.lower().strip() == 'tv': 
            self.storage.set_tv_show(True)
            self.storage.set_show_name(input("What is the name of the TV show?\n"))
        elif tv_or_movie.lower().strip() == 'movie':
            self.storage.set_tv_show(False)
            self.storage.set_show_name(input("What is the name of the movie?\n"))
        else:
            print("Sorry, that isn't a valid option. Please run the program again.")
            return
        self.storage.set_zappai_dir_path(PATH_FOR_RESULTS + self.storage.show_name)
        self.zappai_collector.parse_files_into_lines()
        self.zappai_collector.check_for_zappai()
        self.get_user_feedback()
        self.store_zappai()

    def get_user_feedback(self):
        for zappai in self.zappai_collector.zappai_list:
            if self.check_if_favorite(zappai):
                if self.storage.check_tv_show():
                    season = self.request_season(zappai.filename)
                    episode = self.request_episode(zappai.filename)
                    episode_dir_name = season + '_' + episode
                    self.storage.prepare_zappai_storage_tv(zappai, zappai.filename, zappai.title, episode_dir_name)
                else:
                    self.storage.prepare_zappai_storage_movie(zappai, zappai.filename, zappai.title)

    def check_if_favorite(self, zappai):
        print(str(zappai.text))
        check = input("\nIs this really a 'zappai' and do you like this one? (y / n)\n")
        if check.lower().strip() == 'y':
            zappai.set_favorite()
            return True
        return False

    def store_zappai(self):
        if not self.storage.check_tv_show():
            self.storage.plan_movie_dirs()
            self.storage.make_movie_dirs()
        elif self.storage.check_tv_show():
            self.storage.plan_tv_dirs()
            self.storage.make_tv_dirs()
        print(self.storage.episode_dir_names)
        print(self.storage.zappai_dir_names)

    def request_season(self, filename):
        print('\n' + filename + '\n')
        return input("\nWhat season?\n")

    def request_episode(self, filename): 
        print('\n' + filename + '\n')
        return input("\nWhat episode?\n")

class ZappaiStorage():
    def __init__(self, zappai, zappai_filename, zappai_title):
        self.zappai_filename = zappai_filename
        self.zappai_title = zappai_title
        self.zappai = zappai

    def set_zappai_title(self):
        self.zappai_title = zappai_title

    def set_zappai_episode_dir_name(self, season_episode):
        self.season_episode = season_episode

class StorageFactory():
    def __init__(self):
        self.zappai_dir_names = {} 
        self.episode_dir_names = {}
        self.zappai_storage_dict = {}
        self.movie_zappai_titles = []

    def set_subtitle_path(self, path):
        self.subtitle_path = path

    def set_movie_filename(self, movie_filename):
        self.movie_filename = movie_filename

    def make_tv_dirs(self):
        os.mkdir(self.zappai_dir_path)
        for filepath, episode in self.episode_dir_names.items():
            os.mkdir(self.zappai_dir_path + '/' + episode)
            #save a copy of the  subtitle file in the new episode dir
            copyfile(filepath, self.zappai_dir_path + '/' + episode + '/' + os.path.basename(filepath))

            for zappai_title in self.zappai_dir_names[episode]:
                zappai_path = self.zappai_dir_path + '/' + episode + '/' + zappai_title + '/'
                os.mkdir(zappai_path)

                #save the zappai in a .txt file with info about the video segment start and end times
                zappai_file = open(zappai_path + zappai_title + '.txt', 'w+')
                zappai_file.write(str(self.zappai_storage_dict[zappai_title].zappai.start_time))
                zappai_file.write('\n\n')
                zappai_file.write(self.zappai_storage_dict[zappai_title].zappai.text)

                #make a directory for the screenshots/other visuals
                os.mkdir(zappai_path + 'visuals')

    def plan_tv_dirs(self):
        for title, zappaistorage in self.zappai_storage_dict.items():
            if not zappaistorage.zappai_filename in self.episode_dir_names:
                self.episode_dir_names[zappaistorage.zappai_filename] = zappaistorage.season_episode
            if not zappaistorage.season_episode in self.zappai_dir_names:
                self.zappai_dir_names[zappaistorage.season_episode] = []
            self.zappai_dir_names[zappaistorage.season_episode].append(zappaistorage.zappai_title)

    def make_movie_dirs(self):
        os.mkdir(self.zappai_dir_path)
        for zappai_title in self.movie_zappai_titles:
            zappai_path = self.zappai_dir_path + '/' + zappai_title + '/'
            os.mkdir(zappai_path)
            copyfile(filename, self.zappai_dir_path + '/' + self.movie_filename)

            #save the zappai in a .txt file with info about the video segment start and end times
            zappai_file = open(zappai_path + zappai_title + '.txt', 'w+')
            zappai_file.write(str(self.zappai_storage_dict[zappai_title].zappai.start_time))
            zappai_file.write('\n\n')
            zappai_file.write(self.zappai_storage_dict[zappai_title].zappai.text)

            #make a directory for the screenshots/other visuals
            os.mkdir(zappai_path + 'visuals')

    def plan_movie_dirs(self):
        for title, zappaistorage in self.zappai_storage_dict.items():
            if not zappaistorage.zappai_title in self.movie_zappai_titles:
                self.movie_zappai_titles.append(zappaistorage.zappai_title)

    def prepare_zappai_storage_tv(self, zappai, zappai_filename, zappai_title, episode_dir_name):
        self.zappai_storage_dict[zappai_title] = ZappaiStorage(zappai, zappai_filename, zappai_title)
        self.zappai_storage_dict[zappai_title].set_zappai_episode_dir_name(episode_dir_name)

    def prepare_zappai_storage_movie(self, zappai, zappai_filename, zappai_title):
        self.zappai_storage_dict[zappai_title] = ZappaiStorage(zappai, zappai_filename, zappai_title)
        self.set_movie_filename(zappai_filename)

    def set_zappai_dir_path(self, dir_path):
        self.zappai_dir_path = dir_path

    def check_tv_show(self):
        return self.is_tv_show

    def set_tv_show(self, is_tv_show):
        self.is_tv_show = is_tv_show
    
    def store_movie_zappai(self, zappai):
        os.mkdir(base_zappai_path + self.zappai_dir_names[zappai.filename] + '/' + zappai.title)

    def set_show_name(self, show_name):
        self.show_name = show_name

    def store_tv_zappai(self, zappai):
        os.mkdir(base_zappai_path + zappai.episode_season_dir_names[zappai.filename] + '/' + self.zappai_dirs_to_make[zappai.filename] + '/' + zappai.title)

    def check_for_same_zappai_dir(self, dir_name):
        if filename in self.zappai_dir_names:
            return True
        return False

    def check_for_same_episode_dir(self, dir_name):
        if filename in self.zappai_dir_names:
            return True
        return False

class Zappai():
    def __init__(self, text, title, filename, start_time):
        self.text = text 
        self.title = title
        self.filename = filename
        self.start_time = start_time
        self.favorite = False

    def set_favorite(self):
        self.favorite = True

class SubtitleLine():
    def __init__(self, subtitle_index):
        self.index = subtitle_index
        self.has_typo = False
        self.punctuation_table = str.maketrans('', '', string.punctuation) 

    def set_content(self, content):
        self.content = content

    def format_content(self):
        # remove any html tags like <i> from the subtitle
        cleantags = re.compile('<.*?>')
        self.content = re.sub(cleantags, '', self.content)

        # remove newlines
        self.content = self.content.replace('\n', " ")

        #todo get rid of music notation -- currently counting as a syllable

    def set_times(self, start_time, end_time):
        self.start_time = start_time 
        self.end_time = end_time

    def make_zappai_title(self):
        return "_".join([word.translate(self.punctuation_table).lower() for word in self.content.split(" ")])

    def count_syllables(self):
        words = self.content.split(" ")
        self.syllable_count = 0
        for word in words:
            self.has_typo = False
            word = word.rstrip().lower()
            word = word.rstrip(string.punctuation).lower()
            try:
                num_syl = nsyl(word)[0]
            except:
                self.has_typo = True
                num_syl = word.count("a") + word.count("e") + word.count("i") + word.count("o") + word.count("u") + word.count("y")
                if num_syl == 0 and word != '':
                    num_syl = 1
            self.syllable_count += num_syl

class SubtitleFile():
    def __init__(self, filename):
        self.filename = filename 
        self.lines = []
    
    def set_file_content(self, file_content):
        self.file_content = file_content
    
    def remove_formatting(self):
        tag9999 = self.file_content.find("9999") - 4
        tag_end_font = self.file_content.find("</font>")
        if tag9999 and tag_end_font: 
            if tag_end_font > tag9999:
                self.file_content = self.file_content[0:tag9999] + self.file_content[(tag_end_font+1):len(self.file_content)]

    def parse_subtitles(self):
        self.subtitles_list = list(srt.parse(self.file_content))

    def inspect_subtitles(self):
        for line in self.subtitles_list:

            #check if the subtitle group has more than one speaker
            #todo refactor this
            if '\n-' in line.content:
                line_one = SubtitleLine(line.index)
                line_one.set_content(line.content.split('\n-')[0].strip())
                line_one.set_times(line.start, line.end)
                line_one.format_content()
                line_one.count_syllables()
                self.lines.append(line_one)

                line_two = SubtitleLine(line.index)
                line_two.set_content(line.content.split('\n-')[1].strip())
                line_two.set_times(line.start, line.end)
                line_two.format_content()
                line_two.count_syllables()
                self.lines.append(line_two)

            else:
                new_line = SubtitleLine(line.index)
                new_line.set_content(line.content.strip())
                new_line.set_times(line.start, line.end)
                new_line.format_content()
                new_line.count_syllables()
                self.lines.append(new_line)
        
class ZappaiCollector():
    def __init__(self, dir_name):
        self.dir_name = dir_name
        self.subtitle_files = {}
        self.zappai_list = []
    def parse_files_into_lines(self):
        for f in os.listdir('./' + self.dir_name):
            with codecs.open('./' + self.dir_name +'/' + f, 'r', encoding='utf-8-sig', errors='ignore') as f:
                self.subtitle_files[f.name] = SubtitleFile(f.name)
                file_content = f.read()
                try:
                    self.subtitle_files[f.name].set_file_content(file_content)
                    self.subtitle_files[f.name].remove_formatting()
                    self.subtitle_files[f.name].parse_subtitles()
                    self.subtitle_files[f.name].inspect_subtitles()
                except Exception as e:
                    #todo raise this instead of printing it
                    print(f.name + " wasn't correctly parsed into subtitles because " + str(e))

    def make_unique_title(self, original_title):
        matching_titles_count = 0
        for zappai in self.zappai_list:
            if zappai.title == original_title:
                matching_titles_count += 1
        if matching_titles_count > 0:
            return original_title + str(matching_titles_count)
        else:
            return original_title

    def check_for_zappai(self):
        for filename, subtitle_file in self.subtitle_files.items():
            zappai_line_count = 0
            zappai = ""

            for line in subtitle_file.lines:
               line = line
               if line.has_typo:
                   zappai = ""
                   zappai_line_count = 0
               if line.syllable_count == 5 and (zappai_line_count == 0 or zappai_line_count == 2):
                   start_time = line.start_time
                   zappai_line_count += 1
                   zappai += line.content + "\n"
                   if zappai_line_count == 1:
                       zappai_title = line.make_zappai_title() 
               elif line.syllable_count == 7 and zappai_line_count == 1:
                   zappai_line_count += 1
                   zappai += line.content + "\n"
               else:
                   zappai_line_count = 0
                   zappai = ""
               if zappai_line_count == 3:
                   unique_title = self.make_unique_title(zappai_title)
                   self.zappai_list.append(Zappai(zappai, unique_title, subtitle_file.filename, line.start_time))
                   zappai_line_count = 0
                   zappai = ""

d = cmudict.dict()


def nsyl(word):
   return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]]


terminal_ui = TerminalUi()
terminal_ui.run()

# Example of subtitle syllable count dictionary
# The.Office.S02E01.The.Dundies.srt

# 260
# 00:19:52,368 --> 00:19:54,740
# Ok let's get you home, come.
#
# 261
# 00:19:59,408 --> 00:20:01,823
# - Good bye.
# - Good night, have a good night.
#
#
# {'The.Office.S02E01.The.Dundies.srt': [{
#                                           'frame': 260,
#                                           'start_time': '00:19:52,368',
#                                           'end_time': '00:19:54,740',
#                                           'syllable_info': [{'dialog': 'OK let's get you home, come.',
#                                                               'syllable_count': 7 }]
#                                       },
#                                       {
#                                           'frame': 261,
#                                           'start_time': '00:19:59,408',
#                                           'end_time': '00:20:01,823',
#                                           'syllable_info': [{'dialog': '- Good bye.',
#                                                              'syllable_count': 2 },
#                                                             {'dialog': 'Good night, have a good night.',
#                                                              'syllable_count': 6 }]
#                                       }]
# }
#
#
#

# how to count the syllables in a word
#https://stackoverflow.com/questions/405161/detecting-syllables-in-a-word/4103234#4103234

# how to get rid of escape characters when reading thru a file
#https://stackoverflow.com/questions/23933784/reading-utf-8-escape-sequences-from-a-file

#how to remove trailing punctuation from strings
# https://stackoverflow.com/questions/22469766/how-can-we-strip-punctuation-at-the-start-of-a-string-using-python

#what's a haiku?
#http://www.hsa-haiku.org/archives/HSA_Definitions_2004.html
