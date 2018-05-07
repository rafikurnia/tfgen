import boto3


class AWSClient(object):
    def __init__(self):
        self.ec2_client = boto3.client("ec2")
        self.sns_client = boto3.client("sns")

    @staticmethod
    def __count_checker(outputs):
        count = len(outputs)
        if count < 1:
            raise ValueError("No data was found.")
        elif count > 1:
            raise ValueError("Got more than 1 results (got {}, expect 1)".format(count))

    def get_vpc_id(self, vpc_name):
        filters = [
            {
                "Name": "tag:Name",
                "Values": [
                    vpc_name,
                ],
            },
        ]
        output = self.ec2_client.describe_vpcs(Filters=filters)["Vpcs"]
        self.__count_checker(output)
        return output[0]['VpcId']

    def get_security_group_id(self, group_name, vpc_id=None):
        filters = [
            {
                "Name": "group-name",
                "Values": [
                    group_name,
                ],
            },
        ]
        if vpc_id is not None:
            filters.append(
                {
                    "Name": "vpc-id",
                    "Values": [
                        vpc_id,
                    ],
                }
            )
        output = self.ec2_client.describe_security_groups(Filters=filters)["SecurityGroups"]
        self.__count_checker(output)
        return output[0]['GroupId']

    def get_most_recent_image_id(self, image_name):
        filters = [
            {
                "Name": "name",
                "Values": [
                    image_name,
                ],
            },
        ]
        output = self.ec2_client.describe_images(Filters=filters)["Images"]
        return sorted(output, key=lambda x: x["CreationDate"], reverse=True)[0]["ImageId"]

    def get_sns_topic_arn(self, topic_name):
        all_topics = self.sns_client.list_topics()["Topics"]
        output = list(filter(lambda x: topic_name in x["TopicArn"], all_topics))
        self.__count_checker(output)
        return output[0]["TopicArn"]
