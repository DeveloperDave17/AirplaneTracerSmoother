# # #
# Main function to run and interpolate all the flights
# Assumes it will get a list of instantiated Flight
# objects with ordered lists of Waypoints
# # #

import mysql.connector
import Flight
import Waypoint
import numpy as np
from scipy.interpolate import CubicSpline
import math

db = mysql.connector.connect(
        host= "",
        port= ,
        user = "",
        passwd = "",
        database = ""
    )

mycursor = db.cursor()

flights_to_complete = []  # List of Flights 

mycursor.execute("SELECT flight_id, flight_duration FROM Flight WHERE Completed = 'False'")
flights = mycursor.fetchall()
    
for (flight_id, flight_duration) in flights:
    offsetList = []
    latitudes = []
    longitudes = []
    altitudes = []
    
    mycursor.execute("SELECT latitude, longitude, altitude, offset_ms FROM Waypoint WHERE flight_id = %s ORDER BY offset_ms", [flight_id])
    waypoints = mycursor.fetchall()
    first = True
    for (latitude, longitude, altitude, offset_ms) in waypoints:
        if not first:
            offsetList.append(offset_ms)
            latitudes.append(latitude)
            longitudes.append(longitude)
            altitudes.append(altitude)
        if first:
            first = False
        
    
    flights_to_complete.append([offsetList,latitudes,longitudes,altitudes,flight_id])

# for every flight
for flight in flights_to_complete:
    cs1 = CubicSpline(flight[0],flight[1])
    cs2 = CubicSpline(flight[0],flight[2])

    waypointsAdditionCount = 500

    interval = flight[0][len(flight[0])-1] - flight[0][0]
    timePerPoint = math.ceil(interval / waypointsAdditionCount)

    print(str(flight[1][0]) + " " + str(flight[2][0]))
    print(timePerPoint)
    for x in range(1,500):
        offset = flight[0][1] + x * timePerPoint
        if offset > flight[0][len(flight[0]) - 2]:
            break
        latitude = cs1.__call__(offset)
        longitude = cs2.__call__(offset)
        altitude = np.interp(offset,np.array(flight[0],dtype='float64'),np.array(flight[3],dtype='float64'))
        print(str(latitude) + " " + str(longitude) + " " + str(altitude))
        flight_id = flight[4]
        mycursor.execute("INSERT IGNORE INTO Waypoint (flight_id, latitude, longitude, altitude, offset_ms) \
                         VALUES (%s,%s,%s,%s,%s)", (flight_id, str(latitude), str(longitude), str(altitude), offset))
    
    flight_id = flight[4]
    mycursor.execute("UPDATE Flight SET completed = True WHERE flight_id = %(flight_id)s", {'flight_id':flight_id})
    db.commit()


