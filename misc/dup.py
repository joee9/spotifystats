#%%
import pandas as pd

df = pd.read_csv("../data/11-2021-recentlyplayed.txt")

dup = df["Timestamp"].duplicated()
for i in range(len(dup)):
    print(f"{i}. {dup[i]}")