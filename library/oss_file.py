#!/usr/bin/python
# ansible playbook for oss
#

DOCUMENTATION = '''
---
module: oss_file
short_description: get or put objects from oss bucket.
description:
    - This module allows the user to download or upload  objects from oss buckets.
version_added: "0.1"
options:
  oss_access_key:
    description:
      - Aliyun oss access key id.
    required: false
    default: null
    aliases: []
  oss_secret_key:
    description:
      - ALiyun oss secret key.
    required: false
    default: null
    aliases: []
  oss_bucket:
    description:
      - Aliyun oss Bucket name.
    required: true
    default: null
    aliases: []
  dest:
    description:
      - Save remote file path on local path.
    required: false
    aliases: []
  mode:
    description:
      - put (upload), get (download).
    required: true
    choices: ['get', 'put']
  internal:
    description:
      - Use Aliyun oss internal endpoint
    required: false
    default: no  
  object:
    description:
      - remote object path.
    required: false
    default: null
  region:
    description:
     - Aliyun region name.
    required: false
    default: null
  src:
    description:
      - The local file path.
    required: false
    default: null
    aliases: []
requirements: [ hashlib, hmac, urllib2 ]
author:
    - "feng gao"
'''


EXAMPLES = '''
# GET Object from OSS 
- oss_file: bucket=my_bucket_name object=/dir/test.txt dest=/tmp/myfile.txt mode=get

# PUT Object from OSS 
- oss_file: bucket=my_bucket_name object=/dir/test.txt src=/tmp/myfile.txt mode=put

'''



import base64
import hashlib
import hmac
from time import strftime,gmtime
import urllib2
import os
import sys

def convert_utf8(input_string):
  if isinstance(input_string, unicode):
      input_string = input_string.encode('utf-8')
  return input_string

def generate_oss_auth(oss_access_key,oss_secret_key,oss_object_path,bucket,method_type="GET",object_md5="",object_type=""):
  method = method_type
  content_md5 = object_md5
  content_type = object_type
  gmt_date = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
  canonicalized_oss_headers  = ""
  canonicalized_resource = '/'+ bucket + oss_object_path
  secret_access_id  = convert_utf8(oss_access_key)
  secret_access_key = convert_utf8(oss_secret_key)
  string_to_sign = method + "\n" + content_md5.strip() + "\n" + content_type + "\n" + gmt_date + "\n" + canonicalized_oss_headers + canonicalized_resource

  h = hmac.new(secret_access_key, string_to_sign, hashlib.sha1)
  sign_result = base64.encodestring(h.digest()).strip()
  auth = "%s %s:%s" % ('OSS',secret_access_id,sign_result)
  return auth

def download_oss_object(module,auth,oss_object_path,local_object_path,host):
  url = 'http://' + host + oss_object_path
  gmt_date = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
  request = urllib2.Request(url)
  request.add_header('Host', host)
  request.add_header('Date', gmt_date)
  request.add_header('Authorization', auth)
  try:
    response = urllib2.urlopen(request)
    with open(local_object_path, "wb") as local_file:
      local_file.write(response.read())
    local_file.close()
  except urllib2.HTTPError as e:
    module.fail_json(msg= str(e))
  module.exit_json(changed=True, msg="GET operation complete")

def upload_oss_object(module,auth,oss_object_path,local_object_path,host,object_md5):
  url = 'http://' + host + oss_object_path 
  gmt_date = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
  object_file = open(local_object_path, 'rb')
  object_data = object_file.read()
  length = os.path.getsize(local_object_path)
  request = urllib2.Request(url.encode('utf-8'),data=object_data)
  request.get_method = lambda: str('PUT')
  request.add_header('Host', host)
  request.add_header('Cache-control','no-cache')
  request.add_header('Content-MD5',object_md5)
  request.add_header('Content-Length',  length)
  request.add_header('Content-Type', 'application/octet-stream')
  request.add_header('Date', gmt_date)
  request.add_header('Authorization', auth)
  try:
    response = urllib2.urlopen(request).read()
  except urllib2.HTTPError as e:
    module.fail_json(msg= str(e))
  module.exit_json(changed=True, msg="PUT operation complete")

def get_oss_object_md5(auth,oss_object_path,host):
  url = 'http://' + host + oss_object_path
  gmt_date = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
  request = urllib2.Request(url)
  request.get_method = lambda: str('HEAD')
  request.add_header('Host', host)
  request.add_header('Authorization', auth)
  request.add_header('Date', gmt_date)
  try:
    response = urllib2.urlopen(request)
  except urllib2.HTTPError as e:
    print e.read()
    exit(12)
  file_md5 = response.info().getheaders("ETag")[0].lower()
  file_md5 = file_md5.strip('"')
  return file_md5

def 
  if  os.path.exists(local_object_path):
    if base64_type:
       base64md5 = base64.encodestring(hashlib.md5(open(local_object_path, 'rb').read()).digest())
       if base64md5[-1] == '\n':
         base64md5 = base64md5[0:-1]
       return base64md5
    else:
      return hashlib.md5(open(local_object_path, 'rb').read()).hexdigest()
  else:
    return 'nothing' 

def get_oss_action(module, oss_access_key, oss_secret_key, local_object, oss_object, bucket, host):
  local_md5 = get_local_object_md5(local_object)
  auth = generate_oss_auth(oss_access_key,oss_secret_key,oss_object,bucket,method_type="HEAD")
  oss_md5 = get_oss_object_md5(auth,oss_object,host)
  if local_md5 == oss_md5:
    module.exit_json(changed=False, msg="File no changed") 
  else:
    auth = generate_oss_auth(oss_access_key,oss_secret_key,oss_object,bucket)
    download_oss_object(module,auth,oss_object,local_object,host)

def put_oss_action(module, oss_access_key, oss_secret_key, local_object, oss_object, bucket, host):
  local_md5 = get_local_object_md5(local_object)
  local_base64_md5 = get_local_object_md5(local_object,base64_type=True)
  auth = generate_oss_auth(oss_access_key,oss_secret_key,oss_object,bucket,method_type="HEAD")
  oss_md5 = get_oss_object_md5(auth,oss_object,host)
  if local_md5 == oss_md5:
    module.exit_json(changed=False, msg="Remote File no changed")
  else:
    auth = generate_oss_auth(oss_access_key,oss_secret_key,oss_object,bucket,method_type="PUT",object_md5=local_base64_md5,object_type="application/octet-stream")
    upload_oss_object(module,auth,oss_object,local_object,host,object_md5=local_base64_md5)

def build_endpoint(region,internal):
  endpointlist = {
      "qingdao" : "oss-cn-qingdao.aliyuncs.com",
      "beijing" : "oss-cn-beijing.aliyuncs.com",
      "hangzhou" : "oss-cn-hangzhou.aliyuncs.com",
      "hongkong" : "oss-cn-hongkong.aliyuncs.com",
      "shenzhen" : "oss-cn-shenzhen.aliyuncs.com",
      "shanghai" : "oss-cn-shanghai.aliyuncs.com",
      "ap-southeast-1" : "oss-ap-southeast-1.aliyuncs.com",
      "us-west-1" : "oss-us-west-1.aliyuncs.com",
      "us-east-1" : "oss-us-east-1.aliyuncs.com"
  }
  if internal:
    return endpointlist[region].replace('.aliyuncs','-internal.aliyuncs')
  else:
    return endpointlist[region]


def main():
  module = AnsibleModule(
    argument_spec = dict(
      oss_bucket     = dict(required=True),
      dest           = dict(default=None),
      internal       = dict(default=False, type='bool'),
      mode           = dict(choices=['get', 'put'], required=True),
      object         = dict(),
      region         = dict(),
      src            = dict(),
      ),
    supports_check_mode = False
  )
  oss_bucket = module.params.get('oss_bucket')
  region = module.params.get('region')
  obj = module.params.get('object')
  src = module.params.get('src')
  mode = module.params.get('mode')
  internal = module.params.get('internal')

  if module.params.get('dest'):
    dest = os.path.expanduser(module.params.get('dest'))

  if region in ('', None):
      oss_location = build_endpoint('hangzhou',internal)
  else:
      oss_location = build_endpoint(region,internal)


  if 'OSS_ACCESS_KEY' in os.environ:
    oss_access_key = os.environ['OSS_ACCESS_KEY']
  if 'OSS_SECRET_KEY' in os.environ:
    oss_secret_key = os.environ['OSS_SECRET_KEY']

  host = oss_bucket + '.' + oss_location

  if mode == 'get':
     get_oss_action(module,oss_access_key,oss_secret_key,dest,obj,oss_bucket,host)

  if mode == 'put':
     put_oss_action(module,oss_access_key,oss_secret_key,src,obj,oss_bucket,host)


from ansible.module_utils.basic import *

main()
