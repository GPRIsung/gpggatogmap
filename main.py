#!/usr/bin/env python

import sys
import django 
from django.conf import settings 
from django.template import Template, Context 
TEMPLATES = [{'BACKEND':  'django.template.backends.django.DjangoTemplates'}] 
settings.configure(TEMPLATES=TEMPLATES) 
django.setup()

# RED route file read
file1 = open('COM15_novatel1_test.ubx', 'r',encoding='UTF8') #NOVATEL
Lines1 = file1.readlines()
file1.close()

# BLUE route file read
file2 = open('COM16_ublox1_test.ubx', 'r',encoding='UTF8') #UBLOXwe
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
                    nogps = bool(gpggasplit[13]=="")
                    
                    postemp = '{{ lat: {0:.7f}, lng: {1:.7f}, nogps:{2:d} }}'
                    gpggalist1 += postemp.format(lat, lon, nogps)+",\n"
                    l1endpost = postemp.format(lat, lon, nogps)
                    if(line1count==1):
                        l1startpost = postemp.format(lat, lon, nogps)
                    # postemp = 'new naver.maps.LatLng( {0:.7f}, {1:.7f})'
                    # gpggalist1 += postemp.format(lat, lon)+",\n"
                    # l1endpost = postemp.format(lat, lon)
                    # if(line1count==1):
                    #     l1startpost = postemp.format(lat, lon)


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
                    nogps = bool(gpggasplit[13]=="")
                    
                    postemp = '{{ lat: {0:.7f}, lng: {1:.7f}, nogps:{2:d} }}'
                    gpggalist2 += postemp.format(lat, lon, nogps)+",\n"
                    l2endpost = postemp.format(lat, lon, nogps)
                    if(line2count==1):
                        l2startpost = postemp.format(lat, lon, nogps)

                    # postemp = 'new naver.maps.LatLng( {0:.7f}, {1:.7f})'
                    # gpggalist2 += postemp.format(lat, lon)+",\n"
                    # l2endpost = postemp.format(lat, lon)
                    # if(line2count==1):
                    #     l2startpost = postemp.format(lat, lon)

    if(line1count > 0):
        centlat = totallat1/line1count
        centlon = totallon1/line1count
        postemp = '{{ lat: {0:.7f}, lng: {1:.7f} }},\n'
        # postemp = 'new naver.maps.LatLng( {0:.7f}, {1:.7f})'
        centlatlon.append(postemp.format(centlat, centlon))
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
                const {LatLngAltitude} = await google.maps.importLibrary("core")
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
                
                // define icons
                redcircleImg = "http://fl2.me/red.png";
                bluecircleImg = "http://fl2.me/blue.png";
                greycircleImg = "http://fl2.me/grey.png";
                lightgreycircleImg = "http://fl2.me/lightgrey.png";
                browncircleImg = "http://fl2.me/brown.png";
                darkbluecircleImg = "http://fl2.me/blue.png";
                pinkcircleImg = "http://fl2.me/pink.png";
                lightbluecircleImg = "http://fl2.me/blue.png";

                for (i = 0; i < t1[0].length; i ++)
                {

                    new google.maps.Polyline({
                        path: t1[i],
                        strokeColor: '#FF0000',
                        strokeOpacity: 1.0,
                        strokeWeight: 6,
                        // icons: [{
                        //     icon: redcircleImg,
                        //     offset: '100%'
                        // }],
                        map: map
                    });

                    if(t1[0][i].nogps)
                    {
                    new google.maps.Marker(
                        {
                            map: map,
                            position: t1[0][i],
                            icon: {
                                url:lightgreycircleImg,
                                size: new google.maps.Size(6,6),
                                anchor: new google.maps.Point(3,3)
                            } ,
                            title:"Novatel NOGPS ["+ t1[0][i].lat +","+ t1[0][i].lng +"]"
                        });
                    }
                    else
                    {
                        new google.maps.Marker(
                        {
                            map: map,
                            position: t1[0][i],
                            icon: {
                                url:redcircleImg,
                                size: new google.maps.Size(6,6),
                                anchor: new google.maps.Point(3,3)
                            } ,
                            title:"Novatel GPS["+ t1[0][i].lat +","+ t1[0][i].lng +"]"
                        });
                    }
                }
                
                for (i = 0; i < t2[0].length; i ++)
                {
                    new google.maps.Polyline({
                            path: t2[i],
                            strokeColor: '#0000FF',
                            strokeOpacity: 0.5,
                            strokeWeight: 6,
                            // icons: [{
                            //     icon: redcircleImg,
                            //     offset: '100%'
                            // }],
                            map: map
                        });

                    if(t2[0][i].nogps)
                    {
                    new google.maps.Marker(
                        {
                            map: map,
                            position: t2[0][i],
                            icon: {
                                url:greycircleImg,
                                size: new google.maps.Size(6,6),
                                anchor: new google.maps.Point(3,3)
                            } ,
                            title:"uBlox NOGPS ["+ t2[0][i].lat +","+ t2[0][i].lng +"]"
                        });
                    }
                    else
                    {
                        new google.maps.Marker(
                        {
                            map: map,
                            position: t2[0][i],
                            icon: {
                                url:bluecircleImg,
                                size: new google.maps.Size(6,6),
                                anchor: new google.maps.Point(3,3)
                            } ,
                            title:"Novatel GPS ["+ t2[0][i].lat +","+ t2[0][i].lng +"]"
                        });
                    }
                }

                // add the start and the end point
                new google.maps.Marker(
                {
                    map: map,
                    position: l1startpos,
                    title: 'Novatel Start'
                });

                new google.maps.Marker(
                {
                    map: map,
                    position: l2startpos,
                    title: 'Ublox Start'
                });
                // create map fitted to the track
                
                // set center and zoom level
                map.setCenter( {{centlatlon}} );
                map.setZoom(15);
                
                var legend = document.getElementById('legend');
                var div = document.createElement('div');
                
                div.innerHTML = '<h4><img src="http://fl2.me/red.png"/> Novatel GPS</h4>\
                                <h4><img src="http://fl2.me/lightgrey.png"/> Novatel NOGPS</h4>\
                                <h4><img src="http://fl2.me/blue.png"/> UBLOX GPS</h4>\
                                <h4><img src="http://fl2.me/grey.png"/> UBLOX NOGPS</h4>'
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

template2 = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="X-UA-Compatible" content="IE=11"> >
    <meta http-equiv="Content-Type" content="text/html">
        <title> {{ title }} </title>
    <style> 
     #wrap .buttons { position:absolute;top:0;left:0;z-index:1000;padding:5px; } 
     #wrap .buttons .control-btn { margin:0 5px 5px 0; } 
    .map_wrap {position:relative;width:100%;height:100%;}
    .title {font-weight:bold;display:block;}
	.dot {overflow:hidden;float:left;width:12px;height:12px;background: url('http://t1.daumcdn.net/localimg/localimages/07/mapapidoc/mini_circle.png');}   
	.dotOverlay {position:relative;left:-37%;bottom:5px;border-radius:6px;border: 1px solid #ccc;border-bottom:2px solid #ddd;float:left;font-size:12px;padding:5px;background:#fff;}
	.dotOverlay2 {position:relative;bottom:1px;border-radius:6px;border: 0px solid #ccc;border-bottom:2px solid #ddd;float:left;font-size:12px;padding:5px;background:#fff;}
	.dotOverlay:nth-of-type(n) {border:0; box-shadow:0px 1px 2px #888;}    
	.number {font-weight:bold;color:#ee6152;}
	.dotOverlay:after {content:'';position:absolute;margin-left:-6px;left:50%;bottom:-8px;width:11px;height:8px;background:url('http://t1.daumcdn.net/localimg/localimages/07/mapapidoc/vertex_white_small.png')}
	.distanceInfo {position:relative;top:5px;left:5px;list-style:none;margin:0;}
	.distanceInfo .label {display:inline-block;width:50px;}
	.distanceInfo:after {content:none;}
  .radius_border{border:1px solid #919191;border-radius:5px;}     
	.bAddr {padding:5px;text-overflow: ellipsis;overflow: hidden;white-space: nowrap;} 
.custom_typecontrol {position:absolute;top:10px;right:10px;overflow:hidden;width:195px;height:30px;margin:0;padding:0;z-index:1;font-size:12px;font-family:'Malgun Gothic', '���� ���?' , sans-serif;}
.custom_typecontrol span {display:block;width:65px;height:30px;float:left;text-align:center;line-height:30px;cursor:pointer;}
.custom_typecontrol .btn {background:#fff;background:linear-gradient(#fff,  #e6e6e6);}       
.custom_typecontrol .btn:hover {background:#f5f5f5;background:linear-gradient(#f5f5f5,#e3e3e3);}
.custom_typecontrol .btn:active {background:#e6e6e6;background:linear-gradient(#e6e6e6, #fff);}    
.custom_typecontrol .selected_btn {color:#fff;background:#425470;background:linear-gradient(#425470, #5b6d8a);}
.custom_typecontrol .selected_btn:hover {color:#fff;}   
.custom_zoomcontrol {position:absolute;top:50px;right:10px;width:36px;height:80px;overflow:hidden;z-index:1;background-color:#f5f5f5;} 
.custom_zoomcontrol span {display:block;width:36px;height:40px;text-align:center;cursor:pointer;}     
.custom_zoomcontrol span img {width:15px;height:15px;padding:12px 0;border:none;}    
.custom_zoomcontrol span:first-child{border-bottom:1px solid #bfbfbf;}     
</style>
<script type="text/javascript" src="https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId=e2jjal48we&amp;submodules=geocoder"></script>
</head>
<body>
<div class="map_wrap">
    <div id="map" style="width:100%;height:100%;position:relative;"></div>
<div class="custom_typecontrol radius_border">
        <span id="btnSurvyeDist" class="btn" onclick="setMapType('surveydistmode')">Ž��Ÿ�</span>
        <span id="btnDistance" class="btn" onclick="setMapType('distancemode')">�Ÿ�</span>
        <span id="btnOff" class="selected_btn" onclick="setMapType('offmode')">OFF</span>
    </div>    
    <div class="hAddr">
        <span id="centerAddr"></span>
    </div> 
</div>
<style type="text/css">
    html { height: 100% }
    body { height: 100%; margin: 0; padding: 0 }
    #map { width: 100%; height: 100% }
    </style>
<script type="text/javascript">
		var linePath1 = [
                             {{ gpslist1 }} 
                ];

        var linePath2 = [
                             {{ gpslist2 }} 
                ];

        var startPosition1 = {{ l1startpos }};
        var startmarkerOptions1 = {
        				position: startPosition1,
        				map : map, 
        				icon : {
        				url: 'https://ssl.pstatic.net/static/maps/ux2013/icons/pins_fw_s.png',
        				size : new naver.maps.Size(24, 35), 
        				origin : new naver.maps.Point(0, 0), 
        				anchor : new naver.maps.Point(12, 35)
        			}
        }; 
        var startmarker1 = new naver.maps.Marker(startmarkerOptions1);
        var arrivePosition1 = {{ l1endpos }};
        var arrivemarkerOptions1 = {
        				position: arrivePosition1,
        				map : map, 
        				icon : {
        				url: 'https://ssl.pstatic.net/static/maps/ux2013/icons/pins_fw_e.png',
        				size : new naver.maps.Size(24, 35), 
        				origin : new naver.maps.Point(0, 0), 
        				anchor : new naver.maps.Point(12, 35)
        			}
        }; 
        var arrivemarker1 = new naver.maps.Marker(arrivemarkerOptions1);

        var startPosition2 = {{ l2startpos }};
        var startmarkerOptions2 = {
        				position: startPosition2,
        				map : map, 
        				icon : {
        				url: 'https://ssl.pstatic.net/static/maps/ux2013/icons/pins_fw_s.png',
        				size : new naver.maps.Size(24, 35), 
        				origin : new naver.maps.Point(0, 0), 
        				anchor : new naver.maps.Point(12, 35)
        			}
        }; 
        var startmarker2 = new naver.maps.Marker(startmarkerOptions2);
        var arrivePosition2 = {{ l2endpos }};
        var arrivemarkerOptions2 = {
        				position: arrivePosition2,
        				map : map, 
        				icon : {
        				url: 'https://ssl.pstatic.net/static/maps/ux2013/icons/pins_fw_e.png',
        				size : new naver.maps.Size(24, 35), 
        				origin : new naver.maps.Point(0, 0), 
        				anchor : new naver.maps.Point(12, 35)
        			}
        }; 
        var arrivemarker2 = new naver.maps.Marker(arrivemarkerOptions2);
        
        var position = {{ centlatlon }};
        var map = new naver.maps.Map(document.getElementById('map'), {
           center: position,
           level: 11,
           mapTypeId: naver.maps.MapTypeId.NORMAL,
           mapTypeControl: true,
           mapTypeControlOptions:{
           position:naver.maps.Position.TOP_LEFT
           }
       });
       var drawingFlag = false;  
       var moveLine;  
       var clickLine;  
       var distInfoWnd;
       var dots = [];  
       var mapmode = 0;
       var marker = new naver.maps.Marker(), 
           infowindow = new naver.maps.InfoWindow({zindex:1});  
      map.addListener('click', function(e) {
           var clickPosition = e.coord;
           if(mapmode == 2){ //Distance mode
           if (!clickLine) {
               moveLine = new naver.maps.Polyline({ 
                       map: map,
                       path: [clickPosition],     
                       strokeWeight: 3, 
                       strokeColor: '#db4040', 
                       strokeOpacity: 0.5, 
                       strokeStyle: 'solid'  
                   });
               clickLine = new naver.maps.Polyline({
                   map: map,
                   path: [clickPosition], 
                   strokeWeight: 3,  
                   strokeColor: '#db4040', 
                   strokeOpacity: 1, 
                   strokeStyle: 'solid' 
               });
                   displayCircleDot(clickPosition, 0);

               } else { 
               if(moveLine){ 
						moveLine.setPath([e.coord]);
						clickLine.getPath().push(clickPosition);
						var distance =Math.round(clickLine.getDistance());
						displayCircleDot(clickPosition, distance);
						}
					}
               }
               else if(mapmode == 1){ // surveydist mode
               }
               else { // Off mode = GPS lat/lng mode
               }
           });
      map.addListener( 'mousemove', function (e) {
           if (clickLine){
				if (moveLine){
               var path = moveLine.getPath();
               var distance = Math.round(clickLine.getDistance() + moveLine.getDistance());
               var  content = '<div class="dotOverlay2 distanceInfo">�Ÿ�:<span class="number">' + distance + '</span>m</div>';
               if(path.getLength()===2){    
               path.pop();
               }
               path.push(e.coord);
               }
           } 
       });

       map.addListener( 'idle', function() {
       });
       map.addListener('rightclick', function (mouseEvent) { 
           if (clickLine) {
               moveLine.setMap(null);
               moveLine = null;  
               var path = clickLine.getPath();
               if (path.length > 1) {
                   if (dots[dots.length-1].distance) {
                   }
               } else {
                   deleteInfoWindow();
                   deleteClickLine();
                   deleteCircleDot(); 
                   deleteDistnce();
               }
           }  
               drawingFlag = false;     
       });  

       function displayCircleDot(position, distance) {
              var circleDotPosition = position;
              var circleDotMarkerOption = {
              				position: circleDotPosition,
              				map : map, 
              				icon : {
              				url: 'http://i1.daumcdn.net/localimg/localimages/07/mapapidoc/mini_circle.png',
              				size : new naver.maps.Size(20, 20), 
              				origin : new naver.maps.Point(0, 0), 
                              anchor : new naver.maps.Point(5, 5),
                              zindex: 2
                          }
              };
              var circleDotMarker = new naver.maps.Marker(circleDotMarkerOption);
              if (distance > 0) {
                      distInfoWnd = new naver.maps.InfoWindow({
                          content:'<div class="dotOverlay2">�Ÿ�:<span class="number">' + distance.toFixed(2) + '</span>m</div>'
                          });
                          distInfoWnd.open(map, circleDotMarker);
                  } 
                  dots.push({circle:circleDotMarker, distance:distInfoWnd});
             }; 

       function deleteClickLine() {
           if (clickLine) {
               clickLine.setMap(null);    
               clickLine = null;     
           }
           if (moveLine) {
               moveLine.setMap(null);    
               moveLine = null;     
           }
       };
       function deleteDistnce () {
           if (distInfoWnd) {
               distInfoWnd.setMap(null);
               distInfoWnd = null;
           }
       };
       function deleteCircleDot() {
           var i;
           for ( i = 0; i < dots.length; i++ ){ 
               if (dots[i].circle) { 
                   dots[i].circle.setMap(null); 
               } 
               if (dots[i].distance) { 
                   dots[i].distance.setMap(null); 
               } 
           } 
           dots = []; 
       } 
       function setMapType(modetype) { 
           var surveydistControl = document.getElementById('btnSurvyeDist'); 
           var distanceControl = document.getElementById('btnDistance'); 
           var offControl = document.getElementById('btnOff');
           if(modetype == 'distancemode'){
               mapmode = 2;
               distanceControl.className = 'selected_btn';
               offControl.className = 'btn';
               surveydistControl.className = 'btn';
				 if(totdistOverlay){
					totdistOverlay.setMap(null);
				 }
           } else if(modetype == 'surveydistmode'){
               mapmode = 1;
               surveydistControl.className = 'selected_btn';
               distanceControl.className = 'btn';
               offControl.className = 'btn';
				 if(totdistOverlay){
					totdistOverlay.setMap(map);
				 }
				deleteClickLine();
				deleteCircleDot(); 
           } else {
               mapmode = 0;
               distanceControl.className = 'btn';
               offControl.className = 'selected_btn';
               surveydistControl.className = 'btn';
               deleteallobjects();
           }
       }

       function deleteInfoWindow(){
           infowindow.close();
       }
       function deleteallobjects(){
           deleteInfoWindow();
           deleteClickLine();
           deleteCircleDot(); 
           deleteDistnce();
       }
       var markers = [];
        function addMarker(position) {
        	var marker = new naver.maps.Marker({
        		position: position
        	});
        	marker.setMap(map);
        	markers.push(marker);
        }
        for (var i = 0; i < markers.length; i++) {
        	markers[i].setMap(map);
        }            
        var poimarkers1 = [];
        var poimarkers2 = [];
        var customOverlays = [];
        var circleOverlays = [];
        var poititle = [];
        var poipaths1 = [];
        poipaths1[0]=linePath1[0];
        var poipaths2 = [];
        poipaths2[0]=linePath2[0];

        function addPOIMarker(position, indx) {
            poimarkers1.push(position);
            poimarkers2.push(position);
            poipaths1[1]=position;
            poipaths2[1]=position;
            var temppoipolyline1 = new naver.maps.Polyline({
                    map : map, 
                    path: poipaths1,
                    strokeWeight: 5, 
                    strokeColor: '#FF0000', 
                    strokeOpacity: 0.0, 
                    strokeStyle: 'solid' 
                    });
            var temppoipolyline2 = new naver.maps.Polyline({
                    map : map, 
                    path: poipaths2,
                    strokeWeight: 5, 
                    strokeColor: '#0000FF', 
                    strokeOpacity: 0.0, 
                    strokeStyle: 'solid' 
                    });
            var poidistance1 = Math.round(temppoipolyline1.getDistance()); 
            var poidistance2 = Math.round(temppoipolyline2.getDistance()); 
            var poicircleDotPosition = position;
            var poicircleDotMarkerOption1 = {
                                        position: poicircleDotPosition,
                                        map : map, 
                                        icon : {
                                            url: 'http://i1.daumcdn.net/localimg/localimages/07/mapapidoc/mini_circle.png',
                                            size : new naver.maps.Size(20, 20), 
                                            origin : new naver.maps.Point(0, 0), 
                                            anchor : new naver.maps.Point(5, 5),
                                            zindex: 1000
                                        }
                                    };
            var poicircleDotMarker = new naver.maps.Marker(poicircleDotMarkerOption);
            var markerContent = ['<div class="dotOverlay">'+poititle[indx]+' at <span class="number">' + poidistance.toFixed(2) + '</span>m'+ 
                                '</div>'].join('');
            var htmlMarker = new naver.maps.Marker({
                position: position,
                map: map,
                icon: {
                content: markerContent,
                size: new naver.maps.Size(22, 30),
                anchor: new naver.maps.Point(11, 30)
                }
            });
        };
		var polyline1 = new naver.maps.Polyline({
			path: linePath1, 
			strokeWeight: 5, 
			strokeColor: '#FF0000', 
			strokeOpacity: 0.7,
			strokeStyle: 'solid' 
		});
		polyline1.setMap(map);
        var polyline2 = new naver.maps.Polyline({
			path: linePath2, 
			strokeWeight: 5, 
			strokeColor: '#0000FF', 
			strokeOpacity: 0.7,
			strokeStyle: 'solid' 
		});
		polyline2.setMap(map);
		var totdistance1 = Math.round(polyline1.getDistance()); 
        var totdistance2 = Math.round(polyline2.getDistance()); 
		var totdistOverlay1 = new naver.maps.InfoWindow({
				position:arrivePosition1,
				content:'<div class="dotOverlay2">Ž��Ÿ�:<span class="number">' + totdistance + '</span>m</div>',
				xAnchor: 0.5,
				yAnchor: 0,
				zIndex: 3
				});
        var totdistOverlay2 = new naver.maps.InfoWindow({
				position:arrivePosition2,
				content:'<div class="dotOverlay2">Ž��Ÿ�:<span class="number">' + totdistance + '</span>m</div>',
				xAnchor: 0.5,
				yAnchor: 0,
				zIndex: 3
				});
</script>
</body>
</html>
"""
for i in range(finalhtmfilecount):
    t = Template(template).render(Context({"title": outfilename[i],"gpslist1":line1gpslist[i],"gpslist2":line2gpslist[i], "l1startpos":l1startpos[i], "l1endpos":l1endpos[i],"l2startpos":l2startpos[i], "l2endpos":l2endpos[i], "centlatlon":centlatlon[i]}))
    # print(outfilename[i])
    fileout = open(outfilename[i], 'w', encoding='UTF8')
    fileout.write(t)
    fileout.close()

#print("nolines:{}".format(nolines))