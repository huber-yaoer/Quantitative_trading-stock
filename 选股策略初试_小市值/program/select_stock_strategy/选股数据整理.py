# -*- coding: utf-8 -*-
"""
本段程序用于生成选股策略所需要的数据
"""
import pandas as pd
from program import config
from program import Functions
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行


# ===读取所有股票代码的列表
stock_code_list = Functions.get_stock_code_list_in_one_dir(config.input_data_path+'/stock_data')
stock_code_list = stock_code_list[:20]

# ===循环读取并且合并
# 导入上证指数
index_data = Functions.import_sh000001_data()[['交易日期']]
# 循环读取股票数据
all_stock_data = pd.DataFrame()
for code in stock_code_list:
    print code

    # 读入数据，额外读入'总市值'这一列
    df = Functions.import_stock_data(code, other_columns=['总市值'])
    # 将股票和上证指数合并，补全停牌的日期
    df = Functions.merge_with_index_data(df, index_data)
    # 将日线数据转化为月线，并且计算'是否交易'、'最后一天涨跌幅'、'交易天数'、'市场交易天数'
    # 并且计算'每天资金曲线'，excel展示计算原理
    df = Functions.transfer_to_period_data(df, period_type='m')

    # 对数据进行整理
    # 删除上市的第一个月
    df.drop([0], axis=0, inplace=True)  # 删除第一行数据
    # 开始时间太早
    df = df[df['交易日期'] > pd.to_datetime('20051201')]
    # 计算下月每天涨幅、下月涨幅
    df['下月每天资金曲线'] = df['每天资金曲线'].shift(-1)
    del df['每天资金曲线']
    df.dropna(subset=['下月每天资金曲线'], inplace=True)
    df['下月涨跌幅'] = df['涨跌幅'].shift(-1)
    # 删除当月最后交易日不交易、涨停的股票，因为这些股票在不能买入
    df = df[df['是否交易'] == 1]
    df = df[df['最后一天涨跌幅'] <= 0.097]
    # 删除交易天数过少的月份
    df = df[df['交易天数'] / df['市场交易天数'] >= 0.8]

    # 合并数据
    all_stock_data = all_stock_data.append(df, ignore_index=True)


# 将数据存入数据库之前，先排序、reset_index
all_stock_data.sort_values(['交易日期', '股票代码'], inplace=True)
all_stock_data.reset_index(inplace=True, drop=True)
print '股票数据行数', len(all_stock_data)

# 将数据存储到hdf文件
all_stock_data.to_hdf(config.output_data_path + '/all_stock_data_sample.h5', 'all_stock_data', mode='w')
# all_stock_data.to_hdf(config.output_data_path + '/all_stock_data.h5', 'all_stock_data', mode='w')

# 目前我们只根据市值选股，所以数据中只有一些基本数据加上市值。
# 实际操作中，会根据很多指标进行选股，
# 需要将这些指标都存入到all_stock_data.h5中。