# -*- coding: utf-8 -*-
"""
汇总需要用到的一些常见函数
"""
import config  # 导入config
import pandas as pd  # 导入pandas，我们一般为pandas取一个别名叫做pd
import os
import urllib2
import time
import datetime


# 导入数据
def import_stock_data(stock_code, other_columns=[]):
    """
    导入在data/input_data/stock_data下的股票数据。
    :param stock_code: 股票数据的代码，例如'sh600000'
    :param other_columns: 若为默认值，只导入以下基础字段：'交易日期', '股票代码', '开盘价', '最高价', '最低价', '收盘价', '涨跌幅', '成交额'。
    若不为默认值，会导入除基础字段之外其他指定的字段
    :return:
    """

    df = pd.read_csv(config.input_data_path + '/stock_data/' + stock_code + '.csv', encoding='gbk')
    df.columns = [i.encode('utf8') for i in df.columns]
    df = df[['交易日期', '股票代码', '开盘价', '最高价', '最低价', '收盘价', '涨跌幅', '成交额'] + other_columns]
    df.sort_values(by=['交易日期'], inplace=True)
    df['交易日期'] = pd.to_datetime(df['交易日期'])
    df['股票代码'] = stock_code
    df.reset_index(inplace=True, drop=True)

    return df


# 导入指数
def import_sh000001_data():
    # 导入指数数据
    df_index = pd.read_csv(config.input_data_path + '/index_data/' + 'sh000001.csv', parse_dates=['date'])
    df_index = df_index[['date', 'change']]
    df_index.rename(columns={'date': '交易日期', 'change': '大盘涨跌幅'}, inplace=True)
    df_index.sort_values(by=['交易日期'], inplace=True)
    df_index.dropna(subset=['大盘涨跌幅'], inplace=True)
    df_index.reset_index(inplace=True, drop=True)

    return df_index


# 计算复权价
def cal_fuquan_price(input_stock_data, fuquan_type='后复权'):
    """
    计算复权价
    :param input_stock_data:
    :param fuquan_type:复权类型，可以是'后复权'或者'前复权'
    :return:
    """
    # 创建空的df
    df = pd.DataFrame()

    # 计算复权收盘价
    num = {'后复权': 0, '前复权': -1}
    price1 = input_stock_data['收盘价'].iloc[num[fuquan_type]]
    df['复权因子'] = (1.0 + input_stock_data['涨跌幅']).cumprod()
    price2 = df['复权因子'].iloc[num[fuquan_type]]
    df['收盘价_' + fuquan_type] = df['复权因子'] * (price1 / price2)

    # 计算复权的开盘价、最高价、最低价
    df['开盘价_' + fuquan_type] = input_stock_data['开盘价'] / input_stock_data['收盘价'] * df['收盘价_' + fuquan_type]
    df['最高价_' + fuquan_type] = input_stock_data['最高价'] / input_stock_data['收盘价'] * df['收盘价_' + fuquan_type]
    df['最低价_' + fuquan_type] = input_stock_data['最低价'] / input_stock_data['收盘价'] * df['收盘价_' + fuquan_type]

    return df[[i + '_' + fuquan_type for i in '开盘价', '最高价', '最低价', '收盘价']]


# 导入某文件夹下所有股票的代码
def get_stock_code_list_in_one_dir(path):
    """
    从指定文件夹下，导入所有csv文件的文件名
    :param path:
    :return:
    """

    stock_list = []

    # 系统自带函数os.walk，用于遍历文件夹中的所有文件
    for root, dirs, files in os.walk(path):
        if files:  # 当files不为空的时候
            for f in files:
                if f.endswith('.csv'):
                    stock_list.append(f[:8])

    return stock_list


# 将股票数据和指数数据合并
def merge_with_index_data(df, index_data):
    """
    将股票数据和指数数据合并
    :param df: 股票数据
    :param index_data: 指数数据
    :return:
    """

    # 将股票数据和上证指数合并
    df = pd.merge(left=df, right=index_data, on='交易日期', how='right', sort=True, indicator=True)

    # 将停盘时间的['涨跌幅', '成交额']数据填补为0
    fill_0_list = ['涨跌幅', '成交额']
    df.loc[:, fill_0_list] = df[fill_0_list].fillna(value=0)

    # 用前一天的收盘价，补全收盘价的空值
    df['收盘价'] = df['收盘价'].fillna(method='ffill')

    # 用收盘价补全开盘价、最高价、最低价的空值
    df['开盘价'] = df['开盘价'].fillna(value=df['收盘价'])
    df['最高价'] = df['最高价'].fillna(value=df['收盘价'])
    df['最低价'] = df['最低价'].fillna(value=df['收盘价'])

    # 用前一天的数据，补全其余空值
    df.fillna(method='ffill', inplace=True)

    # 去除上市之前的数据
    df = df[df['股票代码'].notnull()]
    df.reset_index(drop=True, inplace=True)

    # 计算当天是否交易
    df['是否交易'] = 1
    df.loc[df[df['_merge'] == 'right_only'].index, '是否交易'] = 0
    del df['_merge']

    return df


def transfer_to_period_data(df, period_type='m'):
    """

    :param df:
    :param period_type:
    :return:
    """

    # 将交易日期设置为index
    df['周期最后交易日'] = df['交易日期']
    df.set_index('交易日期', inplace=True)

    # 转换为周期数据
    period_df = df.resample(rule=period_type).last()  # 大部分columns，在转换时使用last

    period_df['开盘价'] = df['开盘价'].resample(period_type).first()
    period_df['最高价'] = df['最高价'].resample(period_type).max()
    period_df['最低价'] = df['最低价'].resample(period_type).min()
    period_df['成交额'] = df['成交额'].resample(period_type).sum()
    period_df['涨跌幅'] = df['涨跌幅'].resample(period_type).apply(lambda x: (x + 1.0).prod() - 1.0)

    period_df['每天资金曲线'] = df['涨跌幅'].resample(period_type).apply(lambda x: list((x+1).cumprod()))
    # print period_df
    # print period_df.iloc[1]['每天资金曲线']
    period_df['最后一天涨跌幅'] = df['涨跌幅'].resample(period_type).last()
    period_df['交易天数'] = df['是否交易'].resample(period_type).sum()
    period_df['市场交易天数'] = df['股票代码'].resample(period_type).size()

    # 去除一天都没有交易的周
    period_df.dropna(subset=['股票代码'], inplace=True)

    # 重新设定index
    period_df.reset_index(inplace=True)
    period_df['交易日期'] = period_df['周期最后交易日']
    del period_df['周期最后交易日']

    return period_df

