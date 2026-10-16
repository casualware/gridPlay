#!/usr/bin/env python3
"""GitHub Actions publisher; all private signing happens before SSH push."""
import json,os,subprocess,tempfile
from pathlib import Path
from release import verify
ROOT=Path(__file__).resolve().parents[2]
def gh(*args):return subprocess.run(['gh',*args],check=True,stdout=subprocess.PIPE).stdout.decode()
def main():
 repo=os.environ['GITHUB_REPOSITORY'];root=ROOT/'candidate';meta=json.loads((root/'release.json').read_text());name='gridplay-'+meta['version']+'.bin'
 signed=verify(root/'manifest.json',root/name,ROOT/'keys/ota-public.pem')
 if signed!=meta or signed['channel']!='preview' or signed['url']!=f'https://github.com/{repo}/releases/download/v{meta["version"]}/{name}':raise ValueError('Candidate metadata/preview repository mismatch')
 tag='v'+meta['version'];channel='ota-preview'
 existing=subprocess.run(['gh','release','view',tag,'--repo',repo,'--json','isDraft'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 if existing.returncode==0:
  if json.loads(existing.stdout)['isDraft']:raise ValueError('Existing version is draft; refusing to change its publication state')
  with tempfile.TemporaryDirectory() as tmp:
   gh('release','download',tag,'--repo',repo,'--pattern',name,'--pattern','manifest.json','--dir',tmp)
   verify(Path(tmp)/'manifest.json',Path(tmp)/name,ROOT/'keys/ota-public.pem')
   if (Path(tmp)/'manifest.json').read_bytes()!=(root/'manifest.json').read_bytes():raise ValueError('Immutable version already has different content')
 else:
  with tempfile.TemporaryDirectory() as tmp:
   notes=Path(tmp)/'notes.md';notes.write_text(meta['notes']+'\n\n**Pilot preview — not production-qualified.**\n\nSHA-256: '+meta['sha256']+'\nSequence: '+str(meta['sequence'])+'\n')
   gh('release','create',tag,'--repo',repo,'--target',os.environ['GITHUB_SHA'],'--prerelease','--title','gridPlay '+meta['version'],'--notes-file',str(notes),str(root/name),str(root/'manifest.json'),str(root/'SHA256SUMS'))
 # Re-download the public version before changing the pointer.
 with tempfile.TemporaryDirectory() as tmp:
  gh('release','download',tag,'--repo',repo,'--pattern',name,'--dir',tmp);verify(root/'manifest.json',Path(tmp)/name,ROOT/'keys/ota-public.pem')
 exists=subprocess.run(['gh','release','view',channel,'--repo',repo],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if exists.returncode:gh('release','create',channel,'--repo',repo,'--target',os.environ['GITHUB_SHA'],'--prerelease','--title','OTA preview channel','--notes','Signed pilot update channel. Stable promotion is not enabled.')
 else:
  with tempfile.TemporaryDirectory() as tmp:
   check=subprocess.run(['gh','release','download',channel,'--repo',repo,'--pattern','manifest.json','--dir',tmp],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   if check.returncode==0:
    import base64
    # Pointer metadata is informational here; device performs signature checks.
    # Refuse regressions even when a previous publishing job is replayed.
    previous=json.loads(base64.b64decode(json.loads((Path(tmp)/'manifest.json').read_text())['payload']))
    if previous['sequence']>meta['sequence']:raise ValueError('Channel already points to a newer sequence')
 gh('release','upload',channel,str(root/'manifest.json'),'--repo',repo,'--clobber')
 print('Published verified pilot release and preview channel:',tag)
if __name__=='__main__':main()
