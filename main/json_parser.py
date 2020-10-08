import json, requests, os

LIX_API_ENDPOINT = os.environ.get("LIX_API_ENDPOINT", "https://eu.leanix.net/services/integration-api")
LIX_API_TOKEN = os.environ.get("LIX_API_TOKEN", "zQQEvgNLKmgNdLygWr9EcvtXUv8LOdYzySxgY9C7")

def print_json(json_object):
    """
        pretty printing json
    """
    print(json.dumps(json_object, indent=2)) 

def postDeployMetric(deploy_point):
    """
        Takes in a deploy_point of type dict/hashmap
        Calls the LEAN IX Synchronization Run 
    """
    LIX_SYNC_ENDPOINT = LIX_API_ENDPOINT + "/v1/synchronizationRuns"
    headers = {
        "Content-Type": "application/json",
        "Authorization" : "Bearer " + LIX_API_TOKEN
    }
    try:
        print("Calling " + str(LIX_SYNC_ENDPOINT))
        post_response = requests.post(url=LIX_SYNC_ENDPOINT, data=deploy_point, headers=headers)
        print("Posted!")
        print(json.dumps(post_response.json, indent=2))
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
                            "id": repo_name,
                            "type": "microservice",
                            "data": {
                                "name": repo_name,
                                "deploymentTime": timestamp
                            }
                        }
                    ]
                }
            print_json(deploy_point)
            print("Posting the Deployment LDIF...")
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
