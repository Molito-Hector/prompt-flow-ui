import urllib.request
import json
import os
import ssl

from dotenv import load_dotenv
load_dotenv()
os.environ['https_proxy'] = ''
os.environ['http_proxy'] = ''
os.environ['no_proxy'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['HTTP_PROXY'] = ''
os.environ['NO_PROXY'] = ''

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
data = {"chat_history": [{"inputs": {"question": "Who is Albert Einstein?"}, "outputs": {"answer": "Albert Einstein was a German-born theoretical physicist who developed the theory of relativity, one of the two pillars of modern physics (alongside quantum mechanics). His famous equation E=mc^2 has been called 'the world's most famous equation'."}}], "question": "When did he die?"}

body = str.encode(json.dumps(data))

url = 'https://shahml-hhrub.eastus.inference.ml.azure.com/score'
# Replace this with the primary/secondary key or AMLToken for the endpoint
api_key = os.environ['AZURE_ENDPOINT']
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")

# The azureml-model-deployment header will force the request to go to a specific deployment.
# Remove this header to have the request observe the endpoint traffic rules
headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'shahml-hhrub-1' }

req = urllib.request.Request(url, body, headers)

try:
    response = urllib.request.urlopen(req)

    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))