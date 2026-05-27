from typing import Dict, List


HOSPITAL_RESOURCES: List[Dict[str, str]] = [
    {
        "region": "北京",
        "hospital": "北京大学第一医院",
        "department": "精神心理科 / 心理咨询门诊",
        "phone": "010-83572211（总机，心理门诊请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "北京市西城区西什库大街8号",
    },
    {
        "region": "上海",
        "hospital": "复旦大学附属华山医院",
        "department": "心理医学科",
        "phone": "021-52889999（总机，心理医学科请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "上海市静安区乌鲁木齐中路12号",
    },
    {
        "region": "广州",
        "hospital": "中山大学附属第一医院",
        "department": "心理医学科 / 精神心理相关门诊",
        "phone": "020-28823388（总机，心理门诊请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "广东省广州市越秀区中山二路58号",
    },
    {
        "region": "深圳",
        "hospital": "深圳市人民医院",
        "department": "心理医学科 / 临床心理门诊",
        "phone": "0755-25533018（总机，心理门诊请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "广东省深圳市罗湖区东门北路1017号",
    },
    {
        "region": "成都",
        "hospital": "四川大学华西医院",
        "department": "心理卫生中心 / 心理咨询门诊",
        "phone": "028-85422114（总机，心理卫生中心请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "四川省成都市武侯区国学巷37号",
    },
    {
        "region": "杭州",
        "hospital": "浙江大学医学院附属第一医院",
        "department": "精神卫生科 / 心理咨询门诊",
        "phone": "0571-87236114（总机，心理门诊请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "浙江省杭州市上城区庆春路79号",
    },
    {
        "region": "南京",
        "hospital": "江苏省人民医院",
        "department": "临床心理科 / 医学心理科",
        "phone": "025-68303126（总机，心理门诊请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "江苏省南京市广州路300号",
    },
    {
        "region": "武汉",
        "hospital": "武汉大学人民医院",
        "department": "精神卫生中心 / 心理咨询门诊",
        "phone": "027-88041911（总机，心理门诊请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "湖北省武汉市武昌区张之洞路99号",
    },
    {
        "region": "西安",
        "hospital": "西安交通大学第一附属医院",
        "department": "精神心理卫生科 / 心理咨询门诊",
        "phone": "029-85323112（总机，心理门诊请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "陕西省西安市雁塔区雁塔西路277号",
    },
    {
        "region": "郑州",
        "hospital": "郑州大学第一附属医院",
        "department": "精神医学科 / 心理咨询门诊",
        "phone": "0371-66913114（总机，心理门诊请转相关科室）",
        "email": "请以医院官网公布邮箱为准",
        "address": "河南省郑州市二七区建设东路1号",
    },
]


def search_hospital_resources(keyword: str) -> List[Dict[str, str]]:
    keyword = str(keyword or "").strip().lower()
    if not keyword:
        return HOSPITAL_RESOURCES
    results = []
    for item in HOSPITAL_RESOURCES:
        haystack = " ".join(item.values()).lower()
        if keyword in haystack:
            results.append(item)
    return results
