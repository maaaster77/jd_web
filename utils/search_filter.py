import re


def find_accounts(text):
    # QQ号正则表达式 (5-11位数字)
    qq_pattern = r'\b[1-9][0-9]{8,10}\b'

    # 中国大陆手机号正则表达式
    phone_pattern = r'\b1[3-9]\d{9}\b'

    # Telegram账号正则表达式 (@开头,4-32位字母、数字或下划线)
    telegram_pattern = r'@[a-zA-Z0-9_]{4,32}\b'

    # 查找所有匹配项
    qq_numbers = re.findall(qq_pattern, text)
    phone_numbers = re.findall(phone_pattern, text)
    telegram_accounts = re.findall(telegram_pattern, text)

    return {
        'qq_number': qq_numbers,
        'phone_number': phone_numbers,
        'telegram_number': telegram_accounts
    }


# 测试代码
test_text = """
China 420 Rib Hypalon Inflatable Boat CE 14 FT ...Made-in-China.comhttps://cnhedia.en.made-in-china.com › Chi...Made-in-China.comhttps://cnhedia.en.made-in-china.com › Chi... · 翻译此页China 420 Rib Hypalon Inflatable Boat CE 14 FT Hypalon Boat Semi-Rigid Deep V Aluminum Hull Sport China 420 Rib Hypalon Inflatable Boat ; Warranty. 3-5 Years.CA420 (CCA420) Air China Flight Tracking and HistoryFlightAwarehttps://www.flightaware.com › live › CCA4...FlightAwarehttps://www.flightaware.com › live › CCA4... · 翻译此页Flight status, tracking, and historical data for Air China 420 (CA420/CCA420) including scheduled, estimated, and actual departure and arrival times.China 420 Rib Hypalon Inflatable BoatAlibabahttps://www.alibaba.com › ... › Rowing BoatsAlibabahttps://www.alibaba.com › ... › Rowing BoatsHit the water for a casual sail with a wholesale china 420 rib hypalon inflatable boat from Alibaba.com's range of rowing boats.China 420 Stainless Steel Manufacturers – Coke Series ...Shandong Institute of Metallurgical Science Co., Ltd.https://www.cncrms.com › china-420-stainl...Shandong Institute of Metallurgical Science Co., Ltd.https://www.cncrms.com › china-420-stainl... · 翻译此页China 420 Stainless Steel Manufacturers – Coke Series National And Industrial Reference Materials – Shandong Institute of Metallurgical Science.China 420 Stainless Steel Bar Stock Suppliers - mirror 8k 304 ...jsjoinsteel.comhttps://www.jsjoinsteel.com › ...jsjoinsteel.comhttps://www.jsjoinsteel.com › ... · 翻译此页Moreover, customer pleasure is our everlasting pursuit. China 420 Stainless Steel Bar Stock Suppliers - mirror 8k 304 316 stainless steel sheet – TISCO Detail:.What standard does China 420 stainless steel sheet ...Saky Steelhttps://www.sakysteel.com › news › what-sta...Saky Steelhttps://www.sakysteel.com › news › what-sta... · 翻译此页40Cr13 stainless steel: Harder than 30Cr13 after quenching, used as cutting tools, nozzles, valve seats, valves, etc. Post time ...tg kefuxiaokeai 420 china420 chinaweed icoDribbblehttps://dribbble.com › searchDribbblehttps://dribbble.com › search · 翻译此页Explore thousands of high-quality tg kefuxiaokeai 420 china420 chinaweed ico images on Dribbble. Your resource to get inspired, discover and connect with ...Stone Sinks Manufacture China 420*420*140 Rough ...StoneContact.comhttps://www.stonecontact.com › stone-sinks...StoneContact.comhttps://www.stonecontact.com › stone-sinks... · 翻译此页Stone Sinks Manufacture China 420*420*140 Rough Sunset Red from China, The details include pictures,sizes,color,material and origin.Free 电报tg(@Ppo995)飞叶子420+中国大麻china420.Jlr ...Pexelshttps://www.pexels.com › search › 电报TG(@ppo995)...Pexelshttps://www.pexels.com › search › 电报TG(@ppo995)...Download and use 80+ 电报tg(@ppo995)飞叶子420+中国大麻china420.jlr stock photos for free. ✓ Thousands of new images every day ✓ Completely Free to Use ...电报TG(@ppo995)飞叶子420 中国大麻china420.msb ...Guilford County Schoolshttps://www.gcsnc.com › site › searchstring...Guilford County Schoolshttps://www.gcsnc.com › site › searchstring... · 翻译此页Guilford County Schools, the third largest school district in North Carolina and the 50th largest of more than 14000 in the United States, serves more than ... """

results = find_accounts(test_text)
for account_type, accounts in results.items():
    print(f"{account_type}: {accounts}")

# 号码转小写+去重复
