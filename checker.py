import json

import gzip
import os
BAD=0
GOOD=1
UNK=2

def check_missing(ref):
    for hid in objs[ref]['extids']['handle']:
        if hid not in handles:
          return False
    return True

def get_shock_file(sid):
    return '/disk1/shock/data/%s/%s/%s/%s/%s.data' % (sid[0:2], sid[2:4], sid[4:6], sid, sid)
   
def count_genes(fn):
    ct =0
    if not os.path.exists(fn):
        print("Missing handle file " + fn)
        return -1
    with gzip.open(fn, 'rb') as f:
        for li in f:
            items=li.decode('utf-8').split('\t')
            if len(items)>1 and items[2]=='gene':
                ct+=1
    return ct

def read_kvs(ref):
    kvs=dict()
    for kv in objs[ref]['meta']:
       kvs[kv['k']] = kv['v']
    return kvs

def check_genome(ref, odata):
    if 'original_source_file_name' not in odata:
        gff=handles[odata['gff_handle_ref']]
        gct=count_genes(get_shock_file(gff['id']))
        kvs = read_kvs(ref)
        if int(kvs['Number of Protein Encoding Genes']) == gct:
           return True
        print(gct)
        print(odata.keys())
        print(odata['gff_handle_ref'])
        print(ref)
        return BAD
    fn1=odata['original_source_file_name']
    hrec = handles[odata['genbank_handle_ref']]
    fn1=odata['original_source_file_name']
    fn2=hrec['file_name'].replace('.gz','')
    if fn1==fn2:
        return GOOD
    print(fn1)
    print(fn2)
    return BAD

def check_cat(odata):
     print(odata.keys())
     print(odata['classifier_handle_ref'])
     print(odata['lib_name'])
     hid = odata['handle']['hid']
     oid = odata['handle']['id']
     id2=handles[hid]['id']
     if oid==id2:
         return GOOD
     else:
         return BAD
def check_gff(odata):
     hid = odata['handle']['hid']
     oid = odata['handle']['id']
     id2=handles[hid]['id']
     if oid==id2:
         return GOOD
     else:
         return BAD

def check_report_type(odata):
    good=0
    l = odata['file_links']
    l.extend(odata['html_links'])
    #l.append(odata['direct_html'])
    for f in l:
        if f is None:
           continue
        if f=='':
           continue
        if f['handle'] in handles:
           hid=f['handle']
           id2=handles[hid]['id']
           oid=f['URL'].split('/')[-1]
           if oid==id2:
              good+=1
           else:
              return BAD
    return GOOD
        
def check_bowtie(odata):
     hid = odata['handle']['hid']
     oid = odata['handle']['id']
     id2=handles[hid]['id']
     if oid==id2:
         return GOOD
     else:
         return BAD

def check_single(odata):
       hid = odata['lib']['file']['hid']
       oid = odata['lib']['file']['id']
       id2=handles[hid]['id']
       if oid==id2:
           return GOOD
       else:
           return BAD

def check_paired2(odata):
    good=0
    print(odata)
    li = [odata['handle_1']]
    if 'handle_2' in odata:
       li.append(odata['handle_2']['file'])
    for f in li:
        hid = f['hid']
        oid = f['id']
        id2=handles[hid]['id']
        if oid==id2:
            good+=1
        else:
            return BAD
    return GOOD

def check_paired(odata):
    good=0
    li = [odata['lib1']['file']]
    if 'lib2' in odata:
       li.append(odata['lib2']['file'])
    for f in li:
        hid = f['hid']
        oid = f['id']
        id2=handles[hid]['id']
        if oid==id2:
            good+=1
        else:
            return BAD
    return GOOD

def check_assembly(odata, ref):
    if 'fasta_handle_info' not in odata:
        print(ref)
        return BAD
    oid=odata['fasta_handle_info']['handle']['id']
    hid=odata['fasta_handle_info']['handle']['hid']
    hoid=handles[hid]['id']
    if hoid==oid:
        return GOOD
    else:
        return BAD

def check_alignment(odata):
    good=0
    oid=odata['file']['id']
    hid=odata['file']['hid']
    if hid in handles: 
        hoid=handles[hid]['id']
        if hoid==oid:
            good+=1
        else:
            return BAD
    return GOOD


def check_expression(odata):
    f=odata['file']
    hid = f['hid']
    oid = f['id']
    id2=handles[hid]['id']
    if oid==id2:
        return GOOD
    else:
        return BAD

def get_shock(ref):
    sid = shock[ref]
    with open(sid) as f:
        data = f.read()
    return json.loads(data)

def checker(ref):
    if not check_missing(ref):
       return BAD
    ty = objs[ref]['type']
    odata = get_shock(ref)
    if ty.startswith('KBaseGenomes.Genome'):
        return check_genome(ref, odata)
    if ty=='Empty.AHandle-1.0':
        st=UNK
    elif ty=='KBaseReport.Report-2.0':
        st=check_report_type(odata)
    elif ty=='KBaseRNASeq.Bowtie2IndexV2-1.0':
        st=check_bowtie(odata)   
    elif ty.startswith('KBaseFile.SingleEndLibrary'):
        st=check_single(odata)
    elif ty.startswith('KBaseFile.PairedEndLibrar'):
        st=check_paired(odata)
    elif ty.startswith('KBaseAssembly.PairedEndLibrar'):
        st=check_paired2(odata)
    elif ty.startswith('KBaseGenomeAnnotations.Assembly'):
        st=check_assembly(odata, ref)
    elif ty.startswith('KBaseRNASeq.RNASeqAlignment'):
        st=check_alignment(odata)
    elif ty.startswith('KBaseRNASeq.RNASeqExpression'):
        st=check_expression(odata)
    elif ty.startswith('KBaseRNASeq.GFFAnnotation'):
        st=check_gff(odata)
    elif ty.startswith('KBaseClassifier.GenomeCategorizer'):
        print("Skipping cat")
        return GOOD
        st=check_cat(odata)
    else:
        print(ref)
        print(ty)
        raise ValueError('')
    return st
########

def dump_obj(ref):
    print(get_shock(ref))
   
#with open('objs.json') as f:
with open('all.json') as f:
    data=f.read()
objs = json.loads(data)

with open('handles3.json') as f:
    data=f.read()
handles = json.loads(data)

with open('shock.json') as f:
    data=f.read()
shock = json.loads(data)


#for r in ['48213/264/1','48213/265/1']:
#    print(checker(r))
