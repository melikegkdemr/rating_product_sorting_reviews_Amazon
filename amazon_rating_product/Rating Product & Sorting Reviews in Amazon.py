
###################################################
# PROJE: Rating Product & Sorting Reviews in Amazon
###################################################

# Değişkenler:
# reviewerID: Kullanıcı ID’si
# asin: Ürün ID’si
# reviewerName: Kullanıcı Adı
# helpful: Faydalı değerlendirme derecesi
# reviewText: Değerlendirme
# overall: Ürün rating’i
# summary: Değerlendirme özeti
# unixReviewTime: Değerlendirme zamanı
# reviewTime: Değerlendirme zamanı Raw
# day_diff: Değerlendirmeden itibaren geçen gün sayısı
# helpful_yes: Değerlendirmenin faydalı bulunma sayısı
# total_vote: Değerlendirmeye verilen oy sayısı

import pandas as pd
import math
import scipy.stats as st


pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.width', 0)  # Terminal genişliğine uyacak şekilde ayarlayın

df = pd.read_csv(r"amazon_review.csv")
df.head()

df["overall"].mean()

df.info()

df.loc[df["day_diff"]<=30, "overall"].mean()
df.loc[(df["day_diff"]>30) & (df["day_diff"] <= 90), "overall"].mean()
df.loc[(df["day_diff"]>90) & (df["day_diff"] <= 180), "overall"].mean()
df.loc[df["day_diff"] >= 180, "overall"].mean()

#zamanı ağırlıklandıralım

df.loc[df["day_diff"] <= 30, "overall"].mean() * 28/100 + \
df.loc[(df["day_diff"] > 30) & (df["day_diff"] <= 90), "overall"].mean() * 26/100 + \
df.loc[(df["day_diff"] > 90) & (df["day_diff"] <= 180), "overall"].mean() * 24/100 + \
df.loc[df["day_diff"] >= 180, "overall"].mean() * 22/100

#fonksiyonlaştıralım

def time_based_weighted_average(dataframe, w1=28, w2=26, w3=24, w4=22):
    return df.loc[df["day_diff"] <= 30, "overall"].mean() * w1/100 + \
           df.loc[(df["day_diff"] >30) & (df["day_diff"] <= 90), "overall"].mean() * w2/100 + \
           df.loc[(df["day_diff"] > 90) & (df["day_diff"] <= 180), "overall"].mean() * w3/100 + \
           df.loc[df["day_diff"] > 180,"overall"].mean() * w4/100


time_based_weighted_average(df)

df["helpful_no"] = df["total_vote"] - df["helpful_yes"]

def score_up_down_diff(up,down):
    return up - down

def score_average_rating(up,down):
    if up + down == 0:
        return 0
    return up / (up+down)

def wilson_lower_bound(up,down,confidence=0.95):
    n = up + down

    if n==0:
        return 0
    
    z = st.norm.ppf(1 - ( 1 - confidence) / 2)
    phat = 1.0 * up / n
    return (phat + z * z / (2+n) - z * math.sqrt((phat * ( 1-phat) + z * z / (4+n)) / n)) / (1 + z * z / n)

# score_pos_neg_diff
df["score_pos_neg_diff"] = df.apply(lambda x: score_up_down_diff(x["helpful_yes"],
                                                                             x["helpful_no"]), axis=1)

# score_average_rating
df["score_average_rating"] = df.apply(lambda x: score_average_rating(x["helpful_yes"], x["helpful_no"]), axis=1)

# wilson_lower_bound
df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"], x["helpful_no"]), axis=1)


df.columns

df.sort_values("wilson_lower_bound", ascending=False).head(20)


