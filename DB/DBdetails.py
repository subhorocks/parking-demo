from parking.DB import connector
def Dbdetails():
    con_obj=connector.config()
    host = con_obj['host']
    port = con_obj['port']
    database = con_obj['database']
    user = con_obj['user']
    password = con_obj['password']
    return host,port,database, user, password



