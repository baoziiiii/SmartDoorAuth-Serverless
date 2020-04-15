import boto3


client = boto3.client('rekognition')

def createCollection(collectionId):
    try:
        deleteCollection(collectionId)
        print("create Collection")
        response = client.create_collection(
            CollectionId=collectionId
        )
        print(response)
    except Exception as e:
        print(str(e))
        print("Error createCollection.")

def deleteCollection(collectionId):
    print("delete Collection")
    try:
        response = client.delete_collection(
            CollectionId=collectionId
        )
        
        print(response)
    except Exception as e:
        print(str(e))
        print("Error createCollection.")

def deleteStreamProcessor(spName):
    print("deleteStreamProcessor")
    try:
        response = client.delete_stream_processor(
            Name=spName
        )
        print(response)
    except Exception as e:
        print(str(e))

def createStreamProcessor(spName,kvsARN,kdsARN,roleARN,collectionId,FaceMatchThreshold):
    try:
        stopStreamProcessor(spName)
        deleteStreamProcessor(spName)

        print("createStreamProcessor")
        response = client.create_stream_processor(
            Input={
                'KinesisVideoStream': {
                    'Arn': kvsARN
                }
            },
            Output={
                'KinesisDataStream': {
                    'Arn': kdsARN
                }
            },
            Name=streamProcessorName,
            Settings={
                'FaceSearch': {
                    'CollectionId': collectionId,
                    'FaceMatchThreshold': 60
                }
            },
            RoleArn=roleARN
        )
        print(response)
    except Exception as e:
        print(str(e))
        
def stopStreamProcessor(spName):
    try:
        response = client.stop_stream_processor(
            Name=spName
        )
        print(response)
    except Exception as e:
        print(str(e)) 

def startStreamProcessor(spName):
    try:
        stopStreamProcessor(spName)
        response = client.start_stream_processor(
            Name=spName
        )
        print(response)
    except Exception as e:
        print(str(e))

if __name__ == '__main__':
    streamProcessorName="sp-1"
    kinesisVideoStreamArn="arn:aws:kinesisvideo:us-east-1:591736655990:stream/KVS1/1585923941562"
    kinesisDataStreamArn="arn:aws:kinesis:us-east-1:591736655990:stream/KDS1"
    roleArn="arn:aws:iam::591736655990:role/Rekognition"
    collectionId="collection-1"
    createCollection(collectionId)
    createStreamProcessor(streamProcessorName,kinesisVideoStreamArn,kinesisDataStreamArn,roleArn,collectionId,50)
    startStreamProcessor(streamProcessorName)