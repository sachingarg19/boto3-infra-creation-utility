from botocore.config import Config
import logging
from retry import retry


class DeleteStack:
    '''
    Class to handle stack deletion operation and retry mechanism in case stack deletion fails.
    '''
    @staticmethod
    @retry(tries=3, delay=1, max_delay=4)
    def delete_stack(stack_name, cf_client):
        try:
            response = cf_client.delete_stack(
                StackName=stack_name,
                ClientRequestToken='DELETESTACK'
            )
            waiter = cf_client.get_waiter('stack_delete_complete')
            logging.info("...waiting for stack {0} to be deleted...".format(
                stack_name))
            print("...waiting for stack {0} to be deleted...".format(
                stack_name))
            logging.info("delete - {0}".format(response))
            waiter.wait(StackName=stack_name, WaiterConfig={
                        "Delay": 5, "MaxAttempts": 200})
            print('Stack Deletion Response: {0}'.format(response))
        except Exception as e:
            logging.info('Delete stack failed: {0}'.format(e))
