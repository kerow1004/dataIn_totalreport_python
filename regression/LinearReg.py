import pandas as pd
import numpy as np
from scipy.stats.mstats import zscore
import statsmodels.api as sm

import pymysql

# 디비에서 데이터 가져오기
conn = pymysql.connect(host='datainreportdb.cvszzekzdq2c.us-east-2.rds.amazonaws.com', user='wiseadmin', password='wise1357!', db='dataIn', charset='utf8')
cur = conn.cursor()
cur.execute("select model_variable_element,data_no, quiz_no, data_val, model_type from MM_analysisMM_step02 where model_variable_element not in (2) and model_type = 1")
rows = cur.fetchall()
df = pd.DataFrame(rows, columns=['model_variable_element','data_no', 'quiz_no', 'data_val', 'model_type'])
df_pivot = df.pivot('data_no', 'quiz_no', 'data_val')
data_list = df_pivot.columns.tolist()
df_pivot["1avg"] = df_pivot.mean(axis=1)

print(df)

cur.close()
conn.close()

## 데이터가 없는 부분에 대한 방어로직 생성

# x = df_pivot[[2,3]]
#
# y = df_pivot[['1avg']]
# result= sm.OLS(zscore(y),zscore(x)).fit()
# t_values = result.tvalues
# print(t_values.to_dict())
