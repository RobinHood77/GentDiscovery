

#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable() 


from random import randint				#importeren van functie die ons toelaat een wilkeurig getal te genereren
error = False
N = form.getvalue("amount", "0")		#aantal raadsels dat we willen in totaal
if not N:
	error = True
Coord = form.getvalue("coord", "Null")	#coord speler bij begin van spel(wgs84)
if Coord is Null:
	error = True
vorigspelID = [] #id van locaties van vorige games (cookies)
huidigspelID = []  #Controle zodat we niet 2 keer dezelfde locatie kiezen
conn = pg.connect(port=8032,host='movestud.ugent.be',user='groep1',passwd='groep1',dbname='smartphone')

sql = """SELECT id, geometry_lambert72 FROM groep1."Raadsels"
where distance(geometry_lambert72,transform(geometryfromtext('POINT""" + Coord +"""', 4326), 31370)
)<1000 and id not in (""" + ", ".join(vorigspelID) + ")"
#omzetten van wgs84 naar Lambert72 geometry

# verwerken eerste raadsel	
q = conn.query(sql)
r = q.getresult()
geg = r[randint(0,len(r)-1)]	#gegevens opahalen uit 1 wilkeurig gekozen raadsel
lamcoord = geg[1]				#coordinaten oplslaan voor volgende query
huidigspelID.append(geg[0])			#id opslaan
for _ in range(N-1): #N = aantzal raadsels dat je wilt in totaal
	sql ="""SELECT id, geometry_lambert72 FROM groep1."Raadsels" where distance(geometry_lambert72,""" + lamcoord + ")<1000 and id not in (" + ", ".join(huidigspelID) + "," + ", ".join(vorigspelID) + ")"
	r = q.getresult()
	geg = r[randint(0,len(r)-1)]
	lamcoord = geg[1]
	huidigspelID.append(geg[0])
sql = "SELECT lambert72, locatie_naam, raadsel, foto_url where id in (" + ", ".join(huidigspelID) + ")"
L = q.getresult(sql)

#coord waarden in aparte lijsten stoppen
x = []
y = []
for i in L:
	lambertcoord = (i[0][6:-1]).split(" ")
	x.append(lambertcoord[0])
	y.append(lambertcoord[1])

print(
"""

<html lang="en"
<head>
    <meta charset="utf-8" />
    <title>City Puzzle Gent </title>
	<link rel="stylesheet" type="text/css" href=hoofdpagina.css>
	<script type="text/javascript">
	function initialize() {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(geolocationCallback, error);
        } else {
			error('not supported');
        }
    }

    function geolocationCallback(position) {
		 wgs84 = "'POINT("+position.coords.latitude+","+position.coords.longitude+")'";
    document.getElementById("locatie").innerHTML = wgs84
	
	}

    function error(msg) {
		alert(msg);
    }
    </script>
</head>
<body onload="initialize()">
    <body onload = initialize>
        <h1>Gent Discovery </h1>
        
		
	function newraadsel() {
	
	
	}

        
        
    <div class="common" style="height:400px">
		<div id="raadseldiv" class="opgave sidetoside">
			<h4>Raadsel</h4>
			<p id="raadsel"> We zoeken een straat: plat water in het frans (Enkel de echte burgie zal dit weten) </p>
			<img id="fotoraadsel" src=images\lokaties\josephplateaustra.jpg>
		</div>
		<div id="timediv"> <p>tijd:</p> </div>
		<button id="controle" type="button" onclick= call = warmkoud()> </button>
	</div>
	<img id="hidephoto" src=images\question-mark.jpg onclick=document.getElementById("hidephoto").style.opacity=0>
	<div style="height:300px;">
	</div
		
	<div> <p id=locatie style: style="color:red;" > coord </p></div>
	 
    
	
	</body>









)	