# -*- coding: utf-8 -*-
# @Time : 2023/12/7 21:25
# @Author : icebear
# @Email : millerkai@163.com
# @File : AliYunOCR.py
# @Software: PyCharm

from alibabacloud_ocr_api20210707.client import Client as ocr_api20210707Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from settings import AccessKeyID, AccessKeySecret
import json


class AliYunOCR:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
    ) -> ocr_api20210707Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # Endpoint 请参考 https://api.aliyun.com/product/ocr-api
        config.endpoint = f'ocr-api.cn-hangzhou.aliyuncs.com'
        return ocr_api20210707Client(config)

    @staticmethod
    def main(img_url, img_type) -> None:
        # 请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET。
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议使用更安全的 STS 方式，
        # 更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html
        client = AliYunOCR.create_client(AccessKeyID, AccessKeySecret)
        recognize_all_text_request = ocr_api_20210707_models.RecognizeAllTextRequest(url=img_url, type=img_type)
        runtime = util_models.RuntimeOptions()
        resp = client.recognize_all_text_with_options(recognize_all_text_request, runtime)
        res_json =json.loads(UtilClient.to_jsonstring(resp))
        if img_type == "Invoice" or img_type == "TaxiInvoice":
            # 这里只提取了部分数据进行演示
            res_dict = res_json["body"]["Data"]["SubImages"][0]["KvInfo"]["Data"]
            for key, value in res_dict.items():
                print(f"{key}: {value}")
            # 将数据写入数据库或文件中（略）
        else:
            print(res_json["body"]["Data"]["Content"])
            # 将数据写入数据库或文件中（略）
        # ConsoleClient.log(UtilClient.to_jsonstring(resp))


if __name__ == '__main__':
    type_list = []
    img_url = input("请输入要转换的图片链接：")
    print("图片类型：1.通用高精版; 2.通用基础版; 3.手写文字; 4.增值税发票; 5.出租车发票;")
    choice = int(input("请输入被转换的图片类型（1-5）："))
    type_list = ["Advanced", "General", "HandWriting", "Invoice", "TaxiInvoice"]
    img_type = type_list[choice-1]

    AliYunOCR.main(img_url, img_type)
