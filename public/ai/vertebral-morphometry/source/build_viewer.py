import json, sys
data = json.load(open(sys.argv[1])); out = sys.argv[2]
t = open('/home/user/vmorph/web/template.html').read()
m = open('/home/user/vmorph/web/morph.js').read().replace("if (typeof module !== 'undefined') module.exports = { analyze, levelName };", '')
payload = json.dumps(data, separators=(',', ':')).replace('</', '<\\/')
open(out, 'w').write(t.replace('__MORPH__', m).replace('__DATA__', payload))
print(out, len(t) + len(payload))
