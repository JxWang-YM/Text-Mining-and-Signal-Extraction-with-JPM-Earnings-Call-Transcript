import glob
import os
import sys

import pandas as pd


def parse_args():
    data_path = sys.argv
    return data_path


def process_file(file):
    # throw away top part
    top_part_ending = ["All rights reserved", "FDCH e-Media."]
    for top in top_part_ending:
        if top in file:
            file.split(top)[1]

    f = file.split("\n")
    indexes = []

    f_no_factiva = []
    for line in f:
        if len(line) == 0:
            continue
        if line.startswith("\f"):
            line = line[1:]
        if not line.endswith(" Factiva, Inc. All rights reserved."):
            f_no_factiva.append(line)
    count = 0
    for line in f_no_factiva:
        if ":" in line:
            indexes.append(count)
        count = count + 1

    final_text = []
    tuples = [[x, y] for x, y in zip(indexes, indexes[1:])]
    for tup in tuples:
        line = f_no_factiva[tup[0]:tup[1]]
        line = " ".join(line).replace("\n", "")
        final_text.append(line.strip())
    string_out = ""
    ceos_cfos = ["MARIANNE L", "JAMIE D", "JENNIFER A", "BILL H", "DINA D", "MIKE C"]
    for speaker in final_text:
        for person in ceos_cfos:
            if speaker.startswith(person):
                string_out = string_out + "\n" + speaker
    return string_out


def read_files(entries):
    transcript = []
    quarter_year = []
    # for each earning call do the following
    for file in entries:
        # extract basename of file ( i.e. only "name.txt")
        basename = os.path.basename(file)
        # from file name get the quarter and year
        quarter_f = basename[0:2]
        year_f = basename[3:7]
        # read the file into a string
        with open(file, "r") as call:
            unprocessed_f = call.read()

        # clean file and get only the speakers that we want
        file_clean = process_file(unprocessed_f)
        transcript.append(file_clean)
        quarter_year.append('{}_{}'.format(quarter_f, year_f))

    return transcript, quarter_year


def main():
    # parse input arguements 1. where JP morgan calls flder  is 2. where price  folder is 3. where to write transcript
    try:
        args = parse_args()
        earning_dir = args[1]
        output_dir = args[2]
    except IndexError:
        print('Usage: python preprocess.py <earning call path> <output path>')
        sys.exit()

    # get a list of all the files in a directory
    entries = []

    for f in glob.glob('{}/*'.format(earning_dir)):
        entries.append(f)

    # read all files and return date , transcript and quarter year
    transcript, quarter_year = read_files(entries)
    df_t = pd.DataFrame(data={'quarter_year': quarter_year, 'transcript': transcript})
    df_t.to_csv("{}/transcripts.csv".format(output_dir))


if __name__ == '__main__':
    main()
