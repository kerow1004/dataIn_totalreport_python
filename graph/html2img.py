import logging
import pydot
import pymysql
import sys
import boto3
from botocore.exceptions import ClientError
import os
# 그래프 설정
graph = pydot.Dot(graph_type="graph", rankdir="UD")
graph.set_node_defaults(shape="box", color='#517eb8',style='filled')

# 노드가 그려 지는 영역
def add_edge(root, child):
    edge = pydot.Edge(root, child, )
    graph.add_edge(edge)


def add(root, children):
    for child in children:
        add_edge(root, child)


# 디비에서 데이터 가져오기
def mariaDBconn(idxNo):
    try:
        conn = pymysql.connect(host='datainreportdb.cvszzekzdq2c.us-east-2.rds.amazonaws.com', user='wiseadmin', password='wise1357!', db='dataIn', charset='utf8')
        cur = conn.cursor()
        cur.execute("select "
                    "decision_option_model_quiz_level"
                    ", decision_option_model_quiz_parent"
                    ", analysis_report_decision_option_model_quiz_no"
                    ", view_title "
                    "from dataIn.wise_analysis_report_decision_option_model_quiz "
                    "where decision_option_idx = " + idxNo + "  and view_yn = ''")
        rows = cur.fetchall()

        row = [list(rows[x]) for x in range(len(rows))]
        nodeDeep = list(set(row[i][0] for i in range(len(rows))))
        for x in range(len(nodeDeep)):
            nodeNo = []
            nodes = []
            subnodeNo = []
            subnodetemp = []

            for y in range(len(row)):
                if (row[y][0] == x + 1):
                    nodes.append(row[y][3])
                    nodeNo.append(row[y][2])
                elif (row[y][0] == x + 2):
                    subnodeNo.append((row[y][1]))
                    subnodetemp.append(row[y][3])
            if (x == 0):
                add('목표', nodes)

            for i, no in enumerate(nodeNo):
                subnode = []
                for j, sno in enumerate(subnodeNo):
                    if (no == sno):
                        subnode.append(subnodetemp[j])
                if (len(subnode) != 0):
                    add(nodes[i], subnode)
                else:
                    continue
    except Exception as e:
        print('process err : ', e)
    finally:
        cur.close()
        conn.close()

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True



if __name__ == '__main__':
    id = sys.argv[1]
    do_idx = sys.argv[2]

    mariaDBconn(do_idx)

    graph.write_png("../graphImg/" + id + "_" + do_idx + ".png")
    uploadFile = '../graphImg/' + id + '_' + do_idx + '.png'

    bucket = 'dataintotalreporting'
    s3Path = 'AHPModelImg/' + id + '_' + do_idx + '.png'
    upload_file(uploadFile, bucket, s3Path)

    # graph.write_png("../graphImg/"+id+"_"+do_idx+".png"

    # graph.write_png("../graphImg/"+id+"_"+do_idx+".png")


