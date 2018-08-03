# -*- coding: utf-8 -*-
"""
本程序演示如何抓取股票数据
"""
import pandas as pd
from program import config
import numpy as np
from program import Functions
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行

# 神奇的链接http://hq.sinajs.cn/list=sh600000,sh600004

# 本程序的作用是：从新浪网上，将所有股票最新的数据抓取下来并且保存。
# 可以每天定期运行，然后就能得到每天的数据了。

# ===读取所有股票代码列表
s_list = pd.read_hdf(config.input_data_path + '/stock_code_list_store.h5', 'table')
all_code_list = list(s_list)


# ===分组遍历股票
# 逐个股票的去遍历，会太慢。因为每次请求和新浪的交互时间都比较久。
# 也不能所有股票一次全部请求。
# 可以分组去遍历
chunk_len = 50
for code_list in np.array_split(all_code_list, len(all_code_list) / chunk_len + 1):
    Functions.save_stock_data_from_sina_to_h5(code_list)

# ===从h5文件中中读取数据
code = 'sh600004'
df = pd.read_hdf(config.output_data_path + '/each_stock_data_h5.h5', code)
print df
