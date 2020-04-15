import random

import boto3
import time
import datetime
import cv2
import json
import base64
from DynamoDBService import DynamoDBService

# owner_phone = '+13473351954'
owner_phone = '+19172924010'

s3 = boto3.client("s3")
BUCKET_NAME = "kvslambda"

kvs = boto3.client("kinesisvideo")
rek = boto3.client("rekognition")

endpoint = kvs.get_data_endpoint(
    StreamARN='arn:aws:kinesisvideo:us-east-1:591736655990:stream/KVS1/1585923941562',
    APIName='GET_MEDIA_FOR_FRAGMENT_LIST'
)['DataEndpoint']

kvs_media = boto3.client('kinesis-video-archived-media', endpoint_url=endpoint)

dynamodb = DynamoDBService()

client = boto3.client(
    "sns",
    aws_access_key_id="AKIAJH6DE22FGWFPRW5A",
    aws_secret_access_key="lPFyTCF72osPcubTIQTv6Cu/An3P1q1tDW/a+6HM",
    region_name="us-east-1"
)


def sendMsg(phone_num, msg_text):
    # Send your sms message.
    client.publish(
        PhoneNumber=phone_num,
        Message=msg_text
    )
    print("text message sent:{},{}".format(phone_num,msg_text))



def face_handler(face, fragmentid, test):
    responseBody = ""
    print("======face_handler======")
    print(face)

    detectedface = face["DetectedFace"]
    matchedfaces = face["MatchedFaces"]
    if matchedfaces:  # known face
        
        bestmatches = sorted(matchedfaces, key=lambda face: face["Similarity"], reverse=True)  # fetch best matched face
        vis_items = []
        # TODO: query visitor in DB2 by faceid, if verfied(not pending), generate OTP and send SMS to visitor
        ##   visitor = db.query(faceid)
        ##   if vistor['status'] == 'approved':
        for match in bestmatches:
            faceid = match["Face"]["FaceId"]
            visitor = dynamodb.serach_table(table_name="visitors", key="faceid", value=faceid)
            if visitor:
                vis_items = visitor
                if vis_items[0]['status'] == 'approved':
                    ## generate new otp only if visitor doesn't have one
                    print("matched faceid in db:{}".format(faceid))
                    exist_otp = dynamodb.serach_table(table_name="passcodes",key="faceid",value=faceid)
                    print(exist_otp)
                    if not exist_otp:
                        ##  generateOTP
                        # set ttl value
                        expire = 5 * 60
                        myttl = expire + int(time.time())
                        # set passcode
                        myotp = str(random.randint(1000, 9999))
                        #store otp in db
                        pas_insert_result = dynamodb.insert_to_passcode(table_name="passcodes", myid=faceid, myttl=myttl, myotp=myotp)
            
                        ##  sendSMS(visitor,OTP)
                        myphone = vis_items[0]['phone']
                        text = "This is your otp:" + myotp + ". Your code will be expired in 5 minutes. https://p2wp2.s3.amazonaws.com/index.html"
                        sendMsg(myphone, text)
                        responseBody = "OTP sent to user:" + text
                    else:
                        responseBody = "OTP has already generated. New message won't be sent to visitor."
                    break
        else:
            if vis_items:
                responseBody = "The visitor is not verified yet."
            else:
                responseBody = "+++++++Critical Error++++++++=: matched faceid {} not found in db".format(faceid)
        
    else:  # new face
        payload = ""
        if test:
            payload = s3.get_object(
                Bucket='testdontdelete',
                Key=test
            )['Body']
        else:
            response = kvs_media.get_media_for_fragment_list(
                StreamName='KVS1',
                Fragments=[fragmentid]
            )
            payload = response['Payload']
        
        with open('/tmp/tmp.mkv', 'wb') as f:
            f.write(payload.read())

        vidcap = cv2.VideoCapture('/tmp/tmp.mkv')
        success, image = vidcap.read()
        if success:
            imageb = cv2.imencode('.jpg', image)[1].tobytes()
            # add face to rekognition match collection
            response = rek.index_faces(
                CollectionId="collection-1",
                Image={
                    'Bytes': imageb
                },
                QualityFilter='AUTO'
            )
            if len(response['FaceRecords']) == 1:
                faceid = str(response['FaceRecords'][0]['Face']['FaceId'])  # faceid assigned by rekognition
                if test:
                    faceid = test
                print("New Face:{} indexed".format(faceid))
                # save photo in s3 bucket, faceid as key
                response = s3.put_object(
                    ACL='bucket-owner-full-control',
                    Body=imageb,
                    Bucket=BUCKET_NAME,
                    Key=faceid,
                    Expires=datetime.datetime.now() + datetime.timedelta(days=1)
                )
                # TODO: send link with picture id to owner via SMS
                url = "https://p2wp1.s3.amazonaws.com/index.html?photoid="+faceid+"&faceid="+faceid
                text = "A new visitor applies for access. Click here to approve:" + url
                sendMsg(owner_phone, text)
                
                # TODO: create a new entry with key faceid in DB2, status pending
                ##    db.create(key=faceid, status='pending')
                photo_info = {}
                photo_info['objectKey'] = faceid
                photo_info['bucket'] = BUCKET_NAME
                photo_info['createdTimestamp'] = str(time.time())
                vis_insert_result = dynamodb.insert_to_visitors(table_name="visitors", myid=faceid,myphotos=[photo_info],mystatus='pending')
                responseBody = text
                
        vidcap.release()
    return responseBody

def lambda_handler(event, context):
    print("================start================")
    responseBody = ""
    test = ""
    if 'Test' in event:
        test = event['Test']
    records = event['Records']
    latestrecord = sorted(records, key=lambda record: int(json.loads(base64.b64decode(record["kinesis"]["data"]))["InputInformation"]["KinesisVideo"]["ProducerTimestamp"]), reverse=True)[0]
    data = json.loads(base64.b64decode(latestrecord["kinesis"]["data"]))  # process one record at one invocation to avoid racing
    fragmentid = data["InputInformation"]["KinesisVideo"]["FragmentNumber"]
    timestamp = data["InputInformation"]["KinesisVideo"]["ProducerTimestamp"]
    print("timedelta:"+str(int(time.time()) - int(timestamp)))
    if 0 <= int(time.time()) - int(timestamp) <= 20 or test:
        if len(data["FaceSearchResponse"]) == 1:  # ensure one face in one photo
            responseBody = face_handler(data["FaceSearchResponse"][0], fragmentid, test)
            print(responseBody)
    time.sleep(5)  # avoid racing
    return {
        'statusCode': 200,
        'body': responseBody
    }

