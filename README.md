# qianliu-mcp — 千流软件与网站实测档案 MCP Server

[千流（qianliu.com）](https://qianliu.com) 官方只读 MCP Server。让 Claude Desktop、Cursor、Cherry Studio、Trae、阿里云百炼等 AI 助手实时查询 **1.1 万+ 软件与网站的核验官网、国内直连可访问性实测、费用与登录要求、政务办事官方入口，以及 11 万+ 条交叉核实的同类替代品关系**。

## 解决什么问题？

大模型在回答「推荐几个免费免登录的流程图工具」「XX 官网地址是多少」「Notion 国内打不开有什么平替」时，常常编造已关停的网址，或不清楚国内网络能否直连、是否必须付费注册。

`qianliu-mcp` 直接连接千流实测档案库：
- **找真官网 & 办事入口**：核对真实官网域名、工信部备案/官方主办单位及[官方办事事项表](https://qianliu.com/collection/)；
- **查国内直连状态**：基于国内机房定期实测，区分「国内可直接访问」「国内不可直接访问」「已失联」；
- **筛靠谱替代品**：支持按 **免费/有免费版、国内直连、不用登录、开源** 组合筛选替代方案，并给出完全替代 / 部分替代说明。

## 提供的工具（Tools）

| 工具名 | 用途 |
| --- | --- |
| `lookup_site_or_software(query)` | 查询软件、网站或政务事项的官网地址、国内可访问性、收费与登录事实、相关合集/办事表 |
| `find_alternatives(product, free_only, china_accessible_only, no_login_only, open_source_only)` | 查询目标软件或网站的替代品对比清单 |

## 快速配置

### 方式一：远程 Streamable HTTP 一键直连（推荐，免安装）

千流主站已提供无状态远程 MCP 端点，无需本地安装 Python / `uv`，在 Cursor、Cherry Studio、Trae、阿里云百炼、魔搭社区或任意支持 Streamable HTTP 的 MCP 客户端中直接填入 URL 即可使用：

```text
https://qianliu.com/mcp
```

在支持 `url` 的 MCP 客户端配置（如 Cursor / Cherry Studio / Trae）中加入：

```json
{
  "mcpServers": {
    "qianliu": {
      "url": "https://qianliu.com/mcp"
    }
  }
}
```

### 方式二：本地 stdio 运行（备选）

如果所使用的客户端仅支持本地 stdio MCP，可通过 `uvx` 一行启动：

```json
{
  "mcpServers": {
    "qianliu": {
      "command": "uvx",
      "args": ["qianliu-mcp"]
    }
  }
}
```

或者使用 `pipx` / `pip` 安装后运行：

```bash
pip install qianliu-mcp
qianliu-mcp
```

## HTTP OpenAPI 接入（百炼 / 元器 / 文心 / Dify / 扣子）

除 MCP 外，云端智能体平台可直接导入 OpenAPI 3.0.1 描述地址：

```text
https://qianliu.com/api/v1/openapi.json
```

## License

MIT · 数据来源：[千流 qianliu.com](https://qianliu.com)

---

## English Overview

**qianliu-mcp** is the official read-only MCP (Model Context Protocol) server for [Qianliu (qianliu.com)](https://qianliu.com), a continuously monitored software & website archive covering **11,000+ tools/websites** and **110,000+ cross-verified software alternatives**.

### What It Does
- **`lookup_site_or_software(query)`**: Look up verified official websites, real-time China direct-access / uptime status, pricing & login requirements, and verified official public-service entry tables.
- **`find_alternatives(product, free_only, china_accessible_only, no_login_only, open_source_only)`**: Find cross-verified full/partial software alternatives with concise reasons, filtered by free tier, China direct accessibility, no-login, or open-source.

### Quick Start

**Option 1 — Remote Streamable HTTP (Recommended, zero install):**

```json
{
  "mcpServers": {
    "qianliu": {
      "url": "https://qianliu.com/mcp"
    }
  }
}
```

**Option 2 — Local stdio (`uvx`):**

```json
{
  "mcpServers": {
    "qianliu": {
      "command": "uvx",
      "args": ["qianliu-mcp"]
    }
  }
}
```

OpenAPI 3.0.1 spec for cloud agent platforms: `https://qianliu.com/api/v1/openapi.json`
