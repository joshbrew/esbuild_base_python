# create thread
# create socket server on thread
# stream data 

## Settings
host = 'localhost'
port = 7000

## app available at http://localhost/7000
 
import sys
import os
import asyncio
import threading
import logging
import random
from functools import wraps

# from mangum import Mangum
from quart import Quart, render_template, render_template_string, websocket, send_from_directory

base_dir = '../'

app = Quart(__name__, template_folder=base_dir, static_folder=base_dir)

# handler = Mangum(app)  # optionally set debug=True ### for serverless

# In python command line:
# python server.py

#############################
## Socket server functions ##
#############################


## Send message to all connections
async def broadcast(message):
    global connected_websockets 
    for queue in connected_websockets: ## add new message to each websocket queue (created in collect_websocket)
        await queue.put(message)
##

## transmitter loop, runs per-socket
async def sending(queue):
    while True:
        data = await queue.get() ## get next data on queue (created in collect_websocket)
        await websocket.send(data) ## send the queue data added on this socket
        #await websocket.send_json(data)
##

## receiver loop, runs per-socket
async def receiving(delay =2):
    try:
        while True:
            data = await websocket.receive() # any websocket-received data will be broadcasted to all connections
            broadcast(data) ## relay any received data back to all connections (test)
    except asyncio.CancelledError:
        # Handle disconnection here
        await websocket.close(1000)
        raise    
##

###################
## Test task to emit random numbers to each connection instead of relaying messages
async def test_transmitter(num):
    while True:
        await broadcast(num * random.random())
        await asyncio.sleep(random.random())
###################

### Set up an asyncio queue for each new socket connection for broadcasting data
connected_websockets = set()

def collect_websocket(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global connected_websockets
        socket_rx_queue = asyncio.Queue()
        connected_websockets.add(socket_rx_queue)
        try:
            return await func(socket_rx_queue, *args, **kwargs)
        finally:
            connected_websockets.remove(socket_rx_queue)
    return wrapper
##############

## websocket setup. For each websocket created, these coroutines are added
@app.websocket('/')
@collect_websocket ## Wrapper passes the new socket's queue in
async def ws(queue):
    print('Adding socket', websocket)
    await websocket.accept()
    transmitter = asyncio.create_task(sending(queue)) ## transmitter task, process outgoing messages
    receiver = asyncio.create_task(receiving(2))      ## receiver task, process incoming messages
    await asyncio.gather(transmitter, receiver)

# JavaScript:
# var ws = new WebSocket('ws://' + document.domain + ':' + location.port + '/');
# ws.onmessage = function (event) {
#     console.log(event.data);
# };
# 
# ws.send('bob');

## test route for receiving messages
@app.route('/')
async def index():
    return await render_template('python/index.html')

## Can serv the built app from quart too
@app.route('/build')
async def build():
    return await render_template('src/index.html')

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

@app.route('/<path:path>')
async def get_resource(path):  # pragma: no cover
    p = path.split('/')
    l = len(p)
    return await app.send_static_file(path)

## page not found
@app.errorhandler(404)
async def pageNotFound(error):
    return await render_template_string("<h3>404: resource not found</h3>")

## resource not found
@app.errorhandler(500)
async def handle_exception(error):
    return await  render_template_string("<div>500</div>", e=error), 500 ## this isn't quite right

#############
## Run sync for whatever reason in quart
# def run_sync(func: Callable[..., Any]) -> Callable[..., Coroutine[Any, None, None]]:
#     @wraps(func)
#     async def wrapper(*args: Any, **kwargs: Any) -> Any:
#         loop = asyncio.get_running_loop()
#         result = await loop.run_in_executor(
#             None, copy_context().run, partial(func, *args, **kwargs)
#         )
#         return result

#     return wrapper
#############



#### thread setup

# Setup the socket server on the thread
# Set up the send/receive loop

        
## on each loop run this function
async def _thread_main(queue, ctr=0):
    result = "Thread Running: " + str(ctr)
    global connected_websockets 
    for queue in connected_websockets: ## add new message to each websocket queue for broadcasting results to connections
        await queue.put(result)
    logging.info(result)
    return ctr+1


## thread loop routine
async def _thread(queue, delay=2):
    try:
        ctr = 0
        while True & threading.main_thread().is_alive(): ## This should quit if the main thread quits
            ctr = await _thread_main(queue, ctr) ## Run the thread function
            await asyncio.sleep(delay) ## releases the task on the event loop
    except asyncio.CancelledError:
        raise

## set up the thread asyncio event loop
def thread_event_loop(queue, delay=2):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_thread(queue, delay))
    loop.close()



main_queue = asyncio.Queue() ## http://pymotw.com/2/Queue/


def threadSetup():   
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.info("Thread being created")


    x = threading.Thread(target=thread_event_loop, args=(main_queue,2,)) ## create the thread


    logging.info("Thread starting")
    #x.daemon = True
    x.start()
    logging.info("Thread running")
    
######

## MAIN, THIS IS WHAT RUNS
if __name__ == "__main__":

    threadSetup()  # set up background tasks

    app.run(host=host, port=port) # run the quart server

####


