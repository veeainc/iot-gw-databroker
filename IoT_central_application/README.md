This section explains the procedure of replicating the IoT Central application that is created and available in one subscription to another subscription of the customer.

Prerequisites:

1.  Azure Subscription with relevant access to create IoT Central application

# Export the application

These steps explain how to export the entire IoT Central application by creating a sharable link

1.  Login to the azure portal and to the currently working IoT Central
    application

2.  Navigate to the IoT Central application you want to export, click on
    the **Administration** -\> **Application template export**

3.  Enter the Template name and template description and click on
    export, then a **sharable link** is created.
    
    https://apps.azureiotcentral.com/build/new/bc312530-0b69-46a3-9bd9-063e8d894b41

    ![](.//media/image1.png)

# Replicate an IoT Central application

To replicate an IoT central application from one subscription to another customer's subscription, please follow the steps mentioned below:

1. Use the exported link provided by the Veea Developers or follow the **Export the application** section steps

2. After clicking the exported link, Login with your azure credentials where you want to create an IoT Central application, then we can see the following screen where we need to configure the application name, custom URL, pricing plan, Billing info like Directory, subscription and Location.
    ![](.//media/image2.png)
    ![](.//media/image3.png)

3. Then click on Create button

4. After creation, you will be redirected to the IoT central home page

5. We can view that Device templates and the views for that template are replicated from source


# Custom template:

To create a template, user can go to Iot central dashboard and click on "Device templates" under "App settings". Now to create a template:

![devicetemplate](.//media/devicetemplate.png)


Now once, user has clicked on new template, user can click on "Iot device" option:

![template_type](.//media/template_type.png)

Now user can add a name of the template and then can click on "Next" and then "create".

![template_name](.//media/template_name.png)


Now once a template is created, user has two options to create a capability model:

* **Custom**: With this user can create his own customized capability model.
* **Import capability Model**: Using this user can import capability model from json files. 


Here we will be using "Import capability model" and use already existing json file to create capability model.

![import_model](.//media/import_model.png)

 
Now once Json is imported it will look like below.

![template_updated](.//media/template_updated.png)


To add the Device related tiles on the device dashboard, click on the Views page and select "Visualizing the device"

![visualisedevice](.//media/visualisedevice.png)

Under the Edit view, Update the view name according to your application. And under the Telemetry, select the Property and click on Add tile to create a tile on the dashboard

![view_name](.//media/view_name.png)


The tile now shows on the dashboard where you can change the visualization, resize the tile, and configure it


**Customize tiles**: To customize a tile on the dashboard, the dashboard must be in edit mode. The available customization options depend on the tile type:

 1. The ruler icon on a tile lets you change the visualization. Visualizations include line charts, last known values, and heat maps.

 2. The square icon lets you resize the tile.

 3. The gear icon lets you configure the visualization. For example, for a line chart visualization, you can choose to show the legend and axes, and choose the time range to plot.


Click on save and if all the customization is done, then we can click on publish on the top




## Toggle bulb state:

Navigate to **Toggle Bulb** tile or **Commands** tab in the Dashboard. You can turn on/off the bulb using the dropdown:

      bulb_state : Off or On

## Change the Threshold temperature value

To change threshold temperature,please follow below steps:

1. Navigate to Devices -> <Name of your DeviceTemplate> -> <Name of your Device>
2. Click on Update properties tab
3. Then change the value of Threshold Temperature to any value of your choice
5. Then click on save
6. The modified values can be seen in the device dashboard tab

# Enable the Rule to send Email

1. Navigate to the newly created IoT Central

2. Click on the Rules tab, and click on the existing Rules if available

3. Toggle the button to enable the Rule,

4. Also replace the Email id under email section and save it.

# Receive Email to your personal mail if rule doesn't exist

To receive email to personal mail, then follow below steps:

1. Navigate to rules
2. open the rule with the name: "Send Email if Temperature is greater than Threshold"
3. open the Email1 and add your email address and save it
4. whenever the temperature of zigbee sensor meets the condition of threshold temperature, email will be triggered

# Create a Logic app workflow to execute a command when a rule is triggered

Azure Logic Apps is a cloud service that helps you schedule, automate, and orchestrate tasks, business processes, and workflows when you need to integrate apps, data, systems, and services across enterprises or organizations.

Here we use Logic app to automate the process of turning off the bulb when a rule is triggered in IoT Central.

In the IoT Central application,

1.  Navigate to Rules

2.  If there is no rule, then create it or use an existing rule if it
    meets your purpose

3.  Click on + Microsoft Azure Logic Apps icon to add Logic app action.

    ![](.//media/image13.png)

4.  We will get a screen, Click on Go to redirect us to Azure portal to
    create a Logic app.

    ![](.//media/image14.png)

5.  Select the appropriate Subscription, Resource Group, Logic app name,
    Location and click on Review + Create

    ![](.//media/image15.png)

6.  The creation may take few seconds to get deployed. Then click on the
    resource we have created to navigate to Logic App.

    ![](.//media/image16.png)

7.  The logic app designer will be opened and click on Blank Logic App

    ![](.//media/image17.png)

8.  In the search bar for connectors and triggers, search for IoT
    Central as shown below and select “When a rule is fired trigger”

    ![](.//media/image18.png)

9.  Click on sign in to authenticate your credentials

    ![](.//media/image19.png)

10. Select the appropriate IoT central Application name and Rule for
    which want this action to be triggered

    ![](.//media/image20.png)

11. Click on New Step to add an action to perform after this Rule is
    triggered.

12. Select the IoT Central trigger from the recommended section

    ![](.//media/image21.png)

13. Then we will listed all the action that can be performed for IoT
    Central. Select the “Execute a device Command” action

    ![](.//media/image22.png)

14. Then fill the details in the following sequence from the drop down values
	* Application
	* Device Template
	* Device Component
	* Device Command
	* Device - This is the static device name we enter from IoT Central
	>Raw inputs may not be visible at this time, so first save the logic app and reload the page
	
    ![](.//media/image23.png)
	

15. For Raw inputs, we can select the parameter in the menu list to
    provide the JSON value

    ```{"request":{"on\_off":"0"}}```

    ![](.//media/image24.png)

16. Finally click on Save button.

17. Now the Logic app is ready to use. If the Rule in IoT Central is
    enabled and Rules is getting triggered, we can see the run history
    of the Logic app in the **Overview** tab of logic app as shown below

    ![](.//media/image25.png)


# Export the data to store historical data to blob storage

1. In the IoT Central application, click on **data** **export** tab

2. Click on + New and select Blob Storage

    ![](.//media/image7.png)

3. In the configuration, make the export enabled, select storage
    account if already listed, else use the connection string and
    container name manually. If storage account for blob storage is not
    available for your account, then please follow the below link to
    create it

    https://docs.microsoft.com/en-us/azure/iot-central/core/howto-export-data#create-storage-account

4.  Under data to export,
    
    1.  Enable **Telemetry** to export all the telemetry reported by
        device
    
    2.  Enable **Devices** if you want to export changes to all devices
        including their property changes
    
    3.  Enable **Device templates** if you want to export published
        device templates

5.  Click on Save button

    ![](.//media/image8.png)

    ![](.//media/image9.png)

6.  Now the data is being continuously exported to blob storage.

7.  To view the data in blob storage, navigate to the blob storage
    account resource you have created in the above steps in azure
    portal.

8.  Click on the container you have created

    ![](.//media/image10.png)

9.  Navigate to the folder structure inside for the current day and
    minute data

    ![](.//media/image11.png)

10. Click on the Json file and edit it to look into the contents of the
    telemetry data

    ![](.//media/image12.png)
