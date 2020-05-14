import boto3

session = boto3.Session(profile_name="ops-intel-admin-prod")
ec2_client = session.client('ec2')
volumes = ec2_client.describe_volumes(Filters=[{'Name': 'tag:Name','Values': ['ops-intel-prod-metrics']}, {'Name':'tag:kubernetes.io/created-for/pvc/namespace', "Values":["ops-intel-multitenant-metrics"]}])

for volume in volumes["Volumes"]:

    new_name = "kubernetes-dynamic-"
    for pvc_tag in volume["Tags"]:
        if pvc_tag["Key"] == "kubernetes.io/created-for/pv/name":
            new_name = new_name + pvc_tag["Value"]
            print(new_name)
            ec2_client.create_tags(Resources=[volume["VolumeId"]], Tags=[{'Key': 'Name', 'Value': new_name}])
