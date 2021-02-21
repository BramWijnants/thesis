#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 17:28:31 2021

@author: bram
"""
import base64
from Crypto.Util.number import long_to_bytes

list_question = [99, 114, 121, 112, 116, 111, 123, 65, 83, 67, 73, 73, 95, 112, 114, 49, 110, 116, 52, 98, 108, 51, 125]

flag = ''

for i in list_question:
    flag += chr(i)

print(flag)


hex_string = '72bca9b68fc16ac7beeb8f849dca1d8a783e8acf9679bf9269f7bf'

bytes_string = bytes.fromhex(hex_string)

encodedBytes = base64.b64encode(bytes_string)
encodedStr = str(encodedBytes, "utf-8")




s = 11515195063862318899931685488813747395775516287289682636499965282714637259206269

long_to_bytes(s)
