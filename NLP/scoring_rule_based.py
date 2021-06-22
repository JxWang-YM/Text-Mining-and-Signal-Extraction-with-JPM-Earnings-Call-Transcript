import re
import sys

import pandas as pd
from textblob import TextBlob


def parse_args():
    data_path = sys.argv
    return data_path


def read_lexicon(positive, negative, basecase = False):
    postive_lex = {'big', 'grew', 'growth', 'high', 'increased', 'margin', 'over', 'profit', 'strong', 'up'}
    negative_lex = {'down', 'debt', 'loss', 'not', 'reduce', 'reduced', 'restrict', 'restricted', 'weak'}
    if basecase:
        return postive_lex, negative_lex
    with open(positive, "r") as p:
        pos_word = p.readlines()[1:]
    with open(negative, "r") as n:
        neg_word = n.readlines()[1:]

    postive_lex.update(x.rstrip().lower() for x in pos_word)
    negative_lex.update(x.rstrip().lower() for x in neg_word)
    return postive_lex, negative_lex


def numeric_sentiment_based_scoring(text, positive_lex, negative_lex):
    """ window_size: integer
        alpha: float in range (0, 1)
    """
    tb = TextBlob(text)
    positive = 0
    negative = 0
    index = 0
    numeric_regex = re.compile('\d+\.*\d*')
    window_size = 5
    while index < len(tb.tokens):
        token = tb.tokens[index]
        if re.match(numeric_regex, token) is not None:
            low_bound = index - window_size
            high_bound = index + window_size
            # Iterate window_size words before and after token
            for l in tb.tokens[low_bound:index] + tb.tokens[index + 1:high_bound + 1]:
                if l in positive_lex:
                    positive += 1
                if l in negative_lex:
                    negative += 1
                # More rules can be added in these lines, for example, composite rules.
        index += 1
    score = (positive - negative) / (positive + negative)
    return score


def main():
    try:
        args = parse_args()
        data_path = args[1]
        positive = args[2]
        negative = args[3]
        output_dir = args[4]
    except IndexError:
        print('Usage: python preprocess_data.py <data_path> <lexicon path> <output dir>')
        sys.exit()

    # read csv
    data = pd.read_csv(data_path, index_col=0)
    positive_lex_basecase, negative_lex_basecase = read_lexicon(positive, negative, True)

    positive_lex, negative_lex = read_lexicon(positive, negative)
    data['numeric_sentiment_score_basecase'] = data['transcript'].apply(numeric_sentiment_based_scoring,
                                                               args=(positive_lex, negative_lex))
    data['numeric_sentiment_score'] = data['transcript'].apply(numeric_sentiment_based_scoring,
                                                               args=(positive_lex_basecase, negative_lex_basecase))
    data = data.drop(columns=["transcript"])
    data.to_csv("{}/rule_based_scores.csv".format(output_dir))


if __name__ == '__main__':
    main()
