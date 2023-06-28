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