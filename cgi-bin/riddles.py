#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import random
import time

import pg as postgresql

riddles_seed = None
if 'HTTP_COOKIE' in os.environ:
    for cookie in os.environ['HTTP_COOKIE'].split(';'):
        key, value = map(str.strip, cookie.split('='))
        if key == 'seed':
            riddles_seed = int(value)

if riddles_seed is None:
    riddles_seed = int(time.time() * 1000)

database = postgresql.DB(host='movestud.ugent.be', port=8032, dbname='smartphone', user='groep1', passwd='groep1')
query = database.query('''
    SELECT
        id,
        raadsel AS question,
        locatie_naam AS answer,
        left(split_part(asText(transform(geometry_lambert2008, 4326)), ' ', 2), -1) AS latitude,
        right(split_part(asText(transform(geometry_lambert2008, 4326)), ' ', 1), -6) AS longitude
    FROM groep1."Raadsels"
    ORDER BY id''')

random.seed(riddles_seed)
riddles = random.sample(query.getresult(), 10)

json = str([{'question': question, 'answer': answer, 'latitude': float(latitude), 'longitude': float(longitude)} for id, question, answer, latitude, longitude in riddles])

with open('riddles-template.html') as template:
    html = template.read()

print('Content-Type: text/html')
print('Set-Cookie: seed=%d' % riddles_seed)
print()
print(html.replace('{RIDDLES}', json))

database.close()
