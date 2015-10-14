import json

import requests

import config


class DataStore:
    def __init__(self):
        self.data = None
        self.member_id_by_identification = dict()
        self.member_id_by_barcode = dict()
        self.members_by_id = dict()
        self.load_local_data()

    def load_api_data(self):
        data = {
            'key': config.API_KEY
        }
        req = requests.post(config.API_HOST + "/api/members", data=data)
        result = req.json()
        self.set_data(result)

    def write_data_to_file(self):
        with open('api_data', 'w') as f:
            json.dump(self.data, f)

    def load_local_data(self):
        try:
            with open('api_data', 'r') as f:
                self.set_data(json.load(f))
        except IOError:
            self.load_api_data()

    def set_data(self, data):
        self.data = data
        self.write_data_to_file()
        self.member_id_by_identification = dict()
        self.members_by_id = dict()
        self.member_id_by_barcode = dict()
        for x in data:
            # generate dictionary of identification by barcode
            if 'barcode' in x:
                self.member_id_by_barcode[x['barcode'][:12]] = x['id']
            # generate dictionary of member by member id
            self.members_by_id[x['id']] = x
            # generate dictionary of academic by identification
            self.member_id_by_identification[x['identification']] = x['id']

    def find_member_by_barcode(self, barcode):
        if barcode[:12] in self.member_id_by_barcode:
            return self.find_member(self.member_id_by_barcode[barcode[:12]])
        return None

    def find_member_by_identification(self, identification):
        if identification in self.member_id_by_identification:
            return self.find_member(self.member_id_by_identification[identification])
        return None

    def find_member(self, member_id):
        if member_id in self.members_by_id:
            return self.members_by_id[member_id]
        return None
