import argparse
import os
import re
import math

__author__ = 'ameya'


class BayesLearn():
    class __BayesLearn():
        def __init__(self):
            self.training_dir = None
            self.spam_dirs = []
            self.ham_dirs = []
            self.total_files = 0
            self.spam_files = 0
            self.ham_files = 0
            self.train_data = dict()
            self.spam_words = 0
            self.ham_words = 0
            self.train_less = 0
            self.less_files = 0
            self.less_spam_files = 0
            self.less_ham_files = 0
            self.train_improved = 0
            self.stop_words = []

        def set_training_dir(self, training_dir):
            self.training_dir = training_dir

        def set_train_type(self, train_less, train_improved):
            self.train_less = train_less
            self.train_improved = train_improved
            if self.train_improved != 0:
                # get stop words from stopwords.txt
                try:
                    with open('stopwords_long.txt', 'r', encoding='latin1') as file_handler:
                        file_content = file_handler.read()
                        self.stop_words = file_content.split()
                except:
                    return

        # procedure to recursively determine all the spam and ham directories
        # and store in spam_dirs and ham_dirs
        def map_spam_ham_dirs(self):
            for current_dir, dirnames, filenames in os.walk(self.training_dir):
                last_dir_name = os.path.basename(current_dir)
                if last_dir_name == "spam":
                    for file_name in filenames:
                        file_extension = os.path.splitext(file_name)[1]
                        if file_extension == ".txt":
                            self.total_files += 1
                            self.spam_files += 1
                    self.spam_dirs.append(current_dir)
                elif last_dir_name == "ham":
                    for file_name in filenames:
                        file_extension = os.path.splitext(file_name)[1]
                        if file_extension == ".txt":
                            self.total_files += 1
                            self.ham_files += 1
                    self.ham_dirs.append(current_dir)
            if self.train_less != 0:
                # self.less_files = int((self.train_less / 100) * self.total_files)
                self.less_spam_files = math.ceil((self.train_less / 100) * self.spam_files)
                self.less_ham_files = math.ceil((self.train_less / 100) * self.ham_files)

        def train_model(self):
            self.bayes_train(self.spam_dirs, "spam")
            self.bayes_train(self.ham_dirs, "ham")
            if self.train_improved != 0:
                self.post_train_filter()

        def filter_token(self, token):
            if re.match(r'^[_\W]+$', token):
                return True
            if token in self.stop_words:
                return True
            return False

        def bayes_train(self, type_dir, type_mail):
            for single_dir in type_dir:
                for file_name in os.listdir(single_dir):
                    file_extension = os.path.splitext(file_name)[1]
                    if file_extension != '.txt':
                        continue
                    with open(os.path.join(single_dir, file_name), "r", encoding="latin1") as file_handler:
                        if self.train_less != 0:
                            if type_mail == "spam":
                                if self.less_spam_files > 0:
                                    self.less_spam_files -= 1
                                else:
                                    return
                            elif type_mail == "ham":
                                if self.less_ham_files > 0:
                                    self.less_ham_files -= 1
                                else:
                                    return
                        file_content = file_handler.read()
                        tokens = file_content.split()
                        for token in tokens:
                            if self.train_improved != 0:
                                if self.filter_token(token):
                                    continue
                                token = token.lower()
                            if type_mail == "spam":
                                self.spam_words += 1
                            elif type_mail == "ham":
                                self.ham_words += 1
                            if token in self.train_data:
                                if type_mail == "spam":
                                    self.train_data[token.strip()][0] += 1
                                elif type_mail == "ham":
                                    self.train_data[token.strip()][1] += 1
                            else:
                                if type_mail == "spam":
                                    self.train_data[token.strip()] = [1, 0]
                                elif type_mail == "ham":
                                    self.train_data[token.strip()] = [0, 1]

        def post_train_filter(self):
            # filter common words in both spam and ham
            # check if a word occurs frequently in both spam and ham
            # remove first 1% high freq. words
            top_1 = int(0.01 * len(self.train_data))
            spam_high_freq_words = sorted(self.train_data, key=lambda x: self.train_data[x][0], reverse=True)[:top_1]
            ham_high_freq_words = sorted(self.train_data, key=lambda x: self.train_data[x][1], reverse=True)[:top_1]
            high_freq_words = [word for word in spam_high_freq_words if word in ham_high_freq_words]
            for word in high_freq_words:
                del self.train_data[word]

        def write_training_data(self, write_file):
            try:
                with open(write_file, "w", encoding='latin1') as file_handler:
                    if self.total_files == 0:
                        return
                    # The first 2 lines are probabilities of spam and ham respectively
                    file_handler.write(str(self.spam_files / self.total_files) + '\n')
                    file_handler.write(str(self.ham_files / self.total_files) + '\n')
                    # Rest of the lines are words followed by their probabilities given spam and ham separated by spaces
                    for token in self.train_data:
                        try:
                            token_spam_add_one = (self.train_data[token][0] + 1) / (self.spam_words + len(self.train_data))
                            token_ham_add_one = (self.train_data[token][1] + 1) / (self.ham_words + len(self.train_data))
                            file_handler.write(
                                str(token) + ' ' + str(token_spam_add_one) + ' ' + str(token_ham_add_one) + '\n')
                        except:
                            # print("exception in writing training data")
                            continue
            except:
                return

    __instance = None

    def __init__(self):
        if BayesLearn.__instance is None:
            BayesLearn.__instance = BayesLearn.__BayesLearn()
        self.__dict__['BayesLearn__instance'] = BayesLearn.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


def get_command_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help='Directory of input training data.')
    parser.add_argument("-l", "--less", default=0, type=int, help='Add if data is to be trained with only x% data')
    parser.add_argument("-i", "--improved", default=0, type=int,
                        help='Add if data is to be trained with with additional strategies other than add one smoothing')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    train_instance = BayesLearn()
    args = get_command_args()
    train_instance.set_training_dir(args.input_dir)
    train_instance.set_train_type(args.less, args.improved)
    train_instance.map_spam_ham_dirs()
    train_instance.train_model()
    train_instance.write_training_data('nbmodel.txt')