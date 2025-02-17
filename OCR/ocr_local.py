# -*- coding: utf-8 -*-
# @Time : 7/29/24 2:51 PM
# @Author : 猫哥
# @File : ocrutils.py
# @Software: PyCharm
import os
import json
import pandas as pd
import numpy as np
import re

from alibabacloud_ocr_api20210707.client import Client as ocr_api20210707Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_darabonba_stream.client import Client as StreamClient  # local
from docx import Document  # pip install python-docx
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AliYunOCR:
    def __init__(self):
        self.OCR_AccessKey_ID="***"
        self.OCR_AccessKey_Secret="***"
        self.STATIC_ROOT=r"C:***"
        self.client = self.create_client(self.OCR_AccessKey_ID, self.OCR_AccessKey_Secret)

    def save_string_to_word(self, text, filename):
        """Save a string to a Word document."""
        doc = Document()
        doc.add_paragraph(text)
        doc.save(filename)

    @staticmethod
    def create_client(access_key_id, access_key_secret):
        """Create a client for the OCR API using AK&SK."""
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint='ocr-api.cn-hangzhou.aliyuncs.com'
        )
        return ocr_api20210707Client(config)


    def parse_general_info(self, res_json):
        """
        通用版\高精版\手写文字\多语言文字
        """
        msg = res_json["body"]["Data"]
        if isinstance(msg, str):
            # 如果 data 是字符串，则先解析为字典
            try:
                msg = json.loads(msg)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return "解析失败"
        content = msg["content"]
        return content

     
    def img_to_text_local(self, imgname, img_type):
        """Convert an image to text using the OCR API."""

        image_path = os.getcwd() + os.path.join(self.STATIC_ROOT, imgname)
        # print(image_path)
        logger.info("Processing image from: {}".format(image_path))
        # 获取文件名
        file_name = Path(imgname).name
        dir_path = os.path.join(self.STATIC_ROOT, "OCR/ocr_files")
        try:
            os.makedirs(dir_path, exist_ok=True)
            print("Directory {} created or already exists.".format(dir_path))
        except Exception as e:
            print("Failed to create directory {}. Error: {}".format(dir_path, e))

        docx_name = "{}.docx".format(file_name.split(".")[0])
        full_path = os.getcwd() + os.path.join(self.STATIC_ROOT, "OCR/ocr_files", docx_name)
        # print(full_path)
        logger.info("Saving results to: {}".format(full_path))
        try:
            client = self.create_client(self.OCR_AccessKey_ID, self.OCR_AccessKey_Secret)
            # 需要安装额外的依赖库，直接点击下载完整工程即可看到所有依赖。
            body_stream = StreamClient.read_from_file_path(image_path)
            recognize_advanced_request = ocr_api_20210707_models.RecognizeAdvancedRequest(
                body=body_stream
            )
            runtime = util_models.RuntimeOptions()
            resp = client.recognize_advanced_with_options(recognize_advanced_request, runtime)
            print(resp.body)
            res_json = json.loads(UtilClient.to_jsonstring(resp))
            msg = ""
            # print(res_json)
            if img_type in ["General", "Advanced", "HandWriting", "MultiLang"]:
                msg = self.parse_general_info(res_json)
                new_file_name = docx_name
            
            logger.info("OCR Result: {}...".format(msg[:50]))
            # print(msg, file_name)
            self.save_string_to_word(msg, full_path)
            return msg, new_file_name
        except Exception as e:
            logger.error("Failed to process image: {}".format(e))

    

# Main execution
if __name__ == '__main__':
    ayo = AliYunOCR()
    imgname = input("请输入要转换的图片名称：")  # 2024-07-29/1722243349985710.jpg
    type_list = ["Advanced", "General", "HandWriting", "Invoice", "TaxiInvoice"]
    choice = int(input("请输入被转换的图片类型（1-5）："))
    if 1 <= choice <= len(type_list):
        img_type = type_list[choice-1]
        ayo.img_to_text(imgname, img_type)
    else:
        logger.error("Invalid type choice.")

    ayo.img_to_text_local("test.png", "Advanced")

    