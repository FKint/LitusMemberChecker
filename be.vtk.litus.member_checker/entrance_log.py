import datetime
import json
import time


class EntranceLog:
    def __init__(self):
        self.log = []
        self.load_local_data()

    def load_local_data(self):
        try:
            with open('entrance_log', 'r') as f:
                self.log = json.load(f)
        except IOError:
            self.log = []

    def enter_member(self, member):
        self.__enter({'member_id': member['id'], 'identification': member['identification']})

    def enter_non_member_by_barcode(self, barcode):
        self.__enter({'barcode': barcode})

    def enter_non_member_by_identification(self, identification):
        self.__enter({'identification': identification})

    def enter_member_without_card(self, name):
        self.__enter({'name': name, 'nocard': True})

    def write_log(self):
        with open('entrance_log', 'w') as f:
            json.dump(self.log, f)

    def __enter(self, data):
        self.log.append({
            'timestamp': str(datetime.datetime.now()),
            'data': data
        })
        self.write_log()

    def enter_without_card(self):
        self.__enter({})

    def is_member_inside(self, member):
        for l in self.log:
            print(l)
            if 'member_id' in l['data']:
                if l['data']['member_id'] == member['id']:
                    return True, l['timestamp']
        return False, None

    def inside_count(self):
        return len(self.log)

    def members_inside_count(self):
        count = 0
        for x in self.log:
            if 'member_id' in x['data']:
                count += 1
        return count

    def clear_log(self):
        try:
            with open('entrance_log', 'r') as f:
                with open('entrance_log_' + str(time.time()), 'w') as f2:
                    json.dump(json.load(f), f2)
            self.log = []
            self.write_log()
        except IOError:
            print("ERROR")

    def get_latest_logs(self, num):
        return self.log[-num:]
