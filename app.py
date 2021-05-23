import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# ROOT - DISPLAY ALL ROUTES AVAILABLE
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h1>Available Routes:</h1><br/>"
        f"<table border='1' cellspacing='0' cellpadding='0'>"
        f"<thead><tr><th>Route Name</th><th>Route</th></thead><tbody>"
        f"<tr><td style='text-align:center'>Precipitation</td><td style='text-align:center'>/api/v1.0/precipitation</td></tr>"
        f"<tr><td style='text-align:center'>Stations</td><td style='text-align:center'>/api/v1.0/stations</td></tr>"
        f"<tr><td style='text-align:center'>Tobs</td><td style='text-align:center'>/api/v1.0/tobs</td></tr>"
        f"<tr><td style='text-align:center'>Temperatures for a given date (format: yyyy/mm/dd)</td><td style='text-align:center'>/api/v1.0/yyyy-mm-dd</td></tr>"
        f"<tr><td style='text-align:center'>Temperatures for a given date range (format: yyyy/mm/dd)</td><td style='text-align:center'>/api/v1.0/yyyy-mm-dd/yyyy-mm-dd</td></tr>"
        f"</tbody></table>"
    )


#################################################
# PRECIPITATION
#################################################
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to retrieve precipitation data
    sel = [Measurement.date,Measurement.prcp]
    results = session.query(*sel).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

#################################################
# STATIONS
#################################################
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    #Query to select all stations, order ascending
    results = session.query(Station.station).order_by(Station.station).all()
    session.close()

    #flatten result set and add to list
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)

#################################################
# TEMPERATURE OBSERVATIONS - TOBS
#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    most_recent_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(most_recent_date_str[0], '%Y-%m-%d')
    
    # Calculate the date one year from the last date in data set.
    recent_date_one_year_past = dt.date(most_recent_date.year -1, most_recent_date.month, most_recent_date.day)
    sel = [Measurement.date, Measurement.prcp]
    results = session.query(*sel).\
        filter(Measurement.date >= recent_date_one_year_past).all()

    session.close()

    # Convert the list to Dictionary
    all_tobs = []
    for date,tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

#################################################
# TEMPERATURE DATA >= GIVEN DATE
#################################################
@app.route('/api/v1.0/<start>')
def temperatureGreaterThanStart(start):
    session = Session(engine)

    #Query to get the TMIN, TAVG, TMAX for all dates greater than and equal to the given start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    # Convert the list to Dictionary
    all_tobs = []
    for min,avg,max in results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

#################################################
# TEMPERATURE DATA WITHIN A GIVEN DATE RANGE
#################################################
@app.route('/api/v1.0/<start>/<stop>')
def temperatureDateRange(start,stop):
    session = Session(engine)

    #Query to get TMIN, TAVG, TMAX for a given date range (start and stop)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= stop).all()
    session.close()

    # Convert the list to Dictionary
    all_tobs = []
    for min,avg,max in results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


if __name__ == '__main__':
    app.run(debug=True)
