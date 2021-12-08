import time
import json
from os.path import exists

time_stamp = time.time()

file_path = ""

file_name = "jsontest.json"


def save_mgmt(new_data):
	if not exists(file_path):
		with open(file_name, 'w') as file:
			time_stamp = time.time()
			ts_id = "TS001"
			json.dump((ts_id, time_stamp), file)

	

new = {"lol": "what"}
save_mgmt(new)
