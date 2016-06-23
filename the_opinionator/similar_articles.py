import pandas as pd
from scipy.stats import percentileofscore

def same_other_df(df,author):
    idx = (df['author'] == author)
    sameauthor = df[idx]
    otherauthor = df[~idx]
    return sameauthor, otherauthor

def percentiles(sameauthor,otherauthor,nshares):
    sameperc = percentileofscore(sameauthor['share_count'],nshares)
    otherperc = percentileofscore(otherauthor['share_count'],nshares)
    return sameperc, otherperc

def predict_similar_articles(samedf,otherdf,weights,n_articles=5,n_topics=50):
    articles_same = retrieve_similar_articles(samedf,weights,n_articles,n_topics)
    articles_other = retrieve_similar_articles(otherdf,weights,n_articles,n_topics)
    return articles_same, articles_other

def retrieve_similar_articles(df,weights,n_articles,n_topics,fmt='topic_{0}'):
    fnames = [fmt.format(i) for i in range(n_topics)]
    df['sim'] = df[fnames].dot(weights.T)
    dfsorted = df.sort_values('sim')
    dfsortedrev = dfsorted.iloc[::-1]
    return dfsortedrev.iloc[:n_articles]


    