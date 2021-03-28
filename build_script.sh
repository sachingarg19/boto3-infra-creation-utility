# Create Stack
python3 main.py --cmd c-vpc --stack-config-file ./config/vpc_config.json --cft-template-path ./config/CF1-VPC.json
#python3 main.py --cmd c-app --stack-config-file ./config/webapp_config.json --cft-template-path ./config/CF2-WebApplication.json

# Rollback, Deletion and retry webapp
#python3 main.py --cmd c-app --stack-config-file ./config/webapp_config_rollback_retry.json --cft-template-path ./config/CF2-WebApplication.json

#To delete App & VPC use below commands
#python3 main.py --cmd d-app --stack-config-file ./config/webapp_config.json --cft-template-path ./config/CF2-WebApplication.json
#python3 main.py --cmd d-vpc --stack-config-file ./config/vpc_config.json --cft-template-path ./config/CF1-VPC.json
