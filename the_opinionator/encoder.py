from collections import Counter
import numpy as np
import pandas as pd

class Encoder(object):
    def __init__(self,name,tokens,nonegroup=False,cutoff=0):
        self.tokens = tokens
        self.name = name
        self.nonegroup = nonegroup
        tokencount = Counter(tokens)
        self.uniquetokens = self.get_unique_tokens(tokencount,cutoff)
        self.ntokens = self.get_ntokens()
        self.tokentoid = {token: i for i, token in enumerate(self.uniquetokens)}
        self.idtotoken = {i: token for i, token in enumerate(self.uniquetokens)}
    
    def get_unique_tokens(self,tokencount,cutoff):
        uniquetokens = []
        for token, count in tokencount.items():
            if count > cutoff:
                uniquetokens.append(token)
        return uniquetokens
    
    def get_ntokens(self):
        ntokens = len(self.uniquetokens)
        if self.nonegroup:
            ntokens += 1
        return ntokens
    
    @property
    def feature_names(self):
        return ['{0}_{1}'.format(self.name,i) for i in range(self.ntokens)]
    
    def get_token_id(self,token):
        if self.nonegroup:
            return self.tokentoid.get(token,self.ntokens-1)
        else:
            return self.tokentoid[token]
    
    def encode(self,tokens):
        n = len(tokens)
        encodearray = np.zeros((n,self.ntokens))
        for i, token in enumerate(tokens):
            tokenid = self.get_token_id(token)
            encodearray[i,tokenid] = 1
        return encodearray
            
    def encode_to_df(self,df):
        dftemp = pd.DataFrame(index=df.index,columns=self.feature_names)
        dftemp[self.feature_names] = self.encode(self.tokens)
        return pd.concat([df,dftemp],axis=1)

        
        
