import boto3
import os

client = boto3.client('route53')

hosted_zone_id = os.environ.get('R53_ZONE_ID')
def add_record(name, target):
    response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Comment': 'Add record',
            'Changes': [
                {
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [
                            {
                                'Value': target
                            }
                        ]
                    }
                }
            ]
        }
    )
    return response

def delete_record(name, target):
    response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Comment': 'Delete record',
            'Changes': [
                {
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [
                            {
                                'Value': target
                            }
                        ]
                    }
                }
            ]
        }
    )
    return response

def get_hosted_zone_name():
    response = client.get_hosted_zone(
        Id=hosted_zone_id
    )
    return response['HostedZone']['Name']

def get_resource_record_sets():
    response = client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id
    )
    return response['ResourceRecordSets']

def get_soa_record():
    response = client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id
    )
    for record in response['ResourceRecordSets']:
        if record['Type'] == 'SOA':
            return record