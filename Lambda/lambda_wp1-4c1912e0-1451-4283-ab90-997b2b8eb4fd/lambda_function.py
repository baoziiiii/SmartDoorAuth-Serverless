import json
import boto3
from DynamoDBService import DynamoDBService
import time
import random
import re

# Create an SNS client
client = boto3.client(
    "sns",
    aws_access_key_id="AKIAJH6DE22FGWFPRW5A",
    aws_secret_access_key="lPFyTCF72osPcubTIQTv6Cu/An3P1q1tDW/a+6HM",
    region_name="us-east-1"
)
    
def sendMsg(phone_num, msg_text):
    # Send your sms message.
    response = client.publish(
        PhoneNumber=phone_num,
        Message=msg_text
    )
    return response
        
def lambda_handler(event, context):

    # # get id and phone
    myid = event.get('face_id')
    myphone = '+1' + event.get('phone_number')
    myname = event.get("name")

    dynamodb = DynamoDBService()
    #result = dynamodb.operate_table(table_name="visitors", name=myid)

    # approve user
    if re.match("\+[0-9]{9}", myphone) == None:
        return {
        'statusCode': 300,
        'body': "phone number is wrong!"
    }
    query_item = dynamodb.serach_table(table_name="visitors", key='faceid', value=myid)
    if not query_item:
        return{
            'statusCode': 300,
            'body':"no such visitor's record in database!"
        }
    update_result = dynamodb.update_to_table(table_name="visitors", myid=myid, myname=myname, myphone=myphone)


    # store otp
    # set ttl value
    expire = 5 * 60
    myttl = expire + int(time.time())
    # set passcode
    myotp = str(random.randint(1000, 9999))

    insert_result = dynamodb.insert_to_passcode(table_name="passcodes", myid=myid, myttl=myttl, myotp=myotp)

    ## send sms with otp

    text = "This is your otp:"+myotp+". Your code will be expired in 5 minutes. https://p2wp2.s3.amazonaws.com/index.html"
    print(text)
    sms_result = sendMsg(myphone, text)
    print (sms_result)
    if not sms_result:
        return{
            'statusCode': 300,
            'body': 'failed to send message!'
        }
    return {
        'statusCode': 200,
        'body': {'update_result':update_result,'insert_result':insert_result,'sms_result':sms_result}
    }
