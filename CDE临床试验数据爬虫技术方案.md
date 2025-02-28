# CDE临床试验数据爬虫技术方案

## 1. 项目概述

### 1.1 项目目标
开发一个自动化爬虫程序，用于采集中国药物临床试验登记与信息公示平台（CDE）的临床试验数据。

### 1.2 数据来源
- 网站：中国药物临床试验登记与信息公示平台
- URL：http://www.chinadrugtrials.org.cn

## 2. 技术架构

### 2.1 核心技术栈
- 编程语言：Python 3.x
- 主要依赖库：
  - `undetected-chromedriver`: 反爬虫浏览器驱动
  - `selenium`: Web自动化测试框架
  - `pandas`: 数据处理和导出
  - `openpyxl`/`xlsxwriter`: Excel文件处理

### 2.2 系统架构
```
ClinicalTrialsCrawler/
├── clinical_trials_crawler.py  # 主程序
├── requirements.txt           # 依赖配置
└── data/                     # 数据存储目录
    └── clinical_trials_data_[timestamp].xlsx  # 导出数据
```

## 3. 核心功能模块

### 3.1 浏览器初始化模块
```python
def setup_driver():
    - 配置Chrome选项
    - 禁用GPU
    - 配置窗口大小
    - 初始化undetected-chromedriver
```

### 3.2 页面交互模块
- 元素等待机制
  - 显式等待
  - 超时处理
- 随机延迟策略
  - 页面间随机等待时间：2-4秒
  - 操作间隔：1-2秒

### 3.3 数据采集模块
- 数据字段：
  - 登记号
  - 机构名称
  - 试验专业题目
  - 适应症
  - 药物名称
  - 申请人名称
  - 试验分期
  - 试验状态
  - 主要研究者姓名
  - 主要研究者单位

### 3.4 数据存储模块
- 支持多种格式：
  - Excel (主要格式)
    - openpyxl引擎
    - xlsxwriter引擎（备选）
  - CSV (备选格式)
    - UTF-8-SIG编码
    - 支持中文

## 4. 反爬虫策略

### 4.1 浏览器伪装
- 使用undetected-chromedriver
- 禁用自动化特征
- 自定义窗口大小

### 4.2 请求控制
- 随机等待时间
- 模拟人工操作间隔
- 异常重试机制

### 4.3 错误处理
- 页面加载超时处理
- 元素查找异常处理
- 数据解析异常处理
- 自动重试机制

## 5. 性能优化

### 5.1 爬取策略
- 单线程顺序爬取
- 支持断点续爬
- 可配置爬取页数

### 5.2 资源管理
- 浏览器实例管理
- 内存数据定期保存
- 安全退出机制

## 6. 数据导出

### 6.1 文件命名规则
```
clinical_trials_data_[YYYYMMDDHHMMSS]_[maxCount].xlsx
```

### 6.2 导出格式
- 主要格式：Excel（.xlsx）
- 备选格式：CSV（UTF-8-SIG）
- 自动容错机制

## 7. 使用说明

### 7.1 环境要求
- Python 3.x
- Chrome浏览器
- 相关Python包依赖

### 7.2 安装步骤
```bash
pip install -r requirements.txt
```

### 7.3 运行方式
```bash
python clinical_trials_crawler.py
```

### 7.4 配置参数
- start_page: 起始页码
- max_pages: 最大爬取页数
- 超时时间：5秒
- 随机延迟：2-4秒

## 8. 注意事项

### 8.1 运行环境
- 确保网络稳定
- 安装所有必要依赖
- Chrome浏览器版本兼容性

### 8.2 异常处理
- 网络异常自动重试
- 数据保存多重保障
- 程序异常安全退出

### 8.3 数据质量
- 数据完整性检查
- 字段格式验证
- 导出格式兼容性

## 9. 维护建议

### 9.1 定期维护
- 更新依赖版本
- 检查网站结构变化
- 优化爬取策略

### 9.2 性能监控
- 爬取速度监控
- 成功率统计
- 异常情况记录 