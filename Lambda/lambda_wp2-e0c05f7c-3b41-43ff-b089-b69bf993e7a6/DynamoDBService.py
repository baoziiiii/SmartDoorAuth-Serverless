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
        # 这两个key像是账号和密码一般，需要在后台申请导出，唯一的
        self.AWS_ACCESS_ID = 'AKIAYTRSA2B3KINXZTYR'
        self.AWS_ACCESS_KEY = 'TPDsFfc1Owas33jZxY0uUMvZ7+W/M/VvlcmLP/aN'

    def get_service(self, table_name):
        """将service单独拿出来的目的，我为了初始化类的时候不会那么慢"""
        client = boto3.client('dynamodb', region_name='us-east-1',
                              aws_access_key_id=self.AWS_ACCESS_ID,
                              aws_secret_access_key=self.AWS_ACCESS_KEY)
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1',
                                  aws_access_key_id=self.AWS_ACCESS_ID,
                                  aws_secret_access_key=self.AWS_ACCESS_KEY)
        # 通过dynamodb服务获取目标table的操作对象
        table_handle = dynamodb.Table(table_name)
        return table_handle

    def serach_table(self, table_name="passcodes", key="otp", value="1"):
        # 通过dynamodb服务获取目标table的操作对象
        table_handle_h5_visit_info = self.get_service(table_name)

        """查询,根据某一key（column）查询"""
        response = table_handle_h5_visit_info.query(
            # KeyConditionExpression=Key('name').eq(name)
            KeyConditionExpression=Key(key).eq(value)
        )

        # response中包含了很多内容，response本身是个json字符串，其Items键的内容才是table中的内容
        #print(type(response))
        items = response['Items']
        #print('items:',items)
        #otp = items[0]['passcode']
        #print('otp:',otp)
        #return json.dumps(items)
        #return otp
        return items
    def filter_table(self,table_name, key, value):
        table_handle_h5_visit_info = self.get_service(table_name)
        fe = Key(key).eq(value)
        pe = "#f"
        ean = {"#f": "faceid",}
        response = table_handle_h5_visit_info.scan(
            FilterExpression=fe,
            ProjectionExpression=pe,
            ExpressionAttributeNames=ean
        )
        items = response['Items']
        return items
        
    def delete_item(self,table_name,key, value):
        table_handle_h5_visit_info = self.get_service(table_name)
        response = table_handle_h5_visit_info.delete_item(
            Key={
                key: value
            }
        )
        print("DeleteItem succeeded:")
        return(json.dumps(response,))