import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import yaml

with open('config.yml', 'r') as f:
    doc = yaml.load(f)
    dbname = doc['DBNAME']
    username = doc['USERNAME']
    password = doc['PASSWORD']

engine = create_engine('postgres://{0}:{2}@localhost/{1}'.format(username,dbname,password))
if not database_exists(engine.url):
    create_database(engine.url)
con = None
con = psycopg2.connect(database = dbname, user = username)

def return_df(query):
    return pd.read_sql_query(query,con)

def all_query():
    return """
    SELECT orig.*, text.*, non.*, tw.*, sent.*
    FROM orig
        LEFT JOIN tw
            ON orig.index = tw.index
        LEFT JOIN text
            ON orig.index = text.index
        LEFT JOIN non
            ON orig.index = non.index
        LEFT JOIN sent
            ON orig.index = sent.index
    """

def author_query(author):
    return """
    SELECT orig.*, text.*, non.*, tw.*, sent.*
    FROM orig
        LEFT JOIN tw
            ON orig.index = tw.index
        LEFT JOIN text
            ON orig.index = text.index
        LEFT JOIN non
            ON orig.index=  non.index
        LEFT JOIN sent
            ON orig.index = sent.index
    WHERE orig.author = '{0}';
    """.format(author)