import pandas as pd
import os

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, _ in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(top_words(model,feature_names,n_top_words,topic_idx))
    print()
    
def top_words(model,feature_names,n_top_words, topic_idx):
    topic = model.components_[topic_idx]
    return ' '.join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])

def topic_weights_csv(n_topics,stem='lemma',package='gensim',rows='all'):
    return 'topicweights2_{0}_{1}_{2}_{3}.csv'.format(n_topics,stem,package,rows)

def save_topic_weights(dataall,doc_topic_distrib,stem='lemma',package='gensim',rows='all',fmt='topic_{0}',subdir=''):
    n_topics = doc_topic_distrib.shape[1]
    columns = [fmt.format(topicnum) for topicnum in range(n_topics)]
    df = pd.DataFrame(index=dataall.index,columns=columns)
    for topicnum in range(n_topics):
        topicname = fmt.format(topicnum)
        df[topicname] = doc_topic_distrib[:,topicnum]
    df.to_csv(os.path.join(subdir,topic_weights_csv(n_topics,stem,package,rows)))