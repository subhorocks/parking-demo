from configparser import ConfigParser
import psycopg2
def config(filename='D:\\workspace\\parking\\DB\\database.ini',section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db={}
    if parser.has_section(section):
        params=  parser.items(section)
        #print(params) # return list of tupple

        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception("section is {} is not available in the file {}".format(section,filename))
    return db

def connect():
    db = config()

    conn = psycopg2.connect(
        host=db['host'],
        database=db['database'],
        user=db['user'],
        password=db['password'])
    return conn

# print(connect())
# (print(config()))

# import base64
# db = config()
# password = db['password'].encode("utf-8")
# encoded = base64.b64encode(password)
# print(password)
# print(encoded)










