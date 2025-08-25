from random import randbytes
from json import loads, dumps
import hashlib


hashes = []

def make_file( pre: str, n: int ):
    global hashes

    buff = randbytes( 100*1024*1024 )
    with open( f"keys/{pre}_{n}key", "wb" ) as file:
        file.write(buff)
        file.close()

    hsh = hashlib.sha256( buff )
    hashes.append( hsh.hexdigest() )





f = [[], {}]
try:
    f0 = []
    with open( "db.json", "rt" ) as file:
        f = loads( file.read() )
        file.close()
    f = f0
except:
    print( "cannot open the db" )



num = int(input( "enter the number of keys: " ))
pre = input( "enter pre: " )


for i in range( num ):
    make_file( pre, i )



for h in hashes:
    f[0].append(h)
    f[1][h] = {
        "last-heartbeat" : 1234,
        "bullet-pos" : 5,
        "actual-pos" : 0,
        "actual-ip" : '',
        "score" : 0
    }



with open( "db.json", "wt" ) as file:
    file.write( dumps(f) )
    file.close()