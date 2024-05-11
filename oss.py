# -*- coding: utf-8 -*-
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取访问凭证。运行本代码示例之前，请确保已设置环境变量 OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET。
auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())

# 填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
# yourBucketName填写存储空间名称。
bucket = oss2.Bucket(
    auth=auth,
    endpoint='https://oss-cn-hongkong.aliyuncs.com',
    bucket_name='yangfei-ai'
)


def audio_exists(target_dir: str, filename: str):
    """检查音频是否存在"""
    # 填写Object的完整路径，Object完整路径中不能包含Bucket名称。
    return bucket.object_exists(f'{target_dir}/{filename}')


def audio_download(target_dir: str, filename: str):
    """ 下载音频 """
    # 填写Object的完整路径，Object完整路径中不能包含Bucket名称。
    file = bucket.get_object(f'{target_dir}/{filename}')
    # 返回文件内容
    return file.read()


def audio_del(target_dir: str, filename: str):
    """ 删除音频 """
    # 填写Object的完整路径，Object完整路径中不能包含Bucket名称。
    return bucket.delete_object(f'{target_dir}/{filename}')
