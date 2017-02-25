# Importing some necessary libraries
import os                      # to obtain environment info
from flask import Flask,jsonify,request,abort,make_response
from flask_basicauth import BasicAuth
import json
import uuid
from cloudant import Cloudant

#############################################################
# Database Setup : cloudant nosql db
#############################################################
db_name = 'fidodb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

#############################################################
# Global Variables
#############################################################

# Start Flask
app = Flask(__name__)

# Which CF Service Broker API version do we support?
X_BROKER_API_VERSION = 2.11
X_BROKER_API_VERSION_NAME = 'X-Broker-Api-Version'

# Configure our test username
app.config['BASIC_AUTH_USERNAME'] = 'fido-user'
app.config['BASIC_AUTH_PASSWORD'] = 'fido-pwd'
# Switch off pretty printing of JSON data
app.config['JSONIFY_PRETTYPRINT_REGULAR']=False

basic_auth = BasicAuth(app)

# Some constants we are going to use, save some typing
jsonheaders = {'Content-Type': 'application/json'}
empty_result={}

# Get service information if on Bluemix
if 'VCAP_APPLICATION' in os.environ:
    # get app URL
    service_base=json.loads(os.environ['VCAP_APPLICATION'])['application_uris'][0]
else:
    # we are local, so set service base
    service_base = "localhost:5000"

service_dashboard = "http://"+service_base+"/fido-service/dashboard/"


#############################################################
# Global Variables : FIDO Specific
#############################################################

# Where to get these information? How to insert the values for each?
# Provide a REST API to set the values ?  OR  use config.json ?
fido_admin_url = "https://fido.mybluemix.net";    # {spName}.url = {FIDO Server URL}

rp_id = "rp-id-sample";     
rp_name = "rp-name-sample";
app_id = "https://rp.mybluemix.net"; 
create_user_id = "fido-service-broker";


# api_key = ""; # {spName}.key = {Service Provider API Key}
service_instance_doc = {
    "instanceId" : "",
    "planId" : "",
    "serviceId" : "",
    "orgId" : "",
    "spaceGuid" : "",    
    "rpId" : "",
    "rpName" : "",
    "appId" : "",
    "createUserId" : "",
    "apiKey" : ""
}

service_binding_doc = {
    "instanceId" : "",
    "bindingId" : "",
    "planId" : "",
    "serviceId" : "",
    "appGuid" : "",
    "bindingDetails" : {
        "credentials" : {
            "apiKey" : "",
        },
        "syslog_drain_url" : ""
    }
}


#############################################################
# Definition of Service and Plans : Sample
#############################################################

# Plans
fido_plan_a = {
    "name" : "fidoplan-a",
    "description" : "Describe the characteristics of this plan. For example, Dedicated schema and tablespace per service instance on a shared server. 1GB and 10GB of compressed database storage can hold up to 5GB and 50GB of uncompressed data respectively based on typical compression ratios.",
    "free" : True,
    "id" : uuid.uuid4(), # SHOULD BE UNIQUE
    "metadata" : {
        "bullets" :[
            "A description of the resources that can be used with the plan.",
            "1 Auth Module per instance. Can host 100 concurrent auth operation.",
            "1 GB Min per instance. 10 GB Max per instance."
        ],
        "costs":[
            {
                "unitId" : "INSTANCES_PER_MONTH",
                "unit" : "MONTHLY",
                "partNumber" : ""
            }
        ],
    "displayName":"fidoPlanA"
    }
}

fido_plan_b = {
    "name" : "fidoplan-b",
    "description" : "Describe the characteristics of this plan. For example, Dedicated schema and tablespace per service instance on a shared server. 1GB and 10GB of compressed database storage can hold up to 5GB and 50GB of uncompressed data respectively based on typical compression ratios.",
    "free" : True,
    "id" : uuid.uuid4(), # SHOULD BE UNIQUE
    "metadata" : {
        "bullets" :[
            "A description of the resources that can be used with the plan.",
            "10 Auth Module per instance. Can host 1000 concurrent auth operation.",
            "10 GB Min per instance. 100 GB Max per instance.",
        ],
        "costs" :[
            {
                "unitId" : "INSTANCES_PER_MONTH",
                "unit" : "MONTHLY",
                "partNumber" : ""
            }
        ],
        "displayName":"fidoPlanB"
    }
}


# Service
fido_service_id = uuid.uuid4() # Generate unique service ID
fido_service = {
    'id' : fido_service_id, 
    'name' : 'sds-fido-service',
    'description' : 'fido service to showcase management of private brokers',
    'bindable' : True, 
    'tags' : ['private'], 
    'plan_updateable' : True,
    'plans' : [fido_plan_a, fido_plan_b],
    'dashboard_client' : {
        'id' : uuid.uuid4(),
        'secret' : 'secret-1',
        'redirect_uri' : 'http://bluemix.net'
    },
    'metadata' : {
        'displayName' : 'Fido Service',
        'serviceMonitorApi' : 'https://cf-upsi-app.mybluemix.net/healthcheck',
        'providerDisplayName' : 'S.D.S',
        'longDescription' : 'Write full description of fido service',
        'bullets' : [
            {
                'title' : 'Fast and Simple',
                'description' : 'FIDO Service uses dynamic in-memory columnar technology and innovations, such as parallel vector processing and actionable compression to rapidly scan and return relevant data.'
            },
            {
                'title' : 'Connectivity',
                'description' :' FIDO Service is built to let you connect easily and to all of your services and applications. You can start analyzing your data immediately with familiar tools.'
            }
        ],
        'featuredImageUrl' : 'https://cf-upsi-app.mybluemix.net/images/fidoimg-64x64.png',
        'imageUrl' : 'https://cf-upsi-app.mybluemix.net/images/fidoimg-50x50.png',
        'mediumImageUrl' : 'https://cf-upsi-app.mybluemix.net/images/fidoimg-32x32.png',
        'smallImageUrl' : 'https://cf-upsi-app.mybluemix.net/images/fidoimg-24x24.png',
        'documentationUrl' : 'http://www.samsungsds.com/us/en/solutions/off/nex/nexsign.html',
        'instructionsUrl' : 'http://www.samsungsds.com/us/en/solutions/off/nex/nexsign.html',
        'termsUrl' : 'https://media.termsfeed.com/pdf/terms-and-conditions-template.pdf'
    }
}


########################################################
# Implement Cloud Foundry Broker API
# In thise file:
# * catalog - return service information including related service plans
# * provision - create the service (add it to the Cloud Foundry / Bluemix catalog)
# * deprovision - delete the service (remove it from the catalog)
# * bind - bind/link a service to an app
# * unbind - remove the linkage to an app
########################################################

#
# Catalog
#
@app.route('/v2/catalog', methods=['GET'])
#@basic_auth.required
def catalog():
    # Return the catalog of services handled by this broker
    #
    # GET /v2/catalog:
    #
    # HEADER:
    #     X-Broker-Api-Version: <version>
    #
    # return:
    #     JSON document with details about the
    #     services offered through this broker

    api_version = request.headers.get('X-Broker-Api-Version')
    # Check broker API version
    if not api_version or float(api_version) < X_BROKER_API_VERSION:
        abort(412, "Precondition failed. Missing or incompatible %s. Expecting version %0.1f or later" % (X_BROKER_API_VERSION_NAME, X_BROKER_API_VERSION))
    services={"services": [fido_service]}
    return jsonify(services)


#
# Provision
#
@app.route('/v2/service_instances/<instance_id>', methods=['PUT'])
@basic_auth.required
def provision(instance_id):
    # Provision an instance of this service for the org/space
    # as provided in the JSON data
    #
    # PUT /v2/service_instances/<instance_id>:
    #    <instance_id> provided by Bluemix Cloud Controller,
    #   used for future requests like bind, unbind and deprovision
    #
    # BODY:
    #     {
    #       "service_id":        "<service-guid>",
    #       "plan_id":           "<plan-guid>",
    #       "organization_guid": "<org-guid>",
    #       "space_guid":        "<space-guid>"
    #     }
    #
    # return:
    #     JSON document with service details

    if request.headers['Content-Type'] != 'application/json':
        abort(415, 'Unsupported Content-Type: expecting application/json')

    # provision the service by calling out to the service itself
    # not done here to keep the code simple for the tutorial
    
    # get the JSON document in the BODY
    provision_details = request.get_json(force=True)
    print("Provision details : " + provision_details)

    ### TODO
    # 1. Check the document of specific instance is already exist in db
    #   1-a. if exist, return with "already exist"
    #   1-b. if not, store the new service_instance_doc    <createServiceInstance>

    # Save API Key and RP ID from FidoAdmin
    print("In provision instance_id : " + instance_id)

    if client:
        apikey_data = {'API_Key':'1234567890'}
        rp_id = {'rp_id':'0987654321'}
        db.create_document(apikey_data)
        db.create_document(rp_id)
    else:
        print('No database')

    # return basic service information
    new_service = { "dashboard_url": service_dashboard+instance_id }
    return jsonify(new_service)

#
# Deprovision
#
@app.route('/v2/service_instances/<instance_id>', methods=['DELETE'])
@basic_auth.required
def deprovision(instance_id):
    # Deprovision an existing instance of this service
    #
    # DELETE /v2/service_instances/<instance_id>:
    #    <instance_id> is the Cloud Controller provided
    #      value used to provision the instance
    #
    # return:
    #    An empty JSON document is expected

    # deprovision would call the service here
    # not done to keep our code simple for the tutorial

    ### TODO
    # 1. Check the document of specific instance is exist in db
    #   1-a. if exist, delete the document from db      <deleteServiceInstance>
    #       2. if binding doc for this instance exist, delete them all <unbindAllForServiceInstance>
    #   1-b. if not, return empty_result

    return jsonify(empty_result)

#
# Bind
#
@app.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['PUT'])
@basic_auth.required
def bind(instance_id, binding_id):
    # Bind an existing instance with the given org and space
    #
    # PUT /v2/service_instances/<instance_id>/service_bindings/<binding_id>:
    #     <instance_id> is the Cloud Controller provided
    #       value used to provision the instance
    #     <binding_id> is provided by the Cloud Controller
    #       and will be used for future unbind requests
    #
    # BODY:
    #     {
    #       "plan_id":           "<plan-guid>",
    #       "service_id":        "<service-guid>",
    #       "app_guid":          "<app-guid>"
    #     }
    #
    # return:
    #     JSON document with credentails and access details
    #     for the service based on this binding
    #     http://docs.cloudfoundry.org/services/binding-credentials.html

    if request.headers['Content-Type'] != 'application/json':
        abort(415, 'Unsupported Content-Type: expecting application/json')

    # get the JSON document in the BODY
    binding_details = request.get_json()
    print("Binding details: " + binding_details)

    # bind would call the service here
    # not done to keep our code simple for the tutorial

    ### TODO
    # 1. Check the document of specific instance is already exist in db
    #   1-a. if exist, retrieve the ApiKey 
    #       2. Check whether Binding Doc exist
    #           2-a. if exist, update it with new values then return normal
    #           2-b. if not, create new ServiceBindingDoc   <bindServiceInstance>
    #   1-b. if not, return error


    # return result to the Bluemix Cloud Controller
    result = {  
        "credentials" : {
            "apiKey" : uuid.uuid4(),    # this value will be retrieved from ServiceInstanceDoc 
            "rpId" : "",    # remove if unnecessary
            "appId" : ""    # remove if unnecessary
        }
    }

    return make_response(jsonify(result),201)

#
# Unbind
#
@app.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['DELETE'])
@basic_auth.required
def unbind(instance_id, binding_id):

    # Unbind an existing instance associated with an app
    #
    # DELETE /v2/service_instances/<instance_id>/service_bindings/<binding_id>:
    #     <instance_id> and <binding_id> are provided by the Cloud Controller
    #
    # return:
    #     An empty JSON document is expected

    # unbind would call the service here
    # not done to keep our code simple for the tutorial

    # 1. Check whether Binding Doc exist
    #   1-a. if exist, remove the doc from db   <unbindServiceInstance>
    #   1-b. if not, return empty result

    return jsonify(empty_result)

########################################################
# Service-related functions for some additional testing
#
#
########################################################

@app.route('/fido-service/dashboard/<instance_id>', methods=['GET'])
def dashboard(instance_id):
    # hardcoded HTML, but could be a rendered template, too
    # Consider offering customized page for different instances
    dashboard_page = "<img src='http://contents.dt.co.kr/images/201510/2015102802101860727001[2].jpg' />"
    dashboard_page += "<h3>Welcome!!</h3> You discovered the dashboard for instance : " + instance_id;
    dashboard_page += "<img src='http://news.samsungsds.com/wp-content/uploads/2016/10/19-2.jpg' />"
    return dashboard_page

# SERVICE INSTANCE
def createServiceInstance(instance_id, req_body):
    return jsonify(empty_result)
def deleteServiceInstance(instance_id):
    return jsonify(empty_result)

# BINDING
def bindServiceInstance(instance_id, binding_id, service):
    return jsonify(empty_result)
def unbindServiceInstance(instance_id, binding_id):
    return jsonify(empty_result)
def unbindAllForServiceInstance(instance_id):
    return jsonify(empty_result)

########################################################
# Catch-all section - return HTML page for testing
#
#
########################################################

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    page = '<title>Fido Service Broker</title>'
    page += '<h2>This is a sample service broker for Samsung SDS Nexsign: Fido Solution</h2>'
    page += '<p>See <a href="https://github.com/Mike-msoh/fido-service-broker">the related GitHub repository</a> for details.</p>'
    page += '<p>You requested path: /%s </p>' % path
    return page


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port),threaded=True)
    #app.run(host='0.0.0.0', port=int(port),debug=True,threaded=True)


