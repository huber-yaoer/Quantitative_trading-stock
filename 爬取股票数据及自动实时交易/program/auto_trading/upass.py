# -*- coding:utf-8 -*-

import pandas as pd
import os

BK = 'bk'


def set_broker(broker='', user='', passwd=''):
    df = pd.DataFrame([[broker, user, passwd]], 
                      columns=['broker', 'user', 'passwd'],
                      dtype=object)
    if os.path.exists(BK):
        all = pd.read_csv(BK, dtype=object)
        if (all[all.broker == broker]['user']).any():
            all = all[all.broker != broker]
        all = all.append(df, ignore_index=True)
        all.to_csv(BK, index=False)
    else:
        df.to_csv(BK, index=False)
        
        
def get_broker(broker=''):
    if os.path.exists(BK):
        df = pd.read_csv(BK, dtype=object)
        if broker == '':
            return df
        else:
            return  df[df.broker == broker]
    else:
        return None
    
    
def remove_broker():
    os.remove(BK)
