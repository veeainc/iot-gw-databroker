from abc import ABC, abstractmethod

#Connection manager Interface
class ConnectionManager(ABC):
    """ Interface created for each cloud service. """
    @abstractmethod
    def cloud_connection(self,cloud_connection_details):
        pass

    @abstractmethod
    def send_message_to_cloud(self,cloud_data,mac_appName_dict,routing_table):
        pass

    @abstractmethod
    def receive_message_from_cloud(self,loop):
        pass

