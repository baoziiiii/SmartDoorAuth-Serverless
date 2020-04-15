import random
import boto3
from boto3 import Session
from boto3.dynamodb.conditions import Attr, Key
from datetime import datetime
import json
import time

class DynamoDBService:
    def __init__(self):
        self.this_day = datetime.today()

        self.AWS_ACCESS_ID = 'AKIAYTRSA2B3KINXZTYR'
        self.AWS_ACCESS_KEY = 'TPDsFfc1Owas33jZxY0uUMvZ7+W/M/VvlcmLP/aN'

    def get_service(self, table_name):

        client = boto3.client('dynamodb', region_name='us-east-1',
                              aws_access_key_id=self.AWS_ACCESS_ID,
                              aws_secret_access_key=self.AWS_ACCESS_KEY)
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1',
                                  aws_access_key_id=self.AWS_ACCESS_ID,
                                  aws_secret_access_key=self.AWS_ACCESS_KEY)

        table_handle = dynamodb.Table(table_name)
        return table_handle


        return json.dumps(response)

    def serach_table(self, table_name="passcodes", key="otp", value="1"):

        table_handle_h5_visit_info = self.get_service(table_name)


        response = table_handle_h5_visit_info.query(
            # KeyConditionExpression=Key('name').eq(name)
            KeyConditionExpression=Key(key).eq(value)
        )

        #print(type(response))
        items = response['Items']
        #print('items:',items)
        #otp = items[0]['passcode']
        #print('otp:',otp)
        #return json.dumps(items)
        #return otp
        return items

    def insert_to_visitors(self,table_name="visitors", myid = "" ,myname = "",myphone = "",myphotos=[],mystatus='pending'):
        table_handle_h5_visit_info = self.get_service(table_name)
        '''insert item'''
        item = {}
        if not myid:
            return None
        item['faceid'] = myid
        item['status'] = mystatus

        if myname:
            item['name'] = myname
        if myphone:
            item['photo'] = str(myphotos)
        response=table_handle_h5_visit_info.put_item(
            Item=item
        )
        print("InsertItem succeeded:")
        # print(json.dumps(response, indent=4, cls=DecimalEncoder))
        print(response)
        return json.dumps(response)

    def insert_to_passcode(self,table_name="passcodes", myid="",myttl="",myotp=""):
        table_handle_h5_visit_info = self.get_service(table_name)
        '''insert item'''
        item = {}
        if not myid:
            return None
        item['faceid'] = myid
        if myttl:
            item['ttl'] = myttl
        if myotp:
            item['otp'] = myotp
        response=table_handle_h5_visit_info.put_item(
            Item=item
        )
        print("InsertItem succeeded:")
        # print(json.dumps(response, indent=4, cls=DecimalEncoder))
        print(response)
        return json.dumps(response)