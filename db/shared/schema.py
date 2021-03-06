'''
Variables and queries to set up and work with database schema.
'''

schema_col_names = [
    'proc_date', 
    'county',
    'voter_reg_id',
    'first_name',
    'middle_name',
    'last_name',
    'race',
    'ethnicity',
    'gender',
    'age',
    'street_address',
    'city',
    'state',
    'zip',
    'election_dt',
    'party_code',
    'precinct',
    'cong_dist',
    'st_house',
    'st_senate',
    'ballot_style',
    'ballot_req_dt',
    'ballot_send_dt',
    'ballot_ret_dt',
    'ballot_issue',
    'ballot_rtn_status',
]

schema_col_names_types = ''' 
	proc_date               DATETIME,
	county                  VARCHAR(25),
	voter_reg_id            VARCHAR(25),
	first_name              VARCHAR(50),
	middle_name             VARCHAR(50),
	last_name               VARCHAR(50),
	race                    VARCHAR(50),
	ethnicity               VARCHAR(50),
	gender                  VARCHAR(10),
	age                     INT,
	street_address          VARCHAR(255),
	city                    VARCHAR(50),
	state                   VARCHAR(10),
	zip                     VARCHAR(10),
	election_dt             DATETIME,
	party_code              VARCHAR(10),
	precinct                VARCHAR(50),
	cong_dist               VARCHAR(50),
	st_house                VARCHAR(50),
	st_senate               VARCHAR(50),
	ballot_style            VARCHAR(50),
	ballot_req_dt           DATETIME,
	ballot_send_dt         	DATETIME,
	ballot_ret_dt           DATETIME,
	ballot_issue            VARCHAR(255),
	ballot_rtn_status       VARCHAR(50),
'''

stat_col_names_types = '''
	proc_date               DATETIME,
	election_dt             DATETIME,
        tot_processed           INT,
	tot_cured               INT,
	tot_rejected            INT,
        rej_reason              JSON,         
        gender_tot              JSON,
        gender_cured            JSON,
        gender_rej              JSON,
        race_tot                JSON,
        race_cured              JSON,
        race_rej                JSON,
        age_tot                 JSON,
        age_cured               JSON,
        age_rej                 JSON,
'''

time_series_col_names_types = '''
        proc_date               DATETIME,
        election_dt             DATETIME,
        processed               INT,
        unique_processed        INT,
        rejected                INT,
        unique_rej              INT,
        cured                   INT,
        unique_cured            INT,
'''

# General schema creation functions

def schema_table(table):
    return f'''
    CREATE TABLE IF NOT EXISTS {table} (
      id    INT NOT NULL AUTO_INCREMENT, 
      {schema_col_names_types}
      PRIMARY KEY(id)
    );
    '''

def schema_index(table):
   return f'''
    CREATE UNIQUE INDEX IF NOT EXISTS voter_idx 
    ON {table} (
        county, 
        voter_reg_num, 
        ballot_style, 
        ballot_req_dt, 
        ballot_ret_dt, 
        ballot_issue, 
        ballot_rtn_status
    );
    ''' 

# Functions to create supplementary tables

def create_state_stats_table():
    return f'''
    CREATE TABLE IF NOT EXISTS state_stats (
        {stat_col_names_types}
        PRIMARY KEY (proc_date, election_dt)
    );
  '''

def create_county_stats_table():
    return f'''
    CREATE TABLE IF NOT EXISTS county_stats (
        county                  VARCHAR(25),
        {stat_col_names_types}
        PRIMARY KEY (county, proc_date, election_dt)
    );
    '''

def create_state_time_series_table():
    return f'''
    CREATE TABLE IF NOT EXISTS state_time_series (
        {time_series_col_names_types}
        PRIMARY KEY (proc_date, election_dt)
    );
    '''

def create_county_time_series_table():
    return f'''
    CREATE TABLE IF NOT EXISTS county_time_series (
        county                  VARCHAR(25),
        {time_series_col_names_types}
        PRIMARY KEY (county, proc_date, election_dt)
    );
    '''

# Functions to modify supplementary tables

def add_to_cured(cured_db, entry):
    return f'''
    INSERT IGNORE INTO {cured_db} (
        id, proc_date, county, voter_reg_id, first_name, middle_name, last_name, race, ethnicity, gender, age, street_address, city, state, zip, election_dt, party_code, precinct, cong_dist, st_house, st_senate, ballot_style, ballot_req_dt, ballot_send_dt, ballot_ret_dt, ballot_issue, ballot_rtn_status
    )
    VALUES(
        "{entry["id"]}", "{entry["proc_date"]}", "{entry["county"]}", "{entry["voter_reg_id"]}", "{entry["first_name"]}", "{entry["middle_name"]}", "{entry["last_name"]}", "{entry["race"]}",
	"{entry["ethnicity"]}", "{entry["gender"]}", "{entry["age"]}", "{entry["street_address"]}", "{entry["city"]}", "{entry["state"]}", {entry["zip"]}, "{entry["election_dt"]}",
	"{entry["party_code"]}", "{entry["precinct"]}", "{entry["cong_dist"]}", "{entry["st_house"]}", "{entry["st_senate"]}", "{entry["ballot_style"]}", "{entry["ballot_req_dt"]}",
        "{entry["ballot_send_dt"]}", "{entry["ballot_ret_dt"]}", "{entry["ballot_issue"]}", "{entry["ballot_rtn_status"]}"
    );
'''

def remove_cured_from_rejected(rej_db, entry):
    return f'''
    DELETE FROM {rej_db} 
    WHERE voter_reg_id = "{entry["voter_reg_id"]}";
    '''

def add_to_rejected(rejected_db, entry):
    return f'''
    INSERT IGNORE INTO {rejected_db} (
        id, proc_date, county, voter_reg_id, first_name, middle_name, last_name, race, ethnicity, gender, age, street_address, city, state, zip, election_dt,
	party_code, precinct, cong_dist, st_house, st_senate, ballot_style, ballot_req_dt, ballot_send_dt, ballot_ret_dt, ballot_issue, ballot_rtn_status
    )
    VALUES (
        "{entry["id"]}", "{entry["proc_date"]}", "{entry["county"]}", "{entry["voter_reg_id"]}", "{entry["first_name"]}", "{entry["middle_name"]}", "{entry["last_name"]}", "{entry["race"]}",
	"{entry["ethnicity"]}", "{entry["gender"]}", "{entry["age"]}", "{entry["street_address"]}", "{entry["city"]}", "{entry["state"]}", "{entry["zip"]}", "{entry["election_dt"]}",
	"{entry["party_code"]}", "{entry["precinct"]}", "{entry["cong_dist"]}", "{entry["st_house"]}", "{entry["st_senate"]}", "{entry["ballot_style"]}", "{entry["ballot_req_dt"]}",
	"{entry["ballot_send_dt"]}", "{entry["ballot_ret_dt"]}", "{entry["ballot_issue"]}", "{entry["ballot_rtn_status"]}"
    );
'''

def add_to_cured_NC(cured_db, entry):
    return f'''
    INSERT IGNORE INTO {cured_db} (
        id, proc_date, county, voter_reg_id, first_name, middle_name, last_name, race, ethnicity, gender, age, street_address, city, state, zip, election_dt,
	party_code, precinct, cong_dist, st_house, st_senate, ballot_style, ballot_req_dt, ballot_send_dt, ballot_ret_dt, ballot_issue, ballot_rtn_status
    )
    VALUES (
        "{entry["id"]}", "{entry["proc_date"]}", "{entry["county"]}", "{entry["voter_reg_id"]}", "{entry["first_name"]}", "{entry["middle_name"]}", "{entry["last_name"]}", "{entry["race"]}",
	"{entry["ethnicity"]}", "{entry["gender"]}", "{entry["age"]}", "{entry["street_address"]}", "{entry["city"]}", "{entry["state"]}", {entry["zip"]}, "{entry["election_dt"]}",
	"{entry["party_code"]}", "{entry["precinct"]}", "{entry["cong_dist"]}", "{entry["st_house"]}", "{entry["st_senate"]}", "{entry["ballot_style"]}", "{entry["ballot_req_dt"]}",
	"{entry["ballot_send_dt"]}", "{entry["ballot_ret_dt"]}", "{entry["ballot_issue"]}", "{entry["ballot_rtn_status"]}"
    );
'''

def add_to_rejected_NC(rejected_db, entry):
    return f'''
    INSERT IGNORE INTO {rejected_db} (
        id, proc_date, county, voter_reg_id, first_name, middle_name, last_name, race, ethnicity, gender, age, street_address, city, state, zip, election_dt,
	party_code, precinct, cong_dist, st_house, st_senate, ballot_style, ballot_req_dt, ballot_send_dt, ballot_ret_dt, ballot_issue, ballot_rtn_status
    )
    VALUES (
        "{entry["id"]}", "{entry["proc_date"]}", "{entry["county"]}", "{entry["voter_reg_id"]}", "{entry["first_name"]}", "{entry["middle_name"]}", "{entry["last_name"]}", "{entry["race"]}",
	"{entry["ethnicity"]}", "{entry["gender"]}", "{entry["age"]}", "{entry["street_address"]}", "{entry["city"]}", "{entry["state"]}", "{entry["zip"]}", "{entry["election_dt"]}",
        "{entry["party_code"]}", "{entry["precinct"]}", "{entry["cong_dist"]}", "{entry["st_house"]}", "{entry["st_senate"]}", "{entry["ballot_style"]}", "{entry["ballot_req_dt"]}",
        "{entry["ballot_send_dt"]}", "{entry["ballot_ret_dt"]}", "{entry["ballot_issue"]}", "{entry["ballot_rtn_status"]}"
    );
'''

def insert_stat(county=None):
    table = 'county_stats' if county else 'state_stats'
    county_string = '"{county}",' if county else ''

    return f'''
    INSERT IGNORE INTO {table} 
    VALUES ({county_string} %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''

def insert_time_series(county=None):
    table = 'county_time_series' if county else 'state_time_series'
    county_string = f'"{county}",' if county else ''

    return f'''
    INSERT IGNORE INTO {table} 
    VALUES ({county_string} %s, %s, %s, %s, %s, %s, %s, %s);
    '''

# State-specific functions

def ga_load(csv, table):
    return f'''
    LOAD DATA LOCAL INFILE '{csv}'
    INTO TABLE {table}
    CHARACTER SET latin1
    FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS (county, voter_reg_id, last_name, first_name, middle_name, @dummy, @street_no,
               @street_name, @apt_no, city, state, zip, @dummy, @dummy, @dummy, @dummy,
                   @dummy, @dummy, @dummy, ballot_rtn_status, ballot_issue, @req_dt, @send_dt,
                   @ret_dt, ballot_style, @dummy, @dummy, @dummy, @dummy, precinct, cong_dist, 
                   st_senate, st_house, @dummy, @dummy, @dummy, @dummy, @dummy, party_code)
                   SET proc_date = NOW(),
                       street_address = CONCAT(@street_no, ' ', @street_name, ' ', @apt_no),
                       ballot_req_dt = STR_TO_DATE(@req_dt, '%m/%d/%Y'),
                       ballot_send_dt = STR_TO_DATE(@send_dt, '%m/%d/%Y'),
                       ballot_ret_dt = STR_TO_DATE(@ret_dt, '%m/%d/%Y');
    '''

