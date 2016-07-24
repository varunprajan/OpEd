# The Opinionator

## Description

A 3-week data science project as part of the [Insight Data Science](http://insightdatascience.com/) program. The purpose of the project was to analyze why some opinions fare better than others in social media. In particular, I tried to relate the features of the articles (textual and non-textual) to the number of shares for the URL of the article on Facebook, using a supervised machine learning model.

The website can be found at http://the-opinionator.xyz. It includes a [predictive tool](http://the-opinionator.xyz/), where one can assume an identity and input text from a sample opinion piece, and get an estimate of how many Facebook shares the article is likely to get as well as recommendations to improve the share count. One can also find articles that are topically similar to the sample opinion piece. The website also includes interactive visualizations built using d3, where one can explore the "success" of various articles grouped [by topic](http://the-opinionator.xyz/d3) or [by author](http://the-opinionator.xyz/d32). Finally, it includes a link to the slides for my [Insight demo presentation](http://the-opinionator.xyz/static/insight_demo.pdf)

## Steps in analysis

### Article scraping

Almost 10,000 opinion pieces, from December 2013 to March 2016, were scraped from the New York Times website using the [New York Times Article Search API](https://developer.nytimes.com/article_search_v2.json), wrapped in the Python package [nytimesarticle](https://pypi.python.org/pypi/nytimesarticle/0.1.0). The code for scraping is available in the Python file [nytimes_crawl_2.py](/nytimes_crawl_2.py) and the iPython notebook [OpEd_Analysis.ipynb](/OpEd_Analysis.ipynb)

### Textual features

Textual features, including topic distributions for each article, were extracted from the text after cleaning (removing stopwords and punctuation, stemming, etc.). The topic analysis was conducted using Latent Dirichlet Allocation using the scikit-learn package in Python. The relevant code is available in the Python file [the_opinionator/text_processing.py] and the iPython notebook (NLP.ipynb)[/NLP.ipynb). The topic clustering visualizations were generated using the scikit-learn implementation of (T-SNE)[https://lvdmaaten.github.io/tsne/], a technique for visualizing high-dimensional data in a low-dimensional space; see (T-SNE.ipynb)[/the_opinionator/T-SNE.ipynb]

### Non-textual features

Non-textual features, such as the author writing the article as well as the day of the week that the article was published on, were one-hot encoded before being used in the supervised learning model.

### Machine learning

The number of Facebook shares was log-transformed to narrow the range of the target variable and to bring its distribution closer to normality. All of the feature and target data was stored in a PostgreSQL database, and various regression models were explored using scikit-learn and evaluated using scores on a k-fold cross-validation. Details can be found in the iPython notebook [the_opionionator/SQL_Machine_Learning.ipynb]
