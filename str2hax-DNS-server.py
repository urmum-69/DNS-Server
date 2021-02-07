#!/usr/bin/env python3
# Original sudomemoDNS v1.0
# (c) 2019 Austin Burk/Sudomemo
# All rights reserved

# str2hax DNS Server v1.0
# Created by Austin Burk/Sudomemo. Edited by urmum_69.

from datetime import datetime
from time import sleep

from dnslib import DNSLabel, QTYPE, RD, RR
from dnslib import A, AAAA, CNAME, MX, NS, SOA, TXT
from dnslib.server import DNSServer

import socket
import requests
import json
import sys

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]

STR2HAXDNSSERVER_VERSION = "1.0"

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

EPOCH = datetime(1970, 1, 1)
SERIAL = int((datetime.utcnow() - EPOCH).total_seconds())
MY_IP = get_ip()

print("+===============================+")
print("|    str2hax DNS Server    |")
print("|          Version " + STR2HAXDNSSERVER_VERSION + "          |")
print("+===============================+\n")

print("Hello! This server will allow you to use str2hax when your Internet Service Provider does not work with custom DNS.")


print("#### How To Use ####\n")
print("The process does not differ from what is shown at https://wii.guide/str2hax except for the values to enter in your custom DNS settings.")
print("First, make sure that your Wii is connected to the same network as this computer.")

print("\nHere are the settings you need to type in on your Wii in the DNS section.:\n")
print(":---------------------------:")
print("  Primary DNS:  ",MY_IP  )
print("  Secondary DNS: 1.1.1.1")
print(":---------------------------:")

print("#### Getting Help ####\n")
print("Need help? Visit our Discord server https://discord.gg/b4Y7jfD or contact us at support@riiconnect24.net\n")

print("--- Starting up ---")

TYPE_LOOKUP = {
    A: QTYPE.A,
    AAAA: QTYPE.AAAA,
    CNAME: QTYPE.CNAME,
    MX: QTYPE.MX,
    NS: QTYPE.NS,
    SOA: QTYPE.SOA,
    TXT: QTYPE.TXT,
}

# Can't seem to turn off DNSLogger with a None type so let's just null it out with a dummy function

class RiiConnect24DNSLogger(object):
    def log_recv(self, handler, data):
        pass
    def log_send(self, handler, data):
        pass
    def log_request(self, handler, request):
        print("[DNS] {" + datetime.now().strftime('%H:%M:%S') + "} Received: DNS Request from: " + handler.client_address[0])
    def log_reply(self, handler, reply):
        print("[DNS] {" + datetime.now().strftime('%H:%M:%S') + "} Sent    : DNS Response to:  " + handler.client_address[0])
    def log_error(self, handler, e):
        logger.error("[INFO] {" + datetime.now().strftime('%H:%M:%S') + "} Invalid DNS request from " + handler.client_address[0])
    def log_truncated(self, handler, reply):
        pass
    def log_data(self, dnsobj):
        pass


class Record:
    def __init__(self, rdata_type, *args, rtype=None, rname=None, ttl=None, **kwargs):
        if isinstance(rdata_type, RD):
            # actually an instance, not a type
            self._rtype = TYPE_LOOKUP[rdata_type.__class__]
            rdata = rdata_type
        else:
            self._rtype = TYPE_LOOKUP[rdata_type]
            if rdata_type == SOA and len(args) == 2:
                # add sensible times to SOA
                args += ((
                    SERIAL,  # serial number
                    60 * 60 * 1,  # refresh
                    60 * 60 * 3,  # retry
                    60 * 60 * 24,  # expire
                    60 * 60 * 1,  # minimum
                ),)
            rdata = rdata_type(*args)

        if rtype:
            self._rtype = rtype
        self._rname = rname
        self.kwargs = dict(
            rdata=rdata,
            ttl=self.sensible_ttl() if ttl is None else ttl,
            **kwargs,
        )

    def try_rr(self, q):
        if q.qtype == QTYPE.ANY or q.qtype == self._rtype:
            return self.as_rr(q.qname)

    def as_rr(self, alt_rname):
        return RR(rname=self._rname or alt_rname, rtype=self._rtype, **self.kwargs)

    def sensible_ttl(self):
        if self._rtype in (QTYPE.NS, QTYPE.SOA):
            return 60 * 60 * 24
        else:
            return 300

    @property
    def is_soa(self):
        return self._rtype == QTYPE.SOA

    def __str__(self):
        return '{} {}'.format(QTYPE[self._rtype], self.kwargs)


ZONES = {}

try:
  get_zones = requests.get("https://raw.githubusercontent.com/urmum-69/str2hax-DNS-Server/master/dns_zones.json")
except requests.exceptions.Timeout:
  print("[ERROR] Couldn't load DNS data: connection to GitHub timed out.")
  print("[ERROR] Are you connected to the Internet?")
except requests.exceptions.RequestException as e:
  print("[ERROR] Couldn't load DNS data.")
  print("[ERROR] Exception: ",e)
  sys.exit(1)
try:
  zones = json.loads(get_zones.text)
except ValueError as e:
  print("[ERROR] Couldn't load DNS data: invalid response from server")

for zone in zones:
  if zone["type"] == "a":
    ZONES[zone["name"]] = [ Record(A, zone["value"]) ]
  elif zone["type"] == "p":
    ZONES[zone["name"]] = [ Record(A, socket.gethostbyname(zone["value"])) ]

print("[INFO] DNS information has been downloaded successfully.")

class Resolver:
    def __init__(self):
        self.zones = {DNSLabel(k): v for k, v in ZONES.items()}

    def resolve(self, request, handler):
        reply = request.reply()
        zone = self.zones.get(request.q.qname)
        if zone is not None:
            for zone_records in zone:
                rr = zone_records.try_rr(request.q)
                rr and reply.add_answer(rr)
        else:
            # no direct zone so look for an SOA record for a higher level zone
            found = False
            for zone_label, zone_records in self.zones.items():
                if request.q.qname.matchSuffix(zone_label):
                    try:
                        soa_record = next(r for r in zone_records if r.is_soa)
                    except StopIteration:
                        continue
                    else:
                        reply.add_answer(soa_record.as_rr(zone_label))
                        found = True
                        break
            if not found:
                if "nintendowifi.net" in str(request.q.qname):
                    reply.add_answer(RR(str(request.q.qname),QTYPE.A,rdata=A("95.217.77.151"),ttl=60))
                else:
                    reply.add_answer(RR(str(request.q.qname),QTYPE.A,rdata=A(socket.gethostbyname_ex(str(request.q.qname))[2][0]),ttl=60))

        return reply


resolver = Resolver()
dnsLogger = RiiConnect24DNSLogger()

print("[INFO] Detected operating system:", get_platform());

if get_platform() == 'linux':
  print("[INFO] Please note that you will have to run this as root or with permissions to bind to UDP port 53.")
  print("[INFO] If you aren't seeing any requests, check that this is the case first with lsof -i:53 (requires lsof)")
  print("[INFO] To run as root, prefix the command with 'sudo'")
elif get_platform() == 'OS X':
  print("[INFO] Please note that you will have to run this as root or with permissions to bind to UDP port 53.")
  print("[INFO] If you aren't seeing any requests, check that this is the case first with lsof -i:53 (requires lsof)")
  print("[INFO] To run as root, prefix the command with 'sudo'")
elif get_platform() == 'Windows':
  print("[INFO] Please note: If you see a notification about firewall, allow the application to work. If you're using 3rd party  firewall on your computer - you may want to - this program to your firewall and allow traffic.")

try:
  servers = [
    DNSServer(resolver=resolver, port=53, address=MY_IP, tcp=True, logger=dnsLogger),
    DNSServer(resolver=resolver, port=53, address=MY_IP, tcp=False, logger=dnsLogger),
  ]
except PermissionError:
  print("[ERROR] Permission error: check that you are running this as Administrator or root")
  sys.exit(1)

print("-- Done --- \n")
print("[INFO] Starting str2hax DNS server.")
print("[INFO] Ready. Waiting for your Wii to send DNS Requests...\n")

if __name__ == '__main__':
    for s in servers:
        s.start_thread()

    try:
        while 1:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.stop()
