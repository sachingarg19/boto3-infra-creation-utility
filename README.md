### Boto3 infra utility
Main purpose of utility is perform following
1. Create VPC & VPC related services
1. Create EC2 & Security Group
1. Deploy Word press app on cloud
1. To print out output & store output as JSON format in output folder
1. Delete stacks


#### Note:
Supplied template deployment had been successfully tested with ami-e689729e
('amzn-ami-hvm-2017.09.0.20170930-x86_64-gp2' in us-west-2 region) on a t2.micro machine.

### Download awscli from below link
https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html

### AWS configure commands
`aws configure`
`aws configure list`

### prerequisite
```
Python/Python3
pip/pip33
pip/pip3 install boto3
pip3 install retry
or
pip3 install -r requirements.txt

Create keypair on Ec2 instance before deploying the app.
```

#### Files

#### CF1-VPC.json

This CloudFormation template creates a simple VPC, and requires the following
parameters:

- VpcCidrBlock - A CIDR block that represents the network, i.e. 10.0.0.0/21
- SubnetCidrBlock - A CIDR block that represents a single subnet within
the network, i.e. 10.0.0.0/24 or 10.0.1.0/24, etc.

Outputs are:

- VpcId - The ID of the resulting VPC
- SubnetId - The ID of the resulting Subnet

#### CF2-WebApplication.json

This CloudFormation template creates a simple web application (WordPress),
and requires the following parameters:

- KeyName - Name of a pre-created SSH Key, you may create this manually.
- InstanceType - Instance type to use, i.e. t2.small.
- AmiId - AMI ID to use, this template has been successfully tested with the
  following amazon linux 'amzn-ami-hvm-2017.09.0.20170930-x86_64-gp2'
  aka (ami-e689729e) in us-west-2 region.
- SubnetId - Subnet ID that was created in CF1
- VpcId - VPC ID that was created in CF1
- AllowedIp - Your public IP Address to allow HTTP access to in CIDR format
- DBUser - Database Username
- DBPassword - Database Password

#### Outputs are:

- URL - The URL of the resulting Application
- InstanceId - The ID of the resulting Instance
- SecurityGroupId - The ID of the resulting SecurityGroup


### Features which are added as part of github repo
1. Create High level flow diagram
1. Create VPC based
  * Based on configurable & simplified json(config/vpc_config.json) file passed as a command line arguments
1. Store VPC output in json file (vpc_output.json) under output folder
1. Create deploy stack & deploy app
  * Based on configurable json(config/webapp_config.json) file passed as a command line arguments
1. Generate deployment info json file(webapp_output.json) under output folder
1. Delete deploy stack & deploy app 
1. Delete vpc & other vpc related resources
1. Validate cft before creation of stack
1. Rollback on failure - cleanup the failed stack
1. Add waiter
1. Configure logging
1. Configure stack creation retry attempt on exception using `retry` package
1. Configure waiter MaxAttempts mechanism
1. Configure boto3 retry mechanism
1. Exception handling
1. Create a helper class to support data processing
1. High level flow diagram
```

### Next Steps 
```
* Validate inputs before creation of stack
* Unit Test cases
* Installing additional monitoring tools like Datadog.
* Configure Log rotation
* Stack Exist & Stack Update
* Configurable retry count
```

### How to run
* chmod 775 and Run ./build_script.sh
* To create VPC use `c-vpc` command. Example below
`
python3 main.py --cmd c-vpc --stack-config-file ./config/vpc_config.json --cft-template-path ./config/CF1-VPC.json
`
* To create Webapp stakc use `c-app` command. Example below
`python3 main.py --cmd c-app --stack-config-file ./config/webapp_config.json --cft-template-path ./config/CF2-WebApplication.json`

```
Deployment Successful
    Application URL: <URL>
    VPC ID: <VpcId>
    Instance ID: <InstanceId>
    ..
    ..

cat output/webapp_output.json
{
    "url": "<URL>",
    "vpc_id": "<VpcId",
    "instance_id": "<InstanceId>"
    ..
    ..
}
```

* To delete App & VPC use `d-app or d-vpc` commands. Example below
```
python3 main.py --cmd d-app --stack-config-file ./config/webapp_config.json --cft-template-path ./config/CF2-WebApplication.json
python3 main.py --cmd d-vpc --stack-config-file ./config/vpc_config.json --cft-template-path ./config/CF1-VPC.json
```



### Issues faced & resolved
1. Endpoint was not accessible after deploying.
   * Resolution: updated allowedIP to 0.0.0.0/0 which all the access and updated the SG ingress and egress rule
1. If Subnet is in west D az then needs stack fails as ami doesn't supported in d az
  * Delete the vpc and let it get created it in different az from a - c.

## Relevant Documentation
- Boto3 Documentation - https://boto3.readthedocs.io/en/latest/
- For more info about Free Tier accounts: https://aws.amazon.com/free/
