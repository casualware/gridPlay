#!/usr/bin/env python3
"""Stage a verified candidate over SSH; Actions handles Release API authentication."""
import argparse,json,os,shutil,subprocess,tempfile
from pathlib import Path
from release import repo_name,verify

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True);p.add_argument('--release-dir',required=True);p.add_argument('--push',action='store_true',help='Commit and push the candidate to trigger preview publication');a=p.parse_args();repo=repo_name(a.repo);root=Path(a.release_dir).resolve();m=json.loads((root/'release.json').read_text());name='gridplay-'+m['version']+'.bin'
 if m['channel']!='preview':raise ValueError('SSH publisher is restricted to the pilot preview channel')
 env=dict(os.environ,GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes')
 with tempfile.TemporaryDirectory(prefix='gridplay-release-') as tmp:
  work=Path(tmp)/'repo';subprocess.run(['git','clone','--depth','1',f'git@github.com:{repo}.git',str(work)],env=env,check=True)
  signed=verify(root/'manifest.json',root/name,work/'keys/ota-public.pem')
  if signed!=m or m['url']!=f'https://github.com/{repo}/releases/download/v{m["version"]}/{name}':raise ValueError('Candidate does not match the repository trust anchor/metadata')
  candidate=work/'candidate';candidate.mkdir(exist_ok=True)
  for old in candidate.glob('gridplay-*.bin'):old.unlink()
  for item in [name,'manifest.json','release.json','SHA256SUMS']:shutil.copyfile(root/item,candidate/item)
  subprocess.run(['git','-C',str(work),'add','candidate'],check=True)
  subprocess.run(['git','-C',str(work),'diff','--cached','--stat'],check=True)
  if not a.push:print('Dry run complete. Add --push to publish this signed preview through Actions.');return
  subprocess.run(['git','-C',str(work),'commit','-m','Publish signed gridPlay '+m['version']+' preview candidate'],check=True)
  subprocess.run(['git','-C',str(work),'push','origin','HEAD:main'],env=env,check=True)
  print('SSH push complete. Check GitHub Actions before installing the release.')
if __name__=='__main__':main()
