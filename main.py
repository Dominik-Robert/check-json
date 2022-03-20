import yaml
import json
import requests
import re
import pyjq
import sys
from jinja2 import Template


class check_json:
    data = {}
    status = {}
    icingaStatus = {}
    icingaWording = "OK"
    icingaExitCode = 0

    def __init__(self):
        with open('test.yaml', 'r') as file:
            self.data = yaml.safe_load(file)

    def makeReqests(self):
        for verb, verbValue in self.data['requests'].items():
            for method, methodDetail in verbValue.items():
                for host, hostData in methodDetail.items():
                    for hostDetail in hostData:
                        connectURL = method + '://' + host
                        data = ''

                        if 'port' in hostDetail:
                            connectURL += ':' + str(hostDetail['port'])
                        if 'path' in hostDetail:
                            connectURL += hostDetail['path']
                        if 'data' in hostDetail:
                            data = hostDetail['data']
                        r = {}

                        if verb == "get":
                            r = requests.get(connectURL)
                        elif verb == "post":
                            r = requests.post(
                                connectURL, data=data
                            )

                        self.status[hostDetail['name']] = {
                            'status_code': r.status_code,
                            'content': r.content,
                        }

    def check(self):
        for validationName, validation in self.data['validate'].items():
            if 'status_code' in validation:
                if validation['status_code'] != self.status[validationName]['status_code']:
                    self.icingaStatus[validationName] = {}
                    self.icingaStatus[validationName]['status_code'] = self.status[validationName]['status_code']
                    if self.icingaExitCode < validation['status']:
                        self.icingaExitCode = validation['status']
                        self.icingaWording = self.checkWording(
                            validation['status'])
            if 'regex' in validation:
                if not re.search(
                    validation['regex'],
                    self.status[validationName]['content'].decode('utf-8')
                ):
                    self.icingaStatus[validationName] = self.status[validationName][
                        'regex'] = self.data['general']['regex']['noMatchText']
            if 'jq' in validation:
                jsonData = json.loads(self.status[validationName]['content'])
                x = pyjq.all(
                    validation['jq'],
                    jsonData,
                )
                if True not in x:
                    self.icingaStatus[validationName] = self.status[validationName]['regex'] = self.data['general']['jq']['noMatchText']

    def makeOutput(self):
        if self.data['icinga']['selfGenerated'] == False:
            tmpl = Template(self.data['icinga']['output'])
            print(tmpl.render(
                statusWord=self.icingaWording,
                icingaStatus=self.icingaStatus,
                status=self.status,
                data=self.data
            ))

    def checkWording(self, code):
        if code == 0:
            return "OK"
        if code == 1:
            return "WARNING"
        if code == 2:
            return "CRITICAL"


if __name__ == "__main__":
    icingaCheck = check_json()

    icingaCheck.makeReqests()
    icingaCheck.check()
    icingaCheck.makeOutput()

    sys.exit(icingaCheck.icingaExitCode)
