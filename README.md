# SmartDoorAuth-Serverless

![architecuture diagram](/images/architecture.png)


## Project Directory

### `/Lambda`

  Lambda functions
  - KVSLambda : LF1 in diagram
  - lambda_wp1
  - lambda_wp2

### `/S3`
  
  Webs
  
  - WP1
  - WP2 


### `/Local`

  AWS_env_init.py  
      1. delete collection if exists and create a collection
      2. stop and delete streamprocessor if exists and create a streamprocessor
      3. start the streamprocessor
  



 
