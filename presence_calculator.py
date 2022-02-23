import appdaemon.plugins.hass.hassapi as hass

import csv 
from datetime import datetime, time

import requests


URL = r'https://glb-diagovtnz-prd-frd.azurefd.net/ccms-ptl-inz/v1/presencecalculator'

IDS = '/config/appdaemon/apps/presence_calculator/customer.csv'


class Presence_calculator(hass.Hass):

    def initialize(self):

        self.log(f'{__name__} is now live.')

        try:
            self.run_daily(
                self.stream,
                time(10, 0, 0),
                #time(16, 0, 0),
                #time(9, 0, 0),
            )

        except Exception as e:
            self.send_email_to(
                message=e,
                title=f'{__name__} Error'
            )

    @property
    def ids(self):

        # Yield a row in customer.csv as dict.
        with open(IDS, 'r') as f:

            reader = csv.DictReader(f)

            for x in reader:

                y = x
                del y['customer_id']

                yield y

    def response(self, id_):

        '''Returns a requests response.
        '''

        # client-ref needs to be Passport number.
        headers = {
            'client-ref':f'{id_["travelDocumentSerial"]}',
            'content-type':'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }

        with requests.Session() as s:
        
            r = s.post(
                URL,
                headers=headers,
                json=id_
            )
        
            return r
        
    def send_email_to(self, title='rickhehe', message=''):
        
        # This is an existing service defined in **configuration.ymal**.
        self.call_service(
            'notify/send_email_to_rick_notifier',
            message=message,
            title=title,
        ) 

    def stream(self, kwargs):

        for id_ in self.ids:

            s = self.response(id_)
            j = s.json()
            
            message = f"{j['statusCode']} {id_['givenName']} {id_['familyName']} {j['message']}"

            self.log(message)

            self.send_email_to(title=message)
