'''
@file flexIDMnger.py is an implementation of flex ID Manager
'''
import json
import os
import paho.mqtt.client as mqtt
import hashlib
import codecs
import time


# IP, Port # of universal broker & DB
broker1 = ""
broker2 = ""
db_broker = ""

# global 
deviceID_cache = {}
dbQuery_cache = {}
collision_inc = 4

db_insert = "/dbquery/insert/flexMnger" 
db_select = "/dbquery/select/flexMnger"
db_delete = "/dbquery/delete/flexMnger"
db_update = "/dbquery/update/flexMnger"

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
    newID = deviceID + str(flag)
   
    while newID in deviceID_cache:
        flag = flag + collision_inc
        newID = deviceID + str(flag)
    deviceID_cache[newID] = "None"
    
    print ("\nCheck DeviceID collision...")
    db_query = {'table':'Device', 'data':[{'deviceId':newID}]}
    queryID = send_DBquery(db_query, db_select, True)

    return newID
    
    # check if the data exists
    payload = dbQuery_cache[queryID]
    exist = payload.get('data')

    del dbQuery_cache[queryID]
   
    deviceID_cache[newID] = True
    if exist is '' or not exist:
        return newID
    else:
        return join_genID(deviceID, flag + collision_inc)


def join(tempID, payload, flag):

    print ("\n\n ##Process - Join\n")
    relay = payload.get('relay')

    if flag == 1:
        myclient = client
    elif flag == 2:
        myclient = client2
    else:
        print("Something Wrong!!")

    try:
        error = 0
        
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
         
        print ("Temporary DeviceID: " + deviceID)

        # Device ID collision check
        deviceID = join_genID(deviceID, 0)
        print ("Generated DeviceID: " + deviceID)

        pubKey = payload.get('pubKey')

        neighbors = payload.get('neighbors')
        if neighbors is None:
            neighbors = "NULL"
       
        print ("\n----------Device Info.----------")
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
        
        db_query = {'table':'Device', 'data':info_list}
        queryID = send_DBquery(db_query, db_insert, True)
        db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('Join DB error')
        del db_query

        neighbor_list = []
        print ("\n----------Neighbor info.----------")
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
       
        db_query = {'table':'Neighbor', 'data':neighbor_list}
        queryID = send_DBquery(db_query, db_insert, True)
        db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('Join DB error')
        del db_query
        
        print ("\nDB Update Completed..")
        query = {"error:": error, "id": deviceID, "relay": relay}
        query = json.dumps(query)
        myclient.publish("/configuration/join_ack/" + tempID, query)
        print("/configuration/join_ack/" + tempID, query)

        print ("\n ##Process Completed - Join\n")

    except Exception as e:
        error = 1
        print ("Join error: ", e)
        query = {"error:": error, "deviceID":tempID, "relay":relay}
        query = json.dumps(query)
        myclient.publish("/configuration/join_ack/" + tempID, query)


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
        queryID = send_DBquery(db_query, db_delete, True)
        db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('Leave DB error')
        del dbQuery_cache[queryID]
   
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

    newID = hash_val + str(flag)
   
    print ("\nCheck ID collision...\n")
    db_query = {'table':'RegisterList', 'data':[{'providingId':newID}]}
    queryID = send_DBquery(db_query, db_select, True)

    payload = dbQuery_cache[queryID]
    exist = payload.get('data')

    del dbQuery_cache[queryID]

    if exist is '' or not exist:
        return newID
    else:
        return register_genID(hash_val, flag + collision_inc)

def deviceExist(deviceID):
    db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
    queryID = send_DBquery(db_query, db_select, True)
    db_payload = dbQuery_cache[queryID]
    exist = db_payload.get('data')
    del dbQuery_cache[queryID]
    if exist is '' or not exist:
        exist = False
        #raise Exception ('No Device Error')
    else:
        deviceID_cache[deviceID] = True
        exist = True
    return exist


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
            exist = deviceExist(deivceID)
            if not exist:
                raise Exception ('No Device Error')

        registerList = payload.get('registerList')

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
           
        db_query = {'table':'RegisterList', 'data':regList}
        queryID = send_DBquery(db_query, db_insert, True)
        payload = dbQuery_cache[queryID]
        db_error = payload.get('error')
        if db_error is not 0:
            raise Exception ("Register DB error")
        del dbQuery_cache[queryID]
        

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
            exist = deviceExist(deivceID)
            if not exist:
                raise Exception ('No Device Error')

        providingID = payload.get('id')

        # check if this content/service exists
        db_query = {}
        queryID = send_DBquery(db_query, db_select, True)
        db_payload = dbQuery_cache[queryID]
        exist = db_payload.get('data')
        del dbQuery_cache[queryID]
        if exist is '' or not exist:
            raise Exception ('No Content/Service Error')
        
        # check deregister
        deregister = payload.get('deregister')
        if deregister:
            print ("\n-- Deregister the Service/Content")
            db_query = {'table':'RegisterList', 'data':[{'providingId':providingID}]}
            queryID = send_DBquery(db_query, db_delete, True)
            payload = dbQuery_cache[queryID]
            db_error = payload.get('error')
            if db_error is not 0:
                raise Exception ('Update DB error')
            del dbQuery_cache[queryID]
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
            queryID = send_DBquery(db_query, db_update, True)
            payload = dbQuery_cache[queryID]
            db_error = payload.get('error')
            if db_error is not 0:
                raise Exception ('Update DB error')
            del dbQuery_cache[queryID]
        print ("\nDB Update Completed..")
        
        query = {"error:": error, "updateid": updateID, "relay": relay}
        query = json.dumps(query)
        print (query)
        client.publish("/configuration/update_ack/" + tempID, query)
        
        print ("\n ##process completed - update\n")


    except Exception as e:
        error = 1
        print ("Update error: ", e)
        query = {"error": error, "updateID": updateID, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/update_ack/" + tempID, query)



def query(tempID, payload):
    print ("\n ##Process - Query\n")     
     
    queryID = payload.get('queryID')
    relay = payload.get('relay')

    try:
        error = 0
        
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
   
        # Check whether the device exists 
        if deviceID in deviceID_cache:
            exist = True
        else:
            exist = deviceExist(deivceID)
            if not exist:
                raise Exception ('No Device Error')
        queryType = payload.get('queryType')
        category = payload.get('type')
        order = payload.get('order')
        desc = payload.get('desc')
        limit = payload.get('limit')
        qosRequirements = payload.get('qosRequirements')
        additionalFields = payload.get('additionalFields')

        for req in qosRequirements:
            metricType = req.get('metricType')
            metricUnit = req.get('metricUnit')
            metricValue = req.get('metricValue')
            metricOperator = req.get('metricOperator')

        #print ("\nSearching " + queryType + "..")
        # Search content/service from DB
        db_query = {'table':'Device', 'data':[{'deviceId':deviceID}]}
        queryID = send_DBquery(db_query, db_select, True)
        db_payload = dbQuery_cache[queryID]
        exist = db_payload.get('data')
        del dbQuery_cache[queryID]

        ids = ['TempId1', 'TempId2']
        reply = {"error:": error, "queryID": queryID, "desc": desc, "ids": ids, "relay": relay}
        reply = json.dumps(reply)
        #print (reply)
        client.publish("/utilization/reply/" + tempID, reply)
        
        print ("\n ##Process Completed - Query\n")


    except Exception as e:
        error = 1
        print ("Query error: ", e)
        reply = {"error": error, "queryID": queryID, "relay":relay}
        reply = json.dumps(reply)
        client.publish("/utilization/reply/" + tempID, reply)


def find_group(deviceID, attributes):
    
    # Search DB

    if len(attributes) == 1:
        data = {'attr1':attributes[0]}
    elif len(attributes) == 2:
        data = {'attr1':attributes[0], 'attr2':attributes[1]}
    elif len(attributes) == 3:
        data = {'attr1':attributes[0], 'attr2':attributes[1], 'attr3':attributes[2]}
    else:
        raise Exception ("Group attribute Error!\n")

    # find group
    db_query = {'table':'GroupList', 'data':[data]}
    queryID = send_DBquery(db_query, db_select, True)
    db_payload = dbQuery_cache[queryID]
    exist = db_payload.get('data')
    del dbQuery_cache[queryID]

    if exist is '' or not exist:
        return False 

    return exist


def gen_group(deviceID, attributes):

    # temp group ID
    newID = 'f2a0c067cfcd829625b8a1c2de79b1add72b28a269'

    # collision check

    data = {'groupId':newID, 'memberId':deviceID}
    db_query = {'table':'GroupMember', 'data':[data]}
    queryID = send_DBquery(db_query, db_insert, True)
    db_payload = dbQuery_cache[queryID]
    db_error = db_payload.get('error')
    if db_error is not 0:
        raise Exception ('Group Generate DB error1')
    del dbQuery_cache[db_query]


    if len(attributes) == 1:
        data = {'groupId':newID, 'attr1':attributes[0]}
    elif len(attributes) == 2:
        data = {'groupId':newID, 'attr1':attributes[0], 'attr2':attributes[1]}
    elif len(attributes) == 3:
        data = {'groupId':newID, 'attr1':attributes[0], 'attr2':attributes[1], 'attr3':attributes[2]}
    else:
        raise Exception ("Group attribute Error!\n");
        
    db_query = {'table':'GroupList', 'data':[data]}
    queryID = send_DBquery(db_query, db_insert, True)
    db_payload = dbQuery_cache[queryID]
    db_error = db_payload.get('error')
    if db_error is not 0:
        raise Exception ('Group Generate DB error2')
    del dbQuery_cache[db_query]

    group_id = [newID]
    return group_id


def group_join(tempID, payload):
    print ("\n ##Process - Group Join\n")     

    group_joinID = payload.get('gjoinID')
    relay = payload.get('relay')

    try:
        error = 0

        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]

        print("DeviceID: " + deviceID)

        # Check whether the device exists
        if deviceID in deviceID_cache:
            exist = True
        else:
            exist = deviceExist(deivceID)
            if not exist:
                raise Exception ('No Device Error')

        attributes = payload.get('attributes')
       
        # Find groups which satisfy conditions
        print ("Find Group... ")
        group_ids = find_group(attributes) #group_ids is a list of GroupID
        new = 0
        # If no group exist, generate new group
        if not group_ids:
            print ("Generate New Group...")
            group_ids = gen_group(attributes)
            new = 1

        query = {"error:": error, "gjoinID": group_joinID, "groupId": group_ids, "new":new, "relay": relay}
        query = json.dumps(query)
        print (query)
        client.publish("/configuration/group_join_ack/" + tempID, query)
        
        print ("\n ##process completed - Group Join\n")


    except Exception as e:
        error = 1
        print("Group Join error: ", e)
        query = {"error": error, "gjoinID": group_joinID, "relay": relay}
        query = json.dumps(query)
        client.publish("/configuration/group_join_ack/" + tempID, query)



def group_leave(tempID, payload):
    print ("\n ##Process - Group Leave\n")     

    group_leaveID = payload.get("gleaveID")
    relay = payload.get("relay")
    try:
        error = 0
        
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
        print ("Device ID: " + deviceID)

        groupID = payload.get('groupId')
        print ("Group ID: " + groupID)

        db_query = {'table':'GroupMember', 'data':[{'groupId':groupID, 'memberId':deviceID}]}
        queryID = send_DBquery(db_query, db_delete, True)
        db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('Group Leave DB error')
        del dbQuery_cache[queryID]
    
        print ("\nDB Update Completed..")
        query = {"error:": error, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/group_leave_ack/" + tempID, query)
        
        print ("\n ##Process Completed - Group Leave\n")

    except Exception as e:
        error = 1
        print("Group Leave error: ", e)
        query = {"error": error, "gleaveID":group_leaveID, "relay": relay}
        query = json.dumps(query)
        client.publish("/configuration/group_leave_ack/" + tempID, query)


def group_selection(tempID, payload):
    print ("\n ##Process - Group Selection\n")     
   
    group_selectID = payload.get("gselectID")
    relay = payload.get('relay')
    try:
        error = 0
        
        if relay == "none":
            deviceID = tempID
        else:
            deviceID = relay[-1]
        print ("Device ID: " + deviceID)

        groupID = payload.get('groupId')
        print ("Selected Group ID: " + groupID)
        
        data = {'groupId':groupID, 'memberId':deviceID}
        db_query = {'table':'GroupMember', 'data':[data]}
        queryID = send_DBquery(db_query, db_insert, True)
        db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('Group Generate DB error1')
        del dbQuery_cache[db_query]

        print ("\nDB Update Completed..")
        query = {"error:": error, "relay":relay}
        query = json.dumps(query)
        client.publish("/configuration/group_select_ack/" + tempID, query)
        
        print ("\n ##Process Completed - Group Select\n")

    except Exception as e:
        error = 1
        print("Group Selection error: ", e)
        query = {"error": error, "gselectID":group_selectID, "relay": relay}
        query = json.dumps(query)
        client.publish("/configuration/group_select_ack/" + tempID, query)


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
            queryID = send_DBquery(db_query, db_select, True)
            db_payload = dbQuery_cache[queryID]
            exist = db_payload.get('data')
            del dbQuery_cache[queryID]
            if exist is '' or not exist:
                raise Exception ('No Device Error')
            else:
                deviceID_cache[deviceID] = True
        
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
        
        db_query = {'table':'Device', 'data':info_list}
        queryID = send_DBquery(db_query, db_update, True)
        db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('MapUpdate DB error')
        del db_query

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
       
        db_query = {'table':'Neighbor', 'data':neighbor_list}
        queryID = send_DBquery(db_query, db_update, True)
        db_payload = dbQuery_cache[queryID]
        db_error = db_payload.get('error')
        if db_error is not 0:
            raise Exception ('MapUpdate DB error')
        del db_query

        print ("\nDB Update Completed..")
        query = {"error:": error, "mapUpdateID": mapUpdateID, "relay": relay}
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



def on_connect1(client, userdata, flags, rc):
    print ("Connected with the Message Bus1 ")
    # communication with end-user
    client.subscribe("/configuration/join/#")
    client.subscribe("/configuration/leave/#")
    client.subscribe("/configuration/register/#")
    client.subscribe("/configuration/update/#")
    client.subscribe("/configuration/group_join/#")
    client.subscribe("/configuration/group_leave/#")
    client.subscribe("/configuration/group_select/#")
    client.subscribe("/utilization/query/#")


def on_connect2(client, userdata, flags, rc):
    print ("Connected with the Message Bus2 ")
    # communication with end-user
    client.subscribe("/configuration/join/#")
    client.subscribe("/configuration/leave/#")
    client.subscribe("/configuration/register/#")
    client.subscribe("/configuration/update/#")
    client.subscribe("/configuration/group_join/#")
    client.subscribe("/configuration/group_leave/#")
    client.subscribe("/configuration/group_select/#")
    client.subscribe("/utilization/query/#")


def on_db_connect(client, userdata, flags, rc):
    print ("Connected with the DB Message Bus ")
    # communication with DB
    client.subscribe("/dbquery/iack/flexMnger/#")
    client.subscribe("/dbquery/sack/flexMnger/#")
    client.subscribe("/dbquery/dack/flexMnger/#")
    client.subscribe("/dbquery/uack/flexMnger/#")



def on_message(client, userdata, msg):
    print ("Subscribe - Topic: " + msg.topic)
    topic = msg.topic.split('/')
    payload = json.loads(msg.payload.decode('utf-8'))
    if "configuration" == topic[1]:
        if "join" == topic[2]:
            deviceID = topic[3]
            join(deviceID, payload, 1)
        elif "leave" == topic[2]:
            deviceID = topic[3]
            leave(deviceID, payload)
        elif "register" == topic[2]:
            deviceID = topic[3]
            register(deviceID, payload)
        elif "update" == topic[2]:
            deviceID = topic[3]
            update(deviceID, payload)
        elif "group_join" == topic[2]:
            deviceID = topic[3]
            group_join(deviceID, payload)
        elif "group_select" == topic[2]:
            deviceID = topic[3]
            group_select(deviceID, payload)
        elif "group_leave" == topic[2]:
            deviceID = topic[3]
            group_leave(deviceID, payload)
        elif "mapUpdate" == topic[2]:
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


def on_message2(client, userdata, msg):
    print ("Subscribe - Topic: " + msg.topic)
    topic = msg.topic.split('/')
    payload = json.loads(msg.payload.decode('utf-8'))
    if "configuration" == topic[1]:
        if "join" == topic[2]:
            deviceID = topic[3]
            join(deviceID, payload, 2)
        elif "leave" == topic[2]:
            deviceID = topic[3]
            leave(deviceID, payload)
        elif "register" == topic[2]:
            deviceID = topic[3]
            register(deviceID, payload)
        elif "update" == topic[2]:
            deviceID = topic[3]
            update(deviceID, payload)
        elif "group_join" == topic[2]:
            deviceID = topic[3]
            group_join(deviceID, payload)
        elif "mapUpdate" == topic[2]:
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


client = mqtt.Client()
client2 = mqtt.Client()
db_client = mqtt.Client()


client.on_connect = on_connect1
client.on_message = on_message
client.connect(broker1, 1883, 60)

client2.on_connect = on_connect2
client2.on_message = on_message2
client2.connect(broker2, 1883, 60)

db_client.on_connect = on_db_connect
db_client.on_message = on_db_message
db_client.on_publish = on_db_publish
db_client.connect(db_broker, 1883, 60)
#db_client.connect(broker, 1883, 60)

if __name__ == "__main__":
    print("\n Start FlexID Manager...\n")
    #client.loop_forever()
    #db_client.loop_forever()
    while True:
        client.loop_start()
        client2.loop_start()
        db_client.loop_start()
