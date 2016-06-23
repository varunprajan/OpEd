def gen_row(row,keys1,keys2):
    s = []
    for key1, key2 in zip(keys1,keys2):
        item = row[key1]
        if type(item) == unicode or type(item) == str:
            s.append(u'"{0}": "{1}"'.format(key2,item))
        else:
            s.append(u'"{0}": {1}'.format(key2,item))
    return u'{{{0}}}'.format(', '.join(s))

def to_file(filename,df,keys1,keys2):
    with open(filename,'wb') as f:
        for row in df.iterrows():
            mystring = u'{0},\n'.format(gen_row(row[1],keys1,keys2))
            f.write(mystring.encode('utf-8'))