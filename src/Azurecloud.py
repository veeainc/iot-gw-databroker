from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import MethodResponse
from azure.iot.device import Message
from azure.iot.device import exceptions
import logging
import asyncio
import os
import yaml
import json
import time
import base64
import hmac
import hashlib
from Connection_Manager import ConnectionManager
import threading
import applicationDataRouter
import random

FORMAT = '%(levelname)s: %(asctime)-15s: %(filename)s: %(funcName)s: %(module)s: %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)
logging.getLogger("azure.iot.device.aio").setLevel(logging.WARNING)

device_client = None
RECEIVED_MESSAGES = 0
mac_appname_dict = {}
routing_app_table = {}
mac_list_set = set()
mac_device_client = {}
webdata = {}
cloud_status = False

provisioning_host = "global.azure-devices-provisioning.net"


class Azure_cloud(ConnectionManager):
    """ Azure cloud specific cloud for creating connection,
        sending and receiving data to and from Azure cloud
    """
    def __init__(self,data):
        global webdata
        webdata = data
        mac_list_set.clear()
        logging.debug(f"initialized webdata...!!")

    #method to register and provision individual devices based on MAC addresses and send data to cloud 
    async def send_message_to_cloud(self, azure_data, mac_appName_dict,routing_table,loop):
        global mac_appname_dict, routing_app_table, mac_device_client
        mac_appname_dict = mac_appName_dict
        routing_app_table = routing_table
        try:
            
            if azure_data["mac"] not in mac_list_set:
                device_name = azure_data["mac"].replace(':', '_')
                logging.info(f"{azure_data['mac']} not found in set.. Adding to the set....!!")
                mac_list_set.add(azure_data["mac"])

                # use group symmetric key to generate a device symmetric key
                logging.debug(f"group symmentric key is: {webdata['group_symmetric_key']}")
                device_symmetric_key = await derive_device_key(device_name, webdata["group_symmetric_key"])
                logging.debug(f"device symmetric key generated for {azure_data['mac']} is :  {device_symmetric_key}")
                
                if device_symmetric_key is not False:
                    #Registering and provisioning devices
                    device_client = await device_cloud_connection(device_symmetric_key,webdata["id_scope"],device_name,provisioning_host)
                    logging.debug(f"device client created for {azure_data['mac']} is {device_client}")
                    mac_device_client[azure_data["mac"]] = {}
                    mac_device_client[azure_data["mac"]]["device_client"] = device_client

                    logging.debug(f"updating mac device client list: {mac_device_client}")

                    if device_client is not False:
                        #open a receive cloud thread for handling callbacks from cloud
                        await cloud_data_receiver(loop, device_client, device_name)
                    else:
                        logging.warn(f"unable to establish connection to cloud")
                        return
                else:
                    logging.warning(f"Error deriving Device symmetric key from Group symmetric key. Kindly check connection details")
                    return

            else:
                #retreive device client from mac_device_client
                device_client = mac_device_client[azure_data["mac"]]["device_client"]

            if device_client is not False:
                msg = Message(str(azure_data),content_encoding="utf-8", content_type="application/json")
                try:
                    logging.debug(await device_client.send_message(msg))
                    logging.info("Message successfully sent to Azure !")
                except exceptions.ClientError: # error if the device is blocked
                    logging.warning("ClientError")
                    logging.info(f"Device removed.. Disconnecting now..!!")
                    logging.debug(await device_client.disconnect())
                    mac_list_set.remove(azure_data["mac"])
                    mac_device_client.pop(azure_data["mac"])
                    logging.debug(f"updated mac list set: {mac_list_set}")
                    logging.debug(f"updated mac_device_client: {mac_device_client}")
                except exceptions.ConnectionDroppedError: # error if the key is wrong
                    logging.warning("Connection Dropped Error")

            else:
                logging.warning(f"Not able to connect to cloud.. Check your cloud connection details")

        except Exception as e:
            logging.warning(f"Message failed to send to cloud : {e}")

    # Register and connect the device
    async def cloud_connection(self,cloud_connection_details):
        logging.debug(f"inside cloud_connection")

    #A thread to receive data from azure cloud
    async def receive_message_from_cloud(self,loop): 
        logging.debug(f"receive message thread..!!")
        pass

# derives a symmetric device key for a device id using the group symmetric key
async def derive_device_key(device_id, group_symmetric_key):
    try:
        message = device_id.encode("utf-8")
        signing_key = base64.b64decode(group_symmetric_key.encode("utf-8"))
        signed_hmac = hmac.HMAC(signing_key, message, hashlib.sha256)
        device_key_encoded = base64.b64encode(signed_hmac.digest())
        return device_key_encoded.decode("utf-8")
    except Exception as e:
        logging.warning(f"unable to derive symmetric key for device.. Check your cloud details..!!!!!!!!!!!!! {e}")
        return False



# Register and connect the devices based on MAC addresses
async def device_cloud_connection(device_symmetric_key,id_scope,device_id,provisioning_host):
    try:
        registration_result = await register_device(device_symmetric_key,id_scope,device_id,provisioning_host)
        logging.debug(f"registration result is: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! {registration_result}")
        try:
            if registration_result.status == 'assigned':
                device_client = IoTHubDeviceClient.create_from_symmetric_key(symmetric_key=device_symmetric_key, hostname=registration_result.registration_state.assigned_hub,
                device_id=registration_result.registration_state.device_id,)
                logging.debug(f"Trying to connect")

                # Connect the client.
                await device_client.connect()
                logging.info('Device connected successfully')
                await device_client.disconnect()
                return device_client
            else:
                logging.debug(f"returning cloud connection device client value : !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                return False
        except Exception as e:
            logging.warning(f"Error while registering device.. {e} ")

    except Exception as e:
        logging.error(f"Error connecting to Iot Hub..!!! {e}")
        return False

#Register single devices based on MAC addresses
async def register_device(device_symmetric_key,id_scope,device_id,provisioning_host):
    try:
        id_scope = id_scope
        registration_id = device_id
        symmetric_key = device_symmetric_key
        provisioning_host = provisioning_host
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host=provisioning_host,
            registration_id=registration_id,
            id_scope=id_scope,
            symmetric_key=symmetric_key,
        )
        registration_result = await provisioning_device_client.register()
        logging.debug(f'Registration result: {registration_result.status}')
    except exceptions.CredentialError:
        logging.warning("Credential Error")
        return False
    except exceptions.ConnectionFailedError: 
        logging.warning("Connection Failed Error")
        return False
    except exceptions.ConnectionDroppedError: # error if the key is wrong
        logging.warning("Connection Dropped Error")
        return False
    except exceptions.ClientError: # error if the device is blocked
        logging.warning("ClientError")
        return False
    except Exception:
        logging.warning("Unknown Exception")
        return False
        
    return registration_result



async def cloud_data_receiver(loop, device_client, device_name): 
    logging.info(f"Thread started to receive data from cloud for device: {device_name}...!!")
    device_name = threading.Thread(target=cloud_message_listener_thread, args=(device_client,loop, device_name))
    device_name.daemon = True
    device_name.start()


#Continuosly listen data from cloud
def cloud_message_listener_thread(device_client,loop, device_name):
    async def receive_data(request):
        global RECEIVED_MESSAGES
        logging.info(f"device name {device_name} is : {request.payload}")
        RECEIVED_MESSAGES += 1
        logging.debug(f"mac_device_client details: {mac_device_client}")
        request.payload["mac"] = device_name.replace('_', ':')
        logging.debug(f"updated request payload: {request.payload}")
        await applicationDataRouter.application_data_router(request.payload, mac_appname_dict, routing_app_table) #send payload to application data router
        logging.info(f"Total response published  {RECEIVED_MESSAGES}")

    while True:
        try:
            #Receive data from cloud
            method_request = loop.run_until_complete(device_client.receive_method_request())  # Wait for commands
            logging.info(f"Method request name from Iot Central: {method_request.name}")
        except Exception as e:
            logging.warning(f"error wile receiving message from cloud: {e}")

        try:
            #creating a response to be sent to Iot Hub
            response = MethodResponse.create_from_method_request(
            method_request, status = 202
            )
            loop.run_until_complete(device_client.send_method_response(response))  # send response
        except Exception as e:
            logging.warning(f"Unable to send response to cloud: {e}")

        loop.run_until_complete(receive_data(method_request))


