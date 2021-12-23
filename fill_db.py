import random
from random import randrange

import psycopg2
from config import config
from datetime import datetime, timedelta

conn = psycopg2.connect(
    database=config['db_name'], user=config['db_user'], password=config['db_password'], host=config['db_host'],
    port=config['db_port']
)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE public.table_datarow
(
    id bigint NOT NULL,
    date date NOT NULL,
    name text NOT NULL,
    amount integer NOT NULL,
    distance integer NOT NULL,
    PRIMARY KEY (id)
);''')


index_start = 1
index_end = 100

def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


d1 = datetime.strptime('1/1/2000 1:30 PM', '%m/%d/%Y %I:%M %p')
d2 = datetime.strptime('1/1/2021 4:50 AM', '%m/%d/%Y %I:%M %p')

for i in range(index_start, index_end, 2):
    cursor.execute("INSERT INTO table_datarow (id, date, name, amount, distance) VALUES (%s, %s, %s, %s, %s)",
                   (i, random_date(d1, d2), "foo" + str(i), random.randint(0, 20), random.randint(0, 20)))
    cursor.execute("INSERT INTO table_datarow (id, date, name, amount, distance) VALUES (%s, %s, %s, %s, %s)",
                   (i + 1, random_date(d1, d2), "bar" + str(i+1), random.randint(0, 20), random.randint(0, 20)))

conn.commit()
conn.close()
cursor.close()
print("DB Filled!")