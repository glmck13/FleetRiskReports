#!/usr/bin/env python3

import sys
import os
import json
import requests
import datetime
from urllib.parse import quote

DEFAULT_INTERVAL = 7

Username = os.getenv("API_USER", "")
Password = os.getenv("API_PASS", "")
if len(sys.argv) > 1:
	Interval = sys.argv[1]
else:
	Interval = DEFAULT_INTERVAL

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {"Content-Type" : "application/x-www-form-urlencoded"}
proxies = None
#proxies = {"https" : ""}

cmd = json.loads('{"method":"Authenticate","params":{"database":"","userName":"{}","password":"{}"}}')
cmd["params"]["userName"] = Username
cmd["params"]["password"] = Password

data = 'JSON-RPC=' + quote(json.dumps(cmd))
rsp = requests.post("https://my.geotab.com/apiv1/", proxies=proxies, headers=headers, data=data, verify=False)
try:
	creds = rsp.json()["result"]["credentials"]
	path = rsp.json()["result"]["path"]
except:
	print('Login failed', file=sys.stderr)
	exit()

cmd = json.loads('''
{"method":"ExecuteMultiCall","params":{"calls":[{"method":"GetReportData","params":{"argument":{"runGroupLevel":-1,"isNoDrivingActivityHidden":true,"fromUtc":"","toUtc":"","entityType":"Driver","reportArgumentType":"RiskManagement","groups":[{"id":"GroupCompanyId"}],"reportSubGroup":"None","rules":[{"id":"aN_xVgXdWlU2v2fKEQBgAOQ"},{"id":"RulePostedSpeedingId"},{"id":"abEavtAYWr0aDFoY-D22QRw"},{"id":"RuleJackrabbitStartsId"},{"id":"RuleHarshBrakingId"},{"id":"RuleHarshCorneringId"},{"id":"RuleSeatbeltId"},{"id":"RuleUnauthorizedDeviceRemovalId"}]}}},{"method":"GetReportData","params":{"argument":{"runGroupLevel":-1,"isNoDrivingActivityHidden":true,"fromUtc":"","toUtc":"","entityType":"Device","reportArgumentType":"RiskManagement","groups":[{"id":"GroupCompanyId"}],"reportSubGroup":"None","rules":[{"id":"alD7e1qFzzUWqR3qQOtt6mw"}]}}}]}}
''')
now = datetime.datetime.utcnow()
then = now + datetime.timedelta(days=-int(Interval))
cmd["params"]["credentials"] = creds
for n in range(2):
	cmd["params"]["calls"][n]["params"]["argument"]["fromUtc"] = then.isoformat() + 'Z'
	cmd["params"]["calls"][n]["params"]["argument"]["toUtc"] = now.isoformat() + 'Z'

#print(cmd, file=sys.stderr)

data = 'JSON-RPC=' + quote(json.dumps(cmd))
rsp = requests.post("https://{}/apiv1/".format(path), proxies=proxies, headers=headers, data=data, verify=False)
rpt = rsp.json()

print("<html>")

print("<h1>Reporting Period</h1>")
print("{} days: From {}; To {}\n".format(Interval, then.strftime("%a, %b-%d-%Y"), now.strftime("%a, %b-%d-%Y")))

print("<h1>Driver Exceptions</h1>")
print("<table border=1>")
print("<tr>", end='')
for s in ("Driver", "Speeding", "Harsh Driving", "No Seatbelt"):
	print("<th>{}</th>".format(s), end='')
print("</tr>")
list = []
dict = {}
for row in rpt["result"][0]:
	tally = 0
	violations = []
	for key in (*["exceptionRule{}Count".format(n+1) for n in range(6)], "seatbeltViolation"):
		n = row[key]
		tally += n
		violations.append(str(n))
	if tally > 0:
		speeding = []
		for n in (0, 1, 2):
			speeding.append(violations[n])
		harsh = []
		for n in (3, 4, 5):
			harsh.append(violations[n])
		nobelt = violations[6]
		key = "{}, {}".format(row["item"]["lastName"], row["item"]["firstName"])
		list.append(key)
		dict[key] = {"data" : "{}|{}|{}|{}".format(key, '+'.join(speeding), '+'.join(harsh), nobelt), "info" : row["item"]["name"]}

list.sort()
for key in list:
	print("<tr>", end='')
	for s in dict[key]["data"].split('|'):
		if not s.replace('0','').replace('+', ''):
			s = "&nbsp;"
		print("<td><center>{}</center></td>".format(s), end='')
	print("</tr><!-- DRIVER {} -->".format(dict[key]["info"]))
print("</table>")
print('''
<i>
<br>Speeding = >75MPH + >15MPH over posted limit + >15MPH over posted limit for >20secs
<br>Harsh Driving = Rapid acceleration + Hard braking + Aggressive turn 
</i>
''')

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
	violations = []
	for key in (*["exceptionRule{}Count".format(n+1) for n in range(1)],):
		n = row[key]
		tally += n
		violations.append(str(n))
	if tally > 0:
		key = row["item"]["name"]
		list.append(key)
		dict[key] = {"data" : "{} ({})|{}".format(key, row["item"]["licensePlate"], ' '.join(violations)), "info" : ""}
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
