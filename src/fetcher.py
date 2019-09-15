import pandas as pd
import numpy as np
from worker import MongoWorker

def add_sentiment(dataframe):
    """
    Adds a sentiment class to the dataset based on the rating given by the reviewer.
    """
    def determine_sentiment(row):
        if row['rating'] in [1, 2, 3]:
            return 0
        elif row['rating'] in [4, 5, 6]:
            return 1
        elif row['rating'] in [7, 8, 9, 10]:
            return 2
            
    dataframe['sentiment'] = dataframe.apply(lambda row: determine_sentiment(row), axis=1)
    return dataframe

worker = MongoWorker()
# reviews = worker.getRatedReviews()
reviews = worker.getUnratedReviews()

df = pd.DataFrame(reviews)

# df = pd.read_pickle('rated_reviews.gzip')
# df = df.astype({'rating': 'int32'})
# df = add_sentiment(df)
# df = df.drop(columns=["_id", "title", "author", "movie", "rating", "date", "helpful"])
df = df.drop(columns=["_id", "title", "author", "movie", "date", "helpful"])
# df = df.drop(df.columns[0], axis=1)
df['review'].replace('', np.nan, inplace=True)
df.dropna(subset=['review'], inplace=True)

df.to_csv("not_rated_reviews.csv", index=False)

