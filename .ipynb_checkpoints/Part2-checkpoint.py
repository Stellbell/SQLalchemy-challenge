import datetime as dt
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, create_engine, desc, func, inspect, text

from flask import Flask, jsonify

# Database Setup
#################################################
database_path = "Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement
# Flask Setup
#################################################
app = Flask(__name__)

# Flask Routes
#################################################
@app.route("/")
def routes():
    """List all available api routes."""
    return (
        f"<strong>Available Routes:</strong><br/>"        
        f"<a href=\"api/v1.0/precipitation\">Precipitation ( /api/v1.0/precipitation )</a><br/>"
        f"<a href=\"api/v1.0/stations\">Stations ( /api/v1.0/stations )</a><br/>"
        f"<a href=\"api/v1.0/tobs\">Temperature Observations ( /api/v1.0/tobs )</a><br/>"
        f"<a href=\"api/v1.0/2010-01-01\">Start Date ( /api/v1.0/<start> )</a><br/>"
        f"<a href=\"api/v1.0/2010-01-01/2017-08-23\">Start and End Date ( /api/v1.0/<start>/<end> )</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():    
    
    session = Session(engine)
    
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar();
    most_recent_date = date.fromisoformat(most_recent_date_str)
    last_year_date = most_recent_date + relativedelta(years = -1)
    
    results = session.query(Measurement.date, Measurement.prcp) \
                     .filter(Measurement.date.between(last_year_date, most_recent_date)) 
    
      # Create a dictionary from the row data
    all_precip = []
    for prec_date, prcp in results:
        precip_dict = {}
        precip_dict[prec_date] = prcp
        all_precip.append(precip_dict)
    
    #return "precipitation"
    return jsonify(all_precip) 
@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)
        
    results = session.query(Measurement.station, func.count(Measurement.station).label('count')) \
                  .group_by(Measurement.station) \
                  .order_by(desc('count')) \
                  .all()

    all_stations = []
    for station, count in results:        
        all_stations.append(station)    
    
    #return "stations"
    return jsonify(all_stations)   

@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)
    
    results = session.query(Measurement.station, func.count(Measurement.station).label('count')) \
                  .group_by(Measurement.station) \
                  .order_by(desc('count')) \
                  .all()
    
    most_active_station = results[0].station    
    most_recent_date_str = session.query(func.max(Measurement.date)) \
                              .filter(Measurement.station == most_active_station) \
                              .scalar();
    most_recent_date = date.fromisoformat(most_recent_date_str)
    last_year_date = most_recent_date + relativedelta(years = -1)
       
    results = session.query(Measurement.date, Measurement.tobs) \
                          .filter(Measurement.date.between(last_year_date, most_recent_date)) \
                          .filter(Measurement.station == most_active_station) \
                          .all()
    
    # Create a dictionary from the row data
    all_temp = []
    for temp_date, tobs in results:
        temp_dict = {}
        temp_dict[temp_date] = tobs
        all_temp.append(temp_dict)
    
    #return "tobs"
    return jsonify(all_temp)

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs).label('min'), \
                            func.max(Measurement.tobs).label('max'), \
                            func.avg(Measurement.tobs).label('avg')) \
                     .filter(Measurement.date >= start) \
                     .all()    
    
    tobs_dict = {}
    tobs_dict['min'] = results[0].min
    tobs_dict['max'] = results[0].max
    tobs_dict['avg'] = results[0].avg
                
    return jsonify(tobs_dict)    
    #return "start date"
    
    @app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs).label('min'), \
                            func.max(Measurement.tobs).label('max'), \
                            func.avg(Measurement.tobs).label('avg')) \
                     .filter(Measurement.date >= start) \
                     .filter(Measurement.date <= end) \
                     .all()    
    
    tobs_dict = {}
    tobs_dict['min'] = results[0].min
    tobs_dict['max'] = results[0].max
    tobs_dict['avg'] = results[0].avg
                
    return jsonify(tobs_dict)    
    #return "start and end date"


if __name__ == "__main__":
    app.run(debug=True)








