# WebReg-Scraper
This is a webreg scraper that can do automatic scraping and course scheduling. 
The main interface still need to be planned. But the major modules are ready.
## scraper.py
this file uses selenium to get all the course information from webreg and save them as html file

Things need as parameter
- ucsd account
- ucsd password
- departments need to scrape

## data_parser.py
this file uses beautiful soup as html parser to parse the data scraped by scraper and save it to sqlite3 database

## scheduler.py
this file can create a schedule based on a list of subject code given. Need the database generate by data_parser.py

Things need as parameter
- name of db file
- list of subject codes

For now, it will only provides u with a list of sections_ids of all possible schedule.

### Planned update
1. Build a main file that can complete scraping, parsing and scheduling in one stop
2. provide an optimal schedule based on time, availability, professor rating, (distance between each building?)
3. scrape cape.ucsd.edu (ucsd professor rating website) to provide professor rating
4. provide schedule that can overlook conflicts that specifies (e.g. discussion is optional, or final time is not consistent with syllabus, or labs is not mandatory)
5. a GUI interface, possibly a web app, where the scraping and data parsing will be done in background, and the optimal schedule will be displayed with GUI
6. output schedule to a calendar file

