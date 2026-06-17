"""
ARA - PDF Export Service
"""
import re
import logging
from datetime import datetime
from jinja2 import Environment, BaseLoader
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)

PDF_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>{{ title }}</title>
<style>
@page { size: A4; margin: 2.5cm 2cm; }
body { font-family: "Noto Sans CJK SC","WenQuanYi Micro Hei",sans-serif; font-size: 11pt; line-height: 1.8; color: #1a1a2e; }
.header { text-align: center; border-bottom: 2px solid #6366f1; padding-bottom: 16px; margin-bottom: 24px; }
.header h1 { font-size: 22pt; margin: 0 0 8px; }
.header .meta { font-size: 10pt; color: #6b7280; }
h2 { font-size: 14pt; color: #6366f1; border-left: 4px solid #6366f1; padding-left: 10px; margin: 16px 0 10px; }
p { margin: 6px 0; text-align: justify; }
ul { margin: 6px 0; padding-left: 24px; }
li { margin: 4px 0; }
.footer { text-align: center; font-size: 9pt; color: #9ca3af; margin-top: 40px; border-top: 1px solid #e5e7eb; padding-top: 12px; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 9pt; font-weight: 600; margin-right: 6px; }
.badge-intent { background: #e0e7ff; color: #4338ca; }
.badge-depth { background: #fef3c7; color: #b45309; }
.cover-info { background: #f8fafc; border-radius: 8px; padding: 16px; margin: 16px 0; }
.cover-info p { margin: 4px 0; font-size: 10pt; color: #4b5563; }
</style></head>
<body>
<div class="header"><h1>{{ title }}</h1><div class="meta">ARA - Adaptive Reality Agent | {{ date }}</div></div>
<div class="cover-info">
<p><strong>分析意图：</strong><span class="badge badge-intent">{{ intent }}</span></p>
<p><strong>分析深度：</strong><span class="badge badge-depth">{{ depth }}</span></p>
<p><strong>字数范围：</strong>{{ word_range }}</p>
<p><strong>生成时间：</strong>{{ date }}</p>
</div>
<hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;">
<div class="content">{{ content_html }}</div>
<div class="footer">由 ARA 生成 | ara.chmjk67.top</div>
</body></html>"""

def markdown_to_html(text: str) -> str:
    html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = re.sub(r"【([^】]+)】", r"<h2></h2>", html)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong></strong>", html)
    lines = html.split("\n")
    result = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("• "):
            if not in_list:
                result.append("<ul>")
                in_list = True
            result.append(f"<li>{stripped[2:]}</li>")
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            if stripped:
                result.append(f"<p>{line}</p>")
    if in_list:
        result.append("</ul>")
    return "\n".join(result)

def generate_pdf(title: str, content: str, intent: str = "Reality", depth: str = "Level1", word_range: str = "300~800字") -> bytes:
    env = Environment(loader=BaseLoader())
    template = env.from_string(PDF_TEMPLATE)
    html_str = template.render(
        title=title, content_html=markdown_to_html(content),
        intent=intent, depth=depth, word_range=word_range,
        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    font_config = FontConfiguration()
    pdf_bytes = HTML(string=html_str).write_pdf(font_config=font_config)
    logger.info(f"PDF generated: {len(pdf_bytes)} bytes")
    return pdf_bytes
