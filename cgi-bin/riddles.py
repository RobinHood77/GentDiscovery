#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import math
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
        foto_url AS hintImageUrl,
        locatie_naam AS answer,
        left(split_part(asText(transform(geometry_lambert2008, 4326)), ' ', 2), -1) AS latitude,
        right(split_part(asText(transform(geometry_lambert2008, 4326)), ' ', 1), -6) AS longitude
    FROM groep1."Raadsels"
    ORDER BY id''')

random.seed(riddles_seed)
riddles = random.sample(query.getresult(), 10)

def distanceBetween(riddle0, riddle1):
    latitude0, longitude0 = map(float, riddle0[4:])
    latitude1, longitude1 = map(float, riddle1[4:])

    avg_latitude = (latitude0 + latitude1) / 2
    dlatitude = latitude0 - latitude1
    dlongitude = longitude0 - longitude1
    dx = dlatitude * 40008000 / 360
    dy = dlongitude * math.cos(avg_latitude * math.pi / 180) * 40075160 / 360

    return math.sqrt(dx * dx + dy * dy)

# make sure that the distance between two riddles is rather small
startRiddle = riddles[0]
riddles = [startRiddle] + sorted(riddles[1:], key=lambda riddle: distanceBetween(startRiddle, riddle))

json = str([{'question': question, 'hintImageUrl': '../' + hintImageUrl, 'answer': answer, 'latitude': float(latitude), 'longitude': float(longitude)} for id, question, hintImageUrl, answer, latitude, longitude in riddles])

with open('riddles-template.html') as template:
    html = template.read()

print('Content-Type: text/html')
print('Set-Cookie: seed=%d' % riddles_seed)
print()
print(html.replace('{RIDDLES}', json))

database.close()
