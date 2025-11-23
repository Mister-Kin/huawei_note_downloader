#coding=utf8

import requests,json,html
from lxml import etree
import datetime,os

list_url = "https://cloud.huawei.com/notepad/simplenote/query"
content_url = "https://cloud.huawei.com/notepad/note/query"
payload = json.dumps({
  "traceId": ""
})
header= {
  'Cookie': '填写你的cookie',
  'Content-Type': 'application/json'
}

#解析所有note目录json数据
def getAllNote():
    response = requests.request("POST", list_url, headers=header, data=payload)
    result = json.loads(response.text)
    result_json = result.get('rspInfo').get('noteList')
    return result_json


if __name__ == '__main__':
    dataFile = os.path.dirname(os.path.abspath(__file__)) + "/华为备忘录导出.txt"
    f = open(dataFile,"w+",encoding="utf8")
    result_json = getAllNote()

    parsed_data = []
    for j in result_json:
        data = json.loads(j.get('data'))
        parsed_data.append(data)

    # 按创建时间升序排序
    parsed_data.sort(key=lambda x: x.get('created', 0))

    for data in parsed_data:
        created_timestamp = data.get('created')
        modified_timestamp = data.get('modified')

        # 转换Unix时间戳
        created_time = datetime.datetime.fromtimestamp(created_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
        modified_time = datetime.datetime.fromtimestamp(modified_timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

        f.writelines('【创建时间】：' + created_time + '\n')
        f.writelines('【修改时间】：' + modified_time + '\n')
        f.writelines('【标题】：\n')
        f.writelines(data.get('title')+'\n')
        f.writelines('---------------------------------------------' + '\n')
        f.writelines('----------------标题内容分割线-----------------' + '\n')
        f.writelines('---------------------------------------------' + '\n\n')
        f.writelines('【内容】：\n')

        guid = data.get('guid')
        print(guid)
        ##  request content
        contentPayload = json.dumps({
            "ctagNoteInfo": "123",
            "ctagNoteTag": "123",
            "guid": guid,
            "startCursor":"123",
            "traceId": "123"
        })

        contentRes = requests.request("POST", content_url, headers=header, data=contentPayload)
        # print(contentRes.text[0:100])
        contentData = json.loads(contentRes.text)
        # print(contentData)
        t = contentData.get('rspInfo').get('data')
        content_string = json.loads(t).get('content').get('html_content')

        #
        imgList = json.loads(t).get('fileList')
        if imgList != None and len(imgList) > 0:
            imgpos = 0
            while content_string.find('图片')!=-1:
                content_string.replace('图片',imgList[imgpos].get('name'),1)
                imgpos+=1

        t = html.unescape(content_string)
        html1=etree.HTML(t)
        result = html1.xpath('string(.)')
        # result=etree.tostring(html1,encoding='utf-8')
        # result = result.decode('utf-8')
        # content_string = content_string.replace('<note><element type="Text">','')
        # content_string = content_string.replace('</element></note>','')
        # content_string = content_string.replace('<hw_font size ="1.0">','')
        # content_string = content_string.replace('</hw_font>','')
        # content_string = content_string.replace('<br>','')
        f.writelines(result + '\n\n\n')
        f.writelines('---------------------------------------------------------------------' + '\n')
        f.writelines('---------------备忘录分割线-----------------备忘录分割线-----------------' + '\n')
        f.writelines('---------------------------------------------------------------------' + '\n\n\n')
    f.close()
