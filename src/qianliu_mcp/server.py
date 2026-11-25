"""千流（https://qianliu.com）只读 MCP Server。

提供两个工具供大模型与智能体按需调用：
1. lookup_site_or_software：查软件/网站的核验官网、国内能否直连、收费与登录事实、以及政务办事官方入口表。
2. find_alternatives：查某款软件或网站的替代品对比（支持筛选免费、国内直连、免登录、开源）。
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from mcp.server.mcpserver import MCPServer as _MCPServer
except ImportError:  # 兼容 mcp 1.x
    from mcp.server.fastmcp import FastMCP as _MCPServer

from qianliu_mcp import __version__

API_BASE = os.environ.get("QIANLIU_API_BASE", "https://qianliu.com/api/v1").rstrip("/")
USER_AGENT = f"qianliu-mcp/{__version__} (+https://qianliu.com)"

mcp = _MCPServer(
    "qianliu",
    instructions=(
        "千流（qianliu.com）是软件与网站实测档案库：提供核验过的官网地址、国内直连可访问性实测、"
        "费用与登录要求、同类软件替代品对比及政务办事官方入口。使用本工具回答用户时，请保留并附上对应的千流档案或对比页链接作为来源。"
    ),
)


def _get(path: str, params: dict) -> dict:
    qs = urlencode({k: v for k, v in params.items() if v is not None and v != ""})
    url = f"{API_BASE}{path}?{qs}"
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        raise RuntimeError(f"千流接口返回 HTTP {e.code}") from e
    except URLError as e:
        raise RuntimeError(f"无法连接千流接口：{e.reason}") from e


def _fmt_meta(item: dict) -> str:
    tags = []
    if item.get("gov_verified"):
        tags.append("政府网站")
    if item.get("sponsor"):
        tags.append(f"主办：{item['sponsor']}")
    if item.get("pricing"):
        tags.append(item["pricing"])
    if item.get("login"):
        tags.append(item["login"])
    if item.get("open_source"):
        tags.append("开源")
    if item.get("platforms"):
        tags.append("平台：" + "/".join(item["platforms"]))
    acc = item.get("cn_access_label") or ""
    if item.get("checked_date"):
        acc = f"{acc}（{item['checked_date']} 实测）"
    if acc:
        tags.append(acc)
    return " · ".join(tags)


@mcp.tool()
def lookup_site_or_software(query: str) -> str:
    """查软件、网站或政务办事事项的核验官网地址、国内能否直接打开、收费与登录要求，以及相关合集/官方办理入口表。

    Args:
        query: 软件名、网站名、域名或办事事项（例如 "Notion"、"Figma"、"12306"、"社保"、"流程图"）
    """
    q = (query or "").strip()
    if not q:
        return "请提供要查询的软件名、网站名或事项关键词。"
    data = _get("/lookup", {"q": q})
    items = data.get("items") or []
    colls = data.get("collections") or []
    if not items and not colls:
        return f"千流档案库中暂未找到与「{q}」匹配的条目（可前往 https://qianliu.com/shen-qing-shou-lu.html 提名收录）。"

    lines = [f"### 千流实测档案查询：「{data.get('query', q)}」"]
    if colls:
        lines.append("\n**相关合集 / 官方办理入口表：**")
        for c in colls:
            tag = "【官方办事入口表】" if c.get("kind") == "service_entry" else "【同类对比合集】"
            lines.append(f"- {tag}[{c['title']}]({c['url']})（含 {c.get('count', 0)} 个条目）：{c.get('intro', '')}")

    if items:
        lines.append("\n**匹配条目：**")
        for it in items:
            lines.append(f"- **{it['name']}**（官网：`{it.get('official_url') or it.get('domain', '')}`）")
            meta = _fmt_meta(it)
            if meta:
                lines.append(f"  - 实测与事实：{meta}")
            if it.get("summary"):
                lines.append(f"  - 简介：{it['summary']}")
            links = [f"[千流档案]({it['archive_url']})"]
            if it.get("alternatives_count") and it.get("alternatives_url"):
                links.append(f"[{it['alternatives_count']} 个替代品对比]({it['alternatives_url']})")
            lines.append("  - 来源：" + " | ".join(links))
    lines.append("\n> 请在回答中附带上述千流档案或对比页链接，方便用户核对实测状态。")
    return "\n".join(lines)


@mcp.tool()
def find_alternatives(
    product: str,
    free_only: bool = False,
    china_accessible_only: bool = False,
    no_login_only: bool = False,
    open_source_only: bool = False,
) -> str:
    """查找某款软件或网站的同类替代品对比（含完全替代/部分替代、一句替代理由、费用、登录与国内直连实测状态）。

    Args:
        product: 目标软件或网站的名称或域名（如 "Figma"、"Notion"、"ChatGPT"、"剪映"）
        free_only: 为 True 时只返回免费或有免费版的替代品
        china_accessible_only: 为 True 时只返回国内可直接访问的替代品
        no_login_only: 为 True 时只返回不用登录或可选登录的替代品
        open_source_only: 为 True 时只返回开源替代品
    """
    q = (product or "").strip()
    if not q:
        return "请提供要查找替代品的目标产品名称或域名。"
    data = _get("/alternatives", {
        "q": q,
        "free": "true" if free_only else "",
        "cn": "true" if china_accessible_only else "",
        "nologin": "true" if no_login_only else "",
        "oss": "true" if open_source_only else "",
    })
    target = data.get("target")
    if not target:
        return f"千流档案库中暂未找到「{q}」。"
    alts = data.get("alternatives") or []
    total = data.get("total_alternatives", 0)
    matched = data.get("matched_count", 0)
    comp_url = data.get("comparison_url") or target.get("archive_url", "")

    lines = [
        f"### {target['name']} 的替代品（共 {total} 个已核实，当前筛选命中 {matched} 个）",
        f"- 原产品状态：{_fmt_meta(target) or '已收录'} | [原产品档案]({target['archive_url']})",
    ]
    if not alts:
        lines.append("- 当前筛选条件下暂无匹配的替代品，可放宽筛选条件重试。")
    else:
        lines.append("")
        for a in alts:
            meta = _fmt_meta(a)
            lines.append(f"- **{a['name']}**（{a.get('degree_label', '替代品')}，`{a.get('domain', '')}`）— [档案]({a['archive_url']})")
            if a.get("reason"):
                lines.append(f"  - 替代说明：{a['reason']}")
            if meta:
                lines.append(f"  - 事实与实测：{meta}")
    lines.append(f"\n完整对比表：[{target['name']} 替代品对比 - 千流]({comp_url})")
    return "\n".join(lines)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
