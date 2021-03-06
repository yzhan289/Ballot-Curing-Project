import MySQLdb
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import abort
from datetime import datetime

from config import load_config
from util import mysql_connect

lastProcessed_bp = Blueprint('lastProcessed', __name__)

config = load_config()

@lastProcessed_bp.route('/')
def lastProcessed():

    # get state/election_dt parameters
    try:
        state = request.args['state'].upper()
        election_dt = datetime.strptime(request.args['election_dt'], '%m-%d-%Y')
    except:
        abort(404, description="Resource not found")


    # connect to the database
    try:
        mydb = mysql_connect(state)
    except:
        abort(500, description="internal service failure")

    # run query to get processed date for that election
    cursor = mydb.cursor()
    query = f''' 
    SELECT proc_date 
    FROM elections 
    WHERE election_dt = '{election_dt}';
    '''
    print("debug: " + query)
    try:
        cursor.execute(query)
    except:
        abort(500, description="internal service failure")

    # get result (note should only be one row since only one matching election)
    output = cursor.fetchall()
    # if no result, then input date was invalid
    if len(output) == 0:
        abort(404, description="Resource not found")
    for row in output:
        result = row[0]

    # put results into a dictionary and return as a json
    ret_dict = {
        "state" : state,
        "election_dt" : election_dt.strftime("%m/%d/%Y"),
        "last_proc" : result.strftime("%m/%d/%Y")
    }

    response = jsonify(ret_dict)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
