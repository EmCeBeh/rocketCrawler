#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 14:20:16 2020

@author: dscran
"""


import requests
import re
import sys, os
import ssl


def login(login_data):
    login = requests.post('https://chat.gwdg.de/api/v1/login', data=login_data)
    if login.json()['status'] == 'success':
        #getting login credentials
        name = login.json()['data']['me']['_id']
        token = login.json()['data']['authToken']
        hds = {'X-Auth-Token': token, 'X-User-Id': name}
        print('Login did work :) \n')
    else:
        print('Login did not work :( \n')
    return hds

def download_image(url, filename, hds):
    r = requests.get(url, headers=hds).json()
    with open(filename, 'wb') as f:
        f.write(r.content)

if __name__ == "__main__":
    if '--nocertcheck' in sys.argv[1:]:
        import ssl
#        if True:
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

    folder = './test/'
    if not(os.path.exists(folder + 'png/')):
        print("Creating folder " + folder + 'png/')
        os.mkdir(folder + 'png/')


    # login
    login_data = {'user': 'kathinka.gerlinger@mbi-berlin.de', 'password': 'XKF>9?=t3JESQ@8e'}
    hds = login(login_data)


    # get text
    with open(folder + 'test.md') as f:
        text = ''.join(f.readlines())

    # find urls
    re_image = re.compile(r'https://chat.gwdg.de/ufs/FileSystem:Uploads/.*/.*')
    images = re_image.findall(text)

    #download images and save them, replace url with markdown image inclusion
    for i, s in enumerate(images):
        if s[-1] == ')':
            s_n = s[:-1]
        else:
            s_n = s
        print(i, s, s_n)
        fmt = s_n[-3:]
        if not ((fmt == 'JPG') or (fmt == 'jpg')):
            fmt = 'png'
        fname = f'2009_P04_{i:03d}.{fmt}'
        download_image(s_n, folder + f'png/{fname}', hds)
        text = re.sub(s, f'![](png/{fname} =300x)', text)

    # write new text into file
    with open(folder + 'test2.md', 'w') as f:
        f.write(text)