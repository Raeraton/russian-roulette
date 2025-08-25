import socket
from time import sleep
from threading import Thread, Lock

IP_PORT = ( "192.168.1.77", 61 )


# logging
log_mutex = Lock()
def log( *values: object, sep:str=' ', end:str='\n' ):
    global log_mutex

    tolog = ''
    for i in range( len(values)-1 ):
        v = values[i]
        try:
            v0 = v.decode()
            v = v0
        except: 
            v = str(v)
        tolog += v + sep
    
    v = values[len(values)-1]
    try:
            v0 = v.decode()
            v = v0
    except:
        v = str(v)
    tolog += v
    tolog += end

    log_mutex.acquire()
    with open( "log.txt", "at" ) as file:
        file.write( tolog )
        file.close()
    log_mutex.release()


# requests
request_mutex = Lock()

def request_login( uname: bytes ) -> bool:
    global request_mutex
    request_mutex.acquire()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(IP_PORT)

    sock.send( b'LOGIN' )
    sock.send(uname)
    buff = sock.recv(5)

    request_mutex.release()

    log("login", buff)
    

    return buff == b'SUCCE'

def request_heartbeat() -> bool:
    global request_mutex
    request_mutex.acquire()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(IP_PORT)

    sock.send( b'HEART' )
    buff = sock.recv(5)

    request_mutex.release()

    log("heathbeat", buff)
    

    return buff == b'SUCCE'

def request_shoot() -> bool:
    global request_mutex
    request_mutex.acquire()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(IP_PORT)

    sock.send( b'SHOOT' )
    buff = sock.recv(5)
    
    request_mutex.release()

    log("shoot", buff)

    return buff == b'SURVI'


def request_reload() -> bool:
    global request_mutex
    request_mutex.acquire()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(IP_PORT)

    sock.send( b'RELOA' )
    buff = sock.recv(5)

    request_mutex.release()

    log("reload", buff)

    return buff == b'RELOA'


def request_score() -> int:
    global request_mutex
    request_mutex.acquire()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(IP_PORT)

    sock.send( b'SCORE' )
    buff = sock.recv(5)

    if buff != b'SUCCE':
        return -1


    sc = int(sock.recv(1024).decode())
    request_mutex.release()
    
    log("score", buff, sc)

    return sc



# threads
def hb_thread():
    run = True
    while run:
        run = request_heartbeat()
        sleep(1)








# run
fn = input("enter key path -&")

key: bytes
with open( fn, "rb" ) as file:
    key = file.read()
    file.close()

if request_login(key):
    

    hbth = Thread( target=hb_thread )
    hbth.start()



    run = True
    while run:
        action = input("Enter your action: ").lower()


        if action == "help":
            print( "shoot, reload, score" )
        elif action == "shoot":
            run = request_shoot()
        elif action == "reload":
            run = request_reload()
        elif action == "score":
            score = request_score()
            run = score != -1
            print( "your score is", score )
        else:
            print( "no command exist such as", action )

