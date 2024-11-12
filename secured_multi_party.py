#!/usr/bin/python

import argparse
import xmlrpc.client
import logging
import random

from rsa import RSA
from xmlrpc import *
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class rpc_impl:
    def __init__(self, rsa, x2):
        self.rsa = rsa
        self.x2 = x2   #Bob's wealth
        self.z = [0] * 100

    def getpublickey(self):
        return (self.rsa.get_e(), self.rsa.get_n())  # return public key and n

    # bob generated a sequence in which is plain number
    def getsequence(self, c1):
        logging.debug("get ciper number from Alice %d", c1)
        print("------------------------------")
        print(f"Alice requests to compare wealth with Bob, Alice provide info:{c1}")

        # decrypt c1 from c1+1 to c1+100
        for i in range(100):
            self.z[i] = self.rsa.decrypt(c1+i)

        # set the bob's wealth(x2) in z[i]
        for i in range(self.x2):
            self.z[i] += 1;

        return self.z

    # Alice send the result back to bob
    def setresult(self, result):
        print(result)
        return 0

def get_number(prompt="Enter a number", default=10):
    tmp  = input(f"{prompt} (default: {default}): ")

    if tmp == "":
        return default
    else:
        return int(tmp)

def run_server():
    logging.debug(f"Run as a role Bob")

    # initial the parameter
    p = get_number("Enter RSA p", 61)
    q = get_number("Enter RSA q", 53)
    e = get_number("Enter RSA e", 17)
    x2 = get_number("Enter Bob's wealth(1-100)", 17)

    try:
        rsa = RSA()
        rsa.create(p, q, e)
    except ValueError:
        logging.error("Please enter a correct number for p, q, e.")
        exit(1)

    rpc = rpc_impl(rsa, x2)
    server = SimpleXMLRPCServer(("localhost", 8000), logRequests=False)
    server.register_instance(rpc)

    logging.debug(f"Staring RPC server......")
    print(f"Staring RPC server......")

    server.serve_forever()

# Alice run as RPC client
def run_client():
    logging.debug(f"Run as a role Alice")

    # 1. get public key(e, n) from server
    client = xmlrpc.client.ServerProxy("http://127.0.0.1:8000/")
    (e, n) = client.getpublickey()
    logging.debug("Get public key from server e:%d, n:%d" %(e, n))
    rsa = RSA();
    rsa.public_init(e, n)

    # 2. encryption a large random number
    m1 = random.randint(100, 200)
    logging.debug("generate large random number %ld" %(m1))
    c1 = rsa.encrypt(m1)
    logging.debug("crphier number %ld" %(c1))
   
    # 3. get the number x1
    x1 = int(input("Enter Alice's wealth(1-100): "))
    if x1 < 1 or x1 > 100: 
        logging.error("invalid Alice's wealth, it should be from 1 to 100")
        exit(1)

    # 4. combined cipher and x1
    c1 = c1 - x1

    # 5. Alice sends c1 to Bob and get the sequence back
    z = client.getsequence(c1)
    print(f"Alice requests to compare wealth with Bob, Bob provide info:")
    for i in range(100):
        print("%8d" %(z[i]), end=" ")
        if i % 10 == 9:
            print("\n", end="")

    if z[x1] != m1 :
        result= "Result: Bob is wealthier than Alice"
    else:
        result= "Result: Bob is NOT wealthier than Alice"

    # 6. Alice sends the result to Bob
    print(result)
    client.setresult(result)

    return 0

def main(param):
    if param == "Bob":
        logging.debug(f"Run as a role Bob")
        run_server()
    elif param == "Alice" :
        logging.debug(f"Run as a role Alice")
        run_client()
    else:
        logging.error(f"Error: wrong role")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="one parameter for role is required, possible value is alice or bob")
    parser.add_argument("role", type=str, help="running role: alice or bob")
    args = parser.parse_args()

    main(args.role)

