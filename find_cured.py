
import MySQLdb
import configparser
import queries

from datetime import datetime, timedelta

config = configparser.ConfigParser()
config.read('config.ini')
rejected_db = "rejected"
cured_db = "cured"
table = config['GA']['table']


def mysqlconnect(today_datetime):
  mydb = MySQLdb.connect(host=config['DATABASE']['host'],
                          user=config['DATABASE']['user'],
                          passwd=config['DATABASE']['passwd'],
                          db=config['GA']['db'],
                          local_infile=1)
  print("Connected to db")

  cursor = mydb.cursor(MySQLdb.cursors.DictCursor)

  # make cured table if not made
  cursor.execute(queries.create_cured_table(cured_db))

  # make rejected table if not made
  cursor.execute(queries.create_rejected_table(rejected_db))

  # get rejected ballots from total rejected
  print("Getting all rejected ballots from rejected table")
  cursor.execute(queries.get_all_rejected(rejected_db))

  # for each rejected entry, query for today to see if they were accepted
  output = cursor.fetchall()
  for entry in output:
    print("Found rejected entry: " + str(entry["voter_reg_num"]))
    cursor.execute(queries.query_for_accepted(
        table, today_datetime, entry))
    accepted = cursor.fetchall()

    # if accepted, add to cured and remove from rejected
    if len(accepted) > 0:
      print("Found cured entry for: " + str(entry["voter_reg_num"]))

      cursor.execute(queries.add_to_cured(
          cured_db, entry, today_datetime))
      mydb.commit()
      print("Added to cured table")

      cursor.execute(queries.remove_from_rejected(rejected_db, entry))
      print("Removed from rejected table")
      mydb.commit()

  # query the current day for any new rejected
  print("Getting today's rejected ballots from main table")
  cursor.execute(queries.get_today_rejected(table, today_datetime))
  output = cursor.fetchall()

  # for each rejected entry today, add to rejected table
  for entry in output:
    print("Found rejected entry: " + str(entry["voter_reg_num"]))

    cursor.execute(queries.add_to_rejected(
        rejected_db, entry, today_datetime))
    print("Added to rejected table")
    mydb.commit()

  # To close the connection
  mydb.close()


# Driver Code
if __name__ == "__main__":
  start_date = "11/20/20"
  start_datetime = datetime.strptime(start_date, '%m/%d/%y')
  for i in range(1):
    start_datetime += timedelta(days=1)
    print("Start date: " + str(start_datetime))
    mysqlconnect(start_datetime)