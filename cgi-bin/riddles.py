#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import math
import os
import random
import time

import pg as postgresql

try:
    riddles_seed = None
    if 'HTTP_COOKIE' in os.environ:
        for cookie in os.environ['HTTP_COOKIE'].split(';'):
            key, value = map(str.strip, cookie.split('=', 1))
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
        latitude0, longitude0 = map(float, riddle0[4:6])
        latitude1, longitude1 = map(float, riddle1[4:6])

        avg_latitude = (latitude0 + latitude1) / 2
        dlatitude = latitude0 - latitude1
        dlongitude = longitude0 - longitude1
        dx = dlatitude * 40008000 / 360
        dy = dlongitude * math.cos(avg_latitude * math.pi / 180) * 40075160 / 360

        return math.sqrt(dx * dx + dy * dy)

    def calculateRoute(riddles, start):
        route = [riddles[start]]
        distance = 0
        for i in range(len(riddles) - 1):
            currentRiddle = route[i]
            nextRiddle = min([riddle for riddle in riddles if riddle not in route], key=lambda riddle: distanceBetween(currentRiddle, riddle))
            route.append(nextRiddle)
            distance += distanceBetween(currentRiddle, nextRiddle)
        return route, distance

    # make sure that the travel distance is small
    minDistance = 1e9
    for i in range(len(riddles)):
        newRiddles, distance = calculateRoute(riddles, i)
        if distance < minDistance:
            minTravelDistance = distance
            riddles = newRiddles

    json = str([{'question': question, 'hintImageUrl': '../' + hintImageUrl, 'answer': answer, 'latitude': float(latitude), 'longitude': float(longitude)} for id, question, hintImageUrl, answer, latitude, longitude in riddles])

    with open('riddles-template.html') as template:
        html = template.read()

    print('Content-Type: text/html')
    print('Set-Cookie: seed=%d' % riddles_seed)
    print()
    print(html.replace('{RIDDLES}', json))

    database.close()
except Exception as e:
    print('Content-Type: text/html')
    print()
    print('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/></head><body><h1>Something went wrong!</h1><h2>%s</h2></body>' % e)
