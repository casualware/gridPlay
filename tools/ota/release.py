#!/usr/bin/env python3
"""Offline signed OTA releases. No key upload, repository creation or publishing."""
import argparse,base64,hashlib,json,os,re,subprocess,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BOARD='waveshare-esp32s3-touch-amoled-2.16'; LAYOUT='dual-6m-v1'; MAX_IMAGE=6*1024*1024

def run(*args,**kw):return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw).stdout

def public_key(private):
 pem=run('openssl','pkey','-in',str(private),'-pubout').decode()
 details=run('openssl','pkey','-pubin','-text','-noout',input=pem.encode()).decode()
 if 'Public-Key: (3072 bit)' not in details or 'Exponent:' not in details:raise ValueError('Use an RSA-3072 signing key')
 return pem

def repo_name(value):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',value):raise ValueError('Use owner/repository')
 return value

def version():
 s=(ROOT/'firmware/GridPlay/FirmwareVersion.h').read_text()
 return re.search(r'VERSION\[\]="([^"]+)"',s)[1],int(re.search(r'FIRMWARE_SEQUENCE=(\d+)',s)[1])

def init_key(path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 try:
  with os.fdopen(fd,'wb') as f:f.write(run('openssl','genpkey','-algorithm','RSA','-pkeyopt','rsa_keygen_bits:3072'))
 except BaseException:
  path.unlink(missing_ok=True);raise
 return public_key(path)

def configure(repo,key,channel):
 repo=repo_name(repo);pem=public_key(key)
 text='#pragma once\n// Public verification key only. Keep the private key offline.\n'
 text+=f'static constexpr char OTA_MANIFEST_URL[]="https://github.com/{repo}/releases/download/ota-{channel}/manifest.json";\n'
 text+=f'static constexpr char OTA_CHANNEL[]="{channel}";\nstatic constexpr char OTA_PUBLIC_KEY[]=R"KEY({pem})KEY";\n'
 (ROOT/'firmware/GridPlay/OtaConfig.h').write_text(text)

def package(image,key,repo,channel,out,notes):
 repo=repo_name(repo);v,seq=version();data=Path(image).read_bytes()
 if len(notes.encode())>320:raise ValueError('Release notes must fit 320 UTF-8 bytes')
 if channel=='stable' and '-' in v:raise ValueError('Prerelease firmware cannot be promoted to stable')
 if not 100000<len(data)<=MAX_IMAGE or data[0]!=0xe9 or int.from_bytes(data[12:14],'little')!=9:raise ValueError('Expected ESP32-S3 application image, not merged flash image')
 out=Path(out)
 if out.exists():raise ValueError('Release directory already exists; releases are immutable')
 name=f'gridplay-{v}.bin';now=int(time.time())
 payload={'schema':1,'board':BOARD,'layout':LAYOUT,'channel':channel,'version':v,'sequence':seq,'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'url':f'https://github.com/{repo}/releases/download/v{v}/{name}','issued_at':now,'expires_at':now+90*86400,'notes':notes}
 raw=json.dumps(payload,separators=(',',':'),sort_keys=True).encode()
 if len(raw)>4096:raise ValueError('Manifest payload too large')
 # Sign exact bytes; device never reconstructs JSON for signature verification.
 sig=run('openssl','dgst','-sha256','-sign',str(key),input=raw)
 envelope={'payload':base64.b64encode(raw).decode(),'signature':sig.hex()}
 out.mkdir(parents=True);(out/name).write_bytes(data);(out/'manifest.json').write_text(json.dumps(envelope,separators=(',',':'))+'\n');(out/'release.json').write_text(json.dumps(payload,indent=2)+'\n');(out/'public-key.pem').write_text(public_key(key));(out/'SHA256SUMS').write_text(payload['sha256']+'  '+name+'\n')
 verify(out/'manifest.json',out/name,out/'public-key.pem')
 return out

def verify(manifest,image,pub):
 envelope=json.loads(Path(manifest).read_text());raw=base64.b64decode(envelope['payload'],validate=True);sig=bytes.fromhex(envelope['signature'])
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);(p/'signature').write_bytes(sig);run('openssl','dgst','-sha256','-verify',str(pub),'-signature',str(p/'signature'),input=raw)
 m=json.loads(raw);data=Path(image).read_bytes()
 if m['schema']!=1 or m['board']!=BOARD or m['layout']!=LAYOUT:raise ValueError('Wrong target')
 if m['size']!=len(data) or m['sha256']!=hashlib.sha256(data).hexdigest():raise ValueError('Image digest/size mismatch')
 if m['expires_at']<=time.time():raise ValueError('Expired manifest')
 return m

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 k=sub.add_parser('init-key');k.add_argument('--private',required=True)
 c=sub.add_parser('configure');c.add_argument('--repo',required=True);c.add_argument('--private',required=True);c.add_argument('--channel',choices=['preview','stable'],default='preview')
 b=sub.add_parser('build');b.add_argument('--repo',required=True);b.add_argument('--private',required=True);b.add_argument('--channel',choices=['preview','stable'],default='preview');b.add_argument('--out',required=True);b.add_argument('--notes',required=True)
 v=sub.add_parser('verify');v.add_argument('--manifest',required=True);v.add_argument('--image',required=True);v.add_argument('--public',required=True)
 a=p.parse_args()
 if a.command=='init-key':init_key(a.private);print('Signing key created with owner-only permissions. Back it up securely; it is never uploaded.')
 elif a.command=='configure':configure(a.repo,a.private,a.channel);print('Public key and release channel configured. Bootstrap installation requires USB.')
 elif a.command=='verify':verify(a.manifest,a.image,a.public);print('Signature, board, image size and SHA-256 verified.')
 elif a.command=='build':
  configure(a.repo,a.private,a.channel)
  subprocess.run(['sh','firmware/build.sh'],cwd=ROOT,check=True)
  package(ROOT/'firmware/dist/GridPlay.ino.bin',a.private,a.repo,a.channel,a.out,a.notes);print('Release built and verified:',a.out)
if __name__=='__main__':main()
