import requests
import orjson
from datetime import datetime
from sysinvest.common.interfaces import AgentRequest



data = AgentRequest( timestamp = datetime.now(), source = 'test' )
headers = {
    "Content-Type": "application/json"
}

r = requests.post( 'http://localhost:5000/api/agent', data = orjson.dumps( data.dict() ), headers=headers )
print( r.status_code )
print( r.content )



