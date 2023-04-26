"""
https://lite.ip2location.com/russian-federation-ip-address-ranges

Example of usage:
from network_range import get_cidr_from_file

cidrs = get_cidr_from_file('IP2LOCATION-LITE-DB1.CSV', 'KZ')
"""

from math import log
from argparse import ArgumentParser


def range_to_netranges(ip_first: int, ip_last: int) -> list:

    def __range_count(reverse_mask: int) -> int:
        return 2 ** reverse_mask

    def __net_first_ip(ip_address: int, reverse_mask: int) -> int:
        _ = __range_count(reverse_mask=reverse_mask)
        return _ * (ip_address // _)

    def __net_last_ip(ip_address: int, reverse_mask: int) -> int:
        return ip_address + __range_count(reverse_mask=reverse_mask) - 1

    __res = list()
    __rmask = int(log(ip_last - ip_first + 1, 2))

    while ip_first != __net_first_ip(ip_address=ip_first, reverse_mask=__rmask):
        __rmask -= 1
        if __rmask == 0:
            break

    __res.append(dict(
        address=ip_first,
        netmask=(32 - __rmask),
    ))
    if ip_last != __net_last_ip(ip_address=ip_first, reverse_mask=__rmask):
        __res.extend(range_to_netranges(
            ip_first=__net_last_ip(ip_address=ip_first, reverse_mask=__rmask) + 1,
            ip_last=ip_last
        ))

    return __res


def int_to_cidr(address: int, mask: int) -> str:
    __res = list()
    _ = address
    while _ != 0:
        __res.insert(0, _ % 256)
        _ = _ // 256
    return f"{'.'.join([str(i) for i in __res])}/{mask}"


def get_cidr_from_file(filename: str, zone: str = 'RU') -> list:
    __networks = list()
    with open(file=filename, mode='r') as f:
        for _ in [i.split(',') for i in f.read().splitlines()]:
            if _[2][1:-1] == zone.upper():
                __networks.extend(range_to_netranges(int(_[0][1:-1]), int(_[1][1:-1])))
    return [int_to_cidr(i['address'], i['netmask']) for i in __networks]


def __get_args():
    __parser = ArgumentParser(description="Get networks from ranges\n"
                                          "Get source file from site: \n"
                                          "https://lite.ip2location.com/russian-federation-ip-address-ranges")
    __parser.add_argument('-f', '--file', required=True, help="File in CSV format")
    __parser.add_argument('-z', '--zone', required=False, help="Get zone", default="RU")
    return __parser.parse_args()


def main():
    __args = __get_args()
    print(*get_cidr_from_file(filename=__args.file, zone=__args.zone), sep="\n")


if __name__ == '__main__':
    main()
