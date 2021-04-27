import pandas as pd
import numpy as np
import os

if not os.path.isfile('static/data.csv'):
    import scraper
    print("Scraping finished!")
    

df = pd.read_csv('static/data.csv')

df.loc[df['unit'] == 'Cr', 'price'] = df['price'] * 100
df.drop(['unit'], axis=1, inplace=True)
df.loc[df.groupby('area')['area'].transform('count').lt(10), 'area'] = "Other"

df = df[~(df['sqft'] / df['BHK'] < 300)]

df['price_per_sqft'] = df['price'] * 100000 / df['sqft']

def remove_outliers(df):
    out = pd.DataFrame()
    for key, subdf in df.groupby('area'):
        m = np.mean(subdf.price_per_sqft)
        st = np.std(subdf.price_per_sqft)
        temp = subdf[(subdf['price_per_sqft'] > (m - st)) & (subdf['price_per_sqft'] <= (m + st))]
        out = pd.concat([out,temp],ignore_index=True)
    return out
df = remove_outliers(df)

df.drop(['price_per_sqft'], axis=1, inplace=True)

# Converting house type into numeric values
unq = list(df['type'].unique())
df['type'] = df['type'].apply(lambda x: unq.index(x))

with open('static/types.csv', 'w') as f:
    f.write(','.join(unq))
# Creating dummy variables for area column
dummies = pd.get_dummies(df['area'])
final = pd.concat([df, dummies], axis=1)
final.drop(['area'], axis=1, inplace=True)

with open('static/unique.csv', 'w') as f:
    f.write(','.join(final.drop(['price'], axis=1).columns))

final.to_csv('static/clean_data.csv', index=False)

if __name__ == "__main__":
    print(len(final))
    print(final.head())
