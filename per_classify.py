import argparse
import os
import math

__author__ = 'ameya'

mode = "DEV"


class PerceptronClassify():
    class __PerceptronClassify():
        def __init__(self):
            self.classify_dir = None
            self.bias = 0
            self.weights = {}

        def set_classify_dir(self, classify_dir):
            self.classify_dir = classify_dir

        def cache_training_model(self, model_file):
            try:
                with open(model_file, 'r', encoding='latin1') as file_handler:
                    try:
                        self.bias = int(file_handler.readline())
                    except ValueError as e:
                        self.bias = 0
                    while True:
                        try:
                            line = file_handler.readline()
                            if not line:
                                break
                            line_content = line.split()
                            if line_content[0] in self.weights:
                                print("duplicate: " + str(line_content[0]))
                            else:
                                self.weights[line_content[0]] = int(line_content[1])
                        except:
                            continue
            except (FileNotFoundError, Exception) as e:
                return

        def classify_model(self, write_file):
            correct_spam = 0
            total_spam = 0
            correct_ham = 0
            total_ham = 0
            classified_spam = 0
            classified_ham = 0
            try:
                with open(write_file, "w", encoding='latin1') as write_file_handler:
                    for current_dir, dirnames, filenames in os.walk(self.classify_dir):
                        for file_name in filenames:
                            file_extension = os.path.splitext(file_name)[1]
                            if file_extension != '.txt':
                                continue
                            try:
                                with open(os.path.join(current_dir, file_name), "r",
                                          encoding="latin1") as read_file_handler:
                                    file_content = read_file_handler.read()
                                    tokens = file_content.split()
                                    try:
                                        prob_spam_word = math.log(self.prob_spam)
                                    except ValueError as e:
                                        prob_spam_word = 0
                                    try:
                                        prob_ham_word = math.log(self.prob_ham)
                                    except ValueError as e:
                                        prob_ham_word = 0
                                    for token in tokens:
                                        if token in self.train_data:
                                            try:
                                                prob_spam_word += math.log(self.train_data[token][0])
                                            except ValueError as e:
                                                pass
                                            try:
                                                prob_ham_word += math.log(self.train_data[token][1])
                                            except ValueError as e:
                                                pass
                                    if prob_spam_word > prob_ham_word:
                                        if "spam" in file_name:
                                            total_spam += 1
                                            correct_spam += 1
                                        elif "ham" in file_name:
                                            total_ham += 1
                                        write_file_handler.write(
                                            "spam " + str(os.path.join(current_dir, file_name)) + '\n')
                                        classified_spam += 1
                                    elif prob_ham_word > prob_spam_word:
                                        if "ham" in file_name:
                                            correct_ham += 1
                                            total_ham += 1
                                        elif "spam" in file_name:
                                            total_spam += 1
                                        write_file_handler.write(
                                            "ham " + str(os.path.join(current_dir, file_name)) + '\n')
                                        classified_ham += 1
                                    else:
                                        # equal, so classify as spam
                                        # print("neither spam or ham: " + str(os.path.join(current_dir, file_name)) + " " + str(
                                        # prob_spam_word) + " " + str(prob_ham_word))
                                        write_file_handler.write(
                                            "spam " + str(os.path.join(current_dir, file_name)) + '\n')
                            except:
                                continue
            except:
                return
            if mode == "DEV":
                try:
                    spam_precision = correct_spam / classified_spam
                except ZeroDivisionError as e:
                    spam_precision = float(0)
                try:
                    ham_precision = correct_ham / classified_ham
                except ZeroDivisionError as e:
                    ham_precision = float(0)
                try:
                    spam_recall = correct_spam / total_spam
                except ZeroDivisionError as e:
                    spam_recall = float(0)
                try:
                    ham_recall = correct_ham / total_ham
                except ZeroDivisionError as e:
                    ham_recall = float(0)
                try:
                    spam_f1 = (2 * spam_precision * spam_recall) / (spam_precision + spam_recall)
                except ZeroDivisionError as e:
                    spam_f1 = float(0)
                try:
                    ham_f1 = (2 * ham_precision * ham_recall) / (ham_precision + ham_recall)
                except ZeroDivisionError as e:
                    ham_f1 = float(0)
                print("spam precision: " + str(spam_precision))
                print("spam recall: " + str(spam_recall))
                print("spam F1: " + str(spam_f1))
                print("ham precision: " + str(ham_precision))
                print("ham recall: " + str(ham_recall))
                print("ham F1: " + str(ham_f1))

    __instance = None

    def __init__(self):
        if PerceptronClassify.__instance is None:
            PerceptronClassify.__instance = PerceptronClassify.__PerceptronClassify()
        self.__dict__['PerceptronClassify__instance'] = PerceptronClassify.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


def get_command_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help='Directory of input development data.')
    parser.add_argument("output_file", help='Name of output file')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    classify_instance = PerceptronClassify()
    args = get_command_args()
    classify_instance.set_classify_dir(os.path.abspath(args.input_dir))
    classify_instance.cache_training_model('per_model.txt')
    classify_instance.classify_model(args.output_file)