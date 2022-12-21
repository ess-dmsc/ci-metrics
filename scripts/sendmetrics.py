#!/usr/bin/python

import cmd, sys, os
from SocketDriver import SimpleSocket
import argparse

def send(string):
    print(driver.Ask(string))

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument("-i", metavar='ipaddr', help = "server ip address (default 127.0.0.1)",
                       type = str, default = "127.0.0.1")
   parser.add_argument("-p", metavar='port', help = "server tcp port (default 8888)",
                       type = int, default = 8888)
   args = parser.parse_args()

   driver = SimpleSocket(args.i, args.p)

   # metric_name metric_value timestamp
   # time is seconds in unix epoch
   # date +%s
   send("ingester.rx.proposals 4 1662641550")
