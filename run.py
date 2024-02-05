import subprocess
import json
import time

def run_command(command, return_json=False):
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout.strip()
    if return_json:
        return json.loads(output)
    return output

def main():
    # Initialize, plan, and apply Terraform
    print("Running Terraform commands...")
    run_command("tflocal init")
    run_command("tflocal plan")
    run_command("tflocal apply --auto-approve")

    # Extract API key from Terraform output
    print("Extracting API key...")
    apikey_output = run_command("tflocal output -json", return_json=True)
    apikey = apikey_output['apigw_key']['value']

    # Pause for 5 seconds
    print("Waiting for services to start...")
    time.sleep(5)

    # Fetch the REST API ID
    print("Fetching REST API ID...")
    restapi_output = run_command("aws apigateway --endpoint-url=http://localhost:4566 get-rest-apis", return_json=True)
    restapi_id = restapi_output['items'][0]['id']

    # Make a POST request to the API
    print("Making a POST request...")
    post_url = f"http://{restapi_id}.execute-api.localhost.localstack.cloud:4566/v1/pets"
    post_data = '{"PetType": "dog", "PetName": "tito", "PetPrice": 250}'
    post_command = f'curl {post_url} -H "x-api-key: {apikey}" -H "Content-Type: application/json" --request POST --data-raw \'{post_data}\''
    run_command(post_command)

    # Make a GET request to the API
    print("Making a GET request...")
    get_url = f"http://{restapi_id}.execute-api.localhost.localstack.cloud:4566/v1/pets/dog"
    get_command = f'curl -H "x-api-key: {apikey}" --request GET {get_url}'
    run_command(get_command)

if __name__ == "__main__":
    main()
