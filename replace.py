#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22, 2020

@author: KG
"""

import re

folder = '/home/gerlinger/Dokumente/Beamtimes/2020-01_MAXYMUS/'

with open(folder + 'RocketChat.md') as f:
    text = ''.join(f.readlines())

text = re.sub(r'\\\*', '*', text)

with open(folder + 'RocketChat.md', 'w') as f:
    f.write(text)