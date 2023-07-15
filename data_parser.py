from bs4 import BeautifulSoup
import sqlite3
import os,glob


class class_parser:
    def __init__ (self):
        os.chdir(os.getcwd())
        self.files = glob.glob("*.html")
        self.event_id = 0
        self.last = 0
        self.last_subject_code = ""
        TERM = 'FALL 23'
        self.connect = sqlite3.connect(TERM + '1.db')

        self.cursor = self.connect.cursor()

        table = """ CREATE TABLE IF NOT EXISTS CLASSES(
                    subject_code TEXT,
                    section_id INTEGER,
                    meeting_type TEXT,
                    days TEXT,
                    time TEXT,
                    instructor TEXT,
                    event_code INTEGER);
                """
        
        self.cursor.execute(table)

    # parse all file, if done, close db connection
    #
    # @return: None
    def parse_all_page(self):
        for file in self.files:
            self.parse_page(file)
        self.close()

    # parse the element in each html page
    #
    # @param file: the html page need to be parsed
    # @return: None
    def parse_page(self,file):
        with open(file) as cur_page:
            soup = BeautifulSoup(cur_page,'html.parser')
            rows = soup.find_all(name='tr')
            for row in rows:
                self.parse_row(row)

    # try to find a element within a element
    #
    # @param row: current html element
    # @param name: name of the element
    # @attribute: {class name: class value}
    # @return : None / Web element found
    def try_find_element(self, row, name, attribute):
        element = None
        try:
            if attribute is None:
                element = row.find(name = name)
            else:
                element = row.find(name = name, attrs = attribute)
        except AttributeError:
            element = None
        return element
        
    # parse the element into text
    #
    # @param items: lists of web elements
    # @return: None (not valid web elements) / list of text within elements
    def get_element_text(self, items):
        result = []
        for item in items:
            if item != None:
                if item.get_text() == '\xa0':
                    result.append(None)
                else:
                    result.append(item.get_text())
            else:
                result.append(None)
        # if time is none, then it is not a valid text, return None
        if result[5] != None:
            if result[5][0].isdigit():
                if result[1] is not None:
                    # if there is a valid section id, current line
                    # is not a common event, return as is
                    if result[1][0].isdigit():
                        return result
                    # if there is no section id, it is a common event
                    # (Final, Midterm), remove section_id, and move
                    # common event to meeting_type
                    else:
                        result[3] = result[1]
                        result[1] = None
                        result[2] = None
                        return result
                else:
                    return result
        return None
    
    # parse element in each row, then inject it into db
    # 
    # @param row: the row(html element) to be parsed
    # @return: None
    def parse_row(self,row):
        # fetch all elements

        subject_code = self.try_find_element(self.try_find_element(row, 'table', None), 'td', None)
        
        section_id = self.try_find_element(row, 'td', {'aria-describedby':'search-div-b-table_SECTION_NUMBER'})

        final_label = self.try_find_element(section_id, 'span', None)
        
        meeting_type = self.try_find_element(row,'td',{'aria-describedby':'search-div-b-table_FK_CDI_INSTR_TYPE'})
        
        days =  self.try_find_element(row,'td',{'aria-describedby':'search-div-b-table_DAY_CODE'})

        time = self.try_find_element(row,'td',{'aria-describedby':'search-div-b-table_coltime'})
        
        instructor = self.try_find_element(row,'td',{'aria-describedby':'search-div-b-table_PERSON_FULL_NAME'})
        
        data = [subject_code, section_id, final_label, meeting_type, days, time, instructor]

        result = self.get_element_text(data)

        self.db_insert(result)
    
    # check the validity of text_entries, if valid, insert
    # @param result: text_entries
    def db_insert(self, result):
        increment_event_id = False
        if result != None:
            if result[1] != None:
                # if last line has no section id and current line has
                # it means common event is no longer shared
                # thus change event_id
                if result[1][0].isdigit():
                    if self.last == 1:
                        increment_event_id = True
                    self.last = 0
                else:
                    self.last = 1
            else:
                self.last = 1
            # append event id text_entreis
            if result[0] != self.last_subject_code:
                increment_event_id = True
            
            self.last_subject_code = result[0]

            if increment_event_id:
                self.event_id = self.event_id + 1
            result = result + [self.event_id]

            # delete final_label
            del result[2]

            # if there is a section_id, convert to int
            if result[1] is not None:
                #section id only has 6 digit
                result[1] = int(result[1][0:6])
            
            result[0] = result[0].replace(" ","")
            print(tuple(result))
            #insert into db
            self.cursor.execute("INSERT INTO CLASSES VALUES(?,?,?,?,?,?,?)", tuple(result))
    
    # commit change and close db
    #
    # @return: None
    def close(self):
        self.connect.commit()
        self.connect.close()
        
p = class_parser()
p.parse_all_page()
        
    


