# [class1, class2, class3, class4]
import sqlite3

class scheduler:
    def __init__(self, list_of_classes, db):
        self.classes = list_of_classes
        self.num_classes = len(list_of_classes)
        self.connect = sqlite3.connect(db)
        self.cursor = self.connect.cursor()
        
    # get all possible schedule given list of classes
    #
    # @yield: all possible combination of classes
    def find_schedule(self):
        self.sections = []
        for subject_code in self.classes:
            section_list = self.find_unique_sections(subject_code)
            self.sections.append(section_list)
        self.time_conflict(self.sections[0], 0)



    # determine where there is a conflict given a list of classes and another class
    #
    # @param valid_section_list: a list of class(section) proven to be no conflict
    # @param X: the index of the class needed to detect conflicts
    # @yield: the list of section proven tp be a valid schedule
    def time_conflict(self, valid_sections_list, X):
        for section in self.sections[X]:
            if X == 0:
                    self.time_conflict([section], X+1)
            else:
                isValid = True
                for prev_section in valid_sections_list:
                    isValid = isValid & self.no_overlap(prev_section, section)
                    # print(prev_section, section, self.no_overlap(prev_section, section))
                if isValid:
                    if X + 1 < self.num_classes:
                        self.time_conflict([section] + valid_sections_list, X+1)
                    else:
                        print([section] + valid_sections_list)
            

    # detect whether there is an overlap between 2 sections
    #
    # @param section1: the first section
    # @param section2: the second section
    # @return boolean: overlap will return false, true otherwise
    def no_overlap(self,section1, section2):
        days = ['M', 'Tu', 'W', 'Th', 'F']

        time1_list, final1 = self.find_data(section1)
        time2_list, final2 = self.find_data(section2)
        #print(section1, time1_list)
        #print(section2, time2_list)
        for day in days:
            List_of_time1 = []
            List_of_time2 = []

            for tuple in time1_list:
                if day in tuple[0]:
                    List_of_time1.append(tuple[1])

            for tuple in time2_list:
                if day in tuple[0]:
                    List_of_time2.append(tuple[1])
            
            # print("list1: ", List_of_time1)
            # print("list2: ", List_of_time2)
            # print(day)
            if self.no_overlap_times(List_of_time1, List_of_time2) == False:
                return False
        if (final1 is None) or (final2 is None): 
            return True

        if final1[0] == final2[0]:
            return self.no_overlap_times(final1[1], final2[1])
        else:
            return True
    
    # determine whether there is overlap between 2 lists of time-interval
    # 
    # @param List_of_time1: the first list of time
    # @param List_of_time2: the second list of time
    # @return boolean: overlap will return false, true otherwise
    def no_overlap_times(self,List_of_time1, List_of_time2):
        for time1 in List_of_time1:
            for time2 in List_of_time2:
                start1, end1 = self.parse_time(time1)
                start2, end2 = self.parse_time(time2)
                if (start2 in range(start1, end1)) or (end2 in range(start1, end1)):
                    return False
        return True

    # find unique section_ids given a subject code
    #
    # @param subject_code: subject code eg. "CSE8A"
    # @return list: a list contains all section_ids
    def find_unique_sections(self,subject_code):
        self.cursor.execute('''select distinct section_id from 
                    (select section_id from CLASSES where subject_code=(?)) 
                    where section_id is not null''', (subject_code,))
        unique_section_num = self.cursor.fetchall()
        result = []
        for tuple in unique_section_num:
            result = result + [tuple[0]]
        return result

    # given a section id, find day and time for all events
    #
    # @param section_id: section_id
    # @return result: all events (Lecture, Lab, Discussion, Midterm, etc) and their time
    #                 in the form of list of tuples eg. [("TuTh", "5:00p-5:50p"), ...., ()]
    # @return final: final day and time in the form of tuple eg. ("Tu", "5:00p-5:50p")
    def find_data(self, section_id):
        self.cursor.execute("select days, time from CLASSES where section_id=(?)", (section_id,))
        result = self.cursor.fetchall()
        #print("result: ", result)
        self.cursor.execute("select event_code from CLASSES where section_id=(?)", (section_id,))
        common_event_code = self.cursor.fetchone()
        #print("event_code", common_event_code)
        self.cursor.execute('''select days, time 
                        from CLASSES where event_code=(?) 
                        and section_id is null 
                        and meeting_type != "FINAL" ''', (common_event_code[0],))

        #print("event: ", self.cursor.fetchall())
        result = result + self.cursor.fetchall()

        self.cursor.execute('''select days, time 
                        from CLASSES where event_code=(?) 
                        and section_id is null 
                        and meeting_type = "FINAL" ''', (common_event_code[0],)) 
        final = self.cursor.fetchone()
        return result, final

    # convert time string to a integer eg. 1:00a -> 100, 12:00p -> 1200
    #
    # @param time: a time string eg. "1:00a"
    # @return time_int: conversion from a time string to int
    def time_to_num(self,time):
        if time[0:2] == "12":
            if time[-1] == 'a':
                return int(time[3:5])
            else:
                time = time.replace(':',"")
                return int(time[:-1])
        else:
            time = time.replace(':',"")
            if time[-1] == 'a':

                return int(time[:-1])
            else:
                return int(time[:-1]) + 1200
    
    # given a string of time interval, return two time integer
    # eg. "5:00p-5:50p" -> start = 1700, end = 1750
    # 
    # @param time: a time interval string
    # @return start: integer represetation of start time
    # @return end: interger representation of end time
    def parse_time(self,time):
        start, end = time.split("-")
        return self.time_to_num(start), self.time_to_num(end)

classes = ["CSE11","CSE151A","CSE120", "CSE95"]
scheduler = scheduler(classes,"FALL 23.db")
scheduler.find_schedule()

