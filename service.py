import fido_plans
import uuid

# Service

def fidosvc():
	fido_service_id = uuid.uuid4() # Generate unique service ID
	fido_service = {
	    'id' : fido_service_id, 
	    'name' : 'nexsign-auth-service',
	    'description' : 'fido service to showcase management of private brokers',
	    'bindable' : True, 
	    'tags' : ['private'], 
	    'plan_updateable' : False,
	    'plans' : [fido_plans.plan_a(), fido_plans.plan_b()],
	    'dashboard_client' : {
	        'id' : uuid.uuid4(),
	        'secret' : 'secret-1',
	        'redirect_uri' : 'http://bluemix.net'
	    },
	    'metadata' : {
	        'displayName' : 'Nexsign Service',
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
	        'featuredImageUrl' : 'http://fido-ui-service.mybluemix.net/images/nexsign/Nexsign_icon_64x64.png',
	        # 'imageUrl' : 'http://fido-ui-service.mybluemix.net/images/images/nexsign/Nexsign_icon_50x50.png',
	        'imageUrl' : 'http://fido-ui-service.mybluemix.net/images/images/nexsign/Nexsign_icon_32x32.png',
	        'mediumImageUrl' : 'http://fido-ui-service.mybluemix.net/images/nexsign/Nexsign_icon_32x32.png',
	        'smallImageUrl' : 'http://fido-ui-service.mybluemix.net/images/nexsign/Nexsign_icon_24x24.png',
	        'documentationUrl' : 'http://www.samsungsds.com/us/en/solutions/off/nex/nexsign.html',
	        'instructionsUrl' : 'http://www.samsungsds.com/us/en/solutions/off/nex/nexsign.html',
	        'termsUrl' : 'https://media.termsfeed.com/pdf/terms-and-conditions-template.pdf'
	    }
	}
	return fido_service
