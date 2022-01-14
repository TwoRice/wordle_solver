import json
import random
from urllib.parse import _NetlocResultMixinStr
import requests
import numpy as np

from itertools import groupby
from collections import Counter

WORD_LENGTH = 5
FIRST_WORD = np.array(list('adieu'))

class Worlde():
    
    def __init__(self, all_words):
        self.all_words = all_words
        self.num_guesses = []

    def delete_from_word(self, word, letter):
        idx = word.find(letter)
        if idx == 0: return word[1:]
        return word[0:idx] + word[idx+1:]

    def find_matching_words(self, last_word, matches, words, possible_letters):
        matching_words = []
        last_matching_letters = last_word[matches == 2]
        near_letters = last_word[matches == 1]

        for word in words:
            matching_letters = word[matches == 2]
            other_letters = word[matches != 2]
            valid_letters = [letter in pos_letters for letter, pos_letters in zip(word, possible_letters)]
            contains_near_letters = [letter in other_letters for letter in near_letters]

            if all(matching_letters == last_matching_letters) and all(valid_letters) and all(contains_near_letters):
                matching_words.append(word)
            
        return matching_words

    def adjust_possible_letters(self, last_word, matches, possible_letters):
        present_letters = last_word[matches != 0]
        for i, (letter, match) in enumerate(zip(last_word, matches)):
            if match == 0 and letter not in present_letters:
                for j in range(5):
                    if letter in possible_letters[j]:
                        possible_letters[j].remove(letter)
            elif match == 1 or (match == 0 and letter in present_letters):
                if letter in possible_letters[i]:
                    possible_letters[i].remove(letter)

        return possible_letters

    def select_max_from(self, source, by):
        max_idx = np.argwhere(by == np.amax(by)).flatten()
        select_max = np.array(source)[max_idx]

        return select_max

    def choose_best_word(self, next_word_candidates):
        num_unique_letters = list(map(lambda word: len(set(word)), next_word_candidates))
        next_word_candidates = self.select_max_from(next_word_candidates, num_unique_letters)

        return random.choice(next_word_candidates)

    def check_word(self, guess, target):
        success = np.array([0, 0, 0, 0, 0])
        for i, letter in enumerate(guess):
            if letter == target[i]:
                success[i] = 2

        target = target[success != 2]
        for i, letter in enumerate(guess):
            if success[i] == 2: continue
            if letter in target:
                success[i] = 1
                target = self.delete_from_word(''.join(target), letter)

        return success

    def calc_stats(self):
        num_guesses = np.array(self.num_guesses)
        passed = [i < 7 for i in num_guesses]
        pass_rate = sum(passed) / len(num_guesses)
        mean_guesses = np.mean(num_guesses)
        pass_mean_guesses = np.mean(num_guesses[passed])
        longest_streak = max([sum(group) for _, group in groupby(passed)])

        print(f'Pass Rate: {pass_rate * 100:.2f}%')
        print(f'Average Guesses: {mean_guesses:.4f}')
        print(f'Average Guesses of Passed: {pass_mean_guesses:.4f}')
        print(f'Longest Streak: {longest_streak}')

    def play(self):
        # a 2D array representing the possible letters in each of the 5 positions
        possible_letters = np.array(list('qwertyuiopasdfghjklzxcvbnm') * 5).reshape(5, 26).tolist()
        puzzle_word = random.choice(all_words)

        guess_word = FIRST_WORD
        possible_words = self.all_words
        i = 1
        while True:
            i += 1
            matches = self.check_word(guess_word, puzzle_word)
            possible_letters = self.adjust_possible_letters(guess_word, matches, possible_letters)
            possible_words = self.find_matching_words(guess_word, matches, possible_words, possible_letters)
            guess_word = self.choose_best_word(possible_words)
            if all(guess_word == puzzle_word):
                print(f"Found word {''.join(guess_word)} in {i} guesses") 
                self.num_guesses.append(i)
                break


all_words = np.load('dictionary.npy')
letter_scores = [Counter([word[i] for word in all_words]) for i in range(5)]
wordle = Worlde(all_words)

for i in range(50000):
    wordle.play()
wordle.calc_stats()