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
  
  - WP1  https://p2wp1.s3.amazonaws.com/index.html 
  - WP2  https://p2wp2.s3.amazonaws.com/index.html


### `/Local`

  AWS_env_init.py 
  
  1. delete collection if exists and create a collection. 
  2. stop and delete streamprocessor if exists and create a streamprocessor. 
  3. start the streamprocessor
  



 
