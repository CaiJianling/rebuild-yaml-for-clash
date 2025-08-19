# Clash YAML 配置工具

这个项目提供了一套工具，用于创建、修改和优化 Clash 代理软件的配置文件。主要功能包括从 vmess 链接生成 Clash 配置以及优化现有 Clash 配置文件。

## 功能特点

- **vmess 链接转换**：将 vmess 链接转换为 Clash 可用的配置格式
- **配置文件优化**：优化 DNS 设置、代理规则和分流策略
- **自动依赖安装**：自动检测并安装所需的 Python 依赖
- **批量处理**：支持批量处理多个 vmess 链接

## 安装要求

- Python 3.6+
- PyYAML 库

## 安装

1. 克隆此仓库：

```bash
git clone https://github.com/yourusername/rebuild-yaml-for-clash.git
cd rebuild-yaml-for-clash
```

2. 安装依赖：

```bash
pip install -r requirement.txt
```

## 使用方法

### vmess 链接转 Clash 配置

有三种方式使用 vmess 转换工具：

1. **直接运行并粘贴链接**：
   ```bash
   python vmess_to_yaml.py
   ```
   然后粘贴 vmess 链接，完成后按 Ctrl+D (Mac/Linux) 或 Ctrl+Z (Windows)

2. **从文件读取链接**：
   ```bash
   python vmess_to_yaml.py input.txt
   ```
   其中 `input.txt` 包含一行或多行 vmess 链接

3. **指定输出文件**：
   ```bash
   python vmess_to_yaml.py input.txt custom_config.yaml
   ```

转换后的配置将默认保存为 `modified_config.yaml`（除非指定了其他输出文件名）。

### 优化现有 Clash 配置

```bash
python rebuild_yaml.py
```

此脚本将读取 `original_config.yaml` 并生成优化后的 `modified_config.yaml`。
**注意**：使用此脚本前，请确保 `original_config.yaml` 文件中已包含代理节点信息。

## 配置特点

优化后的配置包含以下特点：

- 优化的 DNS 设置，包括国内外 DNS 分流
- 预配置的规则集，包括常用网站和应用的分流规则
- 增强的隐私保护设置
- 自动选择最佳代理节点的策略组

## 文件说明

- `vmess_to_yaml.py`: vmess 链接转 Clash 配置工具
- `rebuild_yaml.py`: Clash 配置优化工具
- `input.txt`: 存放 vmess 链接的输入文件
- `original_config.yaml`: 原始 Clash 配置文件
- `modified_config.yaml`: 生成的优化配置文件
- `config.js`: 配置模板文件

## 注意事项

- 本工具仅用于学习和研究网络代理技术
- 请遵守当地法律法规使用网络代理服务
- 配置文件中的敏感信息（如服务器地址、密码等）会被自动处理，但仍建议谨慎分享

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

[MIT License](LICENSE)