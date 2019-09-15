from os import listdir
from os.path import isfile, join
from pathlib import Path

docs_path = Path("/users/pawel/datasets/plwiki/docs")
files = [f for f in listdir(docs_path) if isfile(join(docs_path, f)) and f.endswith(".txt")]

to_go_through = len(files)

total_files = 0
total_tokens = 0

total_tokens_over = 0
total_files_over = 0

for file in files:
    if total_tokens % 1000 == 0: print("{}/{}...".format(total_files, to_go_through))

    f = open(docs_path/file, "r")
    contents = f.read()

    tokens = len(contents.split())
    letters = len(contents)

    if letters > 2800: 
        total_tokens_over += tokens
        total_files_over += 1

    total_tokens += tokens
    total_files += 1

print("Total files: {}, total tokens: {}, 2500 - total files over: {}, total tokens over: {}".format(total_files, total_tokens, total_files_over, total_tokens_over))

