# coding=utf-8
"""
本程序演示如何自动交易
"""
import numpy as np
from program.auto_trading import upass as up
from program.auto_trading import trader as tr

# ===读取券商账号、密码
# 在user_info文件中填写上自己的账号密码
user_info = np.loadtxt('user_info.txt', dtype=str, delimiter=',')

# ===设置和修改券商帐号
# 目前只支持中信建投
up.set_broker('zxjt', user=user_info[0], passwd=user_info[1])

# ===登录中信建投的账户
# 不能百分百的保证每次都能登陆成功。所以在实际运行的时候要写try except
csc = tr.TraderAPI('zxjt')
csc.login()

# ===查询账户基本信息
# 查询当前账户的市值、现金等信息
baseinfo = csc.baseinfo()

# ===查询持仓
# 查询当前账户持有的股票
csc.position()

# ===买卖股票
# 因为这个接口只能下限价单，如果想迅速成交，可以在该股票当前价格上多加上5分钱，保证成交。
# 也可以根据五档盘口情况加限价单，自己判断
# 在实际情况中，不保证每次买卖都能成功。所以需要写try except
# 买入股票
csc.buy('000979', price=2.68, count=100)  # 以2.68元买入000979股票(中弘股份）100股
# 卖出股票
csc.sell('000979', price=2.68, count=100)  # 以2.68元卖出000979股票(中弘股份）100股

# ===获取委托单列表
# 返回当天委托单的情况。会告诉你该笔委托单是在排队中、已成、已撤等情况。
# 当买入或者卖出一只股票后，要查询下委托单里面，是否确实买入该股票。只有进入委托单，才证明已经正正下单成功。
csc.entrust_list()

# ===撤单
# 撤单程序。需要输入想要撤单程序的单号、下单日期。单号和日期都来自委托单列表
# 可以同时撤多笔，用逗号隔开
# 撤单同样需要try except。并且在撤单之后，还需要去委托单中查看是否撤单成功。
csc.cancel(ordersno='000001,000002', orderdate='20170110,20170110')

# ===查看成交列表
# 查询一段时间的成交列表
# 进入成交列表之后，一个股票才算真正的买入或者卖出成功。
csc.deal_list(begin=20170112, end=20170113)

# ===远程邮件报错程序
# 有的时候交易的时候是无人值守的，如果发生紧急情况，可以通过自动发送邮件的方式进行报错提醒
# 程序在function文件中
# 更标准的做法是：直接发送短信、或者打电话。电话有个列表，第一个人不接打第二个人，依次往下。
# 自动 发送短信、打电话需要接入第三方的服务。

