import MySQLdb

from datetime import datetime
from flask import Blueprint
from flask import jsonify
from flask import request as req
from flask import abort

import util
from schema import schema_col_names
from config import load_config

ballots_bp = Blueprint('ballots', __name__)

config = load_config()

@ballots_bp.route('/', methods=['GET'])
def ballots():
    # perform the query based off given parameters
    cur = perform_query()

    # attach row headers, remove ID, return json
    row_headers = [x[0] for x in cur.description]
    id_idx = row_headers.index('id')
    row_headers.pop(id_idx)

    rows = cur.fetchall()

    data = []

    data.append({'row_count': len(rows)})

    ret_count = 0

    # only return 10 entries - full query sent from downloads endpoint
    for row in rows:
        mod_row = list(row)
        mod_row.pop(id_idx)
        data.append(dict(zip(row_headers, mod_row)))

        ret_count += 1
        if ret_count == 10:
            break

    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

# function to perform the query based of the parameters
def perform_query():
    # required parameters - throws error if not present
    try:
        state = req.args['state'].upper()
        elec_dt = datetime.strptime(req.args['election_dt'], '%m-%d-%Y')
    except:
        abort(404, description="Resource not found")

    # build WHERE clause for optional parameters on the fly for optimized SQL query times
    where_clause = ''

    # set any default values for params if needed
    rtn_status = req.args.get('ballot_rtn_status', 'R')
    where_clause += f'ballot_rtn_status = "{rtn_status}" AND '

    # optional parameters
    for param in schema_col_names:
        if param in where_clause or param == 'state' or param == 'election_dt': 
            continue
        else:
            val = req.args.get(param, None)
            where_clause += f'{param} = "{val}" AND ' if val else '' # double quotes important to prevent SQL injection

    # remove last AND
    where_clause = where_clause[:-5]

    limit = int(req.args.get('limit', 0))
    limit_clause = f'LIMIT {limit}' if limit else ''

    # TODO support historic data requests - run query on `rejected` table, otherwise run on main table
    historic = req.args.get('show_historic', False)

    try:
        mydb = util.mysql_connect(state)
        cur = mydb.cursor()
    except:
        # if connection failed, then input state was not valid
        abort(500, description="internal service failure")

    election = elec_dt.strftime('%m_%d_%Y')
    db_table_name = f'rejected_{election}'

    query = f'''
    SELECT *
    FROM {db_table_name}
    WHERE {where_clause}
    {limit_clause};
    '''

    print(f'DEBUG:\n{query}')

    try:
        cur.execute(query)
    except:
        # if valid, then election_dt not valid
        abort(500, description="internal service failure")

    # return the cursor with the results
    return cur
