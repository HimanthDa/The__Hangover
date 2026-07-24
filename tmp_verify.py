import sys
sys.path.insert(0, '.')
import api.index as idx

environ = {}

def start_response(status, headers):
    print(status, headers)

result = idx.application(environ, start_response)
print(result)
