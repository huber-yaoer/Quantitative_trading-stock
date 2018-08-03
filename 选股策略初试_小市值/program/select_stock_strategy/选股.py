# -*- coding: utf-8 -*-
"""
本段程序演示选股策略框架
"""
import pandas as pd
import numpy as np
from program import config
from program import Functions
import matplotlib.pyplot as plt
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行


select_stock = pd.DataFrame()  # select_stock用户存储选出的股票数据

# 从hdf文件中读取数据
# stock_data = pd.read_hdf(config.output_data_path + '/all_stock_data.h5', 'all_stock_data')
stock_data = pd.read_hdf(config.output_data_path + '/all_stock_data_sample.h5', 'all_stock_data')

# 所有股票下月平均涨幅，作为比较的benchmark。也可以使用指数的涨幅作为benchmark
select_stock['所有股票下月平均涨跌幅'] = stock_data.groupby('交易日期')['下月涨跌幅'].mean()

# 根据市值对股票进行排名
stock_data['排名'] = stock_data.groupby('交易日期')['总市值'].rank()

# 选取前三的股票
stock_data = stock_data[stock_data['排名'] <= 10]
stock_data['股票代码'] += ' '

# 计算每月资金曲线
stock_data_group = stock_data.groupby('交易日期')
select_stock['股票代码'] = stock_data_group['股票代码'].sum()
select_stock['下月平均涨跌幅'] = stock_data_group['下月涨跌幅'].mean()

select_stock['下月每天平均涨跌幅'] = stock_data_group['下月每天资金曲线'].apply(lambda x: list(pd.DataFrame([1.0] + list(np.array(list(x)).mean(axis=0))).pct_change()[0])[1:])
# x = stock_data.iloc[:3]['下月每天资金曲线']
# print x
# print list(x), len(list(x))  # 将x变成list
# print np.array(list(x))  # 矩阵化
# print np.array(list(x)).mean(axis=0)  # 求每天的资金曲线
# print list(np.array(list(x)).mean(axis=0))
# print [1] + list(np.array(list(x)).mean(axis=0))
# print pd.DataFrame([1] + list(np.array(list(x)).mean(axis=0)))
# print pd.DataFrame([1] + list(np.array(list(x)).mean(axis=0))).pct_change()[0]
# print list(pd.DataFrame([1] + list(np.array(list(x)).mean(axis=0))).pct_change()[0])
# print list(pd.DataFrame([1] + list(np.array(list(x)).mean(axis=0))).pct_change()[0])[1:]
select_stock.reset_index(inplace=True)
select_stock['资金曲线'] =  (select_stock['下月平均涨跌幅'] + 1).cumprod()

# 计算每日资金曲线
index_data = Functions.import_sh000001_data()
equity = pd.merge(left=index_data, right=select_stock[['交易日期', '股票代码']], on=['交易日期'],
                  how='left', sort=True)  # 将选股结果和大盘指数合并

equity['股票代码'] = equity['股票代码'].shift()
equity['股票代码'].fillna(method='ffill', inplace=True)
equity.dropna(subset=['股票代码'], inplace=True)

equity['每日涨幅'] = select_stock['下月每天平均涨跌幅'].sum()
# print select_stock[['交易日期', '下月每天平均涨跌幅']]
# print select_stock['下月每天平均涨跌幅'].sum()

equity['equity_curve'] = (equity['每日涨幅'] + 1).cumprod()
equity['benchmark'] = (equity['大盘涨跌幅'] + 1).cumprod()
print equity

# 存储数据
# select_stock.reset_index(inplace=True, drop=True)
# select_stock = select_stock[['交易日期', '股票代码', '下月平均涨跌幅', '所有股票下月平均涨跌幅', '资金曲线']]
# print select_stock
# select_stock.to_hdf(config.output_data_path + '/市值选股结果.h5', 'select_stock', mode='w')
# equity.reset_index(inplace=True, drop=True)
# equity = equity[['交易日期', '股票代码', '每日涨幅', 'equity_curve', '大盘涨跌幅', 'benchmark']]
# print equity
# equity.to_hdf(config.output_data_path + '/市值选股结果.h5', 'equity', mode='a')

# 画图
# equity.set_index('交易日期', inplace=True)
# plt.plot(equity['equity_curve'])
# plt.plot(equity['benchmark'])
# plt.legend(loc='best')
# plt.show()
