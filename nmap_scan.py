#!./env/bin/python

""" Port Scanner

    This program scans the designated ports on a the specified host using
    nmap. If you supply a stdin of hosts, and a command line argument of ports,
    this script will test the ports on each host.

    Don't be a moron, please don't use this for something illegal.

    Usage:
        nmap_scan.py [-v] <ports>
        nmap_scan.py [-v] <host> <ports>
        nmap_scan.py -h | --help
        nmap_scan.py --version

    Options:
        -v              verbose option, use this if you want to see closed ports and failed connections
        -h, --help      Display this message
        --version       Display the version of this program
        -a, --async     Send requests asynchronously (faster but straining on server)

    Examples:
        ./nmap_scan.py localhost 21,22,80,443
        ./nmap_scan.py localhost,10.0.0.1 21,22,80,443
        ./fping 10.0.1.1/24 | ./nmap_scan.py 21,22,80,443
"""

import sys
import nmap
import socket

from docopt import docopt
from utilities import escape_color


def nmap_scan(scanner, host, port, verbose=False):
    scanner.scan(host, port)

    # is the host an ip? if no then convert it
    try:
        socket.inet_aton(host)
        ip = host
    except socket.error:
        ip = socket.gethostbyaddr(host)[-1][0]

    # if there is a connection error, return False
    try:
        state = scanner[ip]['tcp'][int(port)]['state']
        return (host, port, state)
    except:
        if verbose:
            print escape_color("[*] Can't connect to " + host, "red")
        return False


def main(hosts, ports, verbose=False):
    # Pass the scanner in as a argument, saves a ton of memory
    scanner = nmap.PortScanner()

    for host in hosts:
        for port in ports:
            state = nmap_scan(scanner, host, port, verbose=verbose)

            if state:
                if state[2] == "open":
                    print escape_color("[*] " + state[0] + " tcp/" + state[1] + " " + state[2], "green")
                elif state[2] == "filtered":
                    print escape_color("[*] " + state[0] + " tcp/" + state[1] + " " + state[2], "pink")
                elif state[2] == "closed" and verbose:
                    print escape_color("[*] " + state[0] + " tcp/" + state[1] + " " + state[2], "red")
            else:
                continue

if __name__ == '__main__':
    arguments = docopt(__doc__, version=0.1)

    ports = arguments['<ports>'].split(',')

    if not arguments['<host>']:
        hosts = []
        for line in sys.stdin:
            clear = line.strip('\r').strip('\n')
            hosts.append(clear)

        if arguments['-v']:
            main(hosts, ports, verbose=True)
        else:
            main(hosts, ports)
    else:
        hosts = arguments['<host>'].split(',')

        if arguments['-v']:
            main(hosts, ports, verbose=True)
        else:
            main(hosts, ports)
