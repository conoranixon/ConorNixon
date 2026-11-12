"""Render the chaos report markdown to a styled PDF with embedded figures."""
import re
import markdown
from weasyprint import HTML

SRC = '/cursor/stores/bc-0959e656-639f-4f36-9cde-b9d3406f110a/docs/europa-chaos-subtypes-report.md'
OUT = '/cursor/stores/bc-0959e656-639f-4f36-9cde-b9d3406f110a/docs/europa-chaos-subtypes-report.pdf'

text = open(SRC).read()
text = re.sub(r'^---\ncursor:.*?---\n', '', text, flags=re.S)  # strip frontmatter

body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'smarty'])

css = """
@page { size: A4; margin: 2.1cm 1.9cm;
  @bottom-center { content: counter(page) " / " counter(pages);
                   font-size: 8.5pt; color: #777; } }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 9.6pt;
       line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 17pt; line-height: 1.25; border-bottom: 2px solid #2b5a8a;
     padding-bottom: 6px; color: #17344f; }
h2 { font-size: 13pt; color: #17344f; margin-top: 1.4em;
     border-bottom: 1px solid #c8d4de; padding-bottom: 3px; }
h3 { font-size: 11pt; color: #2b5a8a; }
img { max-width: 100%; margin: 10px auto; display: block; }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt;
        margin: 10px 0; }
th, td { border: 1px solid #b9c4cd; padding: 4px 6px; text-align: left;
         vertical-align: top; }
th { background: #e8eef3; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.6pt;
       background: #f0f2f4; padding: 0 2px; border-radius: 2px; }
blockquote { border-left: 3px solid #c8d4de; margin-left: 0;
             padding-left: 12px; color: #444; }
strong { color: #000; }
li { margin: 2.5px 0; }
"""

html = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
HTML(string=html, base_url='/').write_pdf(OUT)
print("wrote", OUT)
