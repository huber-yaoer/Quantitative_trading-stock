# -*- coding:utf-8 -*-

import json
import time
import six


def nowtime_str():
    return time.time() * 1000


def get_jdata(txtdata):
    txtdata = txtdata.content
    if six.PY3:
        txtdata = txtdata.decode('utf-8')
    jsonobj = json.loads(txtdata)
    return jsonobj


def get_vcode(broker, res):
    from PIL import Image
    import pytesseract as pt
    import io
    if broker == 'csc':
        imgdata = res.content
        img = Image.open(io.BytesIO(imgdata))
        vcode = pt.image_to_string(img)
        return vcode
