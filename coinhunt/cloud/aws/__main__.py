from coinhunt.cloud.aws import get_hosted_zone_name

import pprint

def main():
    pprint.pprint(get_hosted_zone_name())

if __name__ == '__main__':
    main()
