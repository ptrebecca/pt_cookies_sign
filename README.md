# cookies_sign
请安装保证Python版本大于等于3.6


# 简介

- cookies_sign 获取chrome的cookie并利用cookie进行签到 


# 主要功能

- 获取cookies
- 利用cookies签到
- 通过获取到的cookies列表，按照随机顺序进行签到

# 运行环境
请安装大于等于python 3.6 的版本运行此项目
- [Python下载](https://www.python.org/)

# 第三方库

- 需要使用到的库已经放在requirements.txt，使用pip安装的可以使用指令  
`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`

# 钉钉提醒
- url 参考 https://www.dingtalk.com/qidian/help-detail-20781541.html ，自定义关键字填 'pt'
- 修改url： 修改sing_all.py 第 126 行的url

# 运行
- 配置config.xlsx，根据域名，是否签到进行配置
- 获取cookie，只能获取chrome的cookie
    - 运行 get_cookies.py 获取cookie
- 执行签到
    - 运行 sing_all.py 执行签到


