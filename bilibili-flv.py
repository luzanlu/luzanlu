import requests
import json
import os
import time
import hashlib
import re

head = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/85.917',
        'Referer': 'https://www.bilibili.com/'
        }
heads = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/85.917'}

def consize(size):
    size_mb = size / (1024 * 1024)
    if size_mb > 1024:
        size_gb = size_mb / 1024
        size_ = str(round(size_gb, 2)) + 'GB'
    else:
        size_ = str(round(size_mb, 2)) + 'MB'
    return size_

#计算中文字符个数，模糊匹配，可能不精确
def len_zh(data):
    temp = re.findall('[^a-zA-Z0-9. ]+',data)
    count = 0
    for i in temp:
        count += len(i)
    return count

def tv_sign(tvsi):
    text = tvsi + '59b43e04ad6965f34319062b478f83dd'
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()

def get_id(url):
    if '?' in url:
        ep_id = url[url.find('ep')+2:url.find('?')]
    else:
        ep_id = url[url.find('ep')+2:]
    id_api = f'https://api.bilibili.com/pgc/view/web/season?ep_id={ep_id}'
    res = requests.get(id_api,headers=head)
    res.encoding = res.apparent_encoding
    pvcon = res.text
    pvcon = json.loads(pvcon)
    pvcon = pvcon['result']['episodes']
    vlist = []
    for i in range(0,len(pvcon)):
        title = pvcon[i]['share_copy']
        epid = str(pvcon[i]['ep_id'])
        aid = str(pvcon[i]['aid'])
        cid = str(pvcon[i]['cid'])
        if epid == ep_id:
            vlist2 = [epid,aid,cid,title]
            vlist.append(vlist2)
    epid = vlist[0][0]
    aid = vlist[0][1]
    cid = vlist[0][2]
    name = vlist[0][3]
    return epid,aid,cid,name
    
def tv_list(epid,aid,cid,ck_bili):
    tm = int(time.time())
    tvsi = f'access_key={ck_bili}&aid={aid}&appkey=4409e2ce8ffd12b8&build=102801&cid={cid}&device=android&ep_id={epid}&expire=0&fnval=0&fnver=0&fourk=1&mid=0&mobi_app=android_tv_yst&module=bangumi&npcybs=0&otype=json&platform=android&qn=0&ts={tm}'
    sign = tv_sign(tvsi)
    tv_api = 'https://api.snm0516.aisee.tv/pgc/player/api/playurltv?' +  tvsi + f'&sign={sign}'
    res = requests.get(tv_api,headers=heads)
    res.encoding = res.apparent_encoding
    pvcon = res.text
    pvcon = json.loads(pvcon)
    if pvcon['is_preview'] == 1:
        return 'Cookie','过期，','需要重新输入！','！'
    format_name = pvcon['support_formats']
    namedict = {}
    for j in range(0,len(format_name)):
        namedict[format_name[j]['quality']] = format_name[j]['new_description']
    vi = pvcon['durl'][0]['url']
    viid = pvcon['quality']
    size = pvcon['durl'][0]['size']
    return vi,viid,size,namedict

def bilibili(url,downPatch,ck_bili):
    epid,aid,cid,name = get_id(url)
    vi,viid,size,namedict = tv_list(epid,aid,cid,ck_bili)
    if size == '需要重新输入！':
        print(vi+viid+size)
        return None
    else:
        print('开始解析：' + name)
        print('===================================================================')
        print('序号   id        名称              编码   大小')
        print('0'.ljust(7)+str(viid).ljust(10)+namedict[viid].ljust(18-len_zh(namedict[viid]))+'AVC'.ljust(7)+consize(size))
        print('===================================================================')
        print('开始下载序号0清晰度！')
        os.system(f'aria2c -d "{downPatch}" -o "{name}.flv" "{vi}"')
        print(name + '.flv下载完成！')

downPatch = r'E:\Video\work'        #下载目录
ck_bili = 'a824d878ad1379fa77c25b9426789eb2'        #Cookie

url = input('请输入视频地址：')

while url != 'Q':
    bilibili(url,downPatch,ck_bili)
    url = input('请输入视频地址：')
