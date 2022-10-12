
# CHIME Developer Python Application

## Getting Started

### Introduction
CHIME Developer enables users to build apps faster than ever before. Users leverage their own IP and methodologies to address the specific needs of the operator’s network. 
CHIME Developer features a fully hosted development environment, making integration with CHIME services quick and easy. 
Furthermore, CHIME Developer facilitates testing and debugging your application code, without ever having to leave your browser.

This sample application provides a starting point for developing Python applications suitable for execution on the CHIME Developer platform.

* For more information about CHIME, see: [CHIME Platform](https://www.cellwize.com/platform).  
* For the API reference, refer to [CHIME API Reference](https://kb.cellwize.com/display/DPO/API+References).

### Quick Start
The following instructions explain how to configure your URLs and call your first CHIME API.

<b>To call your first CHIME API, simply do as follows:</b>

* Configure API urls in <b>utils/api_init.py</b>

	```python
      # Configure CHIME Services endpoints
      NAAS_URL = 'https:/<chime-developer-uri>/naas'
      XPAAS_URL = 'https://<chime-developer-uri>/xpaas'
      PGW_URL = 'https://<chime-developer-uri>/pgw'
      AUTH_URL = 'https://<chime-developer-token-uri>'
    
      # Configure Client_ID and Client_Secret to enable authentication
      CLIENT_ID = None
      CLIENT_SECRET = None
	```
* Call the API from <b>main.py</b>
     ```python
      from utils.logger_config import logger
      from utils.api_init import naas
      
      def main():
          lte_cells_res = naas.api.cells.get_cells(params={'technology': 'LTE'})
          logger.info("Cells: "+str(lte_cells.res.body))
          
      if __name__ == '__main__':
          main()
    ```

### Project Structure
The following describes the structure of a project using the CHIME SDK.  
Instructions are included in <i>italics</i>. 

* <b>main.py</b>. Main entry point for the application. 
* <b>requirements.txt</b>. Application dependencies configuration.
* <b>getting-started.py</b>. Code samples. <i>Run this code and read the comment to learn the basics of using the CHIME SDK.</i>
* <b>config:</b>
    * <b>config.yaml</b> Application configuration. <i>Specify application metadata as well as the application configuration schema.</i>
    * <b>config-test.yaml</b>. <i>Configure test values for application parameters.</i> This is to be used during development.
* <b>utils:</b>
    * <b>api_init.py</b>. CHIME API clients initialization.
    * <b>context.py</b>. Application context initialization. <i>Do not modify.</i>
    * <b>logger_config</b>. Logging configuration. <i>Do not modify.</i>


### Application Configuration
The following describes application configuration, and includes a sample configuration. 
Application configuration is maintained in <i>/config/config.yaml</i>. The configuration consists of two main sections:
1. meta - metadata for the application.
2. schema - configuration schema for the application. This is where you configure the application parameters.

#### Sample Configuration
```yaml
application:
  meta:
    name: chime-app-1
    description: This is a prototype chime application
    author: john.doe@cellwize.com
  schema:
      name: NAAS_CLUSTER
      displayName: NaaS Cluster
      description: Name of NaaS cluster for this application
      defaultValue:
      type: string
      group: General Settings

```
In the example shown above, the application requires a single parameter. This parameter is known as <i>NAAS_CLUSTER</i>. You can add additional parameters.

<b>For each parameter specify the following:</b>

* <b>name</b>: Name of the parameter. Please use letters only, and no whitespace.
* <b>displayName</b>: Display name for the parameter, used for UI configuration.
* <b>description</b>: Parameter description.
* <b>defaultValue</b> (Optional): Specify a default value for the parameter, if there is no runtime value provided by the user.
* <b>type</b>: Parameter type.  String, Number, and Boolean are supported.
* <b>group</b>: For display purposes, parameters can be grouped based on their <i>group</i> value.
 

### Accessing Application Context
At runtime, CHIME Platform injects the value of each of the parameters defined in <i>config.yaml</i> based on user definition. 
Parameter values are available as environment variables, and are automatically populated into a <i>context</i> dictionary object.
Working with the <i>context</i> object:
```python
from utils.context import context

naas_cluster = context.get('NAAS_CLUSTER')
```

#### Test Application Context
During development, you may wish to set test values for the application parameters.

<b>To test application context:</b>
1. Edit <i>/config/config-test.yaml</i>
2. Specify <i>key: value</i> pairs. 

For example:
```yaml
NAAS_CLUSTER: TEST_CLUSTER
```

Parameter values in <i>config-test.yaml</i> are only used during development. At runtime the values will be overridden by user defined values.

#### Special Context Parameters
At runtime, CHIME injects a set of pre-defined parameters for the convenience of the application developer.
For example, a <i>TRACKING_ID</i> parameters is injected, to track each individual execution of the application.

###  CHIME Client SDK

#### Overview
CHIME client supports the three main CHIME services: 

* NaaS, 
* XPaaS 
* PGW. 

The CHIME Python client library is embedded in the CHIME Developer development and runtime environments. 

#### Client Initialization
This section describes how to initialize the CHIME client. 

<b>To initialize the CHIME Client:</b>
1. Set the API configuration in <b>utils/api_init.py</b>. 
2. To enable authentication, configure the API URLs (provided by Cellwize Support), as well as your application CLIENT_ID and CLIENT_SECRET.

```python
# Configure CHIME Services endpoints
NAAS_URL = 'https:/<chime-developer-uri>/naas'
XPAAS_URL = 'https://<chime-developer-uri>/xpaas'
PGW_URL = 'https://<chime-developer-uri>/pgw'
AUTH_URL = 'http://<chime-developer-token-uri>'

# Configure Client_ID and Client_Secret to enable authentication
CLIENT_ID = None
CLIENT_SECRET = None
```
Once configured, <i>api_init.py</i> initializes three (3) client objects, available throughout the application: <i>naas, xpaas, pgw</i>.
All API calls are routed via an API Gateway, responsible for securing the CHIME APIs. The initialization code authenticates the clients automatically, and configures them with an access token.

#### Making API Calls
This section describes how to make API calls with a CHIME client. 

<b>To use a CHIME client:</b>
Simply import it to your code and invoke the API. For example:

```python
from utils.api_init import naas

lte_cells_res = naas.api.cells.get_cells(params={'technology': 'LTE', 'fields': '_id,name,mcc,mnc,rsi,pci'})
```
In the example above, we are calling the NaaS  <i>cells</i> resource, invoking the <i>get_cells</i> API. 
The response body is available via the <i>body</i> attribute of the response object. It is a dictionary object representing the JSON response of the REST API call.
```python
lte_cells = lte_cells_res.body
```

##### Query Parameters
Sending query string parameters is achieved via the <i>params</i> attribute, which takes a dictionary (json) as its value. 
For example:
```python
from utils.api_init import naas

lte_cells = naas.api.cells.get_cells(params={'technology': 'LTE', 'fields': '_id,name,mcc,mnc,rsi,pci'})
```
... translates to the following request: 
```
GET /naas/v1/cells?technology=LTE&fields=_id,name,mcc,mnc,rsi,pci
```
##### Request Body 
Sending a POST request body is achieved via the <i>body</i> attribute, which takes a dictionary (json) as its value.
For example, sending a workorder request to PGW:
```python
# Preparing a Workorder object
work_order = {
        'mode': 'OFFLINE_SIM',
        'method': 'NON_TRANSACTION',
        'priority': '1',
        'trackingId': context.get('TRACKING_ID'),
        'workItems': work_items
    }

# Sending a Workorder Request
work_order_res = pgw.api.workorders.send_workorder(body=work_order)
```
Note that we pass the auto populated <i>TRACKING_ID</i> in the workorder request. This allows CHIME Developer to correlate the execution of the application and the workorder. 

#####  Path Parameters
Some API calls require a Path parameter. Path parameters are send as explicit values in the API call.
For example, retrieving  all cells of a given cluster:
```python
cells = naas.api.clusters.get_cluster_cells('TEST_CLUSTER')
```
... translates to a request:
```
GET /v1/naas/clusters/TEST_CLUSTER/cells
```
... which returns all cells belonging to the pre-defined cluster named <i>TEST_CLUSTER</i>

##### Listing Available APIs
This section describes how to list all the available APIs. 

<b>To list all the resources available for each client:</b>
Run the following ... 

```python
naas.api.get_resource_list()

['cells', 'clusters', 'controllers', 'mos', 'networkmodel', 'neighbors', 'neural_engine', 'x2links']
```
... and for each resource, you can list available APIs:
```python
naas.api.cells.actions

{
'get_cells': {'method': 'GET', 'url': '/v1/cells'}, 
'get_cells_next_page': {'method': 'GET', 'url': '/v1/cells'}, 
'search_cells': {'method': 'POST', 'url': '/v1/cells'}, 
'get_cell_by_id': {'method': 'GET', 'url': '/v1/cells/{}'}, 
'get_co_sectors': {'method': 'GET', 'url': '/v1/cells/{}/cosectors'}, 
'get_co_sites': {'method': 'GET', 'url': '/v1/cells/{}/cosites'}, 
'get_neighbors': {'method': 'GET', 'url': '/v1/cells/{}/neighbors'}
}

```

### Installing Dependencies 
If your application requires additional Python packages, you can install them into your workspace using the <b>pip install</b> menu command.\
Configure the required libraries in <b>requirements.txt</b>. For example:
```text
PyYAML~=5.3.1
oauthlib~=3.1.0
requests-oauthlib~=1.3.0
```
Use  <i>Terminal --> Run Task</i> to run the pre-defined <b>pip install</b> task, and provide the name of your project. The tasks reads your <i>requirements.txt</i> and installs it into the development environment.

CHIME Platform reads the same <i>requirements.txt</i> as part of the application build process, and installs all required packages into the runtime environment. This ensures that your dev configuration and runtime configurations are always aligned.

