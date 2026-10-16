import base64,importlib.util,json,os,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('release',Path(__file__).with_name('release.py'));r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class Releases(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  r.version=lambda:('0.9.0-preview',9000)
  cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name);cls.key=cls.root/'key.pem';r.init_key(cls.key)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def release(self,name):
  d=self.root/name;image=self.root/(name+'.bin');data=bytearray(110000);data[0]=0xe9;data[12]=9;image.write_bytes(data)
  return r.package(image,self.key,'test/gridplay','preview',d,'Regression fixture')
 def test_signed_image_and_tamper_rejection(self):
  out=self.release('valid');image=next(out.glob('*.bin'));manifest=out/'manifest.json';pub=out/'public-key.pem';self.assertEqual(r.verify(manifest,image,pub)['board'],r.BOARD)
  original=image.read_bytes();image.write_bytes(original[:-1]+b'x')
  with self.assertRaises(ValueError):r.verify(manifest,image,pub)
  image.write_bytes(original);envelope=json.loads(manifest.read_text());payload=json.loads(base64.b64decode(envelope['payload']));payload['sequence']+=1;envelope['payload']=base64.b64encode(json.dumps(payload).encode()).decode();manifest.write_text(json.dumps(envelope))
  with self.assertRaises(Exception):r.verify(manifest,image,pub)
 def test_key_permissions_and_no_overwrite(self):
  self.assertEqual(os.stat(self.key).st_mode&0o777,0o600)
  with self.assertRaises(FileExistsError):r.init_key(self.key)
 def test_immutable_release_directory(self):
  self.release('immutable')
  with self.assertRaises(ValueError):self.release('immutable')
 def test_reject_wrong_image_and_repository(self):
  image=self.root/'bad.bin';image.write_bytes(b'X'*110000)
  with self.assertRaises(ValueError):r.package(image,self.key,'test/gridplay','preview',self.root/'bad','test')
  with self.assertRaises(ValueError):r.repo_name('owner/repo/../../evil')
if __name__=='__main__':unittest.main()
