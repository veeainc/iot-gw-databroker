import logging


FORMAT = '%(levelname)s: %(asctime)-15s: %(filename)s: %(funcName)s: %(module)s: %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)

class applicationDataRouter:
    """ Route cloud data to specific application"""
    def __init(self):
        pass

async def application_data_router(cloud_messagedata, mac_appName_dict, routing_table):
    logging.debug(f"routing dict in applicationDataRouter...!!!!!!!! {routing_table}")
    logging.debug(f"mac_appName dictionary in applicationDataRouter...!!!!!!!! : {mac_appName_dict}")
    logging.debug(f"data received from cloud in applicationDataRouter...!!!!!!!! : {cloud_messagedata}")

    #routing_table ---> {'zig': ['zigbee_in_node', 'zigbee_in_data'], 'response_obj': <vbus.nodes.Attribute object at 0x754964f0>}
    #mac_appName_dict ---> {"zig":["00:17:88:01:06:3a:ec:bf","28:17:88:01:06:3a:ec:bf"],"bluetooth":[]}
    try:
        #check cloud response data where to route data to
        status = await lookup_app_name(cloud_messagedata,mac_appName_dict, routing_table)
        if status is False:
            logging.warning(f"Mac address does not match.. skipping the message..!!")
    except Exception as e:
        logging.warning(f"unable to find app name for mac address: {e}")

    try:
        if status:
            #set value on inbound topic details for app
            await status.set_value(cloud_messagedata)
            logging.info(f"data published to application.....!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    except Exception as e:
        logging.warning(f"Unable to publish data to application: {e}")
        

#lookup table to look app name corresponding to mac address
async def lookup_app_name(cloud_messagedata, mac_appName_dict, routing_table):
    try:
        for app_name,mac_list in mac_appName_dict.items():
            logging.debug(f"Finding mac address {cloud_messagedata['mac']} in app name : {app_name}")
            if cloud_messagedata["mac"] in mac_list:
                logging.info(f"mac address found: {cloud_messagedata['mac']}")
                return routing_table[app_name]["response_obj"]
        else: 
            return False
    except Exception as e:
        logging.warning(f"Key not found: {e}")
        return False
