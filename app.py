import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table

Measurement=Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Set up all rout
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f'Note: input start date in yyyy-mm-dd form <br/>'
        f"/api/v1.0/querydate/2016-08-23 <br/>"
        f'Note: input date range in yyyy-mm-dd/yyyy-mm-dd form<br/>'
        f"/api/v1.0/querydaterange/2016-08-23/2017-08-23 <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    results = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station,Station.name).all()
    session.close()

    station_list=[]
    for station,name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_list.append(station_dict)
    
    return jsonify(station_list)
    

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    query_date=(dt.datetime.strptime(latest_date[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
 
    pr_scores=session.query(Measurement.date, Measurement.prcp).\
         filter(Measurement.date >= query_date).order_by(Measurement.date.desc()).all()
    session.close()
    # date_prcp = list(np.ravel(pr_scores))
    # date_dict= dict(date_prcp)
    # return jsonify(date_dict)

    date_prcp = []
    for date,prcp in pr_scores:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        date_prcp.append(prcp_dict)

    return jsonify(date_prcp)

@app.route('/api/v1.0/querydate/<startDate>')
def start(startDate):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)]

    results =(session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate).\
        group_by(Measurement.date).all())

    session.close()

    dates = []                       
    for TMIN,TMAX,TAVG in results:
        
        date_dict = {}
        date_dict["Min"] = TMIN
        date_dict["Max"] = TMAX
        date_dict["Avg"] = TAVG
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/querydaterange/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)]

    results = (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                        .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                        .group_by(Measurement.date)
                        .all())
    session.close()                   

    date_range = []                       
    for TMIN,TMAX,TAVG in results:
        
        date_dict = {}
        date_dict["Min"] = TMIN
        date_dict["Max"] = TMAX
        date_dict["Avg"] = TAVG
        date_range.append(date_dict)
    return jsonify(date_range)


if __name__ == '__main__':
    app.run(debug=True)

   
