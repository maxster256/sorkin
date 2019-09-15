import pandas as pd
import numpy as np
# from worker import MongoWorker

def add_sentiment(dataframe):
    """
    Adds a sentiment class to the dataset based on the rating given by the reviewer.
    """
    def determine_sentiment(row):
        if row['rating'] in [1, 2, 3, 4]:
            return "negative"
        elif row['rating'] in [5, 6, 7]:
            return "neutral"
        elif row['rating'] in [8, 9, 10]:
            return "positive"
            
    dataframe['sentiment'] = dataframe.apply(lambda row: determine_sentiment(row), axis=1)
    return dataframe

# worker = MongoWorker()
# reviews = worker.getRatedReviews()

df = pd.read_pickle('rated_reviews.gzip')
df = df.astype({'rating': 'int32'})
df = add_sentiment(df)
df = df.drop(columns=["_id", "title", "author", "movie", "rating", "date", "helpful"])
# df = df.drop(df.columns[0], axis=1)
df['review'].replace('', np.nan, inplace=True)
df.dropna(subset=['review'], inplace=True)

df.to_csv("processed_clean.csv", index=False)

