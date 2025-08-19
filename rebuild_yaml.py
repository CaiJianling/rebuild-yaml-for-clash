import sys

# 检查并安装必要的依赖
try:
    import yaml
except ImportError:
    print("正在安装缺失的依赖: pyyaml...")
    import subprocess
    import importlib
    try:
        # 尝试使用pip安装
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "--user"])
        print("pyyaml 安装成功!")
        
        # 尝试动态导入
        try:
            importlib.invalidate_caches()  # 清除导入缓存
            import yaml
            print("成功导入yaml模块!")
        except ImportError:
            # 如果动态导入失败，将在主程序中使用子进程方式重启
            pass
            
    except Exception as e:
        print(f"安装 pyyaml 失败: {e}")
        print("请手动安装: pip install pyyaml --user")
        print("然后重新运行此脚本")
        sys.exit(1)

def process_config(original_config):
    # 国内DNS服务器
    domestic_nameservers = [
        "https://dns.alidns.com/dns-query",  # 阿里云公共DNS
        "https://doh.pub/dns-query",         # 腾讯DNSPod
        "https://doh.360.cn/dns-query"       # 360安全DNS
    ]
    
    # 国外DNS服务器
    foreign_nameservers = [
        "https://1.1.1.1/dns-query",         # Cloudflare(主)
        "https://1.0.0.1/dns-query",         # Cloudflare(备)
        "https://208.67.222.222/dns-query",  # OpenDNS(主)
        "https://208.67.220.220/dns-query",  # OpenDNS(备)
        "https://194.242.2.2/dns-query",     # Mullvad(主)
        "https://194.242.2.3/dns-query"      # Mullvad(备)
    ]
    
    # DNS配置
    dns_config = {
        "enable": True,
        "listen": "0.0.0.0:1053",
        "ipv6": True,
        "use-system-hosts": False,
        "cache-algorithm": "arc",
        "enhanced-mode": "fake-ip",
        "fake-ip-range": "198.18.0.1/16",
        "fake-ip-filter": [
            "+.lan",
            "+.local",
            "+.msftconnecttest.com",
            "+.msftncsi.com",
            "localhost.ptlogin2.qq.com",
            "localhost.sec.qq.com",
            "localhost.work.weixin.qq.com"
        ],
        "default-nameserver": ["223.5.5.5", "119.29.29.29", "1.1.1.1", "8.8.8.8"],
        "nameserver": domestic_nameservers + foreign_nameservers,
        "proxy-server-nameserver": domestic_nameservers + foreign_nameservers,
        "nameserver-policy": {
            "geosite:private,cn,geolocation-cn": domestic_nameservers,
            "geosite:google,youtube,telegram,gfw,geolocation-!cn": foreign_nameservers
        }
    }
    
    # 规则集通用配置
    rule_provider_common = {
        "type": "http",
        "format": "yaml",
        "interval": 86400
    }
    
    # 规则集配置
    rule_providers = {
        "reject": {**rule_provider_common,
            "behavior": "domain",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt",
            "path": "./ruleset/loyalsoldier/reject.yaml"
        },
        "icloud": {** rule_provider_common,
            "behavior": "domain",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/icloud.txt",
            "path": "./ruleset/loyalsoldier/icloud.yaml"
        },
        "apple": {**rule_provider_common,
            "behavior": "domain",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/apple.txt",
            "path": "./ruleset/loyalsoldier/apple.yaml"
        },
        "google": {**rule_provider_common,
            "behavior": "domain",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/google.txt",
            "path": "./ruleset/loyalsoldier/google.yaml"
        },
        "proxy": {**rule_provider_common,
            "behavior": "domain",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt",
            "path": "./ruleset/loyalsoldier/proxy.yaml"
        },
        "direct": {**rule_provider_common,
            "behavior": "domain",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt",
            "path": "./ruleset/loyalsoldier/direct.yaml"
        },
        "private": {**rule_provider_common,
            "behavior": "domain",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt",
            "path": "./ruleset/loyalsoldier/private.yaml"
        },
        "gfw": {**rule_provider_common,
            "behavior": "domain",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/gfw.txt",
            "path": "./ruleset/loyalsoldier/gfw.yaml"
        },
        "tld-not-cn": {**rule_provider_common,
            "behavior": "domain",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/tld-not-cn.txt",
            "path": "./ruleset/loyalsoldier/tld-not-cn.yaml"
        },
        "telegramcidr": {**rule_provider_common,
            "behavior": "ipcidr",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt",
            "path": "./ruleset/loyalsoldier/telegramcidr.yaml"
        },
        "cncidr": {**rule_provider_common,
            "behavior": "ipcidr",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/cncidr.txt",
            "path": "./ruleset/loyalsoldier/cncidr.yaml"
        },
        "lancidr": {**rule_provider_common,
            "behavior": "ipcidr",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt",
            "path": "./ruleset/loyalsoldier/lancidr.yaml"
        },
        "applications": {**rule_provider_common,
            "behavior": "classical",
            "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/applications.txt",
            "path": "./ruleset/loyalsoldier/applications.yaml"
        },
        "openai": {
            **rule_provider_common,
            "behavior": "classical",
            "url": "https://fastly.jsdelivr.net/gh/blackmatrix7/ios_rule_script@master/rule/Clash/OpenAI/OpenAI.yaml",
            "path": "./ruleset/blackmatrix7/openai.yaml"
        }
    }
    
    # 规则配置
    rules = [
        # 自定义规则
        "DOMAIN-SUFFIX,googleapis.cn,节点选择", # Google服务
        "DOMAIN-SUFFIX,gstatic.com,节点选择", # Google静态资源
        "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,节点选择", # Google Play下载服务
        "DOMAIN-SUFFIX,github.io,节点选择", # Github Pages
        "DOMAIN,v2rayse.com,节点选择", # V2rayse节点工具
        # blackmatrix7 规则集
        "RULE-SET,openai,ChatGPT",
        # Loyalsoldier 规则集
        "RULE-SET,applications,全局直连",
        "RULE-SET,private,全局直连",
        "RULE-SET,reject,广告过滤",
        "RULE-SET,icloud,微软服务",
        "RULE-SET,apple,苹果服务",
        "RULE-SET,google,谷歌服务",
        "RULE-SET,proxy,节点选择",
        "RULE-SET,gfw,节点选择",
        "RULE-SET,tld-not-cn,节点选择",
        "RULE-SET,direct,全局直连",
        "RULE-SET,lancidr,全局直连,no-resolve",
        "RULE-SET,cncidr,全局直连,no-resolve",
        "RULE-SET,telegramcidr,电报消息,no-resolve",
        # 其他规则
        "GEOIP,LAN,全局直连,no-resolve",
        "GEOIP,CN,全局直连,no-resolve",
        "MATCH,漏网之鱼"
    ]
    
    # 代理组通用配置
    group_base_option = {
        "interval": 300,
        "timeout": 3000,
        "url": "https://www.google.com/generate_204",
        "lazy": True,
        "max-failed-times": 3,
        "hidden": False
    }
    
    # 代理组配置
    proxy_groups = [
        {** group_base_option,
            "name": "节点选择",
            "type": "select",
            "proxies": ["延迟选优", "故障转移", "负载均衡(散列)", "负载均衡(轮询)"],
            "include-all": True,
            "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/adjust.svg"
        },
        {** group_base_option,
        "name": "延迟选优",
        "type": "url-test",
        "tolerance": 100,
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/speed.svg"
        },
        {** group_base_option,
        "name": "故障转移",
        "type": "fallback",
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/ambulance.svg"
        },
        {** group_base_option,
        "name": "负载均衡(散列)",
        "type": "load-balance",
        "strategy": "consistent-hashing",
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/merry_go.svg"
        },
        {** group_base_option,
        "name": "负载均衡(轮询)",
        "type": "load-balance",
        "strategy": "round-robin",
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/balance.svg"
        },
        {** group_base_option,
        "name": "谷歌服务",
        "type": "select",
        "proxies": ["节点选择", "延迟选优", "故障转移", "负载均衡(散列)", "负载均衡(轮询)", "全局直连"],
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/google.svg"
        },
        {** group_base_option,
        "name": "国外媒体",
        "type": "select",
        "proxies": ["节点选择", "延迟选优", "故障转移", "负载均衡(散列)", "负载均衡(轮询)", "全局直连"],
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/youtube.svg"
        },
        {** group_base_option,
        "name": "电报消息",
        "type": "select",
        "proxies": ["节点选择", "延迟选优", "故障转移", "负载均衡(散列)", "负载均衡(轮询)", "全局直连"],
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/telegram.svg"
        },
        {** group_base_option,
        "url": "https://chatgpt.com",
        "expected-status": "200",
        "name": "ChatGPT",
        "type": "select",
        "include-all": True,
        "filter": "AD|🇦🇩|AE|🇦🇪|AF|🇦🇫|AG|🇦🇬|AL|🇦🇱|AM|🇦🇲|AO|🇦🇴|AR|🇦🇷|AT|🇦🇹|AU|🇦🇺|AZ|🇦🇿|BA|🇧🇦|BB|🇧🇧|BD|🇧🇩|BE|🇧🇪|BF|🇧🇫|BG|🇧🇬|BH|🇧🇭|BI|🇧🇮|BJ|🇧🇯|BN|🇧🇳|BO|🇧🇴|BR|🇧🇷|BS|🇧🇸|BT|🇧🇹|BW|🇧🇼|BZ|🇧🇿|CA|🇨🇦|CD|🇨🇩|CF|🇨🇫|CG|🇨🇬|CH|🇨🇭|CI|🇨🇮|CL|🇨🇱|CM|🇨🇲|CO|🇨🇴|CR|🇨🇷|CV|🇨🇻|CY|🇨🇾|CZ|🇨🇿|DE|🇩🇪|DJ|🇩🇯|DK|🇩🇰|DM|🇩🇲|DO|🇩🇴|DZ|🇩🇿|EC|🇪🇨|EE|🇪🇪|EG|🇪🇬|ER|🇪🇷|ES|🇪🇸|ET|🇪🇹|FI|🇫🇮|FJ|🇫🇯|FM|🇫🇲|FR|🇫🇷|GA|🇬🇦|GB|🇬🇧|GD|🇬🇩|GE|🇬🇪|GH|🇬🇭|GM|🇬🇲|GN|🇬🇳|GQ|🇬🇶|GR|🇬🇷|GT|🇬🇹|GW|🇬🇼|GY|🇬🇾|HN|🇭🇳|HR|🇭🇷|HT|🇭🇹|HU|🇭🇺|ID|🇮🇩|IE|🇮🇪|IL|🇮🇱|IN|🇮🇳|IQ|🇮🇶|IS|🇮🇸|IT|🇮🇹|JM|🇯🇲|JO|🇯🇴|JP|🇯🇵|KE|🇰🇪|KG|🇰🇬|KH|🇰🇭|KI|🇰🇮|KM|🇰🇲|KN|🇰🇳|KR|🇰🇷|KW|🇰🇼|KZ|🇰🇿|LA|🇱🇦|LB|🇱🇧|LC|🇱🇨|LI|🇱🇮|LK|🇱🇰|LR|🇱🇷|LS|🇱🇸|LT|🇱🇹|LU|🇱🇺|LV|🇱🇻|LY|🇱🇾|MA|🇲🇦|MC|🇲🇨|MD|🇲🇩|ME|🇲🇪|MG|🇲🇬|MH|🇲🇭|MK|🇲🇰|ML|🇲🇱|MM|🇲🇲|MN|🇲🇳|MR|🇲🇷|MT|🇲🇹|MU|🇲🇺|MV|🇲🇻|MW|🇲🇼|MX|🇲🇽|MY|🇲🇾|MZ|🇲🇿|NA|🇳🇦|NE|🇳🇪|NG|🇳🇬|NI|🇳🇮|NL|🇳🇱|NO|🇳🇴|NP|🇳🇵|NR|🇳🇷|NZ|🇳🇿|OM|🇴🇲|PA|🇵🇦|PE|🇵🇪|PG|🇵🇬|PH|🇵🇭|PK|🇵🇰|PL|🇵🇱|PS|🇵🇸|PT|🇵🇹|PW|🇵🇼|PY|🇵🇾|QA|🇶🇦|RO|🇷🇴|RS|🇷🇸|RW|🇷🇼|SA|🇸🇦|SB|🇸🇧|SC|🇸🇨|SD|🇸🇩|SE|🇸🇪|SG|🇸🇬|SI|🇸🇮|SK|🇸🇰|SL|🇸🇱|SM|🇸🇲|SN|🇸🇳|SO|🇸🇴|SR|🇸🇷|SS|🇸🇸|ST|🇸🇹|SV|🇸🇻|SZ|🇸🇿|TD|🇹🇩|TG|🇹🇬|TH|🇹🇭|TJ|🇹🇯|TL|🇹🇱|TM|🇹🇲|TN|🇹🇳|TO|🇹🇴|TR|🇹🇷|TT|🇹🇹|TV|🇹🇻|TW|🇹🇼|TZ|🇹🇿|UA|🇺🇦|UG|🇺🇬|US|🇺🇸|UY|🇺🇾|UZ|🇺🇿|VA|🇻🇦|VC|🇻🇨|VN|🇻🇳|VU|🇻🇺|WS|🇼🇸|YE|🇾🇪|ZA|🇿🇦|ZM|🇿🇲|ZW|🇿🇼",
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/chatgpt.svg"
        },
        {** group_base_option,
        "name": "微软服务",
        "type": "select",
        "proxies": ["全局直连", "节点选择", "延迟选优", "故障转移", "负载均衡(散列)", "负载均衡(轮询)"],
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/microsoft.svg"
        },
        {** group_base_option,
        "name": "苹果服务",
        "type": "select",
        "proxies": ["节点选择", "延迟选优", "故障转移", "负载均衡(散列)", "负载均衡(轮询)", "全局直连"],
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/apple.svg"
        },
        {** group_base_option,
        "name": "广告过滤",
        "type": "select",
        "proxies": ["REJECT", "DIRECT"],
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/bug.svg"
        },
        {** group_base_option,
        "name": "全局直连",
        "type": "select",
        "proxies": ["DIRECT", "节点选择", "延迟选优", "故障转移", "负载均衡(散列)", "负载均衡(轮询)"],
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/link.svg"
        },
        {** group_base_option,
        "name": "全局拦截",
        "type": "select",
        "proxies": ["REJECT", "DIRECT"],
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/block.svg"
        },
        {** group_base_option,
        "name": "漏网之鱼",
        "type": "select",
        "proxies": ["节点选择", "延迟选优", "故障转移", "负载均衡(散列)", "负载均衡(轮询)", "全局直连"],
        "include-all": True,
        "icon": "https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/fish.svg"
        }
    ]
    
    # 修改配置
    config = original_config.copy()
    config["dns"] = dns_config
    config["proxy-groups"] = proxy_groups
    config["rule-providers"] = rule_providers
    config["rules"] = rules
    
    return config

# 读取原始配置
with open("original_config.yaml", "r", encoding="utf-8") as f:
    original_config = yaml.safe_load(f)

# 检查是否有代理节点
if not original_config.get("proxies") and not original_config.get("proxy-providers"):
    raise ValueError("配置文件中未找到任何代理")

# 处理配置
modified_config = process_config(original_config)

# 保存修改后的配置
with open("modified_config.yaml", "w", encoding="utf-8") as f:
    yaml.dump(modified_config, f, allow_unicode=True, sort_keys=False)

print("配置文件处理完成，已保存为 modified_config.yaml")
