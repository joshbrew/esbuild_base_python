# create thread
# create socket server on thread
# stream data 

## Settings
host = 'localhost'
port = 7000

## app available at http://localhost/7000
 
import sys
import asyncio
import threading
import time
import logging
from functools import wraps

# from mangum import Mangum
from quart import Quart, render_template, websocket


app = Quart(__name__, template_folder='./')

# handler = Mangum(app)  # optionally set debug=True ### for serverless

# In python command line:
# python sockerserver.py


## Socket server functions


############# 
## Wrapper 

### Sets up an asyncio queue which can broadcast received data to all connections
connected_websockets = set()

main_queue = asyncio.Queue() ## http://pymotw.com/2/Queue/

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

async def broadcast(message):
    global connected_websockets 
    for queue in connected_websockets: ## add new message to each websocket queue
        await queue.put(message)
##

## transmitter loop, runs per-socket
async def sending(queue):
    while True:
        data = await queue.get() ## get next data on queue
        await websocket.send(data) ## send the queue data added on this socket
        #await websocket.send_json(data)
##

## receiver loop, runs per-socket
async def receiving(delay =2):
    try:
        while True:
            data = await websocket.receive()
            broadcast(data) ## relay any received data back to all connections (test)
    except asyncio.CancelledError:
        # Handle disconnection here
        await websocket.close(1000)
        raise    
##

    
async def queue_from_thread():
    try:
        await put_queue()
    except asyncio.CancelledError:
        raise

###################
## Test tasks to emit random numbers instead of relaying messages
async def test_transmitter(num):
    while True:
        await queue.put(num + random.random())
        await asyncio.sleep(random.random())

async def test_receiver(num):
    while True:
        value = await queue.get()
        print('Consumed', num, value)
###################


## websocket setup. For each websocket created, this coroutine is added
@app.websocket('/')
@collect_websocket
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
    return await render_template('index.html')



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
async def test_thread(queue, ctr=0):
    result = "Thread Running: " + str(ctr)
    global connected_websockets 
    for queue in connected_websockets: ## add new message to each websocket queue   
        await queue.put(result)
    logging.info(result)
    return ctr+1


## thread loop routine
async def _thread(queue, delay=2):
    try:
        ctr = 0
        while True & threading.main_thread().is_alive():
            ctr = await test_thread(queue, ctr)
            time.sleep(delay)
    except asyncio.CancelledError:
        raise

## set up the thread asyncio event loop
def thread_loop(queue, delay=2):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_thread(queue, delay))
    loop.close()


def threadSetup():   
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Thread being created")
    x = threading.Thread(target=thread_loop, args=(main_queue,2,))
    logging.info("Thread starting")
    #x.daemon = True

    x.start()
    logging.info("Thread running")
    



if __name__ == "__main__":

    threadSetup()  # set up background tasks

    app.run(host=host, port=port) # run the quart server

####


