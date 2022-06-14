import pandas as pd
import numpy as np
from scipy.stats.mstats import zscore
import statsmodels.api as sm
import sys

import pymysql


#쿼리문
def query_data(report_idx, analysis_idx, model_list, values_round):
    model_list_add = model_list.append((0, 0, 4))
    df_merge = pd.DataFrame()
    for model_type in model_list:
        query = "select model_variable_element,data_no, quiz_no, data_val, model_type " \
                "from MM_analysisMM_step02 " \
                "where model_type = " + str(model_type[0]) + " and report_idx = " + str(report_idx) + " and analysis_idx = " + str(analysis_idx)
        df_pivot = dataframe_pivot(db_query(query, 's'), model_type, report_idx, analysis_idx, values_round)
        df_merge[df_pivot.columns[-1:]] = df_pivot

    regression_process(df_merge, report_idx, analysis_idx, model_type[0], values_round)

def insert_query(report_idx, analysis_idx, model_type, quiz_no, satisfaction_val, IPA_coef, values_round):

    query = "insert into MM_analysis_report_regression (report_idx, analysis_idx, model_type, quiz_no, satisfaction_val, IPA_coef) values " \
            "(" + str(report_idx) + ", " + str(analysis_idx) + ", " + str(model_type) + ", '" + str(quiz_no) + "', round(" + str(satisfaction_val) + ", " + str(values_round) + "), round(" + str(IPA_coef) + ", " + str(values_round) + "))"
# insert = i
# update = u
# select = s
    db_query(query, 'i')


# 디비접속하여 쿼리 실행
def db_query(query, mode):
    conn = pymysql.connect(host='datainreportdb.cvszzekzdq2c.us-east-2.rds.amazonaws.com', user='wiseadmin', password='wise1357!', db='dataIn', charset='utf8')
    try:
        with conn.cursor() as cur:
            cur.execute(query)

        if mode != 's':
            conn.commit()
    finally:
        conn.close()

    return cur

#데이터를 피봇하여 정리
def dataframe_pivot(db_data, model_type, report_idx, analysis_idx, values_round):
    rows = db_data.fetchall()
    df = pd.DataFrame(rows, columns=['model_variable_element', 'data_no', 'quiz_no', 'data_val', 'model_type'])
    df_pivot = df.pivot('data_no', 'quiz_no', 'data_val')
    df_pivot = df_pivot.astype(int)

    if model_type[2] == 0:
        df_pivot[str(model_type[0]) + "-avg"] = df_pivot.mean(axis=1)
        regression_process(df_pivot, report_idx, analysis_idx, model_type[0], values_round)
        return df_pivot.iloc[:, -1:]
    elif model_type[2] == 4:
        df_pivot[str(model_type[0]) + "-avg"] = df_pivot.mean(axis=1)
        return df_pivot.iloc[:, -1:]
    else:
        df_pivot_idx = df_pivot[df_pivot.columns.difference([model_type[1]])]
        df_pivot_idx[model_type[1]] = df_pivot.loc[:, [model_type[1]]]
        regression_process(df_pivot, report_idx, analysis_idx, model_type[0], values_round)
        return df_pivot.iloc[:, -1:]

#회기분석
def regression_process(data_reg, report_idx, analysis_idx, model_type, values_round):
    ## 데이터가 없는 부분에 대한 방어로직 생성

    x = data_reg.iloc[:, :-1]
    y = data_reg.iloc[:, -1:]
    reg = sm.OLS(zscore(y), zscore(x)).fit()
    # 회기계수 합
    reg_sum = reg.params.abs().sum()
    # 회기계수 절대값으로 비율
    result = reg.params.abs() / reg_sum
    data_avg = data_reg.iloc[:, :-1].mean()


    [insert_query(report_idx, analysis_idx, model_type, result.index[(x)], result.values[x], data_avg.values[x], values_round) for x in range(len(result))]

    # for row in range(len(result)):
    #     insert_query(report_idx, analysis_idx, model_type, result.index[(row)], result.values[row],
    #                  data_avg.values[row], values_round)


if __name__ == '__main__':
    report_idx = sys.argv[1]
    analysis_idx = sys.argv[2]
    values_round = sys.argv[3]

    query_model_tuple = "select model_type, quiz_no ,model_variable_element " \
                       "from MM_analysisMM_step02 " \
                       "where model_variable_element != 2 and model_type <100 and model_type != 0 " \
                       "and report_idx = " + str(report_idx) + " and analysis_idx = " + str(analysis_idx) + " group by model_type"

    model_list = list(db_query(query_model_tuple, 's').fetchall())

    query_data(report_idx, analysis_idx, model_list, values_round)