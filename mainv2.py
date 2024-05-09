#!/usr/bin/env python

import django 
from django.conf import settings 
from django.template import Template, Context 
TEMPLATES = [{'BACKEND':  'django.template.backends.django.DjangoTemplates'}] 
settings.configure(TEMPLATES=TEMPLATES) 
django.setup()

file1 = open('COM15.csv', 'r') #NOVATEL
Lines1 = file1.readlines()
file1.close()

file2 = open('COM16.csv', 'r') #UBLOXwe
Lines2 = file2.readlines()
file2.close()
gpggalist1=''
gpggalist2=''
gmaplatlon =''

starttimestr = "{:08.1f}".format(float(Lines1[0].split(",")[1]))
hh,mm,ss = map(int, (starttimestr[:2], starttimestr[2:4], starttimestr[4:6]))
filestarttime = str(hh*10000+mm*100+ss)
endtimestr = "{:08.1f}".format(float(Lines1[len(Lines1)-1].split(",")[1]))
ehh,emm,ess = map(int, (endtimestr[:2], endtimestr[2:4], endtimestr[4:6]))
fileendtime = str(ehh*10000+emm*100+ess)
outfilename = []
centlatlon = []
line1gpslist = []
line2gpslist = []
duration = 5 # 5 min
htmfilecount = int(((ehh-hh)*60+(emm-mm))/duration)+1 # total output html file count
startwithstr = []
endwithstr = []

for i in range(htmfilecount):
    inchh = int((mm+duration*i)/60)
    inchh2 = int((mm+duration*(i+1))/60)
    startstr = str((hh+inchh)*100 + mm+duration*i - 60*inchh)
    startwithstr.append(startstr)
    endstr = str((hh+inchh2)*100 + mm+duration*(i+1) - 60*inchh2)
    if(i == htmfilecount-1):
        endstr = str(ehh*100+emm)
    endwithstr.append(endstr)
    outfilename.append("ublox-{}-{}.htm".format(startstr+'00',endstr+'00' ))


for inc in range(htmfilecount):
    line1count = 0
    line2count = 0
    totallat1 = 0
    totallon1 = 0
    totallat2 = 0
    totallon2 = 0
    gpggalist1 = ''
    gpggalist2 = ''
    for i in range(duration):
        for line1 in Lines1:# RED line
            if line1.startswith("$GPGGA"):
                gpggasplit = line1.split(",")
                utctime = gpggasplit[1]
                tempstr = "{:04d}".format(int(startwithstr[inc]))
                nhh,nmm = map(int,(tempstr[:2], tempstr[2:4]))
                nhh2 = nhh
                nmm2 = nmm+i
                if(nmm+i >= 60):
                    nhh2=nhh+1
                    nmm2=nmm+i-60
                startstrtemp = ("{:d}".format(nhh2*100+nmm2)).rjust(4,'0')
                if utctime.startswith(startstrtemp):
                    line1count += 1
                    gpggalat = float(gpggasplit[2])
                    lat = int(gpggalat/100) + (gpggalat-int(gpggalat/100)*100)/60.0
                    totallat1 += lat
                    gpggalon = float(gpggasplit[4])
                    lon = int(gpggalon/100) + (gpggalon-int(gpggalon/100)*100)/60.0
                    totallon1 += lon
                    gpggalist1 += "new google.maps.LatLng( {:.7f}, {:.7f} ),\n".format(lat, lon)

        for line2 in Lines2:# BLUE line
                if line2.startswith("$GPGGA"):
                    gpggasplit = line2.split(",")
                    utctime = gpggasplit[1]
                    tempstr = "{:04d}".format(int(startwithstr[inc]))
                    nhh,nmm = map(int,(tempstr[:2], tempstr[2:4]))
                    nhh2 = nhh
                    nmm2 = nmm+i
                    if(nmm+i >= 60):
                        nhh2=nhh+1
                        nmm2=nmm+i-60
                    startstrtemp = ("{:d}".format(nhh2*100+nmm2)).rjust(4,'0')
                    if utctime.startswith(startstrtemp):
                        gpggalat = float(gpggasplit[2])
                        lat = int(gpggalat/100) + (gpggalat-int(gpggalat/100)*100)/60.0
                        gpggalon = float(gpggasplit[4])
                        lon = int(gpggalon/100) + (gpggalon-int(gpggalon/100)*100)/60.0
                        gpggalist2 += "new google.maps.LatLng( {:.7f}, {:.7f} ),\n".format(lat, lon)
    if(line1count > 0):
        centlat = totallat1/line1count
        centlon = totallon1/line1count
        centlatlon.append("new google.maps.LatLng( {:.7f}, {:.7f} ),\n".format(centlat, centlon))
    line1gpslist.append(gpggalist1)
    line2gpslist.append(gpggalist2)


template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">
    <!-- this file was created using the export function of u-center by u-blox AG, Switzerland. -->
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
        <title> {{ title }} </title>
        <script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?sensor=false&key=AIzaSyAsYwEsxrWNXPKUwxxlSRCHF4_L2ANRk08"></script>
        <script type="text/javascript">
        //<![CDATA[
            function Format(v)
            {
                var s = "";
                if (v < 0) { v = -v; s = "-"; }
                var i = Math.floor(v);
                var f = Math.floor((v-i)*1e6);
                var fs = f.toString();
                while (fs.length < 6)
                    fs = "0" + fs;
                return s + i.toString() + "." + fs;
            }

            function MouseMove(p)
            {
                window.status = "Lat: " + Format(p.latLng.lat()) + " Lon: " + Format(p.latLng.lng());
            }

            var MAX_ZOOM = 21;
            var GLOBE_WIDTH = 256;

            function Load()
            {
                // create map
                var map = new google.maps.Map(document.getElementById('div'),
                {
                    center: new google.maps.LatLng(  37.362489,126.737600 ),
                    zoom: 13,
                    mapTypeId: google.maps.MapTypeId.ROADMAP,
                    draggableCursor: 'crosshair',
                    overviewMapControl: true
                });
                
                
                var i;
                var j;
                _mSvgEnabled = true;
                _mSvgForced = true;
                
                // add listener 
                google.maps.event.addListener(map, 'mousemove', MouseMove);
                
                // track is a two dimensional array with lat/long points
                var t1 =  [  
                           [
                             {{ gpslist1 }} 
                            ]
                ];

                var t2 =  [  
                           [
                             {{ gpslist2 }} 
                            ]
                ];
                
                // define polyline
                var lineSymbol = {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 2,
                    strokeColor: '#0A0'
                };


                // find bounding box
                for (i = 0; i < t1.length; i ++)
                {
                    
                    new google.maps.Polyline({
                    path: t1[i],
                    strokeColor: '#FF0000',
                    strokeOpacity: 2.0,
                    strokeWeight: 5,
                    // icons: [{
                    // icon: lineSymbol,
                    // offset: '100%'
                    // }],
                    map: map
                    });
                    new google.maps.Marker(
                    {
                        map: map,
                        position: t1[i],
                        icon: lineSymbol
                    });
                }
                
                for (i = 0; i < t2.length; i ++)
                {
                    
                    new google.maps.Polyline({
                    path: t2[i],
                    strokeColor: '#0000FF',
                    strokeOpacity: 2.0,
                    strokeWeight: 5,
                    // icons: [{
                    // icon: lineSymbol,
                    // offset: '100%'
                    // }],
                    map: map
                    });
                    new google.maps.Marker(
                    {
                        map: map,
                        position: t2[i],
                        icon: lineSymbol
                    });
                }
                // add the start and the end point
                new google.maps.Marker(
                {
                    map: map,
                    position: t2[0],
                    title: 'Start'
                });
                new google.maps.Marker(
                {
                    map: map,
                    position: t2[t2.length-1],
                    title: 'End'
                });
                // create map fitted to the track
                
                // set center and zoom level
                map.setCenter(new google.maps.LatLng( {{centlatlon}} ));
                map.setZoom(13);
                
            }
        //]]>
        </script>
    </head>
    <body onload="Load();" style="margin:0px 0px 0px 0px; overflow:hidden;">
        <div id="div"  style="position:absolute; top:0px; left:0px; width:100%; height:100%;"></div>
    </body>
</html>
"""
for i in range(htmfilecount):
    t = Template(template).render(Context({"title": outfilename[i],"gpslist1":line1gpslist[i],"gpslist2":line2gpslist[i], "centlatlon":centlatlon[i]}))
    # print(outfilename[i])
    fileout = open(outfilename[i], 'w')
    fileout.write(t)
    fileout.close()
