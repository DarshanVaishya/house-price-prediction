# import seaborn as sns
# import matplotlib.pyplot as plt
# import pandas as pd

# df = pd.read_csv('static/clean_data.csv')

# g = sns.lmplot(x="sqft", y="price", data=df)
# plt.savefig('static/img/graph.png')


from passlib.hash import sha512_crypt

print(sha512_crypt.hash('admin'))
