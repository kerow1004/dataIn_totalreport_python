import pandas as pd
import numpy as np
from scipy.stats.mstats import zscore
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

import pymysql

# 디비에서 데이터 가져오기
conn = pymysql.connect(host='datainreportdb.cvszzekzdq2c.us-east-2.rds.amazonaws.com', user='wiseadmin', password='wise1357!', db='dataIn', charset='utf8')
cur = conn.cursor()
cur.execute("select model_variable_element,data_no, quiz_no, data_val, model_type from MM_analysisMM_step02 where model_variable_element not in (2) and model_type = 1")
rows = cur.fetchall()
df = pd.DataFrame(rows, columns=['model_variable_element','data_no', 'quiz_no', 'data_val', 'model_type'])

df_pivot = df.pivot('data_no', 'quiz_no', 'data_val')
df_pivot = df_pivot.astype(int)
data_list = df_pivot.columns.tolist()
df_pivot["1avg"] = df_pivot.mean(axis=1)

# print(df_pivot)

cur.close()
conn.close()

## 데이터가 없는 부분에 대한 방어로직 생성

x = df_pivot[data_list]
y = df_pivot[['1avg']]
# print(zscore(y))
# print(zscore(x))
result= sm.OLS(zscore(y),zscore(x)).fit()
result= sm.OLS(y, x).fit()
print(result.summary())
t_values = result.tvalues
print(t_values.to_dict())


# mlr = LinearRegression()
# mlr.fit(zscore(x), zscore(y))
# print(mlr.coef_)
# print(mlr.score(x,y))
# print(mlr.intercept_)