"""
Veea CONFIDENTIAL © 2020 
All rights reserved NOTICE: All information contained herein is, and remains
the property of Veea and its suppliers, if any. The intellectual and technical
concepts contained herein are proprietary to Veea, and its suppliers  and may 
be covered by U.S. and Foreign Patents, patents in process, and are protected by
trade secret or copyright law. Dissemination of this information or reproduction 
of this material is strictly forbidden unless prior written permission is obtained
from Veea.
"""
###########################################################################
# This application will connect to various application running on veeaHub and 
# collect data from applications and send telemetry data to cloud
###########################################################################

import asyncio
from vbus import Client
import nest_asyncio
nest_asyncio.apply()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
import logging
FORMAT = '%(levelname)s: %(asctime)-15s: %(filename)s: %(funcName)s: %(module)s: %(message)s'
logging.basicConfig(filename="databroker.log",level=logging.INFO, format=FORMAT)
from vbus import definitions
import json
from vbus.proxies import NodeProxy
import vbus
import threading
import traceback
from flask import Flask, request, render_template,jsonify, redirect, url_for
from flask_cors import CORS, cross_origin
from Azurecloud import Azure_cloud
from ObjectFactory import ObjectFactory
import os
from observe.observability import Monitor
import yaml

app = Flask(__name__)
CORS(app, support_credentials=True)

CLOUD_RECEIVED_MESSAGES = 0
routing_table = {}
#routing_dict = {}
mac_appName_dict = {}
clientname = "databroker"
app_data_count = 0
subscribed = False
cloud_obj = None
webdata = {}
file_exist = False
cloud_status = {"status":"False"}
home_path = os.environ.get('HOME')
pv_path = "/app"
json_path = "/app"
monitor = Monitor(app)

#singleton class for vbus object creation
class NewClient:
    _instance = None
    _client = None
    @staticmethod
    def create_client():
        if NewClient._instance == None:
            NewClient()
            logging.debug(f"Type of client created:{type(NewClient._client)}")
        return NewClient._client

    def __init__(self):
        if NewClient._instance == None:
            logging.info(f"Creating client in class: '{clientname}'")
            NewClient._client = vbus.Client("system",clientname)
            loop.run_until_complete(NewClient.connect_client(self, NewClient._client))
            NewClient._instance = self

    async def connect_client(self,client):
        await client.connect()
        logging.info("Client connected")


class Initialize_cloud:
    def __init__(self, data):
        cloud_specific_con(data)


def cloud_specific_con(data):
    global cloud_obj
    obj_fac = ObjectFactory()
    cloud_obj = loop.run_until_complete(obj_fac.create(data["webService"], data))
    logging.debug(f"cloud object created for {data['webService']} is : {cloud_obj}")
    return cloud_obj

async def check_app_Key(topic, client):
    global routing_table 
    logging.debug(f"routing table in check_app_key: {routing_table}")
    if topic["app_name"] not in routing_table.keys():
        logging.debug("App not found.. Updating...!!")
        status = await update_databroker_dict(topic)
        if status is True:
            return True
        else:
            return False
    else:
        #Adding a discovery of application
        try:
            nodes = await client.discover("system",topic['app_name'], 2)
            logging.debug(f"discovery result: {nodes.as_node().tree}")
            routing_table[topic["app_name"]]["app_hostname"] = list(nodes.as_node().tree)[0]
            logging.debug(f"routing table in check_app_key after updation: {routing_table}")
        except Exception as e:
            logging.warn(f"unable to discover {topic['app_name']} application")

    logging.debug(f"{topic['app_name']}  already present in {routing_table}")
    return True


#routing table with info regarding app name and topic details
async def update_databroker_dict(topic):
    global routing_table
    try:
        routing_dict = {}
        routing_dict[topic["app_name"]] = {}
        routing_dict[topic["app_name"]]["inbound_topic_details"] = topic["inbound_topic_details"]
        routing_dict[topic["app_name"]]["outbound_topic_details"] = topic["outbound_topic_details"]
        routing_dict[topic["app_name"]]["app_hostname"] = topic["app_hostname"]
        try:
            routing_dictionary = open(pv_path+"/routing_dictionary.yaml","a")
            logging.debug(f"value of routing dict is: {routing_dict}")
            routing_dictionary.write(yaml.dump(routing_dict))
            routing_dictionary.close()
            logging.debug(f"Data saved to routing table: {routing_dict}")
        except:
            logging.error(f"Error while writing data to routing dictionary file: {traceback.print_exc()}")
        routing_table.update(routing_dict)
        routing_table[topic["app_name"]]["response_obj"]  = await create_response_node(topic["inbound_topic_details"])
        logging.debug(f"updated routing dictionary: {routing_table}")

        return True
    except:
        logging.error(f"Error while updating databroker dictionary: {traceback.print_exc()}")
        return False



#response node and attribute creation for each app name
async def create_response_node(inbound_topic_details):
    client = NewClient.create_client()

    # Adding a response node to publish response back to  app
    app_response_node = await client.add_node(inbound_topic_details[0], {  # a data node
        # maybe some static attributes here or nodes...
    })
    app_response_attr = await app_response_node.add_attribute(inbound_topic_details[1], {})
    return app_response_attr


#control interface where databroker publishes its details on vbus for other applications
async def control_interface(client):
    async def is_running(time: int, **kwargs) -> None:
        logging.debug(f"time is: {time}")

    # Receive vbus nodes and attributes details from applications
    async def set_receive_topic(topic: str, **kwargs) -> str:
        global routing_table, cloud_obj

        logging.info(f"Remote application topic details: {topic}")
        # {"app_name":"zig","inbound_topic_details":["zigbee_in_node","zigbee_in_data"], "outbound_topic_details":["zigbee_out_node","zigbee_out_data"]}
        logging.info(f"Remote app name: {topic['app_name']}")

        try:
            logging.info(f"Gettting permission from {'system.'+topic['app_name']}")
            logging.debug(f"len(topic) is {len('system.'+topic['app_name'])}")
            ok = await client.ask_permission('system.'+topic['app_name'])
            ok = await client.ask_permission('system.'+topic['app_name']+".>")
            logging.info(f"permission status: {ok}")


        except Exception as e:
            logging.warning(f"problem while getting permission from application: {traceback.print_exc()}")

        #check client app name
        logging.debug(f"check_app_key started:")

        status  = await check_app_Key(topic, client)
        if status is True:
            if cloud_obj is None:
                if os.path.exists(pv_path + "/webdata.yaml"):
                    with open(pv_path + "/webdata.yaml") as f:
                        data = yaml.load(f, yaml.FullLoader)
                        cloud_obj = cloud_specific_con(data)
            logging.debug(f"cloud_obj in app message listener thread {cloud_obj}")
            app_listener_thread = threading.Thread(target=app_message_listener_thread, args=(loop,client ,cloud_obj,topic["app_name"]))
            app_listener_thread.daemon = True
            app_listener_thread.start()
        else:
            logging.warning("Check failed.. Unable to subscribe..!!")
        logging.debug(f"set_receive_topic completed.. Returning hostname to application")
        return client.hostname

    #adding methods in databroker
    await client.add_node("devices", {
        'set_receive_topic': definitions.MethodDef(set_receive_topic),
        'is_running': definitions.MethodDef(is_running)
    })


#A thread for listening incoming data from applications
def app_message_listener_thread(loop,client, cloud_obj,application_name):
    count = 0
    #get remote attribute application details
    logging.info(f"Routing table details: {routing_table}")
    for app_name, app_details in routing_table.items():
        if app_name == application_name:
            while count < 3:
                try:
                    logging.info(f"Trying to get attribute details of {app_name}")
                    attr = loop.run_until_complete(client.get_remote_attr("system", app_name, app_details["app_hostname"], app_details["outbound_topic_details"][0], app_details["outbound_topic_details"][1], timeout=40))

                    #subscribe to that node
                    loop.run_until_complete(attr.subscribe_set(app_data_received))
                    logging.info(f"Subscribed to {app_name} successfully..!!")
                    break
                except Exception as e:
                    logging.warning(f"Error occured while fetching details of  {app_name}. Trying one more time :  {e}")
                    count = count +1


# send received app data to configured cloud
async def app_data_received(node: NodeProxy) -> None:
    global mac_appName_dict, app_data_count
    app_data_count +=1
    logging.info(f"data received: {node.tree} and app data count is: {app_data_count}")

    #Map  mac address with app name
    await map_mac_with_appName(node, mac_appName_dict)

    #send data to cloud router
    await cloud_router(node.tree)


#creating a table of app name and mac list associated with it
async def map_mac_with_appName(node: NodeProxy ,mac_appName_dict):

    app_data = node.tree
    if app_data["app_name"] not in mac_appName_dict.keys(): 
        mac_appName_dict[app_data["app_name"]] = []
        mac_appName_dict[app_data["app_name"]].append(app_data["mac"])
    else:
        list_of_macs = mac_appName_dict[app_data["app_name"]]
        if app_data["mac"] not in list_of_macs:
            mac_appName_dict[app_data["app_name"]].append(app_data["mac"])
        else:
            logging.debug("mac address already present in dictionary..!!")

    
#cloud router to send data to configured cloud
async def cloud_router(app_data):
    global  mac_appName_dict, routing_table,file_exist
    if os.path.exists(pv_path + "/webdata.yaml"):
        with open(pv_path+"/webdata.yaml","r") as fin:
            webdata = yaml.load(fin, yaml.FullLoader)
            file_exist = True
        
    if file_exist is True:
        logging.debug(f"cloud object details: {cloud_obj}")
        
        #Forwarding data to respective cloud
        await cloud_obj.send_message_to_cloud(app_data,mac_appName_dict,routing_table,loop)
    else:
        logging.warning(f"cloud details found empty: Dropping the packet")



def main_thread():
    home_path = os.environ.get('HOME')
    logging.info(f"Starting databroker application")

    loop.run_until_complete(main())


async def reconnect_apps(client):
    global routing_table
    if os.path.exists(pv_path + "/webdata.yaml"):
        with open(pv_path + "/webdata.yaml") as f:
            data = yaml.load(f, yaml.FullLoader)
            cloud_obj = cloud_specific_con(data)

        if os.path.exists(pv_path+'/routing_dictionary.yaml'):
            with open(pv_path+'/routing_dictionary.yaml', 'rb') as config_dictionary_file:
                routing_dict = yaml.load(config_dictionary_file, yaml.FullLoader)
                logging.info(f"Existing routing table found: {routing_dict}")


                for app_name, app_details in routing_dict.items():
                    logging.info(f"Existing app name is: {app_name}")

                    try:
                        ok = await client.ask_permission('system.'+app_name)
                        ok = await client.ask_permission('system.'+app_name+".>")
                        logging.debug(f"permission status of {app_name}: {ok}")

                        nodes = await client.discover("system", app_name, 2)
                        logging.info(f"Checking whether application {app_name} is discoverable or not: {nodes.as_node()}")
                    
                        #create a response node
                        resp_obj = await create_response_node(app_details["inbound_topic_details"])
                        routing_table = routing_dict
                        routing_table[app_name]["response_obj"] = resp_obj
                        routing_table[app_name]["app_hostname"] = list(nodes.as_node().tree)[0]
                        logging.debug(f"updated existing routing table: {routing_table}")
                        if nodes.as_node().tree == {}:
                            logging.info(f" Seems like {app_name} is not running..!!")

                        else:
                            #call app listener thread
                            logging.info(f"Subscribing to existing {app_name} application")
                            app_message_listener_thread(loop,client, cloud_obj,app_name)
                    except Exception as e:
                        logging.warn(f"error while discovering application: {app_name}")
        else:
            logging.debug(f"No existing application found...!!!")

    else:
        logging.debug(f"No existing cloud details found")


async def main():
    client = NewClient.create_client()

    #method to check existing apps connected to databroker and subscribe back to them in case of databroker starts
    await reconnect_apps(client)

    # Control Interface for dataBroker to publish API's for applications
    await control_interface(client)
    
    #Node details info of databroker app
    nodes = loop.run_until_complete(client.discover("system", clientname, 2))
    logging.info(f"Node details published by Databroker :\n\n {nodes.as_node()}\n\n")

    stopped = asyncio.Event()
    await stopped.wait()



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_logs', methods=['GET','POST'])
@cross_origin(supports_credentials=True)
def getLogs():
    try:
        if os.path.exists(json_path+"/databroker.log"):
            with open(json_path+"/databroker.log", 'r') as broker_logs:
                databroker_logs = broker_logs.readlines()
        return {"data": databroker_logs}
    except Exception as e:
        return "file not found"

@app.route('/submit', methods=['GET','POST'])
@cross_origin(supports_credentials=True)
def submit():
    home_path = os.environ.get('HOME')
    data = request.get_json()
    logging.info(f"data received from UI : {data}")

    propsMap = {}
    if os.path.exists(pv_path + "/webdata.yaml"):
        with open(pv_path+"/webdata.yaml","r") as fin:
            propsMap = yaml.load(fin, yaml.FullLoader)
            logging.debug(f"Existing cloud details found are: {propsMap}")

        if propsMap["id_scope"] == data["id_scope"]  and  propsMap["group_symmetric_key"] == data["group_symmetric_key"]:
            logging.info(f"Same entries found.. !! {cloud_status}  Try Entering different entries ")
            cloud_status["duplicate"] = "True"
            return cloud_status

    try:
        webdata = open(pv_path+"/webdata.yaml","w")
        webdata.write(yaml.dump(data))
        webdata.close()

    except Exception as e:
        logging.warning(f"Unable to write cloud config details to file: {e}")

    logging.info(f"cloud selected is : {data['webService']}")

    #create cloud specific object
    Initialize_cloud(data)
    cloud_status["duplicate"]= "False"
    logging.debug(f"cloud_status returned.. {cloud_status}")
    return cloud_status

if __name__ == '__main__':
    main_databroker_thread = threading.Thread(target=main_thread)
    main_databroker_thread.daemon = True
    main_databroker_thread.start()
    monitor.initialize_app()
    app.run(host='0.0.0.0', port=9060)

