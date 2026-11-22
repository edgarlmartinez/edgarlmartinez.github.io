import json, sys
data = json.load(open(sys.argv[1])); out = sys.argv[3]
t = open(sys.argv[2]).read()
payload = json.dumps(data, separators=(',', ':')).replace('</', '<\\/')
open(out, 'w').write(t.replace('__DATA__', payload))
print(out, (len(t) + len(payload)) // 1024, 'KB')
