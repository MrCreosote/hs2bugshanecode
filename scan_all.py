from pymongo import MongoClient
import json
from collections import defaultdict
import sys
from checker import checker, GOOD, BAD, UNK, dump_obj

   
with open('all.json') as f:
    data=f.read()
objs = json.loads(data)

with open('bad_ids.json') as f:
    data=f.read()
bad = json.loads(data)
known = bad.keys()

def ckpt(li):
   with open('ckpt.json', 'w') as f:
       f.write(json.dumps(li, indent=4))
h2wsobj = defaultdict(list)
for ref in objs:
    d = objs[ref]
    for h in d['extids']['handle']:
         h2wsobj[h].append(ref)

with open('ckpt.json') as f:
    d = f.read()
good_list = json.loads(d)
bad_list = []
all_list = dict()
good_handles = [ 'KBH_3673745' ] 
skip = [ '47530/78/1' ]
ct = 0
for r in objs:
    if (ct%100)==0:
       ckpt(good_list)
    ct += 1
    if objs[r]['copied'] is not None:
        continue
    if r in good_list:
        continue
    #if r in skip:
    #    continue
    #if r in known:
    #    print("Known: "+r)
    #    continue
    st=checker(r)
    if st==BAD:
        bad_list.append(r)
        print("bad:  " +r)
    else:
        good_list.append(r)

ckpt(good_list)
with open('bad3_ids.json','w') as f:
    f.write(json.dumps(bad_list, indent=4))
print("Good ids: %d" % len(good_list))
print("Bad ids: %d" % len(bad_list))

