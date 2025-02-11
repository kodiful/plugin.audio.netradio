#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

json_file = sys.argv[1]

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.loads(f.read())

with open(json_file, 'w', encoding='utf-8') as f:
    f.write(json.dumps(data, indent=2, ensure_ascii=False))
