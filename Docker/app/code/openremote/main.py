import requests
import json
import sys
import configparser
from pysondb import db
from logging import getLogger
from logger.main import Logger as Logger

Logger()

thismodule = sys.modules[__name__]
thismodule.apitoken = ""
db = thismodule.db = db.getDb("assetDB.json")

config = configparser.ConfigParser()
config.read('./or-client.ini')

api_client_id = config['openremote']['client_id']
api_client_secret = config['openremote']['client_secret']

apiurl = 'https://openremote.ready2plugin.dev'

def main():
    print(thismodule.apitoken)


def getApiToken():
    """
    Gets the api token or returns the token if already present
    """
    rData = {'grant_type': 'client_credentials',
            'client_id': f'{api_client_id}',
            'client_secret': f'{api_client_secret}'
            }
    rURL = f'{apiurl}/auth/realms/master/protocol/openid-connect/token'
    r = requests.post(rURL, rData)
    thismodule.apitoken = json.loads(r.content)['access_token']
    return json.loads(r.content)['access_token']

def createAsset(assetName):
    """
    This function will create an OpenRemote Asset and Service User for the Asset.
    The Information about this Asset and User will be saved in a pysondb.

    Args:
        assetName (STRING): An Assetname - may be the Waechter UUID
    """
    getApiToken()
    rURL = f'{apiurl}/api/master/asset'
    rData = {'name':f'{assetName}','type':'ThingAsset','realm':'master','attributes':{'notes':{'name':'notes','type':'text'},'location':{'name':'location','type':'GEO_JSONPoint'},'subscribeAttribute':{'name':'subscribeAttribute','type':'boolean'},'tele':{'name':'tele','type':'JSONObject'}}}
    rHeaders = {'Authorization': f'Bearer {thismodule.apitoken}'}
    r = requests.post(url=rURL, json=rData, headers=rHeaders)
    updateAssetStatus = updateAsset(json.loads(r.content)["id"], assetName)
    
    # Create a Service User for the newly created Asset
    user = createUser(json.loads(r.content)["id"])
    linkAssetToUser(userid=user['userid'], assetid=json.loads(r.content)['id'])
    thismodule.db.add({'assetid': f'{json.loads(r.content)["id"]}',
                       'assetname': f'{assetName}',
                       'userid': f'{user["userid"]}',
                       'username': f'{user["username"]}',
                       'password': 'PLACEHOLDER'})
    # for some reason the random secret will not be accepted
    # so I just generate a new password and set in in the local db -_-
    password = getNewPassword(f'{user["userid"]}')
    return {'assetid': f'{json.loads(r.content)["id"]}',
            'assetname': f'{assetName}',
            'userid': f'{user["userid"]}',
            'username': f'{user["username"]}',
            'password': f'{password["content"]}'}

def updateAsset(assetID, assetName):
    getApiToken()
    rURL = f'{apiurl}/api/master/asset/{assetID}'
    rHeaders = {'Authorization': f'Bearer {thismodule.apitoken}'}
    rData = {"name": f"{assetName}","realm":"master","type":"ThingAsset","attributes":{"notes":{"type":"text","value":None,"name":"notes"},"location":{"type":"GEO_JSONPoint","value":None,"name":"location"},"tele":{"type":"JSONObject","value":None,"name":"tele","meta":{"attributeLinks":[{"ref":{"id":f"{assetID}","name":"client_id"},"filters":[{"type":"jsonPath","path":"$.client_id","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mac"},"filters":[{"type":"jsonPath","path":"$.mac","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"pcb_id"},"filters":[{"type":"jsonPath","path":"$.pcb_id","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"uptime"},"filters":[{"type":"jsonPath","path":"$.uptime","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"pcb_temp"},"filters":[{"type":"jsonPath","path":"$.pcb_temp","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"wifi_rssi"},"filters":[{"type":"jsonPath","path":"$.wifi_rssi","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"localtime"},"filters":[{"type":"jsonPath","path":"$.localtime","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"ts_since_unix_epoch"},"filters":[{"type":"jsonPath","path":"$.ts_since_unix_epoch","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"reset_cause"},"filters":[{"type":"jsonPath","path":"$.reset_cause","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"wake_cause"},"filters":[{"type":"jsonPath","path":"$.wake_cause","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mem_free"},"filters":[{"type":"jsonPath","path":"$.mem_free","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mem_alloc"},"filters":[{"type":"jsonPath","path":"$.mem_alloc","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"part_boot"},"filters":[{"type":"jsonPath","path":"$.part_boot","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"tainted"},"filters":[{"type":"jsonPath","path":"$.tainted","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"cable_temp_esp32"},"filters":[{"type":"jsonPath","path":"$.cable_temp_esp32","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"cable_temp_stm32"},"filters":[{"type":"jsonPath","path":"$.cable_temp_stm32","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"ampere_rms_esp32"},"filters":[{"type":"jsonPath","path":"$.ampere_rms_esp32","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"ampere_rms_stm32"},"filters":[{"type":"jsonPath","path":"$.ampere_rms_stm32","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"volt_gridmeter"},"filters":[{"type":"jsonPath","path":"$.volt_gridmeter","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mpy_sysname"},"filters":[{"type":"jsonPath","path":"$.mpy_sysname","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mpy_nodename"},"filters":[{"type":"jsonPath","path":"$.mpy_nodename","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mpy_release"},"filters":[{"type":"jsonPath","path":"$.mpy_release","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mpy_ver_str"},"filters":[{"type":"jsonPath","path":"$.mpy_ver_str","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mpy_git_tag"},"filters":[{"type":"jsonPath","path":"$.mpy_git_tag","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mpy_git_hash"},"filters":[{"type":"jsonPath","path":"$.mpy_git_hash","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"mpy_machine"},"filters":[{"type":"jsonPath","path":"$.mpy_machine","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"ip_addr"},"filters":[{"type":"jsonPath","path":"$.ip_addr","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"ip_subnet"},"filters":[{"type":"jsonPath","path":"$.ip_subnet","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"ip_gateway"},"filters":[{"type":"jsonPath","path":"$.ip_gateway","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"ip_dns"},"filters":[{"type":"jsonPath","path":"$.ip_dns","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"wifi_essid"},"filters":[{"type":"jsonPath","path":"$.wifi_essid","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"wifi_peer_mac"},"filters":[{"type":"jsonPath","path":"$.wifi_peer_mac","returnFirst":True,"returnLast":False}]},{"ref":{"id":f"{assetID}","name":"dev_id"},"filters":[{"type":"jsonPath","path":"$.dev_id","returnFirst":True,"returnLast":False}]}]}},"subscribeAttribute":{"type":"boolean","value":None,"name":"subscribeAttribute"},"client_id":{"name":"client_id","type":"text","meta":{"storeDataPoints":True}},"mac":{"name":"mac","type":"text","meta":{"storeDataPoints":True}},"pcb_id":{"name":"pcb_id","type":"text","meta":{"storeDataPoints":True}},"dev_id":{"name":"dev_id","type":"text","meta":{"storeDataPoints":True}},"uptime":{"name":"uptime","type":"long","meta":{"storeDataPoints":True}},"localtime":{"name":"localtime","type":"long","meta":{"storeDataPoints":True}},"ts_since_unix_epoch":{"name":"ts_since_unix_epoch","type":"long","meta":{"storeDataPoints":True}},"reset_cause":{"name":"reset_cause","type":"integer","meta":{"storeDataPoints":True}},"wake_cause":{"name":"wake_cause","type":"integer","meta":{"storeDataPoints":True}},"mem_free":{"name":"mem_free","type":"integer","meta":{"storeDataPoints":True}},"mem_alloc":{"name":"mem_alloc","type":"integer","meta":{"storeDataPoints":True}},"mpy_sysname":{"name":"mpy_sysname","type":"text","meta":{"storeDataPoints":True}},"mpy_nodename":{"name":"mpy_nodename","type":"text","meta":{"storeDataPoints":True}},"mpy_release":{"name":"mpy_release","type":"text","meta":{"storeDataPoints":True}},"mpy_ver_str":{"name":"mpy_ver_str","type":"text","meta":{"storeDataPoints":True}},"mpy_git_tag":{"name":"mpy_git_tag","type":"text","meta":{"storeDataPoints":True}},"mpy_git_hash":{"name":"mpy_git_hash","type":"text","meta":{"storeDataPoints":True}},"mpy_machine":{"name":"mpy_machine","type":"text","meta":{"storeDataPoints":True}},"part_boot":{"name":"part_boot","type":"integer","meta":{"storeDataPoints":True}},"tainted":{"name":"tainted","type":"boolean","meta":{"storeDataPoints":True}},"pcb_temp":{"name":"pcb_temp","type":"integer","meta":{"storeDataPoints":True}},"cable_temp_esp32":{"name":"cable_temp_esp32","type":"integer","meta":{"storeDataPoints":True}},"cable_temp_stm32":{"name":"cable_temp_stm32","type":"integer","meta":{"storeDataPoints":True}},"ampere_rms_esp32":{"name":"ampere_rms_esp32","type":"integer","meta":{"storeDataPoints":True}},"ampere_rms_stm32":{"name":"ampere_rms_stm32","type":"integer","meta":{"storeDataPoints":True}},"volt_gridmeter":{"name":"volt_gridmeter","type":"integer","meta":{"storeDataPoints":True}},"ip_addr":{"name":"ip_addr","type":"text","meta":{"storeDataPoints":True}},"ip_subnet":{"name":"ip_subnet","type":"text","meta":{"storeDataPoints":True}},"ip_gateway":{"name":"ip_gateway","type":"text","meta":{"storeDataPoints":True}},"ip_dns":{"name":"ip_dns","type":"text","meta":{"storeDataPoints":True}},"wifi_rssi":{"name":"wifi_rssi","type":"integer","meta":{"storeDataPoints":True}},"wifi_essid":{"name":"wifi_essid","type":"text","meta":{"storeDataPoints":True}},"wifi_peer_mac":{"name":"wifi_peer_mac","type":"text","meta":{"storeDataPoints":True}}}}
    r = requests.put(url=rURL, json=rData, headers=rHeaders)
    return r.status_code

def deleteAsset(assetID):
    """
    Delte an OpenRemote Asset by assetid

    Args:
        assetID (STRING): The OpenRemote AssetID

    Returns:
        INT: requests.status_code
    """
    getApiToken()
    rURL = f'{apiurl}/api/master/asset?assetId={assetID}'
    rHeaders = {'Authorization': f'Bearer {thismodule.apitoken}'}
    r = requests.delete(url=rURL, headers=rHeaders)
    if r.status_code == 204:
        db.deleteById(db.reSearch('assetid', f'{assetID}')[0]['id'])
    return r.status_code

def createUser(assetID):
    """
    Create a new OpenRemote Service Account.

    Args:
        assetID (STRING): The Username will be the assetID

    Returns:
        JSON Object:
        
        Keys: { 'status_code': '', 'userid': ''}
    """
    getApiToken()
    rURL = f'{apiurl}/api/master/user/master/users'
    rHeaders = {'Authorization': f'Bearer {thismodule.apitoken}'}
    rData = {'enabled':True, 'realm':'master','roles':[],'previousRoles':[],'realmRoles':[],'previousRealmRoles':[],'serviceAccount':True,'username':f'{assetID}'}

    r = requests.post(url=rURL, json=rData, headers=rHeaders)
    r2URL = f'{apiurl}/api/master/user/master/userRoles/{json.loads(r.content)["id"]}'
    r2Data = [{"id":"48628d3b-8431-40f1-982b-beff7b1d188e","name":"write:attributes","description":"Write attribute data","composite":False,"assigned":True}]
    r2 = requests.put(url=r2URL, json=r2Data, headers=rHeaders)
    return { 'status_code': f'{r.status_code}','userid': f'{json.loads(r.content)["id"]}', 'username': f'{json.loads(r.content)["username"]}'}

def linkAssetToUser(assetid, userid):
    """
    Links an OpenRemote Asset to a User

    Args:
        assetid (STRING): The OpenRemote assetid
        userid (STRING): The Openremote userid

    Returns:
        int: responose.status_code
    """
    getApiToken()
    rURL = f'{apiurl}/api/master/asset/user/link'
    rHeaders = {'Authorization': f'Bearer {thismodule.apitoken}'}
    rData = [{"id":{"userId":f"{userid}","realm":"master","assetId":f"{assetid}"}}]
    
    r = requests.post(url=rURL, json=rData, headers=rHeaders)
    return r.status_code

def getNewPassword(userid):
    """
    Generete a new password for a User in OpenRemote by userid

    Args:
        userid (STRING):

    Returns:
        _type_: JSON Object
        
        keys: {'status_code': '', 'content': ''}
    
    Usage:
        getNewPassword('c53311e3-d0c0-45f9-aee3-f53e766220b9')
    """
    getApiToken()
    rURL = f'{apiurl}/api/master/user/master/reset-secret/{userid}'
    rHeader = {'Authorization': f'Bearer {thismodule.apitoken}'}
    r = requests.get(url=rURL, headers=rHeader)
    db.updateById(f"{db.reSearch('userid', f'{userid}')[0]['id']}",{"password":f"{r.text}"})
    return {'status_code': f'{r.status_code}', 'content': f'{r.text}'}

def deleteUser(userid):
    """
    Delete an OpenRemote User by userid

    Args:
        userid (STRING): The OpenRemote userid to delte

    Returns:
        INT: requests.status_code
    """
    getApiToken()
    rURL = f'{apiurl}/api/master/user/master/users/{userid}'
    rHeader = {'Authorization': f'Bearer {thismodule.apitoken}'}
    r = requests.delete(url=rURL, headers=rHeader)
    return r.status_code