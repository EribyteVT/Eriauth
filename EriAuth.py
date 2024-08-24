from quart import Quart, request
import requests
import os

env = "PROD"

if(env == "PROD"):
    encryption_url = "http://10.96.46.46:5000"
    crud_url = "http://10.96.46.21:46468"

elif(env == "DEV"):
    encryption_url = "http://127.0.0.1:5000"
    crud_url = "http://127.0.0.1:46468"
app = Quart(__name__)


def encrypt(to_encrypt):
    encryption_request = {"to_encrypt":to_encrypt}

    r = requests.post(encryption_url+"/encrypt",json=encryption_request)

    returned = r.json()

    encrypted = returned["encrypted"]
    salt = returned["salt"]

    print(encrypted)
    print(salt)

    return encrypted, salt

def save_and_encrypt(data):

    access_token = data["access_token"]
    refresh_token = data["refresh_token"]

    headers = {'Authorization': f'Bearer {access_token}',
               'Client-Id':os.environ.get("APP_ID")}

    user = requests.get('https://api.twitch.tv/helix/users',headers=headers)

    print(user.json())

    user_id = user.json()['data'][0]['id']

    


    encrypted_refresh, salt_refresh = encrypt(refresh_token)

    encrypted_access, access_refresh = encrypt(access_token)

    data = {"twitch_id":user_id,
            "refresh_token":encrypted_refresh,
            "refresh_salt":salt_refresh,
            "access_token":encrypted_access,
            "access_salt":access_refresh,
            "password":os.environ.get("CRUD_PASSWORD")}

    response = requests.post(crud_url+'/token/updateToken',json=data)

    print(response.text)

    if(response.text == "UPDATED"):
        return True
    
    return False

@app.route('/', methods=["GET"])
async def authorize():
    auth_code = request.args.get("code")

    params = {'client_id': os.environ.get("APP_ID"), 
              'client_secret': os.environ.get("APP_SECRET"), 
              'code': auth_code, 
              'grant_type': 'authorization_code', 
              'redirect_uri': 'http://localhost:46469', }
    
    r = requests.post("https://id.twitch.tv/oauth2/token",params=params)

    returned = r.json()

    print(returned)

    success = save_and_encrypt(returned)

    if(success):
        return "<h1>AUTHENTICATED</h1>"
    
    else:
        return "<h1>ERROR, CONTACT ERIBYTE</h1>"


app.run(port=46469)