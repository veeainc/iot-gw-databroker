from Azurecloud import Azure_cloud
import logging


logging.basicConfig(level=logging.INFO)


class ObjectFactory:
    """ Returns cloud specific class objects . """

    async def create(self,cloud_name,data): 
        if cloud_name == "azure":
            logging.debug(f"returning Azure object")
            return Azure_cloud(data)
        elif cloud_name == "AWS":            
            pass
        elif cloud_name=="gcp":
            pass

        

