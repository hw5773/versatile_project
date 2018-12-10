import json
import os
import paho.mqtt.client as mqtt
import hashlib
import codecs
import time
import MySQLdb

SQL_HOST = "localhost"
SQL_PORT = 3306
SQL_USERNAME = "root"
SQL_PASSWORD = "mmlab"
SQL_DB = "mydb"
SQL_TABLE = None


# IP, Port # of universal broker & DB
#broker = "iot.eclipse.org"
broker = "147.46.114.149"
#db_broker = "202.30.19.96"
#db_broker = "147.46.114.113"

# global variable for manage number in service ID
deviceID_cache = {}
dbQuery_cache = {}
collision_inc = 4

db_insert = "insert" 
db_select = "select"
db_delete = "delete"
db_update = "update"

db = MySQLdb.connect(SQL_HOST, SQL_USERNAME, SQL_PASSWORD, SQL_DB)
cursor = db.cursor(MySQLdb.cursors.DictCursor)


def db_proc(topic, data):
    #print (time.time(), "db_proc start")
    #db = MySQLdb.connect(SQL_HOST, SQL_USERNAME, SQL_PASSWORD, SQL_DB)
    #cursor = db.cursor(MySQLdb.cursors.DictCursor)

    if topic == db_insert:
        #data = json.loads(payload.decode("utf-8"))
        SQL_TABLE = data['table']
        length = len(data['data'])
        for i in range(0, length):
            query = "INSERT INTO {0} SET ".format(SQL_TABLE)
            for index, (col, value) in enumerate(data['data'][i].items()):
                if isinstance(value, list):
                    value = [v.encode('unicode_escape') for v in value]
                    value = str(value).replace("\'", "\\\'")
                if index == 0:
                    query = query + "{0} = '{1}'".format(col, value)
                else:
                    query = query + ", "
                    query = query + "{0} = '{1}'".format(col, value)
            cursor.execute(query)
        db.commit()
        result = {"error" : 0}
        return result

    elif topic == db_select:
        #data = json.loads(payload.decode("utf-8"))
        if data['data'][0].get('category') == 'Sensor':
            result = {"error":0, "data":["8040f067c1cd83962abf3599de79c1abb77b2f026d", "80ce209e43e85f0089649a0be19d16ea2da0c84e82"]}
            return result
        else:
            SQL_TABLE = data['table']
            query = "SELECT * FROM {0} WHERE ".format(SQL_TABLE)
            for index, (col, value) in enumerate(data['data'][0].items()):
                if index == 0:
                    query = query + "{0} = '{1}'".format(col, value)
                else:
                    query = query + " and "
                    query = query + "{0} = '{1}'".format(col, value)
            cursor.execute(query)
            result = {"error":0, "data":cursor.fetchall()}
            return result 


def send_DBquery(query, topic, wait):

    #queryID = codecs.encode(os.urandom(4), 'hex_codec').decode()
    #queryID = '0x' + queryID
    #while queryID in dbQuery_cache:
    #    queryID = codecs.encode(os.urandom(4), 'hex_codec').decode()
    #    queryID = '0x' + queryID

    #topic = topic + '/' + queryID

    #print (topic, query)
    #db_client.publish(topic, query)
    
    # call db processing
    result = db_proc(topic, query)

    #wait response from DB
    #if wait:
    #    while dbQuery_cache[queryID] == "None":
    #        continue
    return result


def gen_flag(cache_bit, segment_bit, collision_mngt):
   
    flag = 0
    if collision_mngt > 15:
        raise Exception ('Collision range error')
    
    if cache_bit:
       flag = flag | 128
    
    if segment_bit:
        flag = flag | 64

    collision_mngt = collision_mngt << 2
    flag = flag | collision_mngt

    return flag


def join_genID(deviceID, flag):

    # deviceID's cache bit and segment flag are 0, thus only use 4 bit management number
    newID = str(flag) + deviceID
   
    while newID in deviceID_cache:
        flag = flag + collision_inc
        newID = str(flag) + deviceID
    deviceID_cache[newID] = "None"
   
    #print ("\nCheck DeviceID collision...")
    db_query = {'table':'Device', 'data':[{'deviceId':newID}]}
    payload = db_proc(db_select, db_query)

    # TODO:check if the data exists
    #payload = dbQuery_cache[queryID]
    exist = payload.get('data')

    #del dbQuery_cache[queryID]
   
    deviceID_cache[newID] = True
    if exist is '' or not exist:
        return newID
    else:
        return join_genID(deviceID, flag + collision_inc)


def convert_utf(relay):
    if relay == "none":
        return relay
    else:
        new_relay = []
        for node in relay:
            new_relay.append(node.encode('utf-8'))

        return new_relay


def join(tempID, payload):

    print(time.time(), "start")
    #print ("\n\n ##Process - Join\n")
    relay = payload.get('relay') 

    try:
        error = 0
        
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
            
        #print ("Temporary DeviceID: " + deviceID)
 
        # Device ID collision check
        deviceID = join_genID(deviceID, 0)
        #print ("Generated DeviceID: " + deviceID)

        pubKey = payload.get('pubKey')

        neighbors = payload.get('neighbors')
        if neighbors is None:
            neighbors = "NULL"
       
        #print ("\n----------Device Info.----------")
        info_list = []
        uniqueCodes = payload.get('uniqueCodes')
        for data in uniqueCodes:
            ifaceType = data.get('ifaceType')
            hwAddress = data.get('hwAddress')
            ipv4 = data.get('ipv4')
            wifiSSID = data.get('wifiSSID')
            if ifaceType is None:
                ifaceType = "NULL"
            if hwAddress is None:
                ifaceType = "NULL"
            if ipv4 is None:
                ipv4 = "NULL" 
            if wifiSSID is None:
                wifiSSID = "NULL"

            temp_dict = {'deviceId':deviceID, 'relay':relay, 'pubKey':pubKey, 'ifaceType':ifaceType, 'hwAddress':hwAddress, 'ipv4':ipv4, 'wifiSSID':wifiSSID}
            info_list.append(temp_dict)
            #print ("Interface: " + ifaceType)
            #print ("Mac address: " + hwAddress)
            #print ("IPv4 address: " + ipv4)
            #print ("wifiSSID: " + wifiSSID)
        
        db_query = {'table':'Device', 'data':info_list}
        db_payload = db_proc(db_insert, db_query)
        #db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('Join DB error')
        del db_query

        neighbor_list = []
        #print ("\n----------Neighbor info.----------")
        for neighbor in neighbors:
            neighborIface = neighbor.get('neighborIface')
            neighborIpv4 = neighbor.get('neighborIpv4')
            neighborHwAddress = neighbor.get('neighborHwAddress')
            neighborFlexID = neighbor.get('neighborFlexID')
            if (neighborIface is None) or (neighborIface == "none"):
                neighborIface = "NULL"
            if (neighborIpv4 is None) or (neighborIpv4 == "none"):
                neighborIpv4 = "NULL"
            if (neighborHwAddress is None) or (neighborHwAddress == "none"):
                neighborHwAddress = "NULL"
            if (neighborFlexID is None) or (neighborFlexID == "none"):
                raise Exception ('Neighbor FlexID error')

            #print ("neighborIface: " + neighborIface)
            #print ("neighborIpv4: " + neighborIpv4)
            #print ("neighborHwAddress: " + neighborHwAddress)
            #print ("neighborFlexID: " + neighborFlexID)
            temp_dict = {'neighborIface':neighborIface, 'neighborIpv4':neighborIpv4, 'neighborHwAddress':neighborHwAddress, 'neighborId':neighborFlexID, 'deviceId':deviceID}
            neighbor_list.append(temp_dict)
       
        db_query = {'table':'Neighbor', 'data':neighbor_list}
        db_payload = db_proc(db_insert, db_query)
        #db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('Join DB error')
        del db_query

        #print ("\nDB Update Completed..")
        query = {"error:": error, "id": deviceID, "relay": relay}
        query = json.dumps(query)
        print(time.time(), "end")
        client.publish("/configuration/join_ack/" + tempID, query)
        #print("/configuration/join_ack/" + tempID, query)

        print ("\n ##Process Completed - Join\n")

    except Exception as e:
        error = 1
        print ("Join error: ", e)
        query = {"error:": error, "deviceID":tempID, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/join_ack/" + tempID, query)


# Unjoin the target device
def leave(tempID, payload):
    print ("\n\n ##Process - Leave\n")

    relay = payload.get('relay')
    try:
        error = 0
        
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
 
        print ("Device ID: " + deviceID)

        db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
        db_payload = send_DBquery(db_query, db_delete, True)
        #db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('Leave DB error')
        #del dbQuery_cache[queryID]
   
        del deviceID_cache[deviceID]
    
        print ("\nDB Update Completed..")
        query = {"error:": error, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/leave_ack/" + tempID, query)
        
        print ("\n ##Process Completed - Leave\n")


    except Exception as e:
        error = 1
        print ("Leave error: ", e)
        query = {"error:": error, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/leave_ack/" + tempID, query)
 
 

def register_genID(hash_val, flag):

    newID = str(flag) + hash_val
   
    print ("\nCheck ID collision...\n")
    db_query = {'table':'RegisterList', 'data':[{'providingId':newID}]}
    payload = send_DBquery(db_query, db_select, True)

    #payload = dbQuery_cache[queryID]
    exist = payload.get('data')

    #del dbQuery_cache[queryID]

    if exist is '' or not exist:
        return newID
    else:
        return register_genID(hash_val, flag + collision_inc)



def register(tempID, payload):
    print ("\n\n ##Process - Register\n")     
    
    relay = payload.get('relay')
    registerID = payload.get('registerID')
    try:
        error = 0
        
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
            
        print ("DeviceID: " + deviceID)

        # Check whether the device exists 
        if deviceID in deviceID_cache:
            exist = True
        else:
            db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
            db_payload = send_DBquery(db_query, db_select, True)
            #db_payload = dbQuery_cache[queryID]
            exist = db_payload.get('data')
            #del dbQuery_cache[queryID]
            if exist is '' or not exist:
                raise Exception ('No Device Error')
            else:
                deviceID_cache[deviceID] = True

        registerList = payload.get('registerList')

        idList = []
        regList = []
        for item in registerList:
            attrList = []
            index = item.get('index')
            registerType = item.get('registerType')
            category = item.get('category')
            cache = item.get('cache')
            segment = item.get('segment')
            collisionAvoid = item.get('collisionAvoid')
            attributes = item.get('attributes')
            attr_idx = 0
            for attr in attributes:
                attr_idx = attr_idx + 1
                attrList.append(attr)

            # generate service/content ID
            hash_val = item.get('hash')
            flag = gen_flag(cache, segment, 0)
            
            if collisionAvoid:
                newID = register_genID(hash_val, flag)
            else:
                newID = str(flag) + hash_val
            
            temp = {index:newID}

            print ("\nGenerated ID of index " + index + ": " + newID)
            idList.append(temp)

            
            temp_data = {'deviceId':deviceID, 'providingId':newID, 'hash':hash_val, 'registerType':registerType, 'category':category}
            for i in range (attr_idx):
                attr_key = 'attr' + str(i+1)
                attr_val = attrList[i]
                temp_data[attr_key] = attr_val
            
            regList.append(temp_data)
           
        db_query = {'table':'RegisterList', 'data':regList}
        payload = send_DBquery(db_query, db_insert, True)
        #payload = dbQuery_cache[queryID]
        db_error = payload.get('error')
        if db_error is not 0:
            raise Exception ("Register DB error")
        #del dbQuery_cache[queryID]
        

        print ("\nDB Update Completed..")
        query = {"error:": error, "registerID": registerID, "idList": idList, "relay": relay}
        query = json.dumps(query)
        client.publish("/configuration/register_ack/" + tempID, query)
        
        print ("\n ##Process Completed - Register\n")


    except Exception as e:
        error = 1
        print ("Register error: ", e)
        query = {"error": error, "registerID": registerID, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/register_ack/" + tempID, query)



def update(tempID, payload):
    print ("\n\n ##Process - Update\n")     
    
    updateID = payload.get('updateID')
    relay = payload.get('relay')

    try:
        error = 0
        
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
   
        print ("DeviceID: " + deviceID)
 
        # Check whether the device exists 
        if deviceID in deviceID_cache:
            exist = True
        else:
            db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
            db_payload = send_DBquery(db_query, db_select, True)
            #db_payload = dbQuery_cache[queryID]
            exist = db_payload.get('data')
            #del dbQuery_cache[queryID]
            if exist is '' or not exist:
                raise Exception ('No Device Error')
            else:
                deviceID_cache[deviceID] = True

        providingID = payload.get('id')
       
        # check if this content/service exists
        db_query = {}
        db_payload = send_DBquery(db_query, db_select, True)
        #db_payload = dbQuery_cache[queryID]
        exist = db_payload.get('data')
        #del dbQuery_cache[queryID]
        if exist is '' or not exist:
            raise Exception ('No Content/Service Error')

        # check deregister
        deregister = payload.get('deregister')
        if deregister:
            print ("\n-- Deregister the Service/Content")
            db_query = {'table':'RegisterList', 'data':[{'providingId':providingID}]}
            payload = send_DBquery(db_query, db_delete, True)
            #payload = dbQuery_cache[queryID]
            db_error = payload.get('error')
            if db_error is not 0:
                raise Exception ('Update DB error')
            #del dbQuery_cache[queryID]
        
        else:
            attributes = payload.get('attributes')
            attr_idx = 0
            attrList = []
            for attr in attributes:
                attr_idx = attr_idx + 1
                attrList.append(attr)
         
            temp_data = {}
            for i in range (attr_idx):
                attr_key = 'attr' + str(i+1)
                attr_val = attrList[i]
                temp_data[attr_key] = attr_val
            db_query = {'table':'RegisterList', 'sdata':[temp_data], 'wdata':[{'providingId':providingID}]}
            print (db_query)
            payload = send_DBquery(db_query, db_update, True)
            #payload = dbQuery_cache[queryID]
            db_error = payload.get('error')
            if db_error is not 0:
                raise Exception ('Update DB error')
            #del dbQuery_cache[queryID]

        print ("\nDB Update Completed..")
        
        query = {"error:": error, "updateID": updateID, "relay": relay}
        query = json.dumps(query)
        print (query)
        client.publish("/configuration/update_ack/" + tempID, query)
        
        print ("\n ##Process Completed - Update\n")


    except Exception as e:
        error = 1
        print ("Update error: ", e)
        query = {"error": error, "updateID": updateID, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/update_ack/" + tempID, query)



def query(tempID, payload):
    print ("\n ##Process - Query\n")
    time.sleep(1)
    queryID = payload.get('queryID')
    relay = payload.get('relay')

    try:
        error = 0
        
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
   
        print (" Query from: " + deviceID)
        time.sleep(1)

        print ("\n Check if this device exists..")
        time.sleep(1)
        
        # Check whether the device exists 
        if deviceID in deviceID_cache:
            exist = True
        else:
            db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
            db_payload = db_proc(db_select, db_query)
            #db_payload = dbQuery_cache[queryID]
            exist = db_payload.get('data')
            #del dbQuery_cache[queryID]
            if exist is '' or not exist:
                raise Exception ('No Device Error')
            else:
                deviceID_cache[deviceID] = True
        print ("\n > " + deviceID + ": exists in the network\n")

        queryType = payload.get('queryType')
        category = payload.get('category')
        order = payload.get('order')
        desc = payload.get('desc')
        limit = payload.get('limit')
        requirements = payload.get('requirements')
        additionalFields = payload.get('additionalFields')

        for req in requirements:
            attributeType = req.get('attributeType')
            unit = req.get('unit')
            value = req.get('value')
            operator = req.get('operator')

        time.sleep(1)
        print ("\n Searching " + queryType + "s..")
        time.sleep(1)
        #TODO: Search content/service from DB
        db_query = {'table':'RegisterList', 'data':[{'queryType':queryType, 'category':category, 'requirements':requirements}]}
        db_payload = db_proc(db_select, db_query)
        #db_payload = dbQuery_cache[queryID]
        data = db_payload.get('data')
        #del dbQuery_cache[queryID]
         
        ids = data
        print ("\n > Searched IDs:", ids, "\n")
        reply = {"error:": error, "queryID": queryID, "desc": desc, "ids": ids, "relay": relay}
        time.sleep(1)
        reply = json.dumps(reply)
        print ("\n <<< Publish")
        print (" -Topic: /utilization/reply/" + tempID)
        print (" -Payload:", reply)
        client.publish("/utilization/reply/" + tempID, reply)

        print ("\n ##Process Completed - Query\n")


    except Exception as e:
        error = 1
        print ("Query error: ", e)
        reply = {"error": error, "queryID": queryID, "relay":relay}
        reply = json.dumps(reply)
        client.publish("/utilization/reply/" + tempID, reply)




def on_connect(client, userdata, flags, rc):
    print ("Connected with the Message Bus\n")
    # communication with end-user
    client.subscribe("/configuration/join/#")
    client.subscribe("/configuration/leave/#")
    client.subscribe("/configuration/register/#")
    client.subscribe("/configuration/update/#")
    client.subscribe("/utilization/query/#")

def on_db_connect(client, userdata, flags, rc):
    print ("Connected with the Message Bus (DB)")
    # communication with DB
    client.subscribe("/dbquery/iack/flexMnger/#")
    client.subscribe("/dbquery/sack/flexMnger/#")
    client.subscribe("/dbquery/dack/flexMnger/#")
    client.subscribe("/dbquery/uack/flexMnger/#")



def on_message(client, userdata, msg):
    print (" >>> Subscribe")
    print (" -Topic:", msg.topic)
    topic = msg.topic.split('/')
    payload = json.loads(msg.payload.decode('utf-8'))
    print(" -Payload:", payload)
    if "configuration" == topic[1]:
        if "join" == topic[2]:
            deviceID = topic[3]
            join(deviceID, payload)
        elif "leave" == topic[2]:
            deviceID = topic[3]
            leave(deviceID, payload)
        elif "register" == topic[2]:
            deviceID = topic[3]
            register(deviceID, payload)
        elif "update" == topic[2]:
            deviceID = topic[3]
            update(deviceID, payload)
        else:
            print ("Message type error: " + msg.topic)
    
    elif "utilization" == topic[1]:
        if "query" == topic[2]:
            deviceID = topic[3]
            query(deviceID, payload)
        else:
            print ("Message type error: " + msg.topic)
    else:
        print ("Message type error: " + msg.topic)


def on_db_message(client, userdata, msg):
    topic = msg.topic.split('/')
    payload = json.loads(msg.payload.decode('utf-8'))
    print (" >> Subscribe (from DB)...")
    print (" - Topic:", msg.topic)
    queryID = topic[-1]
    dbQuery_cache[queryID] = payload
            


def on_publish(client, userdata, mid):
    print ("\n>> Publish a message\n")

def on_subscribe(client, userdata, mid, granted_qos):
    print ("\n<< Subscribe a message\n")

def on_db_subscribe(client, userdata, mid, granted_qos):
    print ("\n<< Subscribe a message from DB\n")


client = mqtt.Client()
#db_client = mqtt.Client()


client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, 1883, 60)

#db_client.on_connect = on_db_connect
#db_client.on_message = on_db_message
#db_client.on_publish = on_db_publish
#db_client.connect(db_broker, 1883, 60)
#db_client.connect(broker, 1883, 60)

if __name__ == "__main__":
    print("\n Start FlexID Manager...\n")
    #client.loop_forever()
    #db_client.loop_forever()
    while True:
        client.loop_start()
        #db_client.loop_start()
