#!/usr/bin/python3

from sympy import *

class RSA:
    def __init__(self) :
       self.p = self.q = self.n = self.e = self.d = 0

    def create(self, p, q, e) :
        if isprime(p) == False:
            print(p)
            raise ValueError("p is not prime")

        if isprime(q) == False:
            raise ValueError("q is not prime")

        self.p = p  # 0: this class is to encrypt
        self.q = q  # 0: this class is to encrypt
        self.n = p*q
        self.phi_n = (p - 1) * (q - 1)
        self.e = e   # public key
        self.d = self.calc_private_key()   # private key

    def public_init(self, e, n):
        self.n = n
        self.e = e   # public key

    # calculate d(private key) as the modular inverse of
    # e(public key) modulo phi_n
    def calc_private_key(self):
        # Check if e and phi_n are coprime
        if gcd(self.e, self.phi_n) != 1:
            raise ValueError("e and phi_n are not coprime, so the modular inverse of e does not exist.")

        return  mod_inverse(self.e, self.phi_n)
        
    def encrypt(self, m):
        return pow(m, self.e, self.n)

    def decrypt(self, c):
        if self.d == 0:
            raise ValueError("private key is not available")
       
        return (pow(c, self.d, self.n))

    def get_e(self):
        return self.e

    def get_n(self):
        return self.n
