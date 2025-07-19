"""
Contains AttendanceTracker class to be used by JURASSIC PARK.
"""

from datetime import datetime
from datetime import timedelta

import pygsheets
import pandas as pd

import cv2

from google.auth.exceptions import TransportError


class AttendanceTracker:
    """
    Handles all attendance tasks (signing in/out, updating data) for an event.
    """
    def __init__(self, members):
        self.members = members
        self.forgot = {"in": [], "out": []}

        self.in_meeting = {name: False for name in members}
        self.history = {name: [] for name in members}

        self.last_scan = datetime.now()
        self.start_time = datetime.now()


    def __str__(self):
        return f"{self.in_meeting=}, {self.history=}"


    def sign_in(self, name):
        """
        Signs in team members. If they forget to sign out, and then sign back in,
        they get 5 minutes of credit.
        """
        # incorrect prior sign out
        if len(self.history[name]) > 0 and self.history[name][-1]["out"] is None:
            self.history[name][-1]["out"] = self.history[name][-1]["in"] + timedelta(minutes=5)

        # signing in
        self.in_meeting[name] = True
        self.history[name].append({"in": datetime.now(), "out": None})

        self.reset_last_scan()


    def sign_out(self, name):
        """
        Signs out team members. Has three special cases. Both incorrect
        cases award at most one hour of credit.

        1 - signed in and out correctly
        2 - signed in and out once, and forgot to sign in on meeting re-entry
        3 - never signed in and out at all
        """
        self.in_meeting[name] = False

        if len(self.history[name]) != 0:
            last_entry = self.history[name].pop(-1)

            if last_entry["out"] is None:
                # they have correctly signed in - case 1
                last_entry["out"] = datetime.now()
                self.history[name].append(last_entry)
            else:
                # they left, came back, and forgot to sign in - case 2
                self.forgot["in"].append(name)
                one_hr_ago = datetime.now() - timedelta(hours=1)
                new_entry = {"in": self.get_later_timestamp(self.start_time, one_hr_ago), \
                              "out": datetime.now()}
                self.history[name].append(new_entry)

        else:
            # never signed in at all - case 3
            self.forgot["in"].append(name)
            self.forgot["out"].append(name)

            one_hr_ago = datetime.now() - timedelta(hours=1)
            new_entry = {"in": self.get_later_timestamp(self.start_time, one_hr_ago), \
                         "out": datetime.now()}
            self.history[name].append(new_entry)

        self.reset_last_scan()


    def sign_all_out(self):
        """
        Called when JURASSIC PARK is shut down. Signs out all students who have
        forgotten to sign out.

        Should only be called after all still-present students have signed
        out individually.
        """
        self.end_time = datetime.now()

        for name in self.members:
            # if they're "in"" the meeting - sign them out
            if self.in_meeting[name] is True:
                self.in_meeting[name] = False
                self.forgot["out"].append(name)

                # give up to one hr of credit
                one_hr_later = self.history[name][-1]["in"] + timedelta(hours=1)
                self.history[name][-1]["out"] = self.get_earlier_timestamp(self.end_time, \
                                                                           one_hr_later)


    def push_meeting_data(self):
        """
        Called when JURASSIC PARK is shut down. Updates data in
        Google Sheet or to csv if there is no internet connection.
        """
        # authorization
        # TODO - replace with full filepath to your creds.json file
        gc = pygsheets.authorize(service_file="FILE PATH HERE")

        # create empty dataframe
        df = pd.DataFrame()

        # modify lists then update the dataframe
        names = []
        types = []
        dates = []
        arrivals = []
        departures = []
        net_time = []

        # import meeting data
        for name in self.history:
            for entry in self.history[name]:
                names.append(name)
                types.append(self.type)

                # assumes no meetings cross midnight
                dates.append(entry["in"].date())
                arrivals.append(entry["in"].time())
                departures.append(entry["out"].time())
                # str wrapper leaves just the time behind
                net_time.append(str(entry["out"] - entry["in"]))

        # put data into dataframe
        df["name"] = names
        df["meeting type"] = types
        df["date"] = dates
        df["in"] = arrivals
        df["out"] = departures
        df["net time"] = net_time

        # second dataframe for other sheet w forgetting data

        df2 = pd.DataFrame()
        df2["name"] = [name for name in self.forgot["in"]] + [name for name in self.forgot["out"]]
        df2["type"] = ["in" for _ in self.forgot["in"]] + ["out" for _ in self.forgot["out"]]
        df2["date"] = [self.end_time.date() for _ in df2["name"]]

        df3 = pd.DataFrame()
        df3["date"] = [self.end_time.date()]
        df3["type"] = [self.type]
        df3["duration"] = [str(self.end_time - self.start_time)]

        # open the google spreadsheet
        # try/except handles the no wifi case

        try:
            # TODO - replace with name of your google sheet
            sh = gc.open("YOUR SHEET NAME")

            # select the first sheet - where the data goes
            wks = sh[0]

            # inserts after that row - indexing starts at 1 not 0
            # always adds to the top of the sheet

            wks.insert_rows(1, number=len(names))
            wks.set_dataframe(df,(1,1))

            # import forgetting data
            wks2 = sh[1]
            wks2.insert_rows(1, number=len(df2))
            wks2.set_dataframe(df2, (1,1))

            wks3 = sh[2]
            wks3.insert_rows(1,1)
            wks3.set_dataframe(df3, (1,1))

        except TransportError:
            # export all data to csv files
            df.to_csv(f"{self.end_time.date()}_attendance.csv")
            df2.to_csv(f"{self.end_time.date()}_who_forgot.csv")
            df3.to_csv(f"{self.end_time.date()}_total_time.csv")


    def get_earlier_timestamp(self, time1, time2):
        """
        Get the earlier of two timestamps
        """
        if (time1-time2) < timedelta(hours=0):
            return time1

        return time2


    def get_later_timestamp(self, time1, time2):
        """
        Get the later of two timestamps
        """
        if (time1-time2) < timedelta(hours=0):
            return time2

        return time1


    def reset_last_scan(self):
        """
        Updates last scan time
        """
        self.last_scan = datetime.now()


    def valid_scan(self, name, bbox):
        """
        Criteria for valid scans:
        - Not an immediate duplicate scan
        - QR code data is someone on the team
        - A real QR code (bbox/contour conditions)
        """
        if (datetime.now() - self.last_scan) >= timedelta(seconds=5) and name in self.members \
            and bbox is not None  and bbox.shape[1] >= 4 and cv2.contourArea(bbox[0]) > 0.0:
            return True

        return False


    def humans_in_meeting(self):
        """
        Returns a list of individuals present in the meeting
        """
        return [name for name in self.in_meeting if self.in_meeting[name] is True]


    def set_type(self, meeting_type):
        """
        Used on setup screen for meeting type
        """
        self.type = meeting_type
