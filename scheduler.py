from datetime import datetime, timedelta
from math import floor

# Fr

# IF one wants the schedule to start or end at an earlier or later hour:
HOURS_PER_DAY = 16  # from 7 am to 11pm is the max to make it look orderly
START_TIME = 8  # 7am
END_TIME = 19  # 11pm


DAYS_OF_WEEK = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
DOW_ABBREVIATIONS = ["Lun", "Ma", "Mer", "J", "V"]
REF_DAY = datetime.fromisoformat("2021-04-18 00:00:00")
C_CHAR = '|'  # column separator
R_CHAR = '*'  # row separator
COURSE_SEPARATOR_A = "Supprimer"
COURSE_SEPARATOR_B = "Cours\n"
HOUR_SEPARATOR = ""


class Course:
    class Slot:
        def __init(self):
            self.day = 0
            self.start_str = ""
            self.end_str = ""
            self.datetime = None
            self.name = ""
            self.start = None
            self.end = None
            self.chunks = []
            self.datetime = None

        def compute_datetime(self):
            self.datetime = REF_DAY + timedelta(days=int(self.day))
            hours = int(self.start_str[0:2])
            min_val = int(self.start_str[3:])
            self.start = self.datetime + timedelta(hours=hours) + timedelta(minutes=min_val)

            hours = int(self.end_str[0:2])
            min_val = int(self.end_str[3:])
            self.end = self.datetime + timedelta(hours=hours) + timedelta(minutes=min_val)

            self.chunks = []
            self.name = ""
            for i in range(floor((int((self.end - self.start).total_seconds() / 60)) / 30)):
                self.chunks.append(self.start + timedelta(minutes=(30 * i)))

        def date_time(self):
            self.compute_datetime()
            return [self.start, self.end]

        def in_interval(self, start: datetime) -> bool:
            for chunk in self.chunks:
                if chunk == start or (start - timedelta(minutes=30) <= chunk <= start):
                    return True
            return False

        def __eq__(self, other):
            return self.start == other.start and self.end == other.end

    def __init__(self, name: str):
        self.name = name  # example: 'Intro. Programming '
        self.slots = []  # for example, if there is a link lab to it

    def add_slot(self, day, start: str, end: str):
        new_slot = self.Slot()
        new_slot.day = day
        new_slot.start_str = start
        new_slot.end_str = end
        new_slot.date_time()
        new_slot.name = str(self)
        if new_slot not in self.slots:
            self.slots.append(new_slot)

    def __eq__(self, other):
        return other.name == self.name

    def __str__(self):  # outil
        stringify = self.name
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

        def date_time(self):  # return that day at midnight
            return self.day

    def __init__(self, rawInput):
        self.days = []
        self.maxColLength = 0
        self.scheduleArray = []  # 2D string array where rows = hours and columns = days
        self.schedule = {}
        self.init_days()
        self.IsSimplifiedCart = False
        self.parse_input(rawInput)

    def init_days(self):
        for i in range(len(DAYS_OF_WEEK)):
            self.days.append(self.Day(i, START_TIME, END_TIME))

    def create_schedule(self):
        for day_of_week in self.days:
            self.schedule[day_of_week.day] = {}
            curr_time = day_of_week.startTime
            for half_hour in range((END_TIME - START_TIME) * 2):
                self.schedule[day_of_week.day][curr_time] = []
                next_time = curr_time + timedelta(minutes=30)
                self.schedule[day_of_week.day][next_time] = []
                curr_time = next_time

        for course in self.classes:
            for slot in course.slots:
                for timeslot in self.schedule[slot.datetime].keys():
                    if slot.in_interval(timeslot):
                        self.schedule[slot.datetime][timeslot].append(course)

                        if len(self.schedule[slot.datetime][timeslot]) > self.maxColLength:
                            self.maxColLength = len(self.schedule[slot.datetime][timeslot])
        day_idx = 0
        # convert the dictionary to 2D array
        for day in self.schedule.keys():
            self.scheduleArray.append([])
            for half_hour in range(len(self.schedule[day])):
                self.scheduleArray[day_idx].append([])
            day_idx += 1

        day_idx = 0
        for day in self.schedule.keys():
            for half_hour in self.schedule[day].keys():
                distance_from_start_day = int((half_hour.hour * 60 + half_hour.minute - START_TIME * 60) / 30)
                if self.schedule[day][half_hour]:
                    for course in range(len(self.schedule[day][half_hour])):
                        self.scheduleArray[day_idx][distance_from_start_day].append(
                            str(self.schedule[day][half_hour][course]))
            day_idx += 1

    def parse_input(self, input_):
        classes_str = []

        if COURSE_SEPARATOR_A not in input_:
            raw = input_.replace("\n", " ")
            raw = raw.replace("\t", " ")
            self.IsSimplifiedCart = True
            raw = raw.replace("Panier", "")
            raw = raw.split(" ")

            self.organize_simplified_schedule(raw)

        else:
            raw = input_.replace(COURSE_SEPARATOR_A, "#")
            raw = raw.replace(COURSE_SEPARATOR_B, "#")
            raw = raw.replace("\n", " ")
            raw = raw.replace("\t", " ")
            raw = raw.split("#")


            for line in raw:
                # SUPPRIMER -> first row, not counted
                if not len(line) < 3 and "SUPPRIMER" not in line:
                    classes_str.append(line)

            self.organize_table_schedule(classes_str)


        self.create_schedule()

    def organize_table_schedule(self, arr):
        self.classes = []
        for line in arr:
            curr_word = None
            split_line = line.split(" ")
            curr_subject_name = split_line[0:2]
            if "-" in curr_subject_name[1]:  # remove useless data
                curr_subject_name = curr_subject_name[0] + curr_subject_name[1][0:curr_subject_name[1].index("-")]
            curr_course = Course(curr_subject_name)
            if curr_course not in self.classes:  # don't add the same class twice
                self.classes.append(curr_course)

            for day in DOW_ABBREVIATIONS:
                if day in split_line:
                    idx = split_line.index(day)
                    day_week = DOW_ABBREVIATIONS.index(day)
                    start = split_line[idx + 1]
                    end = split_line[idx + 3]
                    self.classes[self.classes.index(curr_course)].add_slot(day_week, start, end)


    def organize_simplified_schedule(self, arr):
        self.classes = []
        splitted_lines = []
        watching_idx = []
        checking_for_class = True
        reading_date = False
        possible_class_name = ""

        #check if int or not
        def is_int(s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        for word_idx in range(len(arr)):
            word = arr[word_idx]
            if word in DOW_ABBREVIATIONS:
                reading_date = True
            elif checking_for_class and not reading_date:
                if possible_class_name:
                    if is_int(word):
                        if len(watching_idx) == 1:
                            splitted_lines.append(arr[watching_idx[0]:word_idx-2])
                        checking_for_class = False
                        possible_class_name += word
                        possible_class_name = ""
                        watching_idx = [word_idx-1]
                    else:
                        possible_class_name = ""
                else:
                    possible_class_name += word
            elif reading_date:
                if (":") in word and "-" in arr[word_idx-1]:
                    reading_date = False
                    checking_for_class = True
        splitted_lines.append(arr[watching_idx[0]:len(arr)])

        for line in splitted_lines:
            curr_word = None
            curr_subject_name = line[0] + line[1]
            if "-" in curr_subject_name:  # remove useless data
                curr_subject_name = curr_subject_name[0:curr_subject_name.index("-")]
            curr_course = Course(curr_subject_name)
            if curr_course not in self.classes:  # don't add the same class twice
                self.classes.append(curr_course)

            for day in DOW_ABBREVIATIONS:
                # if day in line:
                while day in line:
                    idx = line.index(day)
                    day_week = DOW_ABBREVIATIONS.index(day)
                    start = line[idx + 1]
                    end = line[idx + 3]
                    self.classes[self.classes.index(curr_course)].add_slot(day_week, start, end)
                    line.remove(day)

    def pretty_print(self):
        col_width = max((7 + 2) * self.maxColLength,(7 + 2) * 2)  # 7 being the length of the class name
        # todo: don't hardcode the length of the course name .
        heures = list(list(self.schedule.values())[0].keys())
        schedule_print = []
        numberOfLines = ((3 * (END_TIME - START_TIME))) * 2 + 1
        day_line = ""
        header = DAYS_OF_WEEK.copy()
        header.insert(0, "Heure/Jour")
        for day in header:
            day_line += " " * ((col_width + 2 - len(day)) // 2) + day + " " * ((col_width + 1 - len(day)) // 2)

        for line in range(numberOfLines):

            schedule_print.append("")
            if (line % 3) == 0:
                for col in range(len(DAYS_OF_WEEK) + 1):
                    for r_char in range(col_width + 1):
                        schedule_print[line] += R_CHAR  # ROW SEPARATORS
            else:
                for col in range(len(DAYS_OF_WEEK) + 1):
                    lineToAdd = ""
                    for item in range(len(self.scheduleArray[col - 1][(line // 3)])):
                        lineToAdd += self.scheduleArray[col - 1][(line // 3)][item] + " "
                    if line % 2:
                        lineToAdd = ""
                    elif col < 1:
                        lineToAdd = str(heures[(line // 3)].hour) + ":" + str(heures[(line // 3)].minute)
                        if heures[(line // 3)].minute == 0:
                            lineToAdd += "0"
                        lineToAdd = (" " * (3 - len(str(heures[(line // 3)].hour)))) + lineToAdd

                    schedule_print[line] += C_CHAR + " " * (((col_width + 2 - len(lineToAdd)) // 2) - 1) + lineToAdd + \
                                            " " * (((col_width + 2 - len(lineToAdd)) // 2) - 2) + C_CHAR

        schedule_print.insert(0, day_line)
        print("\t APERÇU DU PANIER: ")
        for line in schedule_print:
            print(line)


if __name__ == "__main__":
    print("Colle la selection du ici. Voir le README pour savoir quoi selectionner. \n \
          Après l'avoir collé, appuie sur \"enter\"/\"retour\" 3-4 fois pour générer l'horaire. ")
    entered_schedule = ""
    noEmpties = 0
    while True:
        temp = ""
        try:
            temp = input()
        except EOFError:
            break
        if temp == "":
            noEmpties += 1
        else:
            noEmpties = 0
        if noEmpties > 1:
            break
        entered_schedule += temp + "\n"

    agenda = Schedule(entered_schedule)
    agenda.pretty_print()