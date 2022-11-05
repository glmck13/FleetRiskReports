#!/usr/bin/env python3

import sys
import os
import json
import requests
import datetime
from urllib.parse import quote
from pprint import pprint

DEFAULT_INTERVAL = 7

Username = os.getenv("API_USER", "")
Password = os.getenv("API_PASS", "")
if len(sys.argv) > 1:
	Interval = sys.argv[1]
else:
	Interval = DEFAULT_INTERVAL

try:
	Rules = {}
	Subtypes = {}
	with open(os.getenv("RULES", "")) as f:
		for line in f.read().split('\n'):
			if not line:
				continue
			line = line.split(',')
			Rules[line[0]] = {"type":line[1], "subtype":line[2], "name":line[3]}
			Subtypes[line[2]] = line[1]
except:
	print('Cannot open/read rules file', file=sys.stderr)
	exit()

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {"Content-Type" : "application/x-www-form-urlencoded"}
proxies = None
#proxies = {"https" : ""}

cmd = {"method":"Authenticate","params":{"database":"gwfleet","userName":"","password":""}}
cmd["params"]["userName"] = Username
cmd["params"]["password"] = Password

data = 'JSON-RPC=' + quote(json.dumps(cmd))
rsp = requests.post("https://gov.geotab.com/apiv1/", proxies=proxies, headers=headers, data=data, verify=False)
try:
	creds = rsp.json()["result"]["credentials"]
	path = rsp.json()["result"]["path"]
except:
	print('Login failed', file=sys.stderr)
	exit()

cmd = {"method":"ExecuteMultiCall", "params":{"calls":[{"method":"GetReportData","params":{"argument":{"runGroupLevel":-1,"isNoDrivingActivityHidden":True,"fromUtc":"","toUtc":"","entityType":"Driver","reportArgumentType":"RiskManagement","groups":[{"id":"GroupCompanyId"}],"reportSubGroup":"None","rules":[]}}},{"method":"GetReportData","params":{"argument":{"runGroupLevel":-1,"isNoDrivingActivityHidden":True,"fromUtc":"","toUtc":"","entityType":"Device","reportArgumentType":"RiskManagement","groups":[{"id":"GroupCompanyId"}],"reportSubGroup":"None","rules":[]}}}]}}

now = datetime.datetime.utcnow()
then = now + datetime.timedelta(days=-int(Interval))
cmd["params"]["credentials"] = creds
for n in range(2):
	cmd["params"]["calls"][n]["params"]["argument"]["fromUtc"] = then.isoformat() + 'Z'
	cmd["params"]["calls"][n]["params"]["argument"]["toUtc"] = now.isoformat() + 'Z'
	t = cmd["params"]["calls"][n]["params"]["argument"]["entityType"]
	for k, v in Rules.items():
		if v["type"] == t:
			cmd["params"]["calls"][n]["params"]["argument"]["rules"].append({"id" : k})

#pprint(cmd, stream=sys.stderr)

data = 'JSON-RPC=' + quote(json.dumps(cmd))
rsp = requests.post("https://{}/apiv1/".format(path), proxies=proxies, headers=headers, data=data, verify=False)
rpt = rsp.json()

print("<html>")

print("<h1>Reporting Period</h1>")
print("{} days: From {}; To {}\n".format(Interval, then.strftime("%a, %b-%d-%Y"), now.strftime("%a, %b-%d-%Y")))

print("<h1>Driver Exceptions</h1>")
print("<table border=1>")
print("<tr>", end='')
print("<th>Driver</th>", end='')
for s, t in Subtypes.items():
	if t == "Driver":
		print("<th>{}</th>".format(s), end='')
print("</tr>")
list = []
dict = {}
#pprint(rpt, stream=sys.stderr)
for row in rpt["result"][0]:
	tally = 0
	for x in row["exceptionSummaries"]:
		tally += x["eventCount"]
	if tally > 0:
		tally = {}
		for s in Subtypes.keys():
			tally[s] = []
		for x in row["exceptionSummaries"]:
			tally[Rules[x["exceptionRule"]["id"]]["subtype"]].append(str(x["eventCount"]))
		key = "{}, {}".format(row["item"]["lastName"], row["item"]["firstName"])
		list.append(key)
		dict[key] = {"data" : key, "info" : row["item"]["name"]}
		for s, t in Subtypes.items():
			if t == "Driver":
				dict[key]["data"] += '|' + '+'.join(tally[s])

list.sort()
for key in list:
	print("<tr>", end='')
	for s in dict[key]["data"].split('|'):
		if not s.replace('0','').replace('+', ''):
			s = "&nbsp;"
		print("<td><center>{}</center></td>".format(s), end='')
	print("</tr><!-- DRIVER {} -->".format(dict[key]["info"]))
print("</table>")
print("<br><i>")
for s, t in Subtypes.items():
	if t == "Driver":
		print("<b>{}</b>:".format(s))
		print("<blockquote>")
		for k, v in Rules.items():
			if v["subtype"] == s:
				print("{}<br>".format(v["name"]))
		print("</blockquote>")
print("</i>")

print("<h1>Vehicle Exceptions</h1>")
print("<table border=1>")
print("<tr>", end='')
for s in ("Vehicle", "No Fob"):
	print("<th>{}</th>".format(s), end='')
print("</tr>")
list = []
dict = {}
for row in rpt["result"][1]:
	tally = 0
	for x in row["exceptionSummaries"]:
		tally += x["eventCount"]
	if tally > 0:
		tally = {}
		for s in Subtypes.keys():
			tally[s] = []
		for x in row["exceptionSummaries"]:
			tally[Rules[x["exceptionRule"]["id"]]["subtype"]].append(str(x["eventCount"]))
		key = row["item"]["name"]
		list.append(key)
		dict[key] = {"data" : "{} ({})|{}".format(key, row["item"]["licensePlate"], ' '.join(tally["Fob"])), "info" : ""}

list.sort()
for key in list:
	print("<tr>", end='')
	for s in dict[key]["data"].split('|'):
		if not s.replace('0','').replace('+', ''):
			s = "&nbsp;"
		print("<td><center>{}</center></td>".format(s), end='')
	print("</tr><!-- VEHICLE: {} -->".format(dict[key]["info"]))
print("</table>")

print("</html>")
