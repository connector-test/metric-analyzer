import json, requests, os
# BASE URLS
LIX_BASE_URL = "https://demo-eu.leanix.net/services"
LIX_API_TOKEN_GEN_ENDPOINT = LIX_BASE_URL + "/mtm/v1/oauth2/token"
LIX_SYNC_ENDPOINT = LIX_BASE_URL + "/integration-api/v1/synchronizationRuns"

# OS ENV Vars
LIX_API_TOKEN = os.environ.get("LIX_API_TOKEN", "zQQEvgNLKmgNdLygWr9EcvtXUv8LOdYzySxgY9C7")
LIX_API_ENDPOINT = os.environ.get("LIX_API_ENDPOINT", LIX_BASE_URL + "/integration-api")

def print_json(json_object):
    """
        pretty printing json
    """
    print(json.dumps(json_object, indent=2)) 

def getJWTToken():
    try:
        payload={"grant_type":"client_credentials"}
        print("Generating JWT Token...")
        # do a basic auth to get the jwt token
        response = requests.post(url=LIX_API_TOKEN_GEN_ENDPOINT, data=payload, auth=('apitoken', LIX_API_TOKEN))
        response.raise_for_status() 
        access_token = response.json()['access_token']
        print("Access Token generated!")
        print("Done...")
    except Exception as error:
        access_token = None
        print ("Oops! An exception has occured:", error)
        print ("Exception TYPE:", type(error))
    finally:
        return access_token

def createSyncRun(deploy_point, auth_token):
    """
        Creates a new sync run using the LDIF present in deploy_point dict
        Returns sync_id of the new sync run
    """
    sync_id = None
    try:
        auth_header = "Bearer " + auth_token
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        # submitting a sync run
        print("Invoking " + LIX_SYNC_ENDPOINT)
        json_payload = json.dumps(deploy_point, indent=2)
        response = requests.post(url=LIX_SYNC_ENDPOINT, headers=headers, data=json_payload)
        print("Posted!, STATUS CODE: " + str(response.status_code))
        response.raise_for_status()
        print(response.json())
        sync_id = response.json()['id']
        print("Processing Done...")
    except Exception as error:
        print ("Oops! An exception has occured:", error)
        print ("Exception TYPE:", type(error))
    finally:
        return sync_id

def startSyncRun(sync_id, auth_token):
    """
        Initiates the sync run for a given sync_id
    """
    try:
        auth_header = "Bearer " + auth_token
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        LIX_START_SYNC_ENDPOINT = LIX_SYNC_ENDPOINT + "/" + sync_id + "/start"
        print("Invoking " + LIX_START_SYNC_ENDPOINT )
        response = requests.post(url=LIX_START_SYNC_ENDPOINT, headers=headers)
        print("Posted!, STATUS CODE: " + str(response.status_code))
        response.raise_for_status()
        print("Processing Done...")
    except Exception as error:
        print ("Oops! An exception has occured:", error)
        print ("Exception TYPE:", type(error))

def testParser(json_object):
    """
        takes in a github webhook json, 
        parses it and does a bit of metadata processing
    """
    # checking if it really is a check_suite json object
    if 'check_suite' in json_object and json_object['action'] == 'completed':
        if json_object['check_suite']['conclusion'] == 'success':
            # repo metadata
            repo_name = str(json_object['repository']['name'])
            # CI metadata
            check_suite = json_object['check_suite']
            check_suite_id = str(check_suite['id'])
            timestamp = str(check_suite['updated_at'])
            print("#####################################################################")
            print("INFO CI-ID#" + check_suite_id + ": This looks like a successful deployment | Deployment Timestamp: " + timestamp)
            # aggregating the POST requests into data points
            deploy_point = {
                "connectorId": "leanix-deployment-connector",
                "connectorType": "leanix",
                "connectorVersion": "1.0.0",
                "processingDirection": "inbound",
                "processingMode": "partial",
                "lxVersion": "1.0.0",
                "description": "DeploymentFrequency Metric",
                "content": [
                    {
                        "id": "Deployment Frequency",
                        "type": "microservice",
                        "data": {
                            "name": repo_name,
                            "deploymentTime": timestamp
                        }
                    }
                ]
            }
            # print json and process it
            print_json(deploy_point)
            auth_token = getJWTToken()
            sync_id = createSyncRun(deploy_point, auth_token)
            startSyncRun(sync_id, auth_token)
            print("#####################################################################")
        else:
            print("#####################################################################")
            print("INFO: This seems to be a failed deployment")
            print("#####################################################################")
