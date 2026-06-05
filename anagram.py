"""
CS 162P
Cooper Christensen
Final Project
Anagram Solver the Game
"""

import random
from abc import ABC, abstractmethod




def load_words(path="words.txt"):
    try:
        with open(path) as f:
            return [line.strip().lower() for line in f if line.strip().isalpha()]
    except FileNotFoundError:
        print(f"  Error: '{path}' not found.")
        exit(1)


def find_anagrams(word, word_list):
    """Original anagram finder."""
    sorted_word = sorted(word)
    return [w for w in word_list if sorted(w) == sorted_word and w != word]


def scramble(word):
    letters = list(word)
    for _ in range(100):
        random.shuffle(letters)
        if "".join(letters) != word:
            return "".join(letters)
    return "".join(reversed(word))




class WordGame(ABC):
    """
    Abstract base class for all word games.
    Subclasses must implement play() and score_round().
    """

    high_score = 0      # class variable — shared across all instances
    total_games = 0     # class variable

    def __init__(self, word_list, rounds=5):
        self._word_list = word_list
        self._rounds = rounds
        self._score = 0
        self._history = {}  # dict: round number -> result info

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if value < 0:
            value = 0
        self._score = value

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def score_round(self, correct, hints_used=0):
        pass

    def pick_word(self, min_len, max_len):
        pool = [w for w in self._word_list if min_len <= len(w) <= max_len]
        return random.choice(pool) if pool else random.choice(self._word_list)

    def update_high_score(self):
        if self._score > WordGame.high_score:
            WordGame.high_score = self._score
            return True
        return False

    def show_history(self):
        if not self._history:
            print("  No rounds played.")
            return
        print(f"\n  {'Round':<8} {'Word':<12} {'Guess':<12} {'Result':<10} {'Points'}")
        print("  " + "─" * 50)
        for rnd, info in self._history.items():
            print(f"  {rnd:<8} {info['word']:<12} {info['guess']:<12} "
                  f"{info['result']:<10} {info['points']}")

    def finish(self):
        new_high = self.update_high_score()
        print("═" * 40)
        print(f"  Game over! Final score: {self._score}")
        if new_high:
            print("  🏆 New high score!")
        print(f"  Total games played: {WordGame.total_games}")
        print("═" * 40)
        see = input("\n  View round history? (y/n): ").strip().lower()
        if see == "y":
            self.show_history()

    def __str__(self):
        return (f"{self.__class__.__name__} | "
                f"Score: {self._score} | High Score: {WordGame.high_score}")




class EasyGame(WordGame):
    """
    Short words (4-6 letters), up to 3 hints, 10 pts per correct answer.
    Hints cost 2 pts each.
    """

    POINTS = 10
    HINT_COST = 2
    MAX_HINTS = 3

    def play(self):
        WordGame.total_games += 1
        print("\n  EASY MODE — 4 to 6 letter words, hints allowed.\n")

        for rnd in range(1, self._rounds + 1):
            word = self.pick_word(4, 6)
            anagrams = find_anagrams(word, self._word_list)
            valid = {word} | set(anagrams)
            hints_used = [0]

            print(f"  Round {rnd}/{self._rounds}  |  {self}")
            print(f"  Scrambled: {scramble(word).upper()}")
            print("  (type 'hint' for a letter, 'skip' to skip)\n")

            guess = self._guess_loop(word, valid, hints_used)

            correct = guess in valid
            pts = self.score_round(correct, hints_used=hints_used[0])
            result = "correct" if correct else "skip" if guess == "skip" else "wrong"
            self._history[rnd] = {
                "word": word, "guess": guess or "—",
                "result": result, "points": pts
            }

            if correct:
                print(f"  ✓ Correct! +{pts} pts")
            elif guess == "skip":
                print(f"  Skipped. The word was: {word}")
            else:
                print(f"  ✗ Wrong. The word was: {word}")
            print()

        self.finish()

    def score_round(self, correct, hints_used=0):
        if not correct:
            return 0
        pts = max(0, self.POINTS - hints_used * self.HINT_COST)
        self.score += pts
        return pts

    def _guess_loop(self, word, valid, hints_used, depth=0):
        """Recursively prompt until correct, skip, or hint limit reached."""
        if depth > self.MAX_HINTS:
            return ""

        guess = input("  Your guess: ").strip().lower()

        if guess in ("skip", "quit") or guess in valid:
            return guess

        if guess == "hint":
            if hints_used[0] < self.MAX_HINTS:
                hints_used[0] += 1
                hint = self._build_hint(word, hints_used[0])
                print(f"  💡 Hint {hints_used[0]}: {hint}  (-{self.HINT_COST} pts)")
            else:
                print("  No hints left!")
            return self._guess_loop(word, valid, hints_used, depth + 1)

        print("  Not quite, try again.")
        return self._guess_loop(word, valid, hints_used, depth + 1)

    def _build_hint(self, word, revealed):
        letters = sorted(word)
        return "".join(letters[:revealed]) + "_" * (len(word) - revealed)



class HardGame(WordGame):
    """
    Longer words (7-10 letters), no hints, 20 pts per correct answer.
    Overrides score_round with stricter scoring.
    """

    POINTS = 20

    def play(self):
        WordGame.total_games += 1
        print("\n  HARD MODE — 7 to 10 letter words, no hints.\n")

        for rnd in range(1, self._rounds + 1):
            word = self.pick_word(7, 10)
            anagrams = find_anagrams(word, self._word_list)
            valid = {word} | set(anagrams)

            print(f"  Round {rnd}/{self._rounds}  |  {self}")
            print(f"  Scrambled: {scramble(word).upper()}")
            print("  (type 'skip' to skip)\n")

            guess = input("  Your guess: ").strip().lower()
            correct = guess in valid
            pts = self.score_round(correct)
            result = "correct" if correct else "skip" if guess == "skip" else "wrong"
            self._history[rnd] = {
                "word": word, "guess": guess or "—",
                "result": result, "points": pts
            }

            if correct:
                print(f"  ✓ Correct! +{pts} pts")
            elif guess == "skip":
                print(f"  Skipped. The word was: {word}")
            else:
                print(f"  ✗ Wrong. The word was: {word}")
                if anagrams:
                    print(f"    Valid answers included: {', '.join(list(valid)[:3])}")
            print()

        self.finish()

    def score_round(self, correct, hints_used=0):
        if not correct:
            return 0
        self.score += self.POINTS
        return self.POINTS
