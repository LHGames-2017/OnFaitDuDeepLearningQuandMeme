import pickle
import urllib.request

# create a password manager
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

# Add the username and password.
# If we knew the realm, we could use it instead of None.
server = "http://jabarsz.cz:64345"
password_mgr.add_password(None, server, "admin", "admin")

handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

# create "opener" (OpenerDirector instance)
opener = urllib.request.build_opener(handler)

# Install the opener.
# Now all calls to urllib.request.urlopen use our opener.
urllib.request.install_opener(opener)

def get(resource):
    url = server + "/" + resource
    response = urllib.request.urlopen(url)
    result = response.read()
    return result

def put(resource, data):
    url = server + "/" + resource
    req = urllib.request.Request(url, data, method='PUT')
    response = urllib.request.urlopen(req)
    result = response.read()
    return result == b'Created'

def store(state, name="state"):
    put(name, pickle.dumps(state))

def load(name="state"):
    data = get(name)
    return pickle.loads(data)