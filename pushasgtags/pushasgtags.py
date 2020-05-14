import boto3
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("asg", type=str, help='required ASG identifier')
    parser.add_argument('-t', '--tags', nargs='+', help='required tag names (case-sensitive)', required=True)
    parser.add_argument("-p", "--profile", type=str)
    parser.add_argument("-r", "--region", type=str)
    args = parser.parse_args()

    if args.profile is not None:
        session = boto3.Session(profile_name=args.profile)
    else:
        session = boto3.Session()

    print("Profile:", session.profile_name)
    print("Region:", session.region_name)

    if args.region is not None:
        autoscale_client = session.client('autoscaling', region_name=args.region)
        ec2_client = session.client('ec2', region_name=args.region)
    else:
        autoscale_client = session.client('autoscaling')
        ec2_client = session.client('ec2')

    response = autoscale_client.describe_auto_scaling_groups(AutoScalingGroupNames=[args.asg])

    if len(response["AutoScalingGroups"]) < 1:
        raise(Exception("ASG " + args.asg + " not found"))

    asg = response["AutoScalingGroups"][0]
    print(asg)

    asg_arn = asg["AutoScalingGroupARN"]
    asg_instanceids = list(map(lambda inst: inst["InstanceId"], asg["Instances"]))
    asg_tags = get_propagation_tags(asg["Tags"], args.tags)

    print(asg_tags)

    resourceids = asg_instanceids

    asg_reservations = ec2_client.describe_instances(InstanceIds=asg_instanceids)
    for reservation in asg_reservations["Reservations"]:
        for instance in reservation["Instances"]:
            for block_device in instance["BlockDeviceMappings"]:
                if "Ebs" in block_device:
                    resourceids.append(block_device["Ebs"]["VolumeId"])
                else:
                    print("unsupported mapping:", block_device)

    print(resourceids)
    ec2_client.create_tags(Resources=resourceids, Tags=[{'Key': k, 'Value': v} for k, v in asg_tags.items()])

def get_propagation_tags(tags, tag_whitelist):

    result = dict()
    for tag in tags:
        if tag["PropagateAtLaunch"]:

            # tag inclusions
            if tag["Key"] not in tag_whitelist:
                continue

            result[tag["Key"]] = tag["Value"]

    return result

if __name__ == "__main__":
    main()
