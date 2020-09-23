'''@file flexIDMnger.py is an implementation of flex ID Manager
'''
import json
import os
import paho.mqtt.client as mqtt
import hashlib
import codecs


# IP, Port # of universal broker & DB
broker = "localhost"
db_broker = ""

# global 
deviceID_cache = {}
register_cache = {}
dbQuery_cache = {}
collision_inc = 4

db_insert = "/dbquery/insert/flexMnger" 
db_select = "/dbquery/select/flexMnger"
db_delete = "/dbquery/delete/flexMnger"
db_update = "/dbquery/update/flexMnger"


def get_value(payload, attr):
    if attr in payload:
        val = payload.get(attr)
        val = json.loads(val)
        return val.get('value')
    else:
        return None


def send_DBquery(query, topic, wait):
    queryID = codecs.encode(os.urandom(4), 'hex_codec').decode()
    queryID = '0x' + queryID
    while queryID in dbQuery_cache:
        queryID = codecs.encode(os.urandom(4), 'hex_codec').decode()
        queryID = '0x' + queryID

    #queryID = '0x' + '001'
    dbQuery_cache[queryID] = "None"
  
    query = json.dumps(query).encode('utf-8')
    topic = topic + '/' + queryID

    print (topic, query)
    db_client.publish(topic, query)

    #wait response from DB
    if wait:
        while dbQuery_cache[queryID] == "None":
            continue
    return queryID


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
    

    print ("\nCheck DeviceID collision...")
    newID = deviceID[:-1] + str(flag)
    while newID in deviceID_cache:
        flag = flag + collision_inc
        newID = deviceID[:-1] + str(flag)
    deviceID_cache[newID] = "None"
    
    #db_query = {'table':'Device', 'data':[{'deviceId':newID}]}
    #queryID = send_DBquery(db_query, db_select, True)

    # TODO:check if the data exists
    #payload = dbQuery_cache[queryID]
    #exist = payload.get('data')
    exist = False

    #del dbQuery_cache[queryID]
   
    deviceID_cache[newID] = True
    
    if exist is '' or not exist:
        return newID
    else:
        return join_genID(deviceID, flag + collision_inc)


def join(tempID, payload):

    print ("\n\n ##Process - Join\n") 

    relay = get_value(payload, 'relay') 
    if relay == None:
        relay = "none"

    try:
        error = 0
        
        if relay == "none" or relay == None:
            deviceID = tempID
        else:
            deviceID = relay[-1]
       
        print ("Temporary DeviceID: " + deviceID)
 
        # Device ID collision check
        deviceID = join_genID(deviceID, 0)
        print ("Generated DeviceID: " + deviceID)

        pubKey = get_value(payload, 'pubKey')
        if pubKey == None:
            raise Exception ('No Public Key') 
        
        print ("\n----------Device Info.----------")
        info_list = []
        
        uniqueCodes = get_value(payload, 'uniqueCodes')
        if uniqueCodes == "none" or uniqueCodes == None:
            uniqueCodes = []
        else:
            uniqueCodes = json.loads(uniqueCodes)

        for code in uniqueCodes:
            ifaceType = code.get('ifaceType')
            hwAddress = code.get('hwAddress')
            ipv4 = code.get('ipv4')
            wifiSSID = code.get('wifiSSID')
            if ifaceType is None:
                ifaceType = "none"
            if hwAddress is None:
                ifaceType = "none"
            if ipv4 is None:
                ipv4 = "none" 
            if wifiSSID is None:
                wifiSSID = "none"

            temp_dict = {'deviceId':deviceID, 'relay':relay, 'pubKey':pubKey, 'ifaceType':ifaceType, 'hwAddress':hwAddress, 'ipv4':ipv4, 'wifiSSID':wifiSSID}
            info_list.append(temp_dict)
            print ("Interface: " + ifaceType)
            print ("Mac address: " + hwAddress)
            print ("IPv4 address: " + ipv4)
            print ("wifiSSID: " + wifiSSID)
       
        #db_query = {'table':'Device', 'data':info_list}
        #queryID = send_DBquery(db_query, db_insert, True)
        #db_payload = dbQuery_cache[queryID]
        #db_error = db_payload.get('error')
        #if db_error is not 0:
        #    raise Exception ('Join DB error')
        #del db_query


        neighbor_list = []
        print ("\n----------Neighbor info.----------")
        nbors = get_value(payload, 'neighbors')
        if nbors == None:
            nbors = []
        
        for nbor in nbors:
            neighborIface = nbor.get('neighborIface')
            neighborIpv4 = nbor.get('neighborIpv4')
            neighborHwAddress = nbor.get('neighborHwAddress')
            neighborFlexID = nbor.get('neighborFlexID')
            if neighborIface is None:
                neighborIface = "none"
            if neighborIpv4 is None:
                neighborIpv4 = "none"
            if neighborHwAddress is None:
                neighborHwAddress = "none"
            if neighborFlexID is None:
                raise Exception ('Neighbor FlexID error')

            print ("neighborIface: " + neighborIface)
            print ("neighborIpv4: " + neighborIpv4)
            print ("neighborHwAddress: " + neighborHwAddress)
            print ("neighborFlexID: " + neighborFlexID)
            temp_dict = {'neighborIface':neighborIface, 'neighborIpv4':neighborIpv4, 'neighborHwAddress':neighborHwAddress, 'neighborId':neighborFlexID, 'deviceId':deviceID}
            neighbor_list.append(temp_dict)
      
        #db_query = {'table':'Neighbor', 'data':neighbor_list}
        #queryID = send_DBquery(db_query, db_insert, True)
        #db_payload = dbQuery_cache[queryID]
        #db_error = db_payload.get('error')
        #if db_error is not 0:
        #    raise Exception ('Join DB error')
        #del db_query

        print ("\nDB Update Completed..")
        query = {"error": error, "id": deviceID, "relay": relay}
        query = json.dumps(query)
        client.publish("/configuration/join_ack/" + tempID, query)
        print("/configuration/join_ack/" + tempID, query)

        print ("\n ##Process Completed - Join\n")

    except Exception as e:
        error = 1
        print ("Join error: ", e)
        query = {"error": error, "deviceID":tempID, "relay":relay}
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

        #db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
        #queryID = send_DBquery(db_query, db_delete, True)
        #db_payload = dbQuery_cache[queryID]
        #db_error = db_payload.get('error')
        #if db_error is not 0:
        #    raise Exception ('Leave DB error')
        #del dbQuery_cache[queryID]
   
        #del deviceID_cache[deviceID]
    
        print ("\nDB Update Completed..")
        query = {"error": error, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/leave_ack/" + tempID, query)
        
        print ("\n ##Process Completed - Leave\n")


    except Exception as e:
        error = 1
        print ("Leave error: ", e)
        query = {"error": error, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/leave_ack/" + tempID, query)
 
 

def register_genID(hash_val, flag):

    newID = hash_val + str(flag)
 
    while newID in register_cache:
        flag = flag + collision_inc
        newID = hash_val + str(flag)
    register_cache[newID] = True
   
    print ("\nCheck ID collision...\n")
    #db_query = {'table':'RegisterList', 'data':[{'providingId':newID}]}
    #queryID = send_DBquery(db_query, db_select, True)

    #payload = dbQuery_cache[queryID]
    #exist = payload.get('data')

    #del dbQuery_cache[queryID]

    exist = False
    if exist is '' or not exist:
        return newID
    else:
        return register_genID(hash_val, flag + collision_inc)



def register(tempID, payload):
    print ("\n\n ##Process - Register\n")     
 
    relay = get_value(payload, "relay")
    if relay == None:
        relay = "none"

    print("tempID:", tempID)
    try:
        registerID = get_value(payload, 'registerID')
        print("registerID:", registerID)
        
        error = 0
       
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
            
        print ("DeviceID: " + deviceID)

        # Check whether the device exists 
        if not (deviceID in deviceID_cache):
            print("Check deviceID validity")
            #db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
            #queryID = send_DBquery(db_query, db_select, True)
            #db_payload = dbQuery_cache[queryID]
            #exist = db_payload.get('data')
            #del dbQuery_cache[queryID]
            exist = True
            if exist is '' or not exist:
                raise Exception ('No Device Error')
            else:
                deviceID_cache[deviceID] = True

        registerList = get_value(payload, 'registerList')
        if registerList == "none" or registerList == None:
            registerList = []
        else:
            registerList = json.loads(registerList)
        
        print("registerList:")
        print(registerList)

        idList = []
        attrList = []
        regList = []
        for item in registerList:
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
                newID = hash_val + str(flag)
            
            temp = {index:newID}

            print ("\nGenerated ID of index " + index + ": " + newID)
            idList.append(temp)

            
            temp_data = {'deviceId':deviceID, 'providingId':newID, 'hash':hash_val, 'registerType':registerType, 'category':category}
            for i in range (attr_idx):
                attr_key = 'attr' + str(i+1)
                attr_val = attrList[i]
                temp_data[attr_key] = attr_val
            
            regList.append(temp_data)
           
        #db_query = {'table':'RegisterList', 'data':regList}
        #queryID = send_DBquery(db_query, db_insert, True)
        #payload = dbQuery_cache[queryID]
        #db_error = payload.get('error')
        #if db_error is not 0:
        #    raise Exception ("Register DB error")
        #del dbQuery_cache[queryID]
        

        print ("\nDB Update Completed..")
        query = {"error": error, "registerID": registerID, "idList": idList, "relay": relay}
        query = json.dumps(query)
        print(query)
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
            #db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
            #queryID = send_DBquery(db_query, db_select, True)
            #db_payload = dbQuery_cache[queryID]
            #exist = db_payload.get('data')
            #del dbQuery_cache[queryID]
            exist = True
            if exist is '' or not exist:
                raise Exception ('No Device Error')
            else:
                deviceID_cache[deviceID] = True

        providingID = payload.get('id')
       
        # check if this content/service exists
        #db_query = {}
        #queryID = send_DBquery(db_query, db_select, True)
        #db_payload = dbQuery_cache[queryID]
        #exist = db_payload.get('data')
        #del dbQuery_cache[queryID]
        exist = True
        if exist is '' or not exist:
            raise Exception ('No Content/Service Error')

        # check deregister
        deregister = payload.get('deregister')
        if deregister:
            print ("\n-- Deregister the Service/Content")
            #db_query = {'table':'RegisterList', 'data':[{'providingId':providingID}]}
            #queryID = send_DBquery(db_query, db_delete, True)
            #payload = dbQuery_cache[queryID]
            #db_error = payload.get('error')
            #if db_error is not 0:
            #    raise Exception ('Update DB error')
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
            #db_query = {'table':'RegisterList', 'sdata':[temp_data], 'wdata':[{'providingId':providingID}]}
            #print (db_query)
            #queryID = send_DBquery(db_query, db_update, True)
            #payload = dbQuery_cache[queryID]
            #db_error = payload.get('error')
            #if db_error is not 0:
            #    raise Exception ('Update DB error')
            #del dbQuery_cache[queryID]

        print ("\nDB Update Completed..")
        
        query = {"error": error, "updateID": updateID, "relay": relay}
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
     
    relay = get_value(payload, "relay")
    if relay == None:
        relay = "none"

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
            #queryID = send_DBquery(db_query, db_select, True)
            #db_payload = dbQuery_cache[queryID]
            #exist = db_payload.get('data')
            #del dbQuery_cache[queryID]
            #if exist is '' or not exist:
            #    raise Exception ('No Device Error')
            #else:
            #    deviceID_cache[deviceID] = True

        queryID = get_value(payload, 'queryID')
        queryType = get_value(payload, 'queryType')
        queryCategory = get_value(payload, 'queryCategory')
        order = get_value(payload, 'order')
        desc = bool(get_value(payload, 'desc'))
        limit = int(get_value(payload, 'limit'))
        additionalFields = get_value(payload, 'additionalFields')
        
        requirements = get_value(payload, 'requirements')
        if requirements == "none" or requirements == None:
            requirements = []
        else:
            requirements = json.loads(requirements)
 
        for req in requirements:
            attributeType = req.get('attributeType')
            unit = req.get('unit')
            value = req.get('value')
            operator = req.get('operator')

        print ("\nSearching " + queryType + "/" + queryCategory + "..")
        #TODO: Get content/service from DB
        #db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
        #queryID = send_DBquery(db_query, db_select, True)
        #db_payload = dbQuery_cache[queryID]
        #exist = db_payload.get('data')
        #del dbQuery_cache[queryID]
         
        ids = ['TempId1', 'TempId2']
        reply = {"error": error, "queryID": queryID, "desc": desc, "ids": ids, "relay": relay}
        reply = json.dumps(reply)
        print (reply)
        client.publish("/utilization/reply/" + tempID, reply)
        
        print ("\n ##Process Completed - Query\n")


    except Exception as e:
        error = 1
        print ("Query error: ", e)
        reply = {"error": error, "queryID": queryID, "relay":relay}
        reply = json.dumps(reply)
        client.publish("/utilization/reply/" + tempID, reply)


def map_update (tempID, payload):
    print ("\n ##Process - MapUpdate\n")     
     
    mapUpdateID = payload.get('mapUpdateID')
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
            #queryID = send_DBquery(db_query, db_select, True)
            #db_payload = dbQuery_cache[queryID]
            #exist = db_payload.get('data')
            #del dbQuery_cache[queryID]
            #if exist is '' or not exist:
            #    raise Exception ('No Device Error')
            #else:
            #    deviceID_cache[deviceID] = True

        # Update device information
        print ("\n---------- Update Device Info.----------")
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
            print ("Interface: " + ifaceType)
            print ("Mac address: " + hwAddress)
            print ("IPv4 address: " + ipv4)
            print ("wifiSSID: " + wifiSSID)
        
        #db_query = {'table':'Device', 'data':info_list}
        #queryID = send_DBquery(db_query, db_update, True)
        #db_payload = dbQuery_cache[queryID]
        #db_error = db_payload.get('error')
        #if db_error is not 0:
        #    raise Exception ('MapUpdate DB error')
        #del db_query

        neighbor_list = []
        print ("\n----------Update Neighbor info.----------")
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

            print ("neighborIface: " + neighborIface)
            print ("neighborIpv4: " + neighborIpv4)
            print ("neighborHwAddress: " + neighborHwAddress)
            print ("neighborFlexID: " + neighborFlexID)
            temp_dict = {'neighborIface':neighborIface, 'neighborIpv4':neighborIpv4, 'neighborHwAddress':neighborHwAddress, 'neighborId':neighborFlexID, 'deviceId':deviceID}
            neighbor_list.append(temp_dict)
       
        #db_query = {'table':'Neighbor', 'data':neighbor_list}
        #queryID = send_DBquery(db_query, db_update, True)
        #db_payload = dbQuery_cache[queryID]
        #db_error = db_payload.get('error')
        #if db_error is not 0:
        #    raise Exception ('MapUpdate DB error')
        #del db_query

        print ("\nDB Update Completed..")
        query = {"error": error, "mapUpdateID": mapUpdateID, "relay": relay}
        query = json.dumps(query)
        client.publish("/configuration/mapUpdate_ack/" + tempID, query)
        print("/configuration/mapUpdate_ack/" + tempID, query)

        print ("\n ##Process Completed - MapUpdate\n")

    except Exception as e:
        error = 1
        print ("MapUpdate error: ", e)
        query = {"error": error, "mapUpdateID": mapUpdateID, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/mapUpdate/" + tempID, query)



def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print ("Connected with the Message Bus ")
    else:
        print("Connection Fail, code=", rc)

    # communication with end-user
    client.subscribe("/configuration/join/#")
    client.subscribe("/configuration/leave/#")
    client.subscribe("/configuration/register/#")
    client.subscribe("/configuration/update/#")
    client.subscribe("/configuration/mapUpdate/#")
    client.subscribe("/utilization/query/#")

def on_db_connect(client, userdata, flags, rc):
    print ("Connected with the Message Bus ")
    # communication with DB
    client.subscribe("/dbquery/iack/flexMnger/#")
    client.subscribe("/dbquery/sack/flexMnger/#")
    client.subscribe("/dbquery/dack/flexMnger/#")
    client.subscribe("/dbquery/uack/flexMnger/#")



def on_message(client, userdata, msg):
    print ("Subscribe - Topic: " + msg.topic)
    topic = msg.topic.split('/')
    payload = json.loads(msg.payload.decode('utf-8'))
    print("Payload:", payload)
    print("\n")
    if "configuration" == topic[1]:
        if "join" == topic[2]:
            if len(topic) > 4:
                deviceID = "/".join(topic[3:])
            else:
                deviceID = topic[3]
            join(deviceID, payload)
        elif "leave" == topic[2]:
            if len(topic) > 4:
                deviceID = "/".join(topic[3:])
            else:
                deviceID = topic[3]
            leave(deviceID, payload)
        elif "register" == topic[2]:
            if len(topic) > 4:
                deviceID = "/".join(topic[3:])
            else:
                deviceID = topic[3]
            register(deviceID, payload)
        elif "update" == topic[2]:
            if len(topic) > 4:
                deviceID = "/".join(topic[3:])
            else:
                deviceID = topic[3]
            deviceID = topic[3]
            update(deviceID, payload)
        elif "mapUpdate" == topic[2]:
            if len(topic) > 4:
                deviceID = "/".join(topic[3:])
            else:
                deviceID = topic[3]
            deviceID = topic[3]
            map_update(deviceID, payload)
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
    print ("DB Subscribe - Topic: " + msg.topic)
    print ("             - Payload:", msg.payload)
    queryID = topic[-1]
    dbQuery_cache[queryID] = payload
            


def on_publish(client, userdata, mid):
    print ("\n>> Publish a message\n")

def on_subscribe(client, userdata, mid, granted_qos):
    print ("\n<< Subscribe a message\n")

def on_db_publish(client, userdata, mid):
    print ("\n>> Publish a message to DB\n")
 
def on_db_subscribe(client, userdata, mid, granted_qos):
    print ("\n<< Subscribe a message from DB\n")


client = mqtt.Client("", True, None, mqtt.MQTTv31)
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
