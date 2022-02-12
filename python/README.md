# In python command line:

Make sure you have these pip packages (`pip install x` if not found):

```py
# from mangum import Mangum ## e.g. serverless
from quart import Quart, render_template, websocket #pip install
import logging #pip install
import asyncio 
import sys
import threading 
import time
from functools import wraps
```

Then run: 
`python server.py`

Then find `http://localhost:7000` to test the websocket


> Python is laaaame

For client.py `pip install websockets` also