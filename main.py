from anagram import WordGame, EasyGame, HardGame, load_words

word_list = load_words()
print(f"\n  Welcome to Anagram Blitz! ({len(word_list)} words loaded)")

while True:
    print("\n" + "═" * 40)
    print("  1. Easy  (4-6 letter words, hints allowed)")
    print("  2. Hard  (7-10 letter words, no hints)")
    print("  3. Quit")
    print("═" * 40)

    choice = input("  Choose (1-3): ").strip()

    if choice == "3":
        print(f"\n  Thanks for playing! All-time high score: {WordGame.high_score}\n")
        break
    elif choice in ("1", "2"):
        try:
            rounds = int(input("  How many rounds? (default 5): ").strip() or "5")
        except ValueError:
            rounds = 5
        game = EasyGame(word_list, rounds) if choice == "1" else HardGame(word_list, rounds)
        game.play()
    else:
        print("  Invalid choice.")
