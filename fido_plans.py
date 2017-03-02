def plan_a():
	plan = {
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
    return plan

def plan_b():
		plan = {
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
	return plan


