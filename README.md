oss file get/put playbook 
=================
- 工作需要,原有chef的cookbook切换到ansible, ansible自带了S3 module不需要重写,
根据自己国内的需求,写了一个阿里云OSS module,只有简单的上传/下载功能,但已经满足我自己的需求


- region选择
 - qingdao
 - beijing
 - hangzhou
 - beijing
 - shenzhen
 - shanghai
 - us-west-1
 - us-east-1
 - ap-southeast-1

Example:

```yaml

#从OSS上下载
- oss_file: bucket=my_bucket_name object=/dir/test.txt dest=/tmp/myfile.txt mode=get

#选择其他region的bucket,不指定默认是杭州
- oss_file: bucket=my_bucket_name object=/dir/test.txt dest=/tmp/myfile.txt mode=get region=shanghai

#如果在对应region的内网,用阿里云的internal地址
- oss_file: bucket=my_bucket_name object=/dir/test.txt dest=/tmp/myfile.txt mode=get internal=True

# 将文件上传
- oss_file: bucket=my_bucket_name object=/dir/test.txt src=/tmp/myfile.txt mode=put


```
