
from botocore.config import Config
import argparse
import logging
import json
from logging.handlers import RotatingFileHandler
from retry import retry
from botocore.exceptions import ClientError, NoCredentialsError, HTTPClientError, ReadTimeoutError, WaiterError
from utility import helper
from src.deletestack import DeleteStack
from src.createstack import CreateStack
from jsonschema import validate, ValidationError, SchemaError

'''
Main file which handles all interaction with the tool
'''

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')

LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename="logs/infra.log",
                    level=logging.INFO, format=LOG_FORMAT)
handler = RotatingFileHandler("logs/infra.log", maxBytes=1,
                              backupCount=5)
# logging.addHandler(handler)


cf_client = helper.make_boto3_client()


def delete_stack(args):
    '''
    this method will make a call to delete stack api using boto3
    '''
    logging.info("Deleting Stack...")
    stack_config, cft_template = args_pre_processing(args)
    logging.info('Deleting stack: {0}'.format(
        stack_config['StackName']))
    DeleteStack.delete_stack(stack_config['StackName'], cf_client)


def create_vpc(args):
    '''
     this method will make a call to create vpc stack api using boto3
    '''
    logging.info("Creating VPC...")
    stack_config, cft_template = args_pre_processing(args)
    stack_obj = helper.build_stack_obj(
        stack_config, template_data=cft_template)
    json_obj = CreateStack.create_stack(stack_obj, cf_client)
    helper.populate_output_json(
        json_obj=json_obj, output_file=stack_config['OutputFilePath'])


def create_app_stack(args):
    '''
       this method will make a call to create app stack api using boto3
    '''
    logging.info("Creating app stack...")
    stack_config, cft_template = args_pre_processing(args)

# one of the way to get vpc/subnet id by making describe api call
# and another is by checking vpc output in json for vpc/subnet id
    vpc_id, subnet_id = describe_vpc(
        stack_name=stack_config['VPCStackName'])

    stack_config = helper.build_vpc_subnet_param(
        stack_config=stack_config, vpc_id=vpc_id, subnet_id=subnet_id)
    logging.info('stack_config: {0}'.format(stack_config))

    stack_obj = helper.build_stack_obj(
        stack_config, template_data=cft_template)

    json_resp = CreateStack.create_stack(stack_obj, cf_client)
    json_output = helper.build_output_result(
        json_resp=json_resp, vpc_id=vpc_id, subnet_id=subnet_id)

    logging.info('Deployment output: {0}'.format(json_output))
    print('Deployment Successful: {0}'.format(json_output))
    helper.populate_output_json(
        json_obj=json_output, output_file=stack_config['OutputFilePath'])


@retry(tries=5, delay=5, max_delay=5)
def describe_vpc(stack_name=None):
    '''
      Method to describe VPC stack and retreive vpc/subnet ids
    '''
    response = cf_client.describe_stacks(
        StackName=stack_name,
        NextToken='DescribeStack'
    )

    # we expect a response, if its missing on non 200 then show response
    if 'ResponseMetadata' in response and response['ResponseMetadata']['HTTPStatusCode'] < 300:
        logging.info("Describe succeed. response: {0}".format(response))
        outputs = response['Stacks'][0]['Outputs']
        for output in outputs:  # try python lambda to retreive & filter value
            if(output['OutputValue'].startswith('vpc-')):
                vpc_id = output['OutputValue']
            elif(output['OutputValue'].startswith('subnet-')):
                subnet_id = output['OutputValue']
    else:
        logging.error(
            "There was an Unexpected error. response: {0}".format(json.dumps(response)))
    return vpc_id, subnet_id


@retry(tries=3, delay=2, max_delay=4)
def validate_cft_template(template):
    '''
      Method to validate CFT
    '''
    cft_template = helper.load_template_data(template)
    cf_client.validate_template(TemplateBody=cft_template)
    return cft_template


def args_pre_processing(*args):
    '''
      Method to do preprocessing to load config and call validate cft CFT
    '''
    stack_config = helper.load_json(args[0].stack_config_file)
    logging.info('stack_config:{0}'.format(stack_config))
    cft_template = validate_cft_template(args[0].cft_template_path)
    return stack_config, cft_template


def cli_args():
    '''
      Method to receive args from command line
      ex: python3 main.py --cmd c-vpc --stack-config-file ./config/vpc_config.json --cft-template-path ./config/CF1-VPC.json
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', type=str, required=True,
                        help='use c-vpc/c-app/d-vpc/d-app to create stack.')
    parser.add_argument('--stack-config-file', type=str, required=True,
                        help='Provide the stack configuration file to create stack. It should be in JSON format')
    parser.add_argument('--cft-template-path', type=str, required=True,
                        help='stack creation template path.')

    return parser.parse_args()


def main():
    '''
     Main method to trigger the stack operations
    '''
    args = cli_args()
    logging.info('Stack arguments: {0}'.format(args))
    try:
        if args.cmd == 'c-vpc':
            create_vpc(args=args)
        elif args.cmd == 'c-app':
            create_app_stack(args=args)
        elif args.cmd == 'd-app' or args.cmd == 'd-vpc':
            delete_stack(args=args)
        else:
            print('Please provide input one of the command i.e. c-vpc/c-app/d-app/d-vpc along with input configuration file and cft.')
            print('Example: python3 main.py - -cmd c-vpc - -stack-config-file ./config/vpc_config.json - -cft-template-path ./config/CF1-VPC.json')

    except ValueError as e:
        logging.critical("Value error caught: {0}".format(e))
        print("Deployment failed ValueError: {0}".format(e))
    except (ClientError, HTTPClientError) as e:
        logging.critical("Boto client error caught: {0}".format(e))
        print("Deployment failed ClientError/HTTPClientError: {0}".format(e))
    except NoCredentialsError as e:
        logging.critical(
            "Boto client doesn't have aws credentials: {0}".format(e))
        print(
            "Deployment failed as Boto client doesn't have aws credentials: {0}".format(e))
    except ReadTimeoutError as e:
        logging.critical('Boto client read timeout error: {0}'.format(e))
        print(
            "Deployment failed as ReadTimeoutError: {0}".format(e))
    except Exception as e:
        # catch any failure
        logging.critical("Unexpected error: {0}".format(e))
        print(
            "Deployment failed as Unexpected error. Check infra logs.")


if __name__ == '__main__':
    main()
