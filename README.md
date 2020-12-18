# DataBroker

It collects event data from applications and sends it to Azure IOT hub.

## Pre-requisites
Make sure that VHC toolkit is installed on your system and Veea hubs are configured. If not, refer to VHC toolkit installation guide.


## Build

Use the following command to build the image(according to Veea hub available i.e VHC05/VHE09-10) 
 
```bash
vhc build --target vhc05 --unsigned      #for VHC05 hub
vhc build --target vhx09-10 --unsigned   #for VHE09/VHE10 hub
```

## Deployment
Once the image has been built, you can deploy it to Veea hub

```bash
$ vhc hub image --create bin/databroker-armhf:2.0.1.tar  #for VHC05 hub
Creating image push for file [bin/databroker-armhf:2.0.1.tar] on <HUB_ADDRESS>:9000 (https://<IP_ADDRESS>:9000/images/push)...
   166.82 MB / 166.82 MB  [=============================================================================] 100.00%
   {
      "image_id": "7ebd9f6c1c239675dc5f66fa34b19f3754b71313a7957630ac7bed552730e8bc"
   }


$ vhc hub image --create bin/databroker-arm64v8:2.0.1.tar    #for VHE09/VHE10 hub
Creating image push for file [bin/databroker-arm64v8:2.0.1.tar] on <HUB_ADDRESS>:9000 (https://<IP_ADDRESS>:9000/images/push)...
   185.88 MB / 185.88 MB  [=============================================================================] 100.00%
   {
      "image_id": "7ebd9f6c1c239675dc5f66fa34b19f3754b71313a7957630ac7bed552730e8bc"
   }
```


* **Delete an image**

Use the following command to delete an image:

```bash
    $ vhc hub image --delete 7ebd9f6c1c239675dc5f66fa34b19f3754b71313a7957630ac7bed552730e8bc 
    
    Deleting image 7ebd9f6c1c239675dc5f66fa34b19f3754b71313a7957630ac7bed552730e8bc on <HUB_ADDRESS>:9000(https://<IP_ADDRESS>:9000/images/7ebd9f6c1c239675dc5f66fa34b19f3754b71313a7957630ac7bed552730e8bc)...
```


* **Creating container from image**

Use the following command to create a container:

```bash
    $ vhc hub image --create-container 7ebd9f6c1c239675dc5f66fa34b19f3754b71313a7957630ac7bed552730e8bc 
    
    Creating container from image 7ebd9f6c1c239675dc5f66fa34b19f3754b71313a7957630ac7bed552730e8bc on C05BCB00C0A000001127:9000(https://<IP_ADDRESS>:9000/images/7ebd9f6c1c239675dc5f66fa34b19f3754b71313a7957630ac7bed552730e8bc/create_container)...
    351 B / 351 B [=====================================================================================] 100.00%
    {
      "container_id": "c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a",
      "detached": true
    }  
```

    You will get a container-ID after creating container. Use that ID to start/stop/attach the container.

* **Start container**

Use the following command to start the container:

```bash
    $ vhc hub container --start c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a
    Starting container c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a C05BCB00C0A000001127:9000(https://<IP_ADDRESS>:9000/containers/c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a/start)...
    Success
```


* **Stop container**

Use the following command to stop the container:

```bash
    $ vhc hub container --stop c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a
    Stopping container c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a C05BCB00C0A000001127:9000 (https://<IP_ADDRESS>:9000/containers/c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a/stop)...
    Success
```

* **Attach container**

Use the following command to attach to the container:

```bash
    $ vhc hub container --attach c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a "/bin/sh -il"
     Attaching to stdin/stdout/stderr on C05BCB00C0A000001127:9001...
     Attaching to container c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a C05BCB00C0A000001127:9000 (https://<IP_ADDRESS>:9000/containers/c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a/attach)...
     Success
```

* **Delete Container **

Use the following command to delete the container:

```bash
    $ vhc hub container --delete c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a

    Deleting container c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a on <HUB_ADDRESS>:9000(https://<IP_ADDRESS>:9000/containers/c4a2da5042b95f85cbfca8eb136ad9b390cafe380352606a6654d2dc2c99274a)...
```


## Accessing IoT Central
It is a fully managed SaaS app that makes it easy to connect, monitor, and manage IoT assets. Within the data broker, IoT Central is used for displaying data and controlling devices.

* **Pre-requisites**: Data broker should be up and running to control  devices.
* **Visit the below link to access IOT central:**

  ```https://veeazigbeeappdemo.azureiotcentral.com/```

**Note**: If you want to replicate the creation of IoT Central Application in your subscription rather than using the existing one, please follow the steps provided in ~/databroker/IoT_central_application folder

A GUI for databroker is provided for making connection to IoT Central.
* Access the Databroker UI using ```"<IP-address of VeeaHub>:9060"```.

![updated_broker_ui](.//images/updated_broker_ui.png)

To get these connection details, Navigate to IOT Central

  ```https://veeazigbeeappdemo.azureiotcentral.com/```

For ID Scope, go to Administration->Device Connection->ID scope

![id_scope](.//images/id_scope.png)


For Primary Key, go to Administration -> Device Connection -> Enrollment groups -> SAS-IoT-Devices -> Primary key

![primary_key](.//images/primary_key.png)


**Note**: These cloud details are stored in persistent storage. So no need to enter cloud details again if the container is deleted and recreated again on the same hub. 


Once the application starts sending data, one need to assign a template to the device on IOT central by navigating to:
  ```Devices-><YOUR_DEVICE_NAME>```


## Assigning a template
Once the device gets registered on IoT central, it will have no template assigned to it. 

![not_selected](.//images/not_selected.png)


Now you have two options:

* **Create your own template**: Kindly refer to ```IoT_central_application/README.md``` for creating custom template
* **Choose from existing templates**: Iot central will be pre-populated with few templates. User can choose from them. 

To assign a template just select the device and then "Migrate" option will be visible.

![selected](.//images/selected.png)

Click on "Migrate" option to assign a template to a device. 

![migrate_updated](.//images/migrate_updated.png)

Once template is assigned to a device it will be like below:

![assigned](.//images/assigned.png)
