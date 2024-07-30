import re


def find_accounts(text):
    # QQ号正则表达式 (5-11位数字)
    qq_pattern = r'\b(qq)?[1-9][0-9]{8,10}\b'

    # 中国大陆手机号正则表达式
    phone_pattern = r'\b1[3-9]\d{9}\b'

    # Telegram账号正则表达式 (@开头,4-32位字母、数字或下划线)
    # telegram_pattern = r'@[a-zA-Z0-9_]{4,32}\b'
    telegram_pattern = r'@\+?[a-zA-Z0-9_]{4,32}\b'

    # 查找所有匹配项
    qq_numbers = re.findall(qq_pattern, text)
    phone_numbers = re.findall(phone_pattern, text)
    telegram_accounts = re.findall(telegram_pattern, text)

    return {
        'qq_number': qq_numbers,
        'phone_number': phone_numbers,
        'telegram_number': telegram_accounts
    }


if __name__ == '__main__':

    # 测试代码
    test_text = """
|    联系电报TG（ xincheng8887）依托咪酯上头电子烟烟粉猪肉 ...1111人力銀行https://www.1111.com.tw › search › job1111人力銀行https://www.1111.com.tw › search › job · 转为简体网页幸福企業徵人「联系电报TG（ xincheng8887）依托咪酯上头电子烟烟粉猪肉冰毒K粉.jyh工作」1111人力銀行網羅眾多知名企業職缺，求職者找工作可依照想要的工作地區、 ...飞行上头上头电子烟飞行依托咪酯Telegram Messengerhttps://t.me › sshuntong2Telegram Messengerhttps://t.me › sshuntong2King Louis XIII   路易十三烟油   THC：90%～93% 属性：  Sativa40% indica60% 香气：泥土味、花香  、麝香松   路易斯国王   大麻在医疗和娱乐使用者中闻名 ...上头电子烟飞行员燃料依托咪酯 - TG搜索大师TG搜索大师http://telegram.ikun123.com › GDBWICI_china420TG搜索大师http://telegram.ikun123.com › GDBWICI_china420上头电子烟飞行员燃料依托咪酯. 1912 members. View in Telegram. If you have Telegram, you can view and join 上头电子烟飞行员燃料依托咪酯right away. 红魔馆专线 ...联系电报TG（@ xincheng8887）依托咪酯上头电子烟 ...Shopee.vnhttps://shopee.vn › search › keyword=联系...Shopee.vnhttps://shopee.vn › search › keyword=联系... · 翻译此页Mua 联系电报TG（@ xincheng8887）依托咪酯上头电子烟烟粉猪肉冰毒K粉.lon giao tận nơi và tham khảo thêm nhiều sản phẩm khác. Miễn phí vận chuyển toàn quốc cho ...联系电报TG（@ uup99887）依托咪酯上头电子烟烟粉猪肉 ...CAPILLUS激光活髮帽https://www.capillus.com.hk › result › q...CAPILLUS激光活髮帽https://www.capillus.com.hk › result › q... · 转为简体网页Home · Search results for: '联系电报TG（@ uup99887）依托咪酯上头电子烟烟粉猪肉冰毒K粉.esb' ...“上头电子烟”“上头”更“上刑”！全区首例涉依托咪酯案判了Supreme People's Procuratorate (.gov)http://www.xz.jcy.gov.cn › jwgk › jckxSupreme People's Procuratorate (.gov)http://www.xz.jcy.gov.cn › jwgk › jckx2024年5月13日 — 据悉，2023年10月，被告人熊某甲按照熊某乙的指使将含有依托咪酯成分的“上头电子烟”烟弹从拉萨市运输至山南市辖区售卖并从中获利，二人先后被公安机关抓获 ...缺少字词： TG ‎| 必须包含： TG联系电报TG（@ dahai918）依托咪酯上头电子烟烟粉猪肉 ...GGZ Interventiehttps://ggzinterventie.nl › s=联系电报TG（...GGZ Interventiehttps://ggzinterventie.nl › s=联系电报TG（... · 翻译此页GGZ Interventie is gewaardeerd op ZorgkaartNederland met een 8,5. Bekijk alle waarderingen. Zorgdomein ISO9001. © 2024 ...上头电子烟依托咪酯| TG搜索大师- 最全的Telegram频道群组索引TG搜索大师https://telegram.ikun123.com › channel › DUYAO_VV68TG搜索大师https://telegram.ikun123.com › channel › DUYAO_VV68上头电子烟依托咪酯. 1126 members. View in Telegram. If you have Telegram, you can view and join 上头电子烟依托咪酯right away. Lray高端IEPL专线机场免费体验. 相关 ...联系电报TG（@ kefu6889）依托咪酯上头电子烟烟粉猪肉 ...B站https://m.bilibili.com › search › keyword=联系电报TG...B站https://m.bilibili.com › search › keyword=联系电报TG...bilibili为您提供联系电报TG（@ kefu6889）依托咪酯上头电子烟烟粉猪肉冰毒K粉.oun相关的视频、番剧、影视、动画等内容。bilibili是国内知名的在线视频弹幕网站， ...图片联系电报tg(@Ppo995)依托咪酯上头电子烟烟粉猪肉冰毒k粉.Uaw ...Pexels台城】禁毒科普：含有依托咪酯的“上头电子烟”堪比毒品，吸不得 ...台山市人民政府联系电报tg(@Ppo995)依托咪酯上头电子烟烟粉猪肉冰毒k粉.Uaw ...Pexels反馈所有图片另外 6 张图片 |"""
    results = find_accounts(test_text)
    for account_type, accounts in results.items():
        print(f"{account_type}: {accounts}")

# 号码转小写+去重复
