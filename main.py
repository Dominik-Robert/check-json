import yaml
import requests
import re
import pyjq


class check_json:
    data = {}
    status = {}

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
                    print("STATUS CODE Failed")
            if 'regex' in validation:
                if not re.search(
                    validation['regex'],
                    self.status[validationName]['content'].decode('utf-8')
                ):
                    print("NO MATCH")
            if 'jq' in validation:
                print('JQ enabled')
                x = pyjq.all(
                    validation['jq'],
                    self.status[validationName]['content']
                )
                print(x)


if __name__ == "__main__":
    icingaCheck = check_json()

    icingaCheck.makeReqests()
    icingaCheck.check()
