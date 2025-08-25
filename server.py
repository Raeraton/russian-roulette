import socket
import hashlib
from threading import Thread, Lock
from time import time as time_now, sleep
from random import randrange
from json import dumps, loads




# game datas
keys_mutex = Lock()
keys = [ "test" ]

online_keys_mutex = Lock()
online_keys = []

players_mutex = Lock()
players = {
    "test": {
        "last-heartbeat" : 1234,
        "bullet-pos" : 5,
        "actual-pos" : 0,
        "actual-ip" : '',
        "score" : 0
    }
}


try:
    with open("db.json", "rt") as file:
        keys, players = loads( file.read() )
        file.close()
except:
    print( "cannot read db from disc" )





# functions

TO_TIME = 5   # after 10 sec every player will be logger out
TO_TEST_FREQ = 1 # usudnow
def timeout_test():
    global online_keys, online_keys_mutex, players, players_mutex

    online_keys_mutex.acquire()
    players_mutex.acquire()

    print( players, '\n', online_keys, '\n\n\n\n' )

    time = time_now()
    list_of_online_player = online_keys.copy()
    for name in list_of_online_player:
        last_heartbeat = players[name]["last-heartbeat"]
        if time - last_heartbeat > TO_TIME:
            online_keys.remove( name )
            players[name]["actual-ip"] = ''

    online_keys_mutex.release()
    players_mutex.release()

def save_db():
    global keys, keys_mutex, players, players_mutex
    keys_mutex.acquire()
    players_mutex.acquire()

    with open( "db.json", "wt" ) as file:
        file.write( dumps([keys, players]) )
        file.close()
    
    keys_mutex.release()
    players_mutex.release()

def timeout_loop():
    while 1:
        timeout_test()
        save_db()

        sleep(TO_TEST_FREQ)




def handle_login( client: socket.socket, client_ip: str ):
    global keys, keys_mutex, players, players_mutex, online_keys, online_keys_mutex

    buff = client.recv(100*1024*1024)

    buff = hashlib.sha256(buff)

    name = buff.hexdigest()

    online_keys_mutex.acquire()
    
    if name in online_keys:
        online_keys_mutex.release()
        client.send(b'ERROR')
        return

    keys_mutex.acquire()
    if name in keys:
        players_mutex.acquire()
        
        players[name]["last-heartbeat"] = time_now()
        
        online_keys.append(name)
        players[name]["actual-ip"] = client_ip

        players_mutex.release()

    online_keys_mutex.release()
    keys_mutex.release()

    client.send(b'SUCCE')

def handle_heartbeat(client: socket.socket, client_ip: str):
    global players, players_mutex

    players_mutex.acquire()
    succ = False
    for name in players:
        if players[name]["actual-ip"] == client_ip:
            players[name]["last-heartbeat"] = time_now()
            succ = True
            break
    players_mutex.release()
    
    if succ:
        client.send(b"SUCCE")
    else:
        client.send(b"ERROR")


def handle_shoot(client: socket.socket, client_ip: str):
    global players, players_mutex, keys, keys_mutex, online_keys, online_keys_mutex

    players_mutex.acquire()
    player_key = ''
    for name in players:
        if client_ip == players[name]["actual-ip"]:
            player_key = name
            players[name]["last-heartbeat"] = time_now()
            break
    
    if player_key == '':
        players_mutex.release()
        client.send( b'ERROR' )
        return
    
    if players[player_key]["bullet-pos"] == players[player_key]["actual-pos"]:
        keys_mutex.acquire()
        online_keys_mutex.acquire()

        del players[player_key]
        keys.remove(player_key)
        online_keys.remove(player_key)

        players_mutex.release()
        keys_mutex.release()
        online_keys_mutex.release()

        client.send(b'DEATH')
        return


    players[player_key]["actual-pos"] += 1
    if players[player_key]["actual-pos"] > 5:   players[player_key]["actual-pos"] = 0  # just for some fucked up bug

    players[player_key]["score"] += players[player_key]["actual-pos"]
    
    players_mutex.release()
    client.send( b'SURVI' )


def handle_reload(client: socket.socket, client_ip: str):
    global players, players_mutex

    players_mutex.acquire()
    player_key = ''
    for name in players:
        if client_ip == players[name]["actual-ip"]:
            player_key = name
            players[name]["last-heartbeat"] = time_now()
            break
    
    if player_key == '':
        players_mutex.release()
        client.send( b'ERROR' )
        return
    
    players[player_key]["actual-pos"] = 0
    players[player_key]["bullet-pos"] = randrange(6)
    
    players_mutex.release()
    client.send( b'RELOA' )


def handle_score(client: socket.socket, client_ip: str):
    global players, players_mutex

    players_mutex.acquire()
    player_key = ''
    for name in players:
        if client_ip == players[name]["actual-ip"]:
            player_key = name
            players[name]["last-heartbeat"] = time_now()
            break
    
    if player_key == '':
        players_mutex.release()
        client.send( b'ERROR' )
        return
    
    score = str( players[player_key]["score"] ).encode()
    players_mutex.release()

    if len( score ) > 1024: score = score[:1024]
    client.send( b'SUCCE' )
    client.send( score )


def handle_client( client: socket.socket, client_ip: str ):
    buff = client.recv(5)

    print( client_ip, buff, "<->", time_now() )

    if buff == b'LOGIN':
        handle_login( client, client_ip )
    elif buff == b'HEART':
        handle_heartbeat( client, client_ip )
    elif buff == b'SHOOT':
        handle_shoot(client, client_ip)
    elif buff == b'RELOA':
        handle_reload( client, client_ip )
    elif buff == b'SCORE':
        handle_score( client, client_ip )
    
    client.close()



# connection
IP = socket.gethostbyname( socket.gethostname() )
PORT = 61

sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

sock.bind( ( IP, PORT ) )
sock.listen( 5 )



# runing
tester_thread = Thread( target=timeout_loop )
tester_thread.start()

print(f"runing on {IP}:{PORT}")
while 1:
    client, addr = sock.accept()
    th = Thread( target=handle_client, args=(client, addr[0]) )
    th.start()

#szeriii(veri)