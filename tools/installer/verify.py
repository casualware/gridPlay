#!/usr/bin/env python3
"""Verify the signed factory image and browser flash map before deploying Pages."""
import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ota'))
from release import verify
root=Path(sys.argv[1]);pub=Path(sys.argv[2]);m=json.loads((root/'manifest.json').read_text())
assert len(m['builds'])==1 and m['builds'][0]['chipFamily']=='ESP32-S3'
parts=m['builds'][0]['parts'];assert len(parts)==1 and parts[0]['offset']==0
name=parts[0]['path'];assert Path(name).name==name and name=='gridplay-'+m['version']+'-factory.bin'
f=root/name;meta=verify(root/'bootstrap.json',f,pub);blob=f.read_bytes()
assert meta['purpose']=='factory-install' and meta['version']==m['version'] and meta['channel']=='preview'
assert len(blob)==16*1024*1024 and blob[0]==0xe9 and int.from_bytes(blob[12:14],'little')==9
assert blob[0x9000:0xe000]==b'\xff'*0x5000
assert hashlib.sha256(blob[0x10000:0x10000+meta['app_size']]).hexdigest()==meta['app_sha256']
assert m['new_install_prompt_erase'] is False and m['new_install_improv_wait_time']==0
assert (root/'SHA256SUMS').read_text()==meta['sha256']+'  '+name+'\n'
print('Verified signed factory bundle and ESP32-S3 flash map:',m['version'])
