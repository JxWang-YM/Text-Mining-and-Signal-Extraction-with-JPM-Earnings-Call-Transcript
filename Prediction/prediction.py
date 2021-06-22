import pandas as pd
import numpy as np
import sys

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression

np.set_printoptions(linewidth=100, precision=3)
pd.set_option('display.max_columns', 100)
pd.set_option('display.precision', 3)


def get_data(data, col_name, classification=False):
    if classification == True:
        data_subset = data[[col_name, 'EPS_Spread', 'Trend_Spread_Class']]
    else:
        data_subset = data[[col_name, 'EPS_Spread', 'Trend_Spread']]

    return data_subset


def split_data(data, test_size=0.2):
    x = np.array(data.drop(data.columns[-1], axis=1))
    y = np.array(data[data.columns[-1]])

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2)
    return x_train, x_test, y_train, y_test


def main():
    try:
        data_path = sys.argv[1]
        output_dir = sys.argv[2]
    except:
        print('Please provide appropriate data path & output directory')
        sys.exit()

    data = pd.read_csv(data_path, index_col=0)

    df_prediction = pd.DataFrame({'Model': ['Tree_reg', 'Linear', 'Tree_Class', 'Logistic']})

    for col_name in data.columns[:8]:

        data_pred_r = get_data(data, col_name=col_name, classification=False).dropna(axis=0)
        data_pred_c = get_data(data, col_name=col_name, classification=True).dropna(axis=0)

        iter_cv = 20
        score = np.empty([4, iter_cv])

        for i in range(iter_cv):

            x_train_r, x_test_r, y_train_r, y_test_r = split_data(data_pred_r, test_size=0.2)
            x_train_c, x_test_c, y_train_c, y_test_c = split_data(data_pred_c, test_size=0.2)

            tree_r = DecisionTreeRegressor()
            tree_r.fit(x_train_r, y_train_r)
            score[0, i] = tree_r.score(x_test_r, y_test_r)

            lm = LinearRegression(normalize=True)
            lm.fit(x_train_r, y_train_r)
            score[1, i] = lm.score(x_test_r, y_test_r)

            tree_c = DecisionTreeClassifier()
            tree_c.fit(x_train_c, y_train_c)
            score[2, i] = tree_c.score(x_test_c, y_test_c)

            lg = LogisticRegression(penalty='none')
            lg.fit(x_train_c, y_train_c)
            score[3, i] = lg.score(x_test_c, y_test_c)

        xtra = pd.DataFrame({'with {}'.format(col_name): score.mean(axis=1)})
        df_prediction = pd.concat([df_prediction, xtra], axis=1)

    df_prediction.set_index('Model', inplace=True)
    df_prediction.to_csv('{}/prediction.csv'.format(output_dir))


if __name__ == '__main__':
    main()

