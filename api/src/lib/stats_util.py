def get_county_data(cursor, query, state, elec_dt):
    cursor.execute(query)

    rows = cursor.fetchall()

    # lists for the county_data
    total_rejected =[]
    total_cured = []
    total_processed = []
    rejected_gender = []
    cured_gender = []
    total_gender = []
    rejected_race = []
    cured_race = []
    total_race = []
    rejected_age_group = []
    cured_age_group = []
    total_age_group = []
    ballot_issue_count = []

    # parse each counties data
    for row in rows:   
        # string parsing to convert rej_reason into the right form
        rej_reason = json.loads(row['rej_reason'])
        rej_reason = process_json(rej_reason) 

        # get demographic stats
        demo_stats = get_demographics(state, row) 

        # add the data to each list
        total_rejected.append({"name" : row['county'].title(), "value" : row['tot_rejected']})
        total_cured.append({"name" : row['county'].title(), "value" : row['tot_cured']})
        total_processed.append({"name" : row['county'].title(), "value" : row['tot_processed']})
        rejected_gender.append({"name" : row['county'].title(), "value" : demo_stats['gender_rej']})
        cured_gender.append({"name" : row['county'].title(), "value" : demo_stats['gender_cur']})
        total_gender.append({"name" : row['county'].title(), "value" : demo_stats['gender_tot']})
        rejected_race.append({"name" : row['county'].title(), "value" : demo_stats['race_rej']})
        cured_race.append({"name" : row['county'].title(), "value" : demo_stats['race_cur']})
        total_race.append({"name" : row['county'].title(), "value" : demo_stats['race_tot']})
        rejected_age_group.append({"name" : row['county'].title(), "value" : demo_stats['age_rej']})
        cured_age_group.append({"name" : row['county'].title(), "value" : demo_stats['age_cur']})
        total_age_group.append({"name" : row['county'].title(), "value" : demo_stats['age_tot']})
        ballot_issue_count.append({"name" : row['county'].title(), "value" : rej_reason})


    # build final output
    ret_dict = {
        "state" : state,
        "election_dt" : elec_dt.strftime("%m/%d/%Y"),
        "total_rejected" : total_rejected,
        "total_cured" : total_cured,
        "total_processed" : total_processed,
        "rejected_gender" : rejected_gender,
        "cured_gender" : cured_gender,
        "processed_gender" : total_gender,
        "rejected_race" : rejected_race,
        "cured_race" : cured_race,
        "processed_race" : total_race,
        "rejected_age_group" : rejected_age_group,
        "cured_age_group" : cured_age_group,
        "processed_age_group" : total_age_group,
        "ballot_issue_count" : ballot_issue_count
    }

    return jsonify(ret_dict)

# method to get the demographic info from the mysql row
def get_demographics(state, row):

    ret_dict = {}

    # GA doesn't support these stats so should be null for Georgia
    if (state != "GA"):
        # string parsing to convert gender stats into the right form
        gender_rej = json.loads(row['gender_rej'])
        ret_dict['gender_rej'] = process_json(gender_rej)

        gender_cur = json.loads(row['gender_cured'])
        ret_dict['gender_cur'] = process_json(gender_cur)

        gender_tot = json.loads(row['gender_tot'])
        ret_dict['gender_tot'] = process_json(gender_tot)

        # string parsing to convert race stats into the right form
        race_rej = json.loads(row['race_rej'])
        ret_dict['race_rej'] = process_race_json(race_rej)

        race_cur = json.loads(row['race_cured'])
        ret_dict['race_cur'] = process_race_json(race_cur)

        race_tot = json.loads(row['race_tot'])
        ret_dict['race_tot'] = process_race_json(race_tot)

        # string parsing to convert age stats into right form
        age_rej = json.loads(row['age_rej'])
        ret_dict['age_rej'] = process_age_json(age_rej)

        age_cur = json.loads(row['age_cured'])
        ret_dict['age_cur'] = process_age_json(age_cur)

        age_tot = json.loads(row['age_tot'])
        ret_dict['age_tot'] = process_age_json(age_tot)
    else:
        # everything is null in the case of Georgia
        ret_dict['gender_rej'] = 'null'
        ret_dict['gender_cur'] = 'null'
        ret_dict['gender_tot'] = 'null'
        ret_dict['race_rej'] = 'null'
        ret_dict['race_cur'] = 'null'
        ret_dict['race_tot'] = 'null'
        ret_dict['age_rej'] = 'null'
        ret_dict['age_cur'] = 'null'
        ret_dict['age_tot'] = 'null'

    return ret_dict

# method to process a json response from sql to valid json form 
def process_json(response):
    response = response.replace("},)", "})") # note this isn't in every json string just some of them
    response = response.replace('(', "[")
    response = response.replace(')', "]")
    response = response.replace("'", '"')
    response = response.replace("None", "0")
    response = json.loads(response)
    return response

def process_age_json(response):
    response = process_json(response)
    ret = []
    # update to have names for values
    for key in response[0]:
        ret.append({"age" : key, "age_count" : int(response[0][key])})
    return ret

# special method to process the race stats as there are special cases
def process_race_json(response):
    response = response.replace("},)", "})")
    response = response.replace('(', "[")
    response = response.replace(')', "]")
    response = response.replace("'", '"') 
    response = response.replace(', {"race": ""UNDESIGNATED", "race_count": 2}', "") # TODO: Add 2 to the normal undesignated count to account for this
    response = response.replace(', {"race": ""UNDESIGNATED", "race_count": 1}', "")
    return json.loads(response)