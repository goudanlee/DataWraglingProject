#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import audit as au

# 定义正则表达式规则来获取指定元素
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
# 包含"addr:"街道相关元素匹配的正则
street = re.compile(r'^(addr:)+?')
# 街道内包含双重冒号的正则
street_colon = re.compile(r'^(addr:)+?([a-z])*:([a-z])*$')
#定义需要补充的街道名简称和全称的映射关系
mapping = { "St": "Street",
            "St.": "Street",
            "Rd":"Road",
            "Rd.":"Road",
            "Ave":"Avenue",
            "Ave.":"Avenue"
            }

# 定义CREATED里包含的元素
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_element(element, street_names):
    # 按照指定规则清洗数据
    node = {}

    # 读取所有为node或way的元素
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node['created'] = {}
        node['type'] = element.tag
        #获取way里的nd，并生成node["node_refs"]
        if element.tag == "way" :
            node['node_refs'] = []
            for tag in element.iter("nd"):
                node['node_refs'].append(tag.attrib['ref'])

        #获取子标签里和addr相关的k属性值
        if element.findall("tag[@k='addr:street']"):
            node['address'] = {}
            for tag in element.iter("tag"):
                if street_colon.findall(tag.attrib['k']):
                    # 判断是否出现两次冒号
                    pass
                elif problemchars.findall(tag.attrib['k']):
                    # 判断是否属于异常字符
                    pass
                elif street.findall(tag.attrib['k']):
                    # 判断是否属于street内容的标签
                    if tag.attrib['v'] in street_names:
                        # 如果元素的"v"值在需要修改的街道名称中，则对街道名称进行补充
                        node['address']["street"] = au.update_name(tag.attrib['v'],mapping)
                    else:
                        # 如果为address下的其他元素，则加入到address中
                        key = tag.attrib['k'][5:]
                        node['address'][key] = tag.attrib['v']
                else:
                    node[tag.attrib['k']] = tag.attrib['v']


        #获取node和way中的各属性值
        for attrib in element.attrib:
            if attrib in CREATED:
                # 判读是否属于created里的内容
                node['created'][attrib]  = element.attrib[attrib]
            elif attrib in ('lat','lon'):
                # 判断是否属于经纬度
                node['pos'] = [float(element.attrib['lat']),float(element.attrib['lon'])]
            else:
                node[attrib] = element.attrib[attrib]
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # 读取xml需要进行街道名修改的所有街道名称
    st_types = au.audit(file_in)
    # 需要修改的街道名称
    street_names = []
    #将需要修改的街道名称加入street_names[]
    for st_type, ways in st_types.iteritems():
        for name in ways:
            street_names.append(name)
    
    # 将oms文件解析并转换成json文件
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element, street_names)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.

    OSMFILE = 'G:\A_Udacity_data_analyst\course\project3\sydney_sample.osm'


    #清洗数据
    process_map(OSMFILE, pretty=True)






if __name__ == "__main__":
    test()