from datetime import datetime, time, timedelta
from math import floor,ceil

vals = """
scheduleHere
"""
#Fr
DAYS_OF_WEEK = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
DOW_ABBREVIATIONS = ["Lun", "Ma", "Mer", "J", "V"]
HOURS_PER_DAY = 16 #from 7 am to 11pm is the max
START_TIME = 9 #7am
END_TIME = 19 #11pm
REF_DAY = datetime.fromisoformat("2021-04-18 00:00:00")
C_CHAR = '|' #column separator
R_CHAR = '*' #row separator
COURSE_SEPARATOR_A = "Supprimer"
COURSE_SEPARATOR_B = "Cours\n"
HOUR_SEPARATOR = ""


class Course:
    class Slot:
        def __init(self):
            self.day = 0
            self.start_str = ""
            self.end_str = ""
            # self.professor = ""
            # self.place = place
        def computeDateTime(self):
            self.datetime = REF_DAY +  timedelta(days=int(self.day))
            hours = int(self.start_str[0:2])
            min = int(self.start_str[3:])
            self.start = self.datetime + \
                         timedelta(hours=hours) + timedelta(minutes=min)

            hours = int(self.end_str[0:2])
            min = int(self.end_str[3:])
            self.end = self.datetime + \
                       timedelta(hours=hours) + timedelta(minutes=min)

            self.chunks = []
            self.name = ""
            for i in range(floor((int((self.end-self.start).total_seconds()/60))/30)):
                self.chunks.append(self.start + timedelta(minutes=(30*i)))


        def dateTime(self):
            self.computeDateTime()
            return [self.start, self.end]

        def in_interval(self, start: datetime) -> bool:
            for chunk in self.chunks:
                if chunk == start or (chunk >= (start-timedelta(minutes=30)) and chunk <= (start)):
                    return True
            return False

    def __init__(self, name: str):
        self.name = name  # example: 'Intro. Programming '
        self.slots = []  # for example, if there is a link lab to it

    def addSlot(self, day, start:str, end:str):
        new_slot = self.Slot()
        new_slot.day = day
        new_slot.start_str = start
        new_slot.end_str = end
        new_slot.dateTime()
        new_slot.name = str(self)
        self.slots.append(new_slot)

    def __eq__(self, other):
        return other.name == self.name

    def __str__(self): #outil
        stringify = self.name
        # if self.slots:
        #     stringify += ":\n"
        #     for slot in self.slots:
        #         stringify += "\t" + str(slot.day) + ": " + slot.start_str +"-" + slot.end_str
        return stringify




class Schedule:
    class Day:
        # only from monday to friday
        def __init__(self, dayOfWeek: int, startTime: int, endTime: int):
            self.day = REF_DAY + timedelta(days=dayOfWeek)  # day of week at midnight
            self.day_abbr = DOW_ABBREVIATIONS[dayOfWeek]
            self.startTime = self.day + timedelta(hours=startTime)
            self.endTime = self.day + timedelta(hours=endTime)
            self.classList = []  # contains a list of the classes on that day

        def __eq__(self, abbreviation):
            return self.day_abbr == DAYS_OF_WEEK[DOW_ABBREVIATIONS.index(abbreviation)]

        def dateTime(self):  # return that day at midnight
            return self.day

    def __init__(self, rawInput):
        self.days = []
        self.maxAmountClassesInDay = 0
        self.scheduleArray = [] #2D string array where rows = hours and columns = days
        self.schedule = {}
        self.initDays()
        self.parseInput(rawInput)

    def initDays(self):
        for i in range(len(DAYS_OF_WEEK)):
            self.days.append(self.Day(i, START_TIME, END_TIME))

    def createSchedule(self):
        for day_of_week in self.days:
            self.schedule[day_of_week.day] = {}
            curr_time = day_of_week.startTime
            for half_hour in range((END_TIME-START_TIME)*2):
                self.schedule[day_of_week.day][curr_time] = []
                next_time = curr_time + timedelta(minutes=30)
                self.schedule[day_of_week.day][next_time] = []
                curr_time = next_time

        for course in self.classes:
            for slot in course.slots:
                for timeslot in self.schedule[slot.datetime].keys():
                    if slot.in_interval(timeslot):
                        self.schedule[slot.datetime][timeslot].append(course)
                        if len(self.schedule[slot.datetime][timeslot]) > self.maxAmountClassesInDay:
                            self.maxAmountClassesInDay = len(self.schedule[slot.datetime][timeslot])
        day_idx = 0
        #convert the dictionary to 2D array
        for day in self.schedule.keys():
            self.scheduleArray.append([])
            for half_hour in range(len(self.schedule[day])):
                self.scheduleArray[day_idx].append([])
            day_idx += 1

        day_idx = 0
        for day in self.schedule.keys():
            for half_hour in self.schedule[day].keys():
                distance_from_start_day = int((half_hour.hour*60 + half_hour.minute - START_TIME*60)/30)
                if self.schedule[day][half_hour]:
                    for course in range(len(self.schedule[day][half_hour])):
                        self.scheduleArray[day_idx][distance_from_start_day].append(
                            str(self.schedule[day][half_hour][course]))
            day_idx += 1




    def parseInput(self, input_):
        raw = input_.replace(COURSE_SEPARATOR_A, "#")
        raw = raw.replace(COURSE_SEPARATOR_B, "#")
        raw = raw.replace("\n", " ")
        raw = raw.replace("\t", " ")
        raw = raw.split("#")

        classes_str = []

        for line in raw:
            #SUPPRIMER -> first row, not counted
            if not len(line) < 3 and not "SUPPRIMER" in line:
                classes_str.append(line)

        self.assign_dates_to_classes(classes_str)
        self.createSchedule()
        print("d")


    def assign_dates_to_classes(self, arr):
        self.classes = []
        for line in arr:
            curr_word = None
            split_line = line.split(" ")
            curr_subject_name = split_line[0:2]
            if "-" in curr_subject_name[1]:  # remove useless data
                curr_subject_name = curr_subject_name[0] + curr_subject_name[1][0:curr_subject_name[1].index("-")]
            curr_course = Course(curr_subject_name)
            if not curr_course in self.classes:  # don't add the same class twice
                self.classes.append(curr_course)

            for day in DOW_ABBREVIATIONS:
                if day in split_line:
                    idx = split_line.index(day)
                    day_week = DOW_ABBREVIATIONS.index(day)
                    start = split_line[idx + 1]
                    end = split_line[idx + 3]
                    self.classes[self.classes.index(curr_course)].addSlot(day_week, start, end)


            # for course in self.classes:
            #     print(course)

    def prettyPrint(self):
        col_width = 20

        schedule_print = []
        numberOfLines = (3 * (END_TIME - START_TIME)) + 1
        numberChars = ((col_width - 1) * len(DAYS_OF_WEEK)) + 1
        day_line = ""
        lineToAdd = ""
        for day in DAYS_OF_WEEK:
            day_line += " " * ((col_width + 2 - len(day)) // 2) + day + " " * ((col_width + 1 - len(day)) // 2)
        for line in range(numberOfLines):
            schedule_print.append("")
            if (line % 3) == 0:
                for col in range(len(DAYS_OF_WEEK)):
                    for r_char in range(col_width + 1):
                        schedule_print[line] += R_CHAR
            else:
                for col in range(len(DAYS_OF_WEEK)):
                    if ((line - 1) % 3) == 0 and (line-1 < len(self.scheduleArray[col])):
                        lineToAdd = ""
                        for item in range(len(self.scheduleArray[col][(line - 1)])):
                            lineToAdd += self.scheduleArray[col][(line - 1)][item] + " "
                        for c_char in range(max(col_width+1, len(" " * ((col_width + 2 - len(lineToAdd)) // 2) + \
                                                         lineToAdd + " " * ((col_width + 1 - len(lineToAdd)) // 2)))):
                            if (c_char % (col_width)) == 0:
                                schedule_print[line] += C_CHAR
                        schedule_print[line] += " " * ((col_width + 2 - len(lineToAdd)) // 2) + lineToAdd + \
                                                " " * ((col_width + 1 - len(lineToAdd)) // 2)
                    else:
                        for c_char in range(max(col_width+1, len(" " * ((col_width + 2 - len(lineToAdd)) // 2) + \
                                                         lineToAdd + " " * ((col_width + 1 - len(lineToAdd)) // 2)))):
                            if (c_char % (col_width)) == 0:
                                schedule_print[line] += C_CHAR
                            else:
                                schedule_print[line] += " "

        schedule_print.insert(0, day_line)
        for line in schedule_print:
            print(line)


agenda = Schedule(vals)
agenda.prettyPrint()
listf = ["IFT1025", "MAT1000", "IFT1015"]
bla = 5
ne = 9
sep = '*'
sip = '|'
