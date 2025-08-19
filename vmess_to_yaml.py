#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
import sys
import re
import os

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

def decode_vmess_link(vmess_link):
    """解码vmess链接为JSON对象"""
    if not vmess_link.startswith('vmess://'):
        raise ValueError("不是有效的vmess链接")
    
    # 移除vmess://前缀并解码base64
    encoded_content = vmess_link.replace('vmess://', '')
    try:
        decoded_content = base64.b64decode(encoded_content).decode('utf-8')
        return json.loads(decoded_content)
    except Exception as e:
        raise ValueError(f"解码vmess链接失败: {e}")

def vmess_to_clash_config(vmess_data):
    """将vmess数据转换为Clash配置格式"""
    # 基本配置
    clash_config = {
        'name': vmess_data.get('ps', 'Unknown'),
        'type': 'vmess',
        'server': vmess_data.get('add', ''),
        'port': int(vmess_data.get('port', 0)),
        'cipher': vmess_data.get('scy', 'auto'),
        'uuid': vmess_data.get('id', ''),
        'alterId': int(vmess_data.get('aid', 0)),
        'tls': vmess_data.get('tls', '') == 'tls',
        'skip-cert-verify': True,
    }
    
    # 处理网络类型
    network = vmess_data.get('net', '')
    if network:
        clash_config['network'] = network
    
    # 处理ws配置
    if network == 'ws':
        ws_opts = {
            'path': vmess_data.get('path', '/')
        }
        
        # 添加headers如果存在
        if vmess_data.get('host'):
            ws_opts['headers'] = {
                'host': vmess_data.get('host')
            }
        
        clash_config['ws-opts'] = ws_opts
    
    # 处理h2配置
    elif network == 'h2':
        h2_opts = {
            'path': vmess_data.get('path', '/')
        }
        
        # 添加host如果存在
        if vmess_data.get('host'):
            h2_opts['host'] = [vmess_data.get('host')]
        
        clash_config['h2-opts'] = h2_opts
    
    # 处理http配置
    elif network == 'http':
        http_opts = {
            'path': [vmess_data.get('path', '/')]
        }
        
        # 添加headers如果存在
        if vmess_data.get('host'):
            http_opts['headers'] = {
                'host': [vmess_data.get('host')]
            }
        
        clash_config['http-opts'] = http_opts
    
    # 处理grpc配置
    elif network == 'grpc':
        grpc_opts = {
            'service-name': vmess_data.get('path', '')
        }
        clash_config['grpc-opts'] = grpc_opts
    
    # 处理TLS相关配置
    if clash_config['tls']:
        # 如果有SNI设置
        if vmess_data.get('sni'):
            clash_config['servername'] = vmess_data.get('sni')
        elif vmess_data.get('host'):
            clash_config['servername'] = vmess_data.get('host')
    
    return clash_config

def process_vmess_links(input_text):
    """处理多行vmess链接文本"""
    # 使用正则表达式匹配vmess链接
    vmess_links = re.findall(r'vmess://[A-Za-z0-9+/=]+', input_text)
    
    if not vmess_links:
        print("未找到有效的vmess链接")
        return []
    
    proxies = []
    for link in vmess_links:
        try:
            vmess_data = decode_vmess_link(link)
            clash_config = vmess_to_clash_config(vmess_data)
            proxies.append(clash_config)
            print(f"成功转换: {clash_config['name']}")
        except Exception as e:
            print(f"转换失败: {e}")
    
    return proxies

def generate_clash_config(proxies, output_file='modified_config.yaml'):
    """生成完整的Clash配置文件"""
    # 读取现有配置文件作为模板（如果存在）
    template_file = 'modified_config.yaml'
    if os.path.exists(template_file):
        with open(template_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        # 创建基本配置
        config = {
            'mixed-port': 7890,
            'allow-lan': True,
            'log-level': 'info',
            'external-controller': '0.0.0.0:9090',
            'dns': {
                'enable': True,
                'listen': '0.0.0.0:1053',
                'ipv6': True,
                'use-system-hosts': False,
                'cache-algorithm': 'arc',
                'enhanced-mode': 'fake-ip',
                'fake-ip-range': '198.18.0.1/16',
                'fake-ip-filter': [
                    '+.lan',
                    '+.local',
                    '+.msftconnecttest.com',
                    '+.msftncsi.com',
                    'localhost.ptlogin2.qq.com',
                    'localhost.sec.qq.com',
                    'localhost.work.weixin.qq.com'
                ],
                'default-nameserver': [
                    '223.5.5.5',
                    '119.29.29.29',
                    '1.1.1.1',
                    '8.8.8.8'
                ],
                'nameserver': [
                    'https://dns.alidns.com/dns-query',
                    'https://doh.pub/dns-query',
                    'https://doh.360.cn/dns-query',
                    'https://1.1.1.1/dns-query',
                    'https://1.0.0.1/dns-query',
                    'https://208.67.222.222/dns-query',
                    'https://208.67.220.220/dns-query',
                    'https://194.242.2.2/dns-query',
                    'https://194.242.2.3/dns-query'
                ],
                'proxy-server-nameserver': [
                    'https://dns.alidns.com/dns-query',
                    'https://doh.pub/dns-query',
                    'https://doh.360.cn/dns-query',
                    'https://1.1.1.1/dns-query',
                    'https://1.0.0.1/dns-query',
                    'https://208.67.222.222/dns-query',
                    'https://208.67.220.220/dns-query',
                    'https://194.242.2.2/dns-query',
                    'https://194.242.2.3/dns-query'
                ],
                'nameserver-policy': {
                    'geosite:private,cn,geolocation-cn': [
                        'https://dns.alidns.com/dns-query',
                        'https://doh.pub/dns-query',
                        'https://doh.360.cn/dns-query'
                    ],
                    'geosite:google,youtube,telegram,gfw,geolocation-!cn': [
                        'https://1.1.1.1/dns-query',
                        'https://1.0.0.1/dns-query',
                        'https://208.67.222.222/dns-query',
                        'https://208.67.220.220/dns-query',
                        'https://194.242.2.2/dns-query',
                        'https://194.242.2.3/dns-query'
                    ]
                }
            }
        }
    
    # 更新代理列表，保留现有代理并添加新代理
    existing_proxies = config.get('proxies', [])
    existing_names = {proxy['name'] for proxy in existing_proxies}
    
    # 只添加不重复的新代理
    new_proxies = []
    for proxy in proxies:
        if proxy['name'] not in existing_names:
            new_proxies.append(proxy)
            existing_names.add(proxy['name'])
    
    # 合并代理列表
    config['proxies'] = existing_proxies + new_proxies
    
    # 自动生成代理组
    proxy_names = [proxy['name'] for proxy in config['proxies']]
    
    # 创建或更新代理组
    if 'proxy-groups' not in config:
        config['proxy-groups'] = []
    
    # 检查是否已存在节点选择组
    select_group_exists = False
    for group in config.get('proxy-groups', []):
        if group.get('name') == '节点选择':
            # 保留原有的基本代理组
            group['proxies'] = ['延迟选优', '故障转移', '负载均衡(散列)', '负载均衡(轮询)']
            group['include-all'] = True
            select_group_exists = True
            break
    
    if not select_group_exists:
        config['proxy-groups'].append({
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '节点选择',
            'type': 'select',
            'proxies': ['延迟选优', '故障转移', '负载均衡(散列)', '负载均衡(轮询)'],
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/adjust.svg'
        })
    
    # 检查是否已存在延迟选优组
    url_test_group_exists = False
    for group in config.get('proxy-groups', []):
        if group.get('name') == '延迟选优':
            group['include-all'] = True
            url_test_group_exists = True
            break
    
    if not url_test_group_exists:
        config['proxy-groups'].append({
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '延迟选优',
            'type': 'url-test',
            'tolerance': 100,
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/speed.svg'
        })
    
    # 检查是否已存在故障转移组
    fallback_group_exists = False
    for group in config.get('proxy-groups', []):
        if group.get('name') == '故障转移':
            group['include-all'] = True
            fallback_group_exists = True
            break
    
    if not fallback_group_exists:
        config['proxy-groups'].append({
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '故障转移',
            'type': 'fallback',
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/ambulance.svg'
        })
    
    # 检查是否已存在负载均衡(散列)组
    load_balance_hash_group_exists = False
    for group in config.get('proxy-groups', []):
        if group.get('name') == '负载均衡(散列)':
            group['include-all'] = True
            load_balance_hash_group_exists = True
            break
    
    if not load_balance_hash_group_exists:
        config['proxy-groups'].append({
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '负载均衡(散列)',
            'type': 'load-balance',
            'strategy': 'consistent-hashing',
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/merry_go.svg'
        })
    
    # 检查是否已存在负载均衡(轮询)组
    load_balance_round_group_exists = False
    for group in config.get('proxy-groups', []):
        if group.get('name') == '负载均衡(轮询)':
            group['include-all'] = True
            load_balance_round_group_exists = True
            break
    
    if not load_balance_round_group_exists:
        config['proxy-groups'].append({
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '负载均衡(轮询)',
            'type': 'load-balance',
            'strategy': 'round-robin',
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/balance.svg'
        })
    
    # 添加更多代理组
    proxy_groups = [
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '谷歌服务',
            'type': 'select',
            'proxies': ['节点选择', '延迟选优', '故障转移', '负载均衡(散列)', '负载均衡(轮询)', '全局直连'],
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/google.svg'
        },
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '国外媒体',
            'type': 'select',
            'proxies': ['节点选择', '延迟选优', '故障转移', '负载均衡(散列)', '负载均衡(轮询)', '全局直连'],
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/youtube.svg'
        },
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '电报消息',
            'type': 'select',
            'proxies': ['节点选择', '延迟选优', '故障转移', '负载均衡(散列)', '负载均衡(轮询)', '全局直连'],
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/telegram.svg'
        },
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://chatgpt.com',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'expected-status': '200',
            'name': 'ChatGPT',
            'type': 'select',
            'include-all': True,
            'filter': 'AD|🇦🇩|AE|🇦🇪|AF|🇦🇫|AG|🇦🇬|AL|🇦🇱|AM|🇦🇲|AO|🇦🇴|AR|🇦🇷|AT|🇦🇹|AU|🇦🇺|AZ|🇦🇿|BA|🇧🇦|BB|🇧🇧|BD|🇧🇩|BE|🇧🇪|BF|🇧🇫|BG|🇧🇬|BH|🇧🇭|BI|🇧🇮|BJ|🇧🇯|BN|🇧🇳|BO|🇧🇴|BR|🇧🇷|BS|🇧🇸|BT|🇧🇹|BW|🇧🇼|BZ|🇧🇿|CA|🇨🇦|CD|🇨🇩|CF|🇨🇫|CG|🇨🇬|CH|🇨🇭|CI|🇨🇮|CL|🇨🇱|CM|🇨🇲|CO|🇨🇴|CR|🇨🇷|CV|🇨🇻|CY|🇨🇾|CZ|🇨🇿|DE|🇩🇪|DJ|🇩🇯|DK|🇩🇰|DM|🇩🇲|DO|🇩🇴|DZ|🇩🇿|EC|🇪🇨|EE|🇪🇪|EG|🇪🇬|ER|🇪🇷|ES|🇪🇸|ET|🇪🇹|FI|🇫🇮|FJ|🇫🇯|FM|🇫🇲|FR|🇫🇷|GA|🇬🇦|GB|🇬🇧|GD|🇬🇩|GE|🇬🇪|GH|🇬🇭|GM|🇬🇲|GN|🇬🇳|GQ|🇬🇶|GR|🇬🇷|GT|🇬🇹|GW|🇬🇼|GY|🇬🇾|HN|🇭🇳|HR|🇭🇷|HT|🇭🇹|HU|🇭🇺|ID|🇮🇩|IE|🇮🇪|IL|🇮🇱|IN|🇮🇳|IQ|🇮🇶|IS|🇮🇸|IT|🇮🇹|JM|🇯🇲|JO|🇯🇴|JP|🇯🇵|KE|🇰🇪|KG|🇰🇬|KH|🇰🇭|KI|🇰🇮|KM|🇰🇲|KN|🇰🇳|KR|🇰🇷|KW|🇰🇼|KZ|🇰🇿|LA|🇱🇦|LB|🇱🇧|LC|🇱🇨|LI|🇱🇮|LK|🇱🇰|LR|🇱🇷|LS|🇱🇸|LT|🇱🇹|LU|🇱🇺|LV|🇱🇻|LY|🇱🇾|MA|🇲🇦|MC|🇲🇨|MD|🇲🇩|ME|🇲🇪|MG|🇲🇬|MH|🇲🇭|MK|🇲🇰|ML|🇲🇱|MM|🇲🇲|MN|🇲🇳|MR|🇲🇷|MT|🇲🇹|MU|🇲🇺|MV|🇲🇻|MW|🇲🇼|MX|🇲🇽|MY|🇲🇾|MZ|🇲🇿|NA|🇳🇦|NE|🇳🇪|NG|🇳🇬|NI|🇳🇮|NL|🇳🇱|NO|🇳🇴|NP|🇳🇵|NR|🇳🇷|NZ|🇳🇿|OM|🇴🇲|PA|🇵🇦|PE|🇵🇪|PG|🇵🇬|PH|🇵🇭|PK|🇵🇰|PL|🇵🇱|PS|🇵🇸|PT|🇵🇹|PW|🇵🇼|PY|🇵🇾|QA|🇶🇦|RO|🇷🇴|RS|🇷🇸|RW|🇷🇼|SA|🇸🇦|SB|🇸🇧|SC|🇸🇨|SD|🇸🇩|SE|🇸🇪|SG|🇸🇬|SI|🇸🇮|SK|🇸🇰|SL|🇸🇱|SM|🇸🇲|SN|🇸🇳|SO|🇸🇴|SR|🇸🇷|SS|🇸🇸|ST|🇸🇹|SV|🇸🇻|SZ|🇸🇿|TD|🇹🇩|TG|🇹🇬|TH|🇹🇭|TJ|🇹🇯|TL|🇹🇱|TM|🇹🇲|TN|🇹🇳|TO|🇹🇴|TR|🇹🇷|TT|🇹🇹|TV|🇹🇻|TW|🇹🇼|TZ|🇹🇿|UA|🇺🇦|UG|🇺🇬|US|🇺🇸|UY|🇺🇾|UZ|🇺🇿|VA|🇻🇦|VC|🇻🇨|VN|🇻🇳|VU|🇻🇺|WS|🇼🇸|YE|🇾🇪|ZA|🇿🇦|ZM|🇿🇲|ZW|🇿🇼',
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/chatgpt.svg'
        },
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '微软服务',
            'type': 'select',
            'proxies': ['全局直连', '节点选择', '延迟选优', '故障转移', '负载均衡(散列)', '负载均衡(轮询)'],
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/microsoft.svg'
        },
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '苹果服务',
            'type': 'select',
            'proxies': ['节点选择', '延迟选优', '故障转移', '负载均衡(散列)', '负载均衡(轮询)', '全局直连'],
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/apple.svg'
        },
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '广告过滤',
            'type': 'select',
            'proxies': ['REJECT', 'DIRECT'],
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/bug.svg'
        },
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '全局直连',
            'type': 'select',
            'proxies': ['DIRECT', '节点选择', '延迟选优', '故障转移', '负载均衡(散列)', '负载均衡(轮询)'],
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/link.svg'
        },
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '全局拦截',
            'type': 'select',
            'proxies': ['REJECT', 'DIRECT'],
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/block.svg'
        },
        {
            'interval': 300,
            'timeout': 3000,
            'url': 'https://www.google.com/generate_204',
            'lazy': True,
            'max-failed-times': 3,
            'hidden': False,
            'name': '漏网之鱼',
            'type': 'select',
            'proxies': ['节点选择', '延迟选优', '故障转移', '负载均衡(散列)', '负载均衡(轮询)', '全局直连'],
            'include-all': True,
            'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/fish.svg'
        }
    ]
    
    # 添加新的代理组，避免重复
    for new_group in proxy_groups:
        exists = False
        for group in config.get('proxy-groups', []):
            if group.get('name') == new_group['name']:
                exists = True
                break
        if not exists:
            config['proxy-groups'].append(new_group)
    
    # 添加规则集
    if 'rules' not in config:
        config['rules'] = [
            'DOMAIN-SUFFIX,googleapis.cn,节点选择',
            'DOMAIN-SUFFIX,gstatic.com,节点选择',
            'DOMAIN-SUFFIX,xn--ngstr-lra8j.com,节点选择',
            'DOMAIN-SUFFIX,github.io,节点选择',
            'DOMAIN,v2rayse.com,节点选择',
            'RULE-SET,openai,ChatGPT',
            'RULE-SET,applications,全局直连',
            'RULE-SET,private,全局直连',
            'RULE-SET,reject,广告过滤',
            'RULE-SET,icloud,微软服务',
            'RULE-SET,apple,苹果服务',
            'RULE-SET,google,谷歌服务',
            'RULE-SET,proxy,节点选择',
            'RULE-SET,gfw,节点选择',
            'RULE-SET,tld-not-cn,节点选择',
            'RULE-SET,direct,全局直连',
            'RULE-SET,lancidr,全局直连,no-resolve',
            'RULE-SET,cncidr,全局直连,no-resolve',
            'RULE-SET,telegramcidr,电报消息,no-resolve',
            'GEOIP,LAN,全局直连,no-resolve',
            'GEOIP,CN,全局直连,no-resolve',
            'MATCH,漏网之鱼'
        ]
        
    # 添加规则提供者
    if 'rule-providers' not in config:
        config['rule-providers'] = {
            'reject': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'domain',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt',
                'path': './ruleset/loyalsoldier/reject.yaml'
            },
            'icloud': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'domain',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/icloud.txt',
                'path': './ruleset/loyalsoldier/icloud.yaml'
            },
            'apple': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'domain',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/apple.txt',
                'path': './ruleset/loyalsoldier/apple.yaml'
            },
            'google': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'domain',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/google.txt',
                'path': './ruleset/loyalsoldier/google.yaml'
            },
            'proxy': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'domain',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt',
                'path': './ruleset/loyalsoldier/proxy.yaml'
            },
            'direct': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'domain',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt',
                'path': './ruleset/loyalsoldier/direct.yaml'
            },
            'private': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'domain',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt',
                'path': './ruleset/loyalsoldier/private.yaml'
            },
            'gfw': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'domain',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/gfw.txt',
                'path': './ruleset/loyalsoldier/gfw.yaml'
            },
            'tld-not-cn': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'domain',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/tld-not-cn.txt',
                'path': './ruleset/loyalsoldier/tld-not-cn.yaml'
            },
            'telegramcidr': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'ipcidr',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt',
                'path': './ruleset/loyalsoldier/telegramcidr.yaml'
            },
            'cncidr': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'ipcidr',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/cncidr.txt',
                'path': './ruleset/loyalsoldier/cncidr.yaml'
            },
            'lancidr': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'ipcidr',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt',
                'path': './ruleset/loyalsoldier/lancidr.yaml'
            },
            'applications': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'classical',
                'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/applications.txt',
                'path': './ruleset/loyalsoldier/applications.yaml'
            },
            'openai': {
                'type': 'http',
                'format': 'yaml',
                'interval': 86400,
                'behavior': 'classical',
                'url': 'https://fastly.jsdelivr.net/gh/blackmatrix7/ios_rule_script@master/rule/Clash/OpenAI/OpenAI.yaml',
                'path': './ruleset/blackmatrix7/openai.yaml'
            }
        }
    
    # 写入配置文件
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    
    print(f"配置已保存到 {output_file}")

def main():
    """主函数"""
    try:
        if len(sys.argv) > 1:
            # 从文件读取
            input_file = sys.argv[1]
            try:
                with open(input_file, 'r') as f:
                    input_text = f.read()
            except FileNotFoundError:
                print(f"错误: 找不到文件 '{input_file}'")
                print_usage()
                return
            except Exception as e:
                print(f"读取文件时出错: {e}")
                return
        else:
            # 从标准输入读取
            print("请粘贴vmess链接，完成后按Ctrl+D (Unix/Linux/Mac) 或 Ctrl+Z (Windows):")
            input_text = sys.stdin.read()
        
        proxies = process_vmess_links(input_text)
        
        if proxies:
            output_file = 'modified_config.yaml'
            if len(sys.argv) > 2:
                output_file = sys.argv[2]
            
            generate_clash_config(proxies, output_file)
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"发生错误: {e}")
        print_usage()

def print_usage():
    """打印使用说明"""
    print("\n使用方法:")
    print("  1. 直接运行: ./vmess_to_yaml.py")
    print("     然后粘贴vmess链接，完成后按Ctrl+D (Mac/Linux) 或 Ctrl+Z (Windows)")
    print("  2. 从文件读取: ./vmess_to_yaml.py input.txt")
    print("  3. 指定输出文件: ./vmess_to_yaml.py input.txt custom_config.yaml")
    print("\n配置文件说明:")
    print("  - 生成的配置文件包含完整的Clash配置，包括代理、代理组和规则")
    print("  - 自动创建多个代理组：自动选择、手动选择、国外网站、电报消息等")
    print("  - 包含常用规则集，可以直接导入到Clash使用")
    print("  - 如果已有配置文件，会保留原有设置并更新代理列表")
    print("\n注意事项:")
    print("  - 确保vmess链接格式正确")
    print("  - 如果遇到导入问题，请检查生成的YAML文件格式")

if __name__ == "__main__":
    # 检查是否有命令行参数指示这是重启后的运行
    restart_flag = "--after-pip-install" in sys.argv
    if restart_flag:
        # 移除重启标志
        sys.argv.remove("--after-pip-install")
    
    # 如果yaml导入失败但pip安装成功，尝试使用子进程方式运行
    if "yaml" not in sys.modules and not restart_flag:
        try:
            print("尝试使用子进程方式运行...")
            cmd = [sys.executable] + sys.argv + ["--after-pip-install"]
            result = subprocess.run(cmd, check=True)
            sys.exit(result.returncode)
        except Exception as e:
            print(f"子进程运行失败: {e}")
    
    main()