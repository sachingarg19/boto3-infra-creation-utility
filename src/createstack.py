from botocore.config import Config
import boto3
import logging
import json
from logging.handlers import RotatingFileHandler
from retry import retry
from botocore.exceptions import ClientError, HTTPClientError, ReadTimeoutError, WaiterError
from utility import helper
from utility.exceptions import UploadError
from src.deletestack import DeleteStack


class CreateStack:
    '''
    Create Stack class which handles create stack operation adn retry mechanism in case of failure
    '''

    @staticmethod
    @retry(tries=3, delay=2, max_delay=10)
    def create_stack(stack_info, cf_client):
        '''
        Method to create stack based on stack info.
        '''
        # logging.info('stack name: {0}'.format(stack_info))
        try:
            response = cf_client.create_stack(**stack_info)
            waiter = cf_client.get_waiter('stack_create_complete')
            print("...waiting for stack {0} to be ready...".format(
                stack_info['StackName']))
            waiter.wait(StackName=stack_info['StackName'], WaiterConfig={
                        "Delay": 5, "MaxAttempts": 200})
            logging.info("Stack Created. response: {0}".format(
                json.dumps(response)))
            json_obj = json.dumps(
                cf_client.describe_stacks(StackName=response['StackId']),
                indent=2,
                default=helper.json_serial
            )
        except (ClientError, WaiterError, ConnectionError, ReadTimeoutError, EOFError, HTTPClientError, Exception) as e:
            logging.error("Creation failed for stack '%s'",
                          stack_info['StackName'], exc_info=e)
            desc_response = cf_client.describe_stacks(
                StackName=response['StackId'])
            logging.error('Failure response: {0}'.format(desc_response))
            failure_status = desc_response['Stacks'][0]['StackStatus']
            print('status:{0}'.format(failure_status))
            if(failure_status.startswith('ROLLBACK') or failure_status.endswith('FAILED')):
                CreateStack.stack_cleanup(
                    stack_info['StackName'], cf_client)
            raise UploadError(
                "Failed to create '{}' stack".format(stack_info['StackName'])
            ) from e

        logging.info('Create stack output response: {0}'.format(json_obj))
        return json_obj

    @staticmethod
    def stack_cleanup(stack_name, cf_client):
        '''
        Method to call delete method in case of Rollback_ or _Failes stack sta
        '''
        DeleteStack.delete_stack(stack_name=stack_name, cf_client=cf_client)
