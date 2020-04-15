import json
import boto3
from DynamoDBService import DynamoDBService
import time
import random


def lambda_handler(event, context):
    # get id and input_otp
    #myid = event.get('faceid')
    input_otp = event.get('otp')

    dynamodb = DynamoDBService()

    # validate OTP
    # otp = dynamodb.serach_table(table_name="passcodes", myid=myid)
    pass_items = dynamodb.filter_table(table_name="passcodes", key="otp",value=input_otp)
    # print(items[0])
    #myid = pass_items[0]['faceid']
    # # retrieve visitor information
    # items = dynamodb.serach_table(table_name="visitors", myid=myid)
    # name = items[0]['name']
    #
    # if (input_otp == otp):
    #     return {
    #         'statusCode': 200,
    #         'body': 'Hi,' + name + '!'
    #     }
    # else:
    #     return {
    #         'statusCode': 200,
    #         'body': 'Permission denied!'
    #     }
    if (pass_items):
        myid = pass_items[0]['faceid']
        # retrieve visitor information
        vis_items = dynamodb.serach_table(table_name="visitors", key="faceid",value=myid)
        name = vis_items[0]['name']
        print("OTP ACKed:{}".format(myid))
        #delte otp
        print(input_otp)
        dynamodb.delete_item(table_name="passcodes",key="faceid",value=myid)
        return {
            'statusCode': 200,
            'body': 'Hi,' + name + '!'
        }

    else:
        return {
            'statusCode': 200,
            'body': 'Permission denied!'
        }
