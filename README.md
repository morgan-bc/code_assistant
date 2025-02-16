## 代码注释质量分析系统
### 系统架构设计

```
代码解析层
├─ 增量扫描模块（暂未实现）
├─ 多语言解析器 pygments 找出所有注释代码
↓
注释分析层
├─ 规则引擎
│   ├─ 长度检测（长度小于5的注释）
│   ├─ 重复检测（注释文本相似度>0.9）
├─ AI分析模块（Azure OpenAI / modelscope）
│   ├─ 利用 CoT 对注释进行评估
│   └─ 低质量注释分类和修改建议
↓
结果展示层
├─ 输出HTML报告
```

### 核心组件说明
#### 注释提取器
- 功能：从代码仓库中提取出所有的注释。
- 实现：使用正则表达式或AST解析器来提取注释。
- 输入：代码文件或目录、需要检测的语言
- 输出：所有的注释、注释所在行以及注释相关的代码

#### 注释质量评估引擎
- 功能：对提取出的注释进行质量评估。
- 规则引擎：长度检测、重复检测。重复检查使用 `TfidfVectorizer` 计算注释相似度.
- AI分析模块：结合CoT，使用大模型对注释进行评估，并给出修改建议和备选的修改注释
- 输入：注释提取器的输出
- 输出：评估结果、改进建议


### 工程化实现方案
- 语言：Python 3.10
- 大模型服务提供商：Azure OpenAI 或者 modelscope
- 大模型： gpt-turbo-3.5, Qwen2.5-72B

### 输出报告示例
[math_utils.py](example/math_utils.py.html)

## 使用方法
1. 安装依赖
```
python setup.py develop
```
2. 设置环境变量

```
export AZURE_ENDPOINT="",
export AZURE_OPENAI_API_KEY=""
export MODELSCOPE_API_KEY=""
```
3. 运行
```
comment_analyzer -i "D:\Github\autogen-0.2.38\autogen\runtime_logging.py" -o .\output\ --llm-provider azure_openai
```
