import random
from retry import retry
from jsonschema import validate, ValidationError, SchemaError
import ipaddress

output_1 = {
    "Parameters": [
        {
            "Key": "abc",
            "Value": "123",
        },
        {
            "Key": "xyz",
            "Value": "5678",
        }
    ]

}
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {
            "type": "string",
            "minLength": 9,
            "maxLength": 18,
            "pattern": "(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})"
        }
    },
    "required": ["age", "name"]

}

validJson = {"name": "Eggs", "age": "10.0.0.0/21"}

output = [
    {
        "OutputKey": "InstanceId",
        "OutputValue": "i-01bbb242ff7404a9c",
        "Description": "EC2 Instance ID"
    },
    {
        "OutputKey": "SecurityGroupId",
        "OutputValue": "sg-0e70ed5bb536d7af5",
        "Description": "Security Group ID"
    },
    {
        "OutputKey": "URL",
        "OutputValue": "http://ec2-52-89-136-17.us-west-2.compute.amazonaws.com/wordpress",
        "Description": "WordPress Website URL"
    }
]


def validate_json():
    try:
        print('Ip_address:{0}'.format(ipaddress.ip_network("10.0.0.1/21")))
        validate(validJson, schema)
    except SchemaError as e:
        print('Schema error: {0}'.format(e))
    except ValidationError as e:
        print('Validation error: {0}'.format(e))
        print("---------")
        print(e.absolute_path)
        print("---------")
        print(e.absolute_schema_path)


def parse_output():
    # param_list = output['Parameters']
    for param in output:
        print(param)
        key = param['OutputKey']
        if(key.startswith('URL')):
            print(param['OutputValue'])
            url = param['OutputValue']
        elif(key.startswith('InstanceId')):
            print(param['OutputValue'])
            instance_id = param['OutputValue']

    return url, instance_id


def parse_values(param):
    print(param)
    key = param['OutputKey']
    if(key.startswith('URL')):
        print(param['OutputValue'])
    if(key.startswith('InstanceId')):
        print(param['OutputValue'])

    # y = (lambda key: key, param_list)


def parse_obj(param, param_key, param_value, key_name):
    print(param)
    key = param[param_key]
    if(key.startswith(key_name)):
        print(param[param_value])


def numbers_to_strings(param, argument):
    switcher = {
        'URL': param['OutputValue'],
        'InstanceId': param['OutputValue'],
    }

    # get() method of dictionary data type returns
    # value of passed argument if it is present
    # in dictionary otherwise second argument will
    # be assigned as default value of passed argument
    return switcher.get(argument, "nothing")


# @retry(stop_max_attempt_number=2)
def do_something_unreliable():
    if random.randint(0, 10) > 1:
        print('error')
        raise IOError("Broken sauce, everything is hosed!!!111one")
    else:
        return "Awesome sauce!"


@ retry(tries=3, delay=1, max_delay=4)
def do_something_unreliable_retry():
    if random.randint(0, 10) > 1:
        print('do_something_unreliable_retry')
        raise ValueError("Broken sauce, everything is hosed!!!111one")
    else:
        return "Awesome sauce!"


if __name__ == '__main__':
    url, instance_id = parse_output()
    print(url)

    # print(do_something_unreliable())
    # print(do_something_unreliable_retry())
    print(validate_json())
    # param_list = output_1['Parameters']

    # values = filter(parse_values, output)
    # print(list(values))

    # for param in output:
    #  key = param['OutputKey']
    # parse_obj(param, 'OutputKey', 'OutputValue', key)
    #  print(numbers_to_strings(param, key))
