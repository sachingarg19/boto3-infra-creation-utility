import boto3
from datetime import datetime
import logging
import json
from logging.handlers import RotatingFileHandler
from botocore.config import Config

'''
Helper methods are defined here
'''


def make_boto3_client():
    """
    this method will attempt to make a boto3 client
    """
    retry_config = Config(
        retries={
            'max_attempts': 10,
            'mode': 'standard'
        }
    )

    try:
        logging.info("using default config.")
        client = boto3.client(
            'cloudformation', config=retry_config)
    except ValueError as e:
        logging.critical(
            'Not able to initialize boto3 client with configuration.{0}'.format(e))

    return client


def load_json(json_config):
    '''
    Method to load JSON config
    '''
    with open(json_config) as stack_config_obj:
        stack_config = json.load(stack_config_obj)
    logging.info('stack_config: {0}'.format(stack_config))
    return stack_config


def load_template_data(template):
    '''
    Method to read template files
    '''
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
    return template_data


def build_stack_obj(*stack_config, template_data=None):
    '''
    Method to build object which needs to be passed to create stack
    '''
    logging.info('stackconfig:{0}'.format(stack_config))
    return {
        'StackName': stack_config[0]['StackName'],
        'TemplateBody': template_data,
        'Parameters': stack_config[0]['Parameters'],
        'TimeoutInMinutes': stack_config[0]['TimeoutInMinutes'],
        'OnFailure': stack_config[0]['OnFailure'],
        'Tags': stack_config[0]['Tags'],
        'ClientRequestToken': stack_config[0]['ClientRequestToken']
    }


def build_vpc_subnet_param(stack_config=None, vpc_id=None, subnet_id=None):
    '''
    Method to append vpc & subnet id to app stack parameters
    '''
    vpc_param = {
        'ParameterKey': 'VpcId',
        'ParameterValue': vpc_id
    }
    subnet_param = {
        'ParameterKey': 'SubnetId',
        'ParameterValue': subnet_id
    }
    stack_config['Parameters'].append(vpc_param)
    stack_config['Parameters'].append(subnet_param)
    return stack_config


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def populate_output_json(json_obj, output_file):
    """
    Write to output file in json format
    """
    with open(output_file, "w") as outfile:
        outfile.write(json_obj)


def build_output_result(json_resp, vpc_id=None, subnet_id=None):
    '''
    Method to build output result as a JSON dumps
    '''
    logging.info('build_output_result: {0}'.format(json_resp))
    output = json.loads(json_resp)['Stacks'][0]
    url, instance_id = parse_output(output['Outputs'])
    return json.dumps({
        'stack_id': output['StackId'],
        'stack_name': output['StackName'],
        'vpc_id': vpc_id,
        'subnet_id': subnet_id,
        'StackStatus': output['StackStatus'],
        'url': url,
        'instance_id': instance_id
    })


def parse_output(outputs):
    '''
    Method to parse output and retreive specific fields
    '''
    for param in outputs:
        key = param['OutputKey']
        if(key.startswith('URL')):
            url = param['OutputValue']
        elif(key.startswith('InstanceId')):
            instance_id = param['OutputValue']
    return url, instance_id
