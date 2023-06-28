from logger.main import Logger as Logger
import mqtt.main as mqtt
from logging import getLogger
from pysondb import db
import openremote.main as openremote
import ssl
import time
import re
from threading import Thread
import json

r2pclient = mqtt.MqttConnector('r2p-or-connector')
r2pclient.sub_topics('#')
orClients = {}

def liveCycleTest():
    assetid = openremote.createAsset('LIVECYCLE')
    getLogger(__name__).info(assetid)
    device = openremote.db.reSearch('assetid', f'{assetid}')
    getLogger(__name__).info(device[0])
    openremote.getNewPassword(f"{device[0]['userid']}")
    getLogger(__name__).info(openremote.deleteUser(device[0]['userid']))
    openremote.deleteAsset(assetid)

def r2pToOrAsset():
    getLogger(__name__).debug("Started r2pToOrAsset Thread")
    try:
        while 1:
            while not r2pclient.q.empty():
                qItem = r2pclient.q.get()
                p = re.compile('r2p\/waechter\/(.*)\/tele')
                m = p.match(json.loads(qItem)['topic'])
                dbquerry = openremote.db.reSearch('assetname', f"{m.group(1)}")
                if dbquerry != []:
                    if dbquerry[0]['assetname'] == m.group(1) and len(dbquerry) == 1:
                        getLogger(__name__).debug("Asset already in DB. Sending Data to OpenRemote")
                        # Get username and password from DB
                        # publish qItem
                        getLogger(__name__).debug(orClients)
                        orClients[f"{m.group(1)}"].pub_topic(topic=f"master/master:{dbquerry[0]['username']}/writeattributevalue/tele/{dbquerry[0]['assetid']}", message=f"{json.dumps(json.loads(qItem)['message'])}")
                else:
                    getLogger(__name__).debug("Asset not found in DB. Creating new Asset and sending Data.")
                    getLogger(__name__).info(f'New device detected with UUID: {m.group(1)}')
                    Asset = openremote.createAsset(f"{m.group(1)}")
                    orClients[f"{Asset['assetname']}"] = mqtt.MqttConnector(mqtt_id=f"master:{Asset['username']}", mqtt_password=Asset['password'], config_file='or-client.ini')
                    orClients[f"{Asset['assetname']}"].pub_topic(topic=f"master/master:{Asset['assetid']}/writeattributevalue/tele/{Asset['assetid']}", message=f"{json.dumps(json.loads(qItem)['message'])}")
            else:
                # getLogger(__name__).debug(f"Messages Queue: {r2pclient.q.qsize()}")
                time.sleep(0.1)
    except KeyboardInterrupt:
        exit()

def orMqttClients():
    # getLogger(__name__).debug(openremote.db.getAll())
    for device in openremote.db.getAll():
        orClients[f"{device['assetname']}"] = mqtt.MqttConnector(mqtt_id=f"master:{device['username']}", mqtt_password=device['password'], config_file='or-client.ini')

if __name__ == '__main__':
    # assetid = openremote.createAsset('DEVELOP-WAECHTER-CONSOLE')
    # liveCycleTest()
    # main()
    orMqttClients()
    r2pToOrAsset_Thread = Thread(target=r2pToOrAsset)
    r2pToOrAsset_Thread.run()
    # orClient = mqtt.MqttConnector(mqtt_id='master:44257rrkqdpsg3kxzah8tm', mqtt_password=openremote.db.reSearch('username', '44257rrkqdpsg3kxzah8tm')[0]['password'], config_file="or-client.ini")
    # orClient.pub_topic(f"master/{orClient.mqtt_id}/writeattributevalue/writeAttribute/{openremote.db.reSearch('username', '44257rrkqdpsg3kxzah8tm')[0]['assetid']}", '5000')
    # try:
    #     while 1:
    #         # while not r2pclient.q.empty():
    #         #     getLogger(__name__).info(r2pclient.q.qsize())
    #         #     qitem = r2pclient.q.get()
    #         #     thisClient = orClients['DEVELOP-WAECHTER-CONSOLE']
    #         #     getLogger(__name__).debug(json.loads(qitem)['message'])
    #         #     getLogger(__name__).debug(type(json.loads(qitem)['message']))
    #         #     thisClient.pub_topic(f"master/{thisClient.mqtt_id}/writeattributevalue/tele/5y3q73uGln16OwghUhJ01f", message=f"{json.loads(qitem)['message']}")
    #         #     #
    #         pass
    # except KeyboardInterrupt:
    #     exit()
