from lazydata import track

with open(track("../data/some_data_file.txt"), "r") as f:
    print(f.read())
