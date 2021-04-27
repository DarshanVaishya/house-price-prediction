import numpy as np
import pandas as pd
import os
import pickle

if (not os.path.isfile('static/clean_data.csv')) or (not os.path.isfile('static/types.csv')):
    import data_preprocess
    print("Clean data generated")

df = pd.read_csv('static/clean_data.csv')
with open('static/types.csv', 'r') as f:
    types = f.read().split(',')

X = df.drop(['price'], axis=1)
Y = df['price']
columns = list(X.columns)

# from sklearn.model_selection import train_test_split
# xtrain, xtest, ytrain, ytest = train_test_split(X, Y, test_size=0.2)

from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X, Y)

with open('static/model.pickle', 'wb') as f:
    pickle.dump(model, f)

def predict_value(area, house_type, BHK, sqft):
    y = np.zeros(len(columns))
    y[:3] = types.index(house_type), BHK, sqft
    y[columns.index(area)] = 1

    price = model.predict(y.reshape(1, -1))

    return "{:.2f}".format(price[0])

if __name__ == "__main__":
    print(predict_value("Memnagar", 'Apartment', 4, 4691))
    print(predict_value("Bodakdev", 'Apartment', 2, 900))
