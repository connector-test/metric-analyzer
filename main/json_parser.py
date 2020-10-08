import json, requests, os

LIX_API_ENDPOINT = os.environ.get("LIX_API_ENDPOINT", "https://eu.leanix.net/services/integration-api")
LIX_API_TOKEN = os.environ.get("LIX_API_TOKEN", "zQQEvgNLKmgNdLygWr9EcvtXUv8LOdYzySxgY9C7")
TOKEN_GEN_ENDPOINT="https://app.leanix.net/services/mtm/v1/oauth2/token"

# Class that uses BearerAuth
class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        r.headers["Content-Type"] = "application/json"
        return r

def print_json(json_object):
    """
        pretty printing json
    """
    print(json.dumps(json_object, indent=2)) 

def getJWTToken():
    data={
        "grant_type":"client_credentials"
    }
    print("Generating JWT Token...")
    post_response = requests.post(url=TOKEN_GEN_ENDPOINT, data=data, auth=('apitoken',LIX_API_TOKEN),)
    if post_response.status_code == 200:
        print("Everything looks good!")
    else:
        print("Something went wrong!")
        return None
    response_json = post_response.json()
    print(response_json)
    print("##DEBUG")
    print("ACCESS_TOKEN: " + response_json["access_token"])
    print("Done...")
    return str(response_json["access_token"])

def postDeployMetric(deploy_point):
    """
        Takes in a deploy_point of type dict/hashmap
        Calls the LEAN IX Synchronization Run 
    """
    LIX_SYNC_ENDPOINT = LIX_API_ENDPOINT + "/v1/synchronizationRuns"
    try:
        print("Calling " + str(LIX_SYNC_ENDPOINT))
        JWT_TOKEN = getJWTToken()
        post_response = requests.post(url=LIX_SYNC_ENDPOINT, data=json.dumps(deploy_point), auth=BearerAuth(JWT_TOKEN))
        print("Posted!")
        if post_response.status_code == 200:
            print("Everything looks good!")
        response_json = post_response.json()
        print(response_json)
        print("Processing Done...")
        #TODO add wait until it successfully posts, poll for sync run using ID
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
            conclusion = str(check_suite['conclusion'])
            print("#####################################################################")
            print("INFO CI-ID#" + check_suite_id + ": This looks like a valid deployment | Deployment Timestamp: " + timestamp)
            # aggregating the POST requests into data points
            deploy_point = {
                    "connectorId": "leanix-deployment-connector",
                    "connectorType": "leanix",
                    "connectorVersion": "1.0",
                    "processingDirection": "inbound",
                    "processingMode": "partial",
                    "lxVersion": "1.0.0",
                    "description": "DeploymentFrequency Metric",
                    "content": [
                        {
                            "id": "Deployment Frequency",
                            "type": "microservice",
                            "data": {
                                "name": json.dumps(repo_name),
                                "deploymentTime": json.dumps(timestamp)
                            }
                        }
                    ]
                }
            print_json(deploy_point)
            postDeployMetric(deploy_point)
            # aggregating that into a file for now
            # with open('./data/aggregation.json', 'r+') as file:
            #     print("Aggregating data...")
            #     aggregated_json = json.load(file)
            #     file.seek(0)
            #     # appending the deploy point to the content array
            #     aggregated_json['content'].append(deploy_point)
            #     # sorting keys to maintain order
            #     json.dump(aggregated_json, file, indent=2, sort_keys=True)         
            #     print("Done...")       
            print("#####################################################################")
        else:
            print("#####################################################################")
            print("INFO: This seems to be a failed deployment")
            print("#####################################################################")
