import sys, json, os
from remotezip import RemoteZip
from concurrent.futures import ThreadPoolExecutor
url, pattern, out = sys.argv[1], sys.argv[2], sys.argv[3]
subs = sys.argv[4].split(',') if len(sys.argv)>4 else None
with RemoteZip(url) as z:
    names=[i.filename for i in z.infolist() if i.file_size>0 and '__MACOSX' not in i.filename and pattern in i.filename and (subs is None or any(s+'_' in i.filename or s+'/' in i.filename for s in subs))]
def get(n):
    dst=os.path.join(out, os.path.basename(n))
    if os.path.exists(dst): return
    with RemoteZip(url) as z:
        with open(dst+'.part','wb') as f: f.write(z.read(n))
    os.rename(dst+'.part', dst); print('got', n, flush=True)
os.makedirs(out, exist_ok=True)
with ThreadPoolExecutor(8) as ex: list(ex.map(get, names))
print('done', len(names))
