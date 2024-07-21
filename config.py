
# 路由前缀
API_PREFIX = '/api'

# mysql相关配置
SQLALCHEMY_ECHO = True
SQLALCHEMY_ENABLE_POOL = False
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:Hzc123123..@127.0.0.1:3306/jd?charset=utf8mb4'
SQLALCHEMY_BINDS = {
}

# jwt 配置
JWT_SECRET_KEY = "hello!jd"
JWT_ACCESS_TOKEN_EXPIRES = 7 * 24 * 60 * 60

SESSION_SECRET_KEY = "hello!jd"

# spider
# 注意更换cookie及代理
BAIDU_COOKIE = 'BIDUPSID=27BC6EC24B54E2F826B782255A1A1F52; PSTM=1653906529; BD_UPN=123253; BDUSS_BFESS=DN4RXlteXktbmlzQlhUMHUxNTVVeW9yNzFJWG4xYVk5R3QxSGZUdngwTTBHWlJrSVFBQUFBJCQAAAAAAAAAAAEAAACf8y47ta3RxV~I5bfnAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADSMbGQ0jGxkV; MCITY=-289%3A; BAIDUID=CF8D388406718128A63DE9B6C9742339:FG=1; H_WISE_SIDS_BFESS=60362_60450_60360; H_PS_PSSID=60450_60360_60467_60498; H_WISE_SIDS=60450_60360_60467_60498; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; sugstore=1; BA_HECTOR=842g2g258k2l2l00a0a10l850m43co1j9oli91v; BAIDUID_BFESS=CF8D388406718128A63DE9B6C9742339:FG=1; ZFY=Rohc0dv0kRhp0iowv8E4d2H0P:A2:Amim2X3VIfMoJtTM:C; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; BD_CK_SAM=1; PSINO=3; delPer=0; H_PS_645EC=e6a4WhvrUl37rhTmwjgXctx96fwZDS0Be1GKvnH%2BAHISRCl2Zh3PxGaYuoW%2B%2FiiXzQi3; BDSVRTM=192; COOKIE_SESSION=83_0_9_9_17_23_1_1_8_9_24_2_524_0_0_0_1721491010_0_1721521743%7C9%230_0_1721521743%7C1'
GOOGLE_COOKIE = '__Secure-ENID=16.SE=QMgMmolWzCYdOAeWRlYYdKeYjbSUFtP2bwuE0OMrE_ebnwJbdQxm5VPGQuBTEPYqMdsAa2ld23JthOaPOdPm2q9Jv-WHeRGf9aB278SqWWx4KF00IpFm0Z7HP0q4kXiQASU3MkiNUYPlZ5Vihtce6FVfczkFk8rMc9tZt1qErFhi6LvLKhAQBJqiXkSFq5c9RRiaW9Jxz6kcqAb1ZKQ_RGqp0t6bxlWMGvx7aVw38VyB2lUr7G-113F7AsUiQ5A4u_laKTtghDWUGhKkd43QTMTu27bZbYqf1g; HSID=AvWG5KqO0t9fvJKB0; APISID=3837aOQHeYkdHXW1/A0mgzNX8EkVyq_szU; SSID=A17iKpYob6bPznAW2; SAPISID=-QoUT7j7KIgXB98d/AUgrFYcobmWymHFJe; __Secure-1PAPISID=-QoUT7j7KIgXB98d/AUgrFYcobmWymHFJe; __Secure-3PAPISID=-QoUT7j7KIgXB98d/AUgrFYcobmWymHFJe; SEARCH_SAMESITE=CgQImJsB; receive-cookie-deprecation=1; SID=g.a000lgisNDBV6eudW89kWIu93qPlnCX9CPq7lWvN1yqJus22xdw1W9X0q4dmSB-dP05Ma7ugrgACgYKAfwSARMSFQHGX2MiCe81DImGQA9mrrJUCqrc8BoVAUF8yKoPRhgiGmnOuxV_gvpvpcMI0076; __Secure-1PSID=g.a000lgisNDBV6eudW89kWIu93qPlnCX9CPq7lWvN1yqJus22xdw1RRraPWxJO6FfcowdTQE2vgACgYKAYsSARMSFQHGX2MilMO5dHxdNr_WweuJOwdoBRoVAUF8yKrfSvEWlLObfWgAaxSwopc10076; __Secure-3PSID=g.a000lgisNDBV6eudW89kWIu93qPlnCX9CPq7lWvN1yqJus22xdw1mQiUlqYwhtk5OkUpbihSZAACgYKAeMSARMSFQHGX2Mi2UA0RsGX7g4jjUSxtAzR9hoVAUF8yKrtPzfW0blCk-x-VRac5M560076; AEC=AVYB7cpfnoCDxGq5pnzT5u8l03znz04x2-wMixmDpF9lQFgc9n-kY3h3-g; NID=516=Nk3EsuhH2pHXgqXGZJoz_erpiIBW9bz1RnMAKOIZR0nkSsk3vhxdFp9hju5clRaCXx3GrfDyqPy4qUadiZae99uBvJZ08jsQP0YHMvwI0W9yVNkdVOiJpwHAfy33c4p13qOBSNS2c29JCOAkvpmthNJbgDZSwkeAeUrCbHBx5PGfT24cXG8Se7szqaBEn_tWPorFWcUf3SwKYEqowwyRqJzDZmUpDxQAjI-cPrNhz_kJAEk9hWZBSDLtkebIrsfzMtJe_c6TzXDlNlF32ORqbFJAPhzcGMrVshq_NtINTURmV-hvqybQyQ50TS5XFLH5Jcxo4j6c_xfCsqyEidLAjZ1sg4s-SzUJdYULCWYnfQV_qurW_K2XeMRw0CjRIcq3QN76wSjIlfTxxWwAzSY8YCZZTW5S9Rhn9OIeX1hYix8vRXn8Dw3LtfqXXCs; __Secure-1PSIDTS=sidts-CjIB4E2dkVAXCgcyP3ccdj-s-nEY1ZyIdD4XGNO3MH766_iMJCe25-n1zyfunoB7LUPZMRAA; __Secure-3PSIDTS=sidts-CjIB4E2dkVAXCgcyP3ccdj-s-nEY1ZyIdD4XGNO3MH766_iMJCe25-n1zyfunoB7LUPZMRAA; DV=c02k6EW5e6FYUAuW96t36_6uQ-c0DVkafDRcv1lcQwAAAKC_gZ31WkiLkgAAAASIm0L1K13fJQAAAGiYBOOXTyoPCwAAAA; SIDCC=AKEyXzVLnrhkt4dgG7EPpU9b0TspaZJ89aihBo25YPIGr7E8QAJ9fHzN_bbUxb63l61AaKfV; __Secure-1PSIDCC=AKEyXzUTyFT5f54vlByHLP-s0mO2780I4jvMc_cDLFqGZfTZQQadHFdDRmC2iCoxvzSHsUP5; __Secure-3PSIDCC=AKEyXzWgxRg7pWpSHXPnGRABwKc5UIigfKa3dHWiL70aM5v6--hgGox3qm6VhZUqoM8qQu58_vc'
BAIDU_SPIDER_PROXIES = {}
GOOGLE_SPIDER_PROXIES = {}
