#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
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

riddles = query.getresult()
hint_image_urls = [hint_image_url for _, _, hint_image_url, _, _, _ in riddles]
for hint_image_url in hint_image_urls:
    if not os.path.isfile(hint_image_url):
        print('Missing asset: %s' % hint_image_url)

database.close()
