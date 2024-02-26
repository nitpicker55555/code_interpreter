# -*- coding: gbk -*-
import ast
import json

a='[[snippet: 西安网是西安市委市政府主管的新闻资讯平台，提供西安市内外的政治、经济、社会、文化、体育等方面的新闻报道和评论。网站内容涵盖西安市的各个区县、各个领域、各个时期的新闻，以及西安市的特色活动、特色产品、特色风, title: 西安-西安网 - xiancity.cn, link: http://news.xiancity.cn/xian/index.shtml], [snippet: 1月26日上午，备受关注的陕西省第十四届人民代表大会第二次会议在西安隆重开幕。 500多名省人大 省委常委会（扩大）会议强调 以更高站位更实举措更严 2024-01-26 02:15 现场 | 陕西省十四届人大二次会议在西安开幕 2024-01-26 02:00 1月26日上午，陕西省十四届人大二次会议在西安开幕，会期4天。 会议期间，来自全省10个设区的市和驻陕部队共11个代表团的500多名省人大代表， 下一页 第 1 / 1176 页 到第 页 确定, title: 陕西-西安网, link: https://news.xiancity.cn/shanxi/index.shtml], [snippet: 西安新闻 华商网-华商报 2024-02-21 07:27:47 华商报讯 (记者 田睿)2月20日，西安市委市政府召开2024年全市"八个新突破"重点工作动员部署会议，深入学习贯彻党的二十大和习近平总书记历次来陕考察重要讲话重要指示精神，全面落实省委省政府工作要求，进一步动员全市上下振奋精神、顽强拼搏，创新推进中国式现代化西安实践取得新气象新成效，在奋力谱写中国式现代化建设的陕西新篇章中勇当先行示范。 省委常委、西安市委书记方红卫讲话，西安市长叶牛平主持，西安市人大常委会主任韩松、市政协主席王吉德、市委副书记李婧出席会议。 会上，印发了《2024年全市"八个新突破"实施方案》《2024年全市"八个新突破"抓落实方案》，各专项推进组组长分别作表态发言。, title: 西安召开八个新突破重点工作动员部署会议-西安新闻华商网新闻, link: https://news.hsw.cn/system/2024/0221/1719729.shtml], [snippet: 01. 《西安市以制造业为重点. 扩大利用外资若干措施》. 这个文件从鼓励制造业投资、优化外资结构、加强外汇金融服务、提升外资营商环境等方面提出10条具体举措，重在对制造业外资的政策支持，引导外资设立研发中心、区域总部、打造相关产业链集群，鼓励 ..., title: 推动对外开放，西安出台这些措施→澎湃号·政务_澎湃新闻-The Paper, link: https://www.thepaper.cn/newsDetail_forward_25893217]]'
def len_str2list(result):
    # result=result.replace("None","").replace(" ","")
    try:
        # 尝试使用 ast.literal_eval 解析字符串
        result = ast.literal_eval(result)
        # 检查解析结果是否为列表
        print("list")
        return len(result)
    except Exception as e:
        # 如果解析时发生错误，说明字符串不是有效的列表字符串
        print(e)
        try:
            dict_result=json.loads(result)
            return len(dict_result)
        except:

            return len(result)
print(len_str2list(a))