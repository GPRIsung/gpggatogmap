#!/usr/bin/env python

import sys
import django 
from django.conf import settings 
from django.template import Template, Context 
TEMPLATES = [{'BACKEND':  'django.template.backends.django.DjangoTemplates'}] 
settings.configure(TEMPLATES=TEMPLATES) 
django.setup()

# RED route file read
file1 = open('COM15_novatel1_240517.ubx.txt', 'r',encoding='UTF8') #NOVATEL
Lines1 = file1.readlines()
file1.close()

# BLUE route file read
file2 = open('COM16_ublox1_240517.ubx.txt', 'r',encoding='UTF8') #UBLOXwe
Lines2 = file2.readlines()
file2.close()

# 1 duration gpggalist arrays initialize
gpggalist1=''
gpggalist2=''

# Get start / end time and calculate no. of files
starttimestr = "{:08.1f}".format(float(Lines1[0].split(",")[1]))
hh,mm,ss = map(int, (starttimestr[:2], starttimestr[2:4], starttimestr[4:6]))
filestarttime = str(hh*10000+mm*100+ss)
endtimestr = "{:08.1f}".format(float(Lines1[len(Lines1)-1].split(",")[1]))
ehh,emm,ess = map(int, (endtimestr[:2], endtimestr[2:4], endtimestr[4:6]))
fileendtime = str(ehh*10000+emm*100+ess)
outfilename = []  # output filename array 
centlatlon = []   # each file name 
line1gpslist = []
line2gpslist = []
duration = 10 # 5 min
htmfilecount = int(((ehh-hh)*60+(emm-mm))/duration)+1 # total output html file count
startwithstr = []
endwithstr = []
l1startpos = []
l2startpos = []
l1endpos = []
l2endpos = []

# Generation of starttime number based on first data. extract hh and mm from $GPGGA hhmmss.s section.
for i in range(htmfilecount):
    inchh = int((mm+duration*i)/60)
    inchh2 = int((mm+duration*(i+1))/60)
    startstr = "{:02d}".format(hh+9+inchh)+"{:02d}".format( mm+duration*i - 60*inchh)
    startwithstr.append("{:02d}".format(hh+inchh)+"{:02d}".format( mm+duration*i - 60*inchh))
    endstr = "{:02d}".format(hh+9+inchh2)+"{:02d}".format( mm+duration*(i+1) - 60*inchh2)
    endstr2 = "{:02d}".format(hh+inchh2)+"{:02d}".format( mm+duration*(i+1) - 60*inchh2)
    if(i == htmfilecount-1):
        endstr = "{:02d}".format(ehh+9)+"{:02d}".format(emm)
        endstr2 = "{:02d}".format(ehh)+"{:02d}".format(emm)
    endwithstr.append(endstr2)
    outfilename.append("ublox-{}-{}.htm".format(startstr+'00',endstr+'00' ))

nolines = 0
finalhtmfilecount = htmfilecount
for inc in range(htmfilecount):
    line1count = 0
    line2count = 0
    totallat1 = 0
    totallon1 = 0
    totallat2 = 0
    totallon2 = 0
    gpggalist1 = ''
    gpggalist2 = ''
    l1startpost = ''
    l2startpost = ''
    l1endpost = ''
    l2endpost = ''

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
                if (utctime.startswith(startstrtemp) and gpggasplit[2]!='' and gpggasplit[4]!=''): # need to check no lat and lng data
                    line1count += 1
                    gpggalat = float(gpggasplit[2])
                    lat = int(gpggalat/100) + (gpggalat-int(gpggalat/100)*100)/60.0
                    totallat1 += lat
                    gpggalon = float(gpggasplit[4])
                    lon = int(gpggalon/100) + (gpggalon-int(gpggalon/100)*100)/60.0
                    totallon1 += lon
                    gpggalist1 += "new google.maps.LatLng( {:.7f}, {:.7f} ),\n".format(lat, lon)
                    postemp = '{{ lat: {0:.7f}, lng: {1:.7f} }}'
                    l1endpost = postemp.format(lat, lon)
                    if(line1count==1):
                        l1startpost = postemp.format(lat, lon)


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
                if ( utctime.startswith(startstrtemp) and gpggasplit[2]!='' and gpggasplit[4]!=''): # need to check no lat and lng data:
                    line2count += 1
                    gpggalat = float(gpggasplit[2])
                    lat = int(gpggalat/100) + (gpggalat-int(gpggalat/100)*100)/60.0
                    gpggalon = float(gpggasplit[4])
                    lon = int(gpggalon/100) + (gpggalon-int(gpggalon/100)*100)/60.0
                    gpggalist2 += "new google.maps.LatLng( {:.7f}, {:.7f} ),\n".format(lat, lon)
                    postemp = '{{ lat: {0:.7f}, lng: {1:.7f} }}'
                    l2endpost = postemp.format(lat, lon)
                    if(line2count==1):
                        l2startpost = postemp.format(lat, lon)

    if(line1count > 0):
        centlat = totallat1/line1count
        centlon = totallon1/line1count
        centlatlon.append("new google.maps.LatLng( {:.7f}, {:.7f} ),\n".format(centlat, centlon))
        line1gpslist.append(gpggalist1)
        line2gpslist.append(gpggalist2)
        l1startpos.append(l1startpost)
        l2startpos.append(l2startpost)
        l1endpos.append(l1endpost)
        l2endpos.append(l2endpost)
    else:
        finalhtmfilecount -=1
        nolines+=1
        outfilename.pop(inc)



template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">
    <!-- this file was created using the export function of u-center by u-blox AG, Switzerland. -->
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
        <title> {{ title }} </title>
        <script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?key=AIzaSyAsYwEsxrWNXPKUwxxlSRCHF4_L2ANRk08&libraries=marker"></script>
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
            let map;
            async function Load()
            {
                // create map
                const { Map } = await google.maps.importLibrary("maps");
                map = new Map(document.getElementById('div'),
                {
                    center: new google.maps.LatLng(  37.362489,126.737600 ),
                    zoom: 16,
                    mapTypeId: google.maps.MapTypeId.ROADMAP,
                    draggableCursor: 'crosshair',
                    overviewMapControl: true,
                    mapId: "MarkerMap",
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

                var l1startpos = {{ l1startpos }}
                var l1endpos = {{ l1endpos }}
                var l2startpos = {{ l2startpos }}
                var l2endpos = {{ l2endpos }}
                
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
                    strokeOpacity: 1.0,
                    strokeWeight: 1,
                    // icons: [{
                    // icon: lineSymbol,
                    // offset: '100%'
                    // }],
                    map: map
                    });

                    //new google.maps.marker.AdvancedMarkerElement(
                    //{
                    //    map: map,
                    //    position: t1[i],
                    //    icon: lineSymbol
                    //});
                }
                
                for (i = 0; i < t2.length; i ++)
                {
                    
                    new google.maps.Polyline({
                    path: t2[i],
                    strokeColor: '#0000FF',
                    strokeOpacity: 1.0,
                    strokeWeight: 1,
                    // icons: [{
                    // icon: lineSymbol,
                    // offset: '100%'
                    // }],
                    map: map
                    });

                    //new google.maps.marker.AdvancedMarkerElement(
                    //{
                    //    map: map,
                    //    position: t2[i],
                    //   icon: lineSymbol
                    //});
                }
                // add the start and the end point
                new google.maps.marker.AdvancedMarkerElement(
                {
                    map: map,
                    position: l1startpos,
                    title: 'L1Start'
                });
                new google.maps.marker.AdvancedMarkerElement(
                {
                    map: map,
                    position: l2startpos,
                    title: 'L2Start'
                });
                // create map fitted to the track
                
                // set center and zoom level
                map.setCenter( {{centlatlon}} );
                map.setZoom(15);
                
                var legend = document.getElementById('legend');
                var div = document.createElement('div');
                
                div.innerHTML = '<h4><font color="red">&#8212; </font> Novatel </h4><h4><font color="blue">&#8212; </font> UBLOX </h4><h4><font color="grey">&#8212; </font> NO GPS </h4>'
                legend.appendChild(div);
                map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(legend);
            }
        //]]>
        </script>
        <style>
        #legend {
            font-family: Arial, sans-serif;
            background: #fff;
            padding: 10px;
            margin: 10px;
            border: 3px solid #000;
        }
        #legend h3 {
            margin-top: 0;
        }

        #legend img {
            vertical-align: middle;
        }
        </style>
    </head>
    <body onload="Load();" style="margin:0px 0px 0px 0px; overflow:hidden;">
        <div id="div"  style="position:absolute; top:0px; left:0px; width:100%; height:100%;"></div>
        <div id="legend"><h3>Legend</h3></div>
    </body>
</html>
"""
for i in range(finalhtmfilecount):
    t = Template(template).render(Context({"title": outfilename[i],"gpslist1":line1gpslist[i],"gpslist2":line2gpslist[i], "l1startpos":l1startpos[i], "l1endpos":l1endpos[i],"l2startpos":l2startpos[i], "l2endpos":l2endpos[i], "centlatlon":centlatlon[i]}))
    # print(outfilename[i])
    fileout = open(outfilename[i], 'w')
    fileout.write(t)
    fileout.close()

print("nolines:{}".format(nolines))