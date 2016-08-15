__author__ = 'umutcan'
import argparse
import os
import sys
import yaml
from boto.ec2.connection import EC2Connection


def get_instances(search_key, aws_conf):
    aws_access_key_id = aws_conf["access_key_id"]
    aws_secret_access_key = aws_conf["secret_access_key"]
    conn = EC2Connection(aws_access_key_id, aws_secret_access_key)
    filters = {
        "tag:Name": "*%s*" % search_key
    }
    instance_list = []
    item = 0
    reservations = conn.get_all_instances(filters=filters)
    for reservation in reservations:
        for instance in reservation.instances:
            instance_list.append(instance)
            item += 1
    return instance_list


def print_instaces(instances):
    item = 0
    for instance in instances:
        print "(%s)" % item + instance.instance_type + "\t" + instance.tags["Name"] + "\t" + instance.launch_time
        item += 1


def connect(ip_address, username='', ssh_identities=None):
    command = "ssh "
    if ssh_identities:
        for ssh_key in ssh_identities:
            command += "-i %s " % ssh_key
    if username > '':
        command += "%s@" % username

    command += "%s" % ip_address
    os.system(command)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', action='store_true', default=False)
    parser.add_argument('-c', '--choice', type=int, default=0)
    parser.add_argument('-s', '--search_key', default='')
    parser.add_argument('-i', '--use-identities', action='store_true', default=False)
    parser.add_argument('-u', '--ssh-user-name', default='')
    args = parser.parse_args()

    conf = yaml.safe_load(open("config.yml"))
    instances = get_instances(args.search_key, conf["aws"])
    ssh_identities = None
    if args.use_identities:
        ssh_identities = conf["ssh"]["identities"]

    if args.list:
        while True:
            print_instaces(instances)
            item = raw_input("Choose a instance to connect or (q) for quit\n")
            if item == "q":
                sys.exit()
            else:
                try:
                    print "Connection to item: %s" % item
                    connect(instances[int(item)].ip_address, username=args.ssh_user_name,
                            ssh_identities=ssh_identities)
                    break
                except ValueError:
                    print "Invalid input"

    else:
        connect(instances[args.choice].ip_address, username=args.ssh_user_name,
                ssh_identities=ssh_identities)


if __name__ == '__main__':
    main()
