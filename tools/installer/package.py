#!/usr/bin/env python3
"""Package a build-produced factory image; never read device flash or credentials."""
import argparse,base64,hashlib,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ota'))
from release import verify,run,BOARD,LAYOUT
p=argparse.ArgumentParser();p.add_argument('--release-dir',required=True);p.add_argument('--dist',required=True);p.add_argument('--private',required=True);p.add_argument('--out',required=True);a=p.parse_args()
r=Path(a.release_dir);d=Path(a.dist);o=Path(a.out)
if o.exists():raise ValueError('Bootstrap bundles are immutable; use a new output directory')
m=json.loads((r/'release.json').read_text());app=r/('gridplay-'+m['version']+'.bin');verify(r/'manifest.json',app,r/'public-key.pem')
blob=(d/'GridPlay.ino.merged.bin').read_bytes();image=app.read_bytes()
assert len(blob)==16*1024*1024 and blob[0]==0xe9 and int.from_bytes(blob[12:14],'little')==9,'Expected 16 MB ESP32-S3 factory image'
assert blob[0x10000:0x10000+len(image)]==image,'Factory app differs from signed release'
assert blob[:len((d/'GridPlay.ino.bootloader.bin').read_bytes())]==(d/'GridPlay.ino.bootloader.bin').read_bytes()
assert blob[0x8000:0x8c00]==(d/'GridPlay.ino.partitions.bin').read_bytes()
# NVS must be blank in a factory build; never distribute a device backup.
assert blob[0x9000:0xe000]==b'\xff'*0x5000,'Factory image contains nonblank NVS'
name='gridplay-'+m['version']+'-factory.bin'
payload={'schema':1,'purpose':'factory-install','board':BOARD,'layout':LAYOUT,'version':m['version'],'channel':m['channel'],'sequence':m['sequence'],'size':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'app_sha256':m['sha256'],'app_size':len(image),'issued_at':int(time.time()),'expires_at':m['expires_at']}
raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode();sig=run('openssl','dgst','-sha256','-sign',a.private,input=raw)
o.mkdir(parents=True);(o/name).write_bytes(blob)
(o/'bootstrap.json').write_text(json.dumps({'payload':base64.b64encode(raw).decode(),'signature':sig.hex()})+'\n')
(o/'manifest.json').write_text(json.dumps({'name':'gridPlay Preview','version':m['version'],'new_install_prompt_erase':False,'new_install_improv_wait_time':0,'builds':[{'chipFamily':'ESP32-S3','parts':[{'path':name,'offset':0}]}]},indent=2)+'\n')
(o/'SHA256SUMS').write_text(payload['sha256']+'  '+name+'\n');verify(o/'bootstrap.json',o/name,r/'public-key.pem')
print('Signed factory installer bundle:',o)
