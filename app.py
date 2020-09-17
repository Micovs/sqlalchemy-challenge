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
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"*****************<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"*****************<br/>"
        f"/api/v1.0/stations<br/>"
        f"*****************<br/>"
        f"/api/v1.0/tobs<br/>"
        f"*****************<br/>"
        f"NOTE: For the following link, as a start date, any date after 2010-01-01 can be used. <br/>"
        f"Use date format YYYY-MM-DD<br/>"
        f"/api/v1.0/2010-01-01<br/>"
        f"*****************<br/>"
        f"NOTE: For the following link, as a start date, any date after 2010-01-01 can be used. <br/>"
        f"As a end date, any date before 2017-08-23 can be used. Use date format YYYY-MM-DD <br/>"
        f"Choose a dates range between the start and end date inclusive<br/>"
        f"/api/v1.0/2010-01-01/2017-08-23"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Designing a query to retrieve the last 12 months of precipitation data 
    lastdatapoint = session.query(func.max(measurement.date)).scalar()

    # Finding the date 1 year ago from the last data point in the database
    lastdatapoint = dt.datetime.strptime(lastdatapoint, '%Y-%m-%d')
    year_ago = lastdatapoint - dt.timedelta(365)

    # Perform a query to retrieve the data and precipitation scores
    result = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()
    
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    dictionary = {}
    for x in result:
        dictionary[x[0]] = x[1]

    # Alternate method to create a list of dictionaries, where date is the key and prcp as the value
    # all_data = []
    # for date, prcpi in result:
    #     dictionary = {}
    #     dictionary[date] = prcpi
    #     all_data.append(dictionary)   


    return jsonify(dictionary)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve all the stations from the database
    results = session.query(measurement.date).all()

    session.close()

    cleaned = list(np.ravel(results))
    return jsonify(cleaned)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

     # Designing a query to retrieve the last 12 months of precipitation data 
    lastdatapoint = session.query(func.max(measurement.date)).scalar()

    # Finding the date 1 year ago from the last data point in the database
    lastdatapoint = dt.datetime.strptime(lastdatapoint, '%Y-%m-%d')
    year_ago = lastdatapoint - dt.timedelta(365)
    
    # Perform a query to retrieve the dates and temperature observations of the most active station for the last year of data.
    most_active_station = session.query(measurement.date, measurement.tobs).filter(measurement.date >= year_ago).\
    filter(measurement.station == "USC00519281").all()

    session.close()

    # Converts the result into a list of dictionary with keys as the date and tobs as value
    all_data_most_active = []
    for date, temp in most_active_station:
        dictionary = {}
        dictionary[date] = temp
        all_data_most_active.append(dictionary) 


    return jsonify(all_data_most_active)

@app.route("/api/v1.0/<startd>")
def tempcalc(startd):
    """Calculates TMIN, TAVG, and TMAX for all dates 
       greater than and equal to the start date, or a 404 if invalid date is provided"""

# Create a query to get all the dates that are availlable in the table
    session = Session(engine)

    result = session.query(measurement.date).all()

    session.close()

    cleaned = list(np.ravel(result))


# Check if the date entered is containd in the data, meaning good date was entered and we can retrive data
    if startd in cleaned:

    # Create our session (link) from Python to the DB
        session = Session(engine)

    # Perform a query to calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
        result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= startd).first()

        session.close()

        cleanedd = list(np.ravel(result))
        return jsonify(cleanedd)

    return jsonify({"error": "Date not found. Try another date. Use date format YYYY-MM-DD "}), 404


@app.route("/api/v1.0/<startd>/<endd>")
def tempcalc_with_endd(startd, endd):
    """Calculates TMIN, TAVG, and TMAX for all dates 
       between the start and end date, or a 404 if invalid date is provided"""


# Create a query to get all the dates that are availlable in the table
    session = Session(engine)

    result = session.query(measurement.date).all()

    session.close()

    cleaned = list(np.ravel(result))

# Check if the dates entered are containd in the data
    if startd and endd in cleaned:           

# Create our session (link) from Python to the DB
        session = Session(engine)

# Perform a query to calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
        result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= startd).filter(measurement.date <= endd).all()

        session.close()

        cleanedd = list(np.ravel(result))
        return jsonify(cleanedd)

    return jsonify({"error": "Date not found. Try another date. Use date format YYYY-MM-DD "}), 404
    
if __name__ == '__main__':
    app.run(debug=True)
