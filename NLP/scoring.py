import glob
import sys
import numpy as np
import pandas as pd
from textblob import TextBlob
from nltk.tokenize import sent_tokenize


def parse_args():
    data_path = sys.argv
    return data_path


def text_polarity(r, column):
    text_in_sentences = [r[column].split("\n")[1:]][0]
    #  we want to score without the name of the speaker
    keep_only_text = [x.split(":")[1] for x in text_in_sentences]
    tb = TextBlob("".join(keep_only_text))
    return tb.polarity


def sentence_polarity_avg(r, column):
    polarities = []
    text_in_sentences = [r[column].split("\n")[1:]][0]
    #  we want to score without the name of the speaker
    keep_only_text = [x.split(":")[1] for x in text_in_sentences]
    tb = TextBlob("".join(keep_only_text))
    for sentence in tb.sentences:
        polarities.append(sentence.polarity)
    return np.mean(polarities)


def check_sentence_length(sentence):
    tokens = sentence.split()
    if len(tokens) < 4:
        return True
    else:
        return False


def check_word_in_lexicon(sentence, lexicon):
    # todo: we can refine the string matching here or normalize our words?
    tokens = sentence.split()
    for tok in tokens:
        if tok in lexicon:
            return False
    return True


def filtering(r, column, method, lexicon=None):
    text = r[column].split("\n")[1:]
    words_filtered = []
    words_thrown = []
    for speaker in text:
        # sentences we keep
        filtered_sentences = []
        # sentences we throw out
        kicked_out = []
        # split their name and their words
        split = speaker.split(":")
        person = split[0]
        words = speaker.split(":")[1]
        words = sent_tokenize(words)

        for sentence in words:
            # use the sentence length method to calculate score or lexicon method
            if method == "len":
                if check_sentence_length(sentence):
                    kicked_out.append(sentence)
                    continue
                else:
                    filtered_sentences.append(sentence)
            elif method == "lexicon":
                if check_word_in_lexicon(sentence, lexicon):
                    kicked_out.append(sentence)
                    continue
                else:
                    filtered_sentences.append(sentence)

        # put together again their words without the filtered sentences
        if len(filtered_sentences) > 0:
            words_filtered.append("\n" + person + ":" + "".join(filtered_sentences))
        if len(kicked_out) > 0:
            words_thrown.append(kicked_out)
        # put together all the turns of the speakers

    return "".join(words_filtered)


def read_lexicon(entries):
    list_words = []
    for file in entries:
        with open(file, "r") as f:
            list_words.append(f.readlines()[1:])
    keep_words = set()
    for sentiment_list in list_words:
        for word in sentiment_list:
            keep_words.add(word.rstrip().lower())
    return keep_words


def main():
    try:
        args = parse_args()
        data_path = args[1]
        lexicon_dir = args[2]
        output_dir = args[3]
    except IndexError:
        print('Usage: python preprocess_data.py <data_path> <lexicon path> <output dir>')
        sys.exit()
    # read csv
    data = pd.read_csv(data_path, index_col=0)

    # get a list of lexicon files
    entries = []
    for f in glob.glob('{}/*.csv'.format(lexicon_dir)):
        entries.append(f)
    lexicon_dictionary = read_lexicon(entries)

    # Base case scoring without filtering with the two methods
    data['txt_polarity_basecase'] = data.apply(text_polarity, args=("transcript",), axis=1)
    data['sentence_polarity_basecase'] = data.apply(sentence_polarity_avg, args=("transcript",), axis=1)

    # Do the filtering Method length
    data['transcripts_filtered_length'] = data.apply(filtering, args=("transcript", "len"), axis=1)
    # Do the filtering Method lexicon
    data['transcripts_filtered_lexicon'] = data.apply(filtering, args=("transcript", "lexicon", lexicon_dictionary), axis=1)

    # Calculate the new scores for length method
    data['txt_polarity_filtered_length'] = data.apply(text_polarity, args=("transcripts_filtered_length",), axis=1)
    data['sentence_polarity_filtered_length'] = data.apply(sentence_polarity_avg, args=("transcripts_filtered_length",), axis=1)

    # Calcualte the new scores for lexicon method
    data['txt_polarity_filtered_lexicon'] = data.apply(text_polarity, args=("transcripts_filtered_lexicon",), axis=1)
    data['sentence_polarity_filtered_lexicon'] = data.apply(sentence_polarity_avg, args=("transcripts_filtered_lexicon",),
                                                           axis=1)

    data = data.drop(columns=["transcripts_filtered_length", "transcript", "transcripts_filtered_lexicon"])
    data.to_csv("{}/NPL_scores.csv".format(output_dir))


if __name__ == '__main__':
    main()
