# -*- coding: utf-8 -*-
"""
本段程序用于演示策略评价指标
"""
import pandas as pd  # 导入pandas，我们一般为pandas去一个别名叫做pd
import program.config
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行


# ===导入数据
select_stock = pd.read_hdf(program.config.output_data_path + '/市值选股结果.h5', 'select_stock')
equity = pd.read_hdf(program.config.output_data_path + '/市值选股结果.h5', 'equity')

# ===对资金曲线从收益角度进行评价
# 总收益
total_return = (equity.iloc[-1]['equity_curve'] / 1) - 1

# 年华收益
# pow(x, y),计算x的y次方
# 年华收益：pow((1 + x), 年数) = 总收益
# 日化收益：pow((1 + x), 天数) = 总收益
# pow((1 + 日化收益), 365) = 年华收益
# 整理得到：年华收益 = pow(总收益, 365/天数) - 1
trading_days = (equity['交易日期'].iloc[-1] -  equity['交易日期'].iloc[0]).days + 1
annual_return = pow(total_return, 365.0/trading_days) - 1
print '年华收益（%）：', round(annual_return * 100, 2)

# ===对资金曲线从风险角度进行评价
# 使用每日收益的方差衡量风险
print equity['每日涨幅'].std()

# 使用最大回撤衡量风险
# 最大回撤：从某一个高点，到之后的某个低点，之间最大的下跌幅度。实际意义：在最最坏的情况下，会亏多少钱。
# 计算当日之前的资金曲线的最高点
equity['max2here'] = equity['equity_curve'].expanding().max()
# 计算到历史最高值到当日的跌幅，drowdwon
equity['dd2here'] = equity['equity_curve'] / equity['max2here'] - 1
# 计算最大回撤，以及最大回撤结束时间
end_date, max_draw_down = tuple(equity.sort_values(by=['dd2here']).iloc[0][['交易日期', 'dd2here']])
print '最大回撤（%）：', round(max_draw_down * 100, 2)
# 计算最大回撤开始时间
start_date = equity[equity['交易日期'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0]['交易日期']
print '最大回撤开始时间', start_date.date()
print '最大回撤结束时间', end_date.date()


# ===终极指标
# 如果只用一个指标来衡量策略，我最常用的就是：年化收益 / abs(最大回撤)
# 越高越好，一般这个指标大于1，说明这个策略值得进一步探索。


# ===对每次操作的评价
# 平均涨幅
print '平均涨幅（%）', round(select_stock['下月平均涨跌幅'].mean() * 100, 2)

# 胜率
print '涨幅>0比例（%）', select_stock[select_stock['下月平均涨跌幅'] > 0].shape[0] / float(select_stock.shape[0]) * 100

# 胜率
print '跑赢同期均值比例（%）', select_stock[select_stock['下月平均涨跌幅'] > select_stock['所有股票下月平均涨跌幅']].shape[0] / float(select_stock.shape[0]) * 100

# 最大单月涨幅，最大单月跌幅
print '最大单月涨幅（%）：', round(select_stock['下月平均涨跌幅'].max() * 100, 2)
print '最大单月跌幅（%）：', round(select_stock['下月平均涨跌幅'].min() * 100, 2)  # 单月最大下跌30%，是否还有信心坚持策略？


# 其他指标如夏普比率，信息比率，详见：http://bbs.pinggu.org/thread-4454429-1-1.html
