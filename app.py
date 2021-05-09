import os
import boto3
import uuid
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from flask import Flask, jsonify, request
from datetime import datetime
from initialize import create_app
from flask_cors import cross_origin

app = create_app()
print("app is started")

client = boto3.client('dynamodb')

def lambda_handler(event, context):
  print('## ENVIRONMENT VARIABLES')
  print(os.environ)
  print('## EVENT')
  print(event)
  print('## CONTEXT')
  print(context)
  return event

ERROR_HELP_STRINGS = {
    # Operation specific errors
    'ConditionalCheckFailedException': 'Condition check specified in the operation failed, review and update the condition check before retrying',
    'TransactionConflictException': 'Operation was rejected because there is an ongoing transaction for the item, generally safe to retry with exponential back-off',
    'ItemCollectionSizeLimitExceededException': 'An item collection is too large, you\'re using Local Secondary Index and exceeded size limit of items per partition key.' +
                                                ' Consider using Global Secondary Index instead',
    # Common Errors
    'InternalServerError': 'Internal Server Error, generally safe to retry with exponential back-off',
    'ProvisionedThroughputExceededException': 'Request rate is too high. If you\'re using a custom retry strategy make sure to retry with exponential back-off.' +
                                              'Otherwise consider reducing frequency of requests or increasing provisioned capacity for your table or secondary index',
    'ResourceNotFoundException': 'One of the tables was not found, verify table exists before retrying',
    'ServiceUnavailable': 'Had trouble reaching DynamoDB. generally safe to retry with exponential back-off',
    'ThrottlingException': 'Request denied due to throttling, generally safe to retry with exponential back-off',
    'UnrecognizedClientException': 'The request signature is incorrect most likely due to an invalid AWS access key ID or secret key, fix before retrying',
    'ValidationException': 'The input fails to satisfy the constraints specified by DynamoDB, fix input before retrying',
    'RequestLimitExceeded': 'Throughput exceeds the current throughput limit for your account, increase account level throughput before retrying',
}

def handle_error(error):
  error_code = error.response['Error']['Code']
  error_message = error.response['Error']['Message']

  error_help_string = ERROR_HELP_STRINGS[error_code]

  print(f'[{error_code}]. Error message: {error_message}')

@app.route("/")
@app.route("/api/register", methods=['POST'])
def register_user():
  print('## ENVIRONMENT VARIABLES')
  print(os.environ)
  print('request')
  print(request)
  request_body = request.get_json()
  print("request body")
  print(request_body)
  first_name = request_body['firstName']
  last_name = request_body['lastName']
  address_one = request_body['addressOne']
  address_two = request_body['addressTwo']
  city = request_body['city']
  state = request_body['state']
  zipcode = request_body['zipcode']
  country = request_body['country']
  new_uuid = str(uuid.uuid1())
  created_date = datetime.now()
  created_date_timestamp = str(created_date.timestamp())
  user_info = {
    "uuid": {"S": new_uuid}, 
    "created_date": {"N": created_date_timestamp}, 
    "first_name": {"S": first_name}, 
    "last_name": {"S": last_name}, 
    "city": {"S": city}, 
    "state": {"S": state}, 
    "zipcode": {"S": zipcode}, 
    "country": {"S": country}, 
    "address_one": {"S": address_one}, 
    "address_two": {"S": address_two}
  }
  try:
    client.put_item(TableName="users", Item=user_info)
    print("successfully put item")
  except ClientError as error:
    handle_error(error)
  except BaseException as error:
    print(error)

  return jsonify({'user_info': user_info}), 200


@app.route('/api/admin', methods=['GET'])
def get_users():
  try:
    response = client.scan(TableName="users", Limit=50)
    
    print("Scan successful.")
    print(response)
    users = response["Items"]
    users.sort(key=lambda user : user["created_date"]["N"], reverse=True)
  except ClientError as error:
    handle_error(error)
  except BaseException as error:
    print(error)

  return jsonify({"users": users}), 200
