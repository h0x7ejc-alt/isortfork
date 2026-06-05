# isort --show-config 增强功能

## 概述

本次增强为 isort 的 `--show-config` 命令添加了配置源信息，让用户能够快速识别：
- 当前生效的配置文件路径
- 使用的 profile 名称
- 是否存在运行时参数覆盖

## 新增输出内容

### config_source 字段

在 `--show-config` 的 JSON 输出中新增了 `config_source` 字段，包含以下信息：

```json
{
  "config_source": {
    "config_file": "/path/to/.isort.cfg",
    "profile": "hug",
    "has_runtime_override": false
  },
  "py_version": "py310",
  "line_length": 120,
  ...
}
```

### 字段说明

1. **config_file**: 当前正在使用的配置文件的完整路径（如 `.isort.cfg`、`pyproject.toml` 等）。仅在找到配置文件时存在。

2. **profile**: 当前正在使用的 profile 名称。仅在配置文件或命令行中指定了 profile 时存在。

3. **has_runtime_override**: 布尔值，表示是否存在通过命令行参数对配置的覆盖。

## 代码变更

主要修改在 `isort/main.py` 文件中：

1. 复制配置字典以避免修改原始对象
2. 分析 `config.sources` 属性来提取配置源信息：
   - 寻找非默认、非 profile、非运行时来源的配置文件路径
   - 识别 profile 来源
   - 检查是否有运行时覆盖
3. 将这些信息打包成 `config_source` 字典并添加到输出中
4. 使用现有的 `_preconvert` 函数（无需修改）进行 JSON 序列化

## 兼容性

- 保持 JSON 输出格式不变，向后兼容现有脚本
- 保持其他功能的完整性
- 仅在 `--show-config` 命令中添加新内容

## 示例

### 示例 1：使用配置文件

```bash
isort --show-config
```

输出会包含：
```json
{
  "config_source": {
    "config_file": "/app/isortfork/pyproject.toml",
    "profile": "hug",
    "has_runtime_override": false
  },
  ...
}
```

### 示例 2：使用运行时覆盖

```bash
isort --show-config --line-length=150
```

输出会包含：
```json
{
  "config_source": {
    "config_file": "/app/isortfork/pyproject.toml",
    "profile": "hug",
    "has_runtime_override": true
  },
  "line_length": 150,
  ...
}
```

### 示例 3：无配置文件

```bash
mkdir temp && cd temp && isort --show-config
```

输出会包含：
```json
{
  "config_source": {
    "has_runtime_override": false
  },
  ...
}
```
