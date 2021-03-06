import os
import sys
import shutil
import time
import zipfile
import MySQLdb

from datetime import date 
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select

from schema import schema_table, ga_load
from elections import elections_table, update_proc_date
from config import load_config

config = load_config()

year = config['GA']['year']
name = config['GA']['name']

# start selenium webdriver
op = ChromeOptions()
op.add_argument('--headless')
browser = Chrome(options=op)
browser.get('https://elections.sos.ga.gov/Elections/voterabsenteefile.do')
print('Selenium driver started.')

# select year
select_election_year = browser.find_element_by_id('nbElecYear')
for option in select_election_year.find_elements_by_tag_name('option'):
  if option.text == year:
    option.click()
    break
print('Year selected.')

# wait 10 seconds for election year data to load
WebDriverWait(browser, 10)

# select election name
select_election_name = browser.find_element_by_id('idElection')
for option in select_election_name.find_elements_by_tag_name('option'):
  if option.text == name:
    option.click()
    break
print('Election selected.')

# wait 10 seconds for election data to load
WebDriverWait(browser, 10)

# download the file
url = 'javascript:downLoadFile();'
download = browser.find_element_by_xpath('//a[@href="'+url+'"]')
download.click()
print('File download started.')

# download filename can either be set in config
# or programmed in script i.e. grab from .crdownload
# or find pattern from SOS site
filename = config['GA']['filename']

download_path = config['SYSTEM']['download_dir']

file_path = os.path.join(download_path, filename)
timeout = int(config['GA']['Timeout'])
count = 0

while not os.path.exists(file_path):
    time.sleep(1)
    count += 1
    if count > timeout:
      print('Timeout on downloading file. Exiting program.')
      break

if not os.path.isfile(file_path):
  raise ValueError("%s isn't a file!" % file_path)

storage_path = config['GA']['storage_dir']
today = date.today().strftime('%Y-%m-%d')

new_file_path = storage_path + filename
shutil.move(file_path, new_file_path)

new_file_dir = os.path.join(storage_path, today)
if not os.path.exists(new_file_dir):
  os.mkdir(new_file_dir)

with zipfile.ZipFile(new_file_path, 'r') as zip_ref:
  print(f'Unzipping file: {filename}.')
  zip_ref.extractall(new_file_dir)

os.remove(new_file_path) # delete zip file

# TODO rm all non-STATEWIDE.csv files
print(f'Files located at: {new_file_dir}')

mydb = MySQLdb.connect(host=config['DATABASE']['host'],
    user=config['DATABASE']['user'],
    passwd=config['DATABASE']['passwd'],
    db=config['GA']['db'],
    local_infile = 1)

cursor = mydb.cursor()

query = schema_table(config['GA']['table'])
cursor.execute(query)

csv_file = os.path.join(new_file_dir, config['GA']['csv_name'])

query = ga_load(csv_file, config['GA']['table'])

print('Database insertion started.')
start_time = time.time()

cursor.execute(query)
mydb.commit()

print('Database insertion executed.')
print(f'Total time: {time.time() - start_time} seconds')

print('Updating processed date.')
# create the elections table
query = elections_table()
cursor.execute(query)
mydb.commit()

# update processed date
query = update_proc_date(config['GA']['table'])
cursor.execute(query)
mydb.commit()
