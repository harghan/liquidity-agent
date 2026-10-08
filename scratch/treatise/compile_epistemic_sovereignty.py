import os
import markdown
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

VOLUMES = [
    "/Users/harshaghandikota/Liquidity Agent/docs/treatise/vol1.md",
    "/Users/harshaghandikota/Liquidity Agent/docs/treatise/vol2.md",
    "/Users/harshaghandikota/Liquidity Agent/docs/treatise/vol3.md",
    "/Users/harshaghandikota/Liquidity Agent/docs/treatise/vol4.md",
    "/Users/harshaghandikota/Liquidity Agent/docs/treatise/vol5.md",
]

MD_OUT = "/Users/harshaghandikota/Liquidity Agent/docs/treatise/EPISTEMIC_SOVEREIGNTY.md"
HTML_OUT = "/Users/harshaghandikota/Liquidity Agent/docs/treatise/EPISTEMIC_SOVEREIGNTY.html"
DOCX_OUT = "/Users/harshaghandikota/Liquidity Agent/docs/treatise/EPISTEMIC_SOVEREIGNTY.docx"
PDF_OUT = "/Users/harshaghandikota/Liquidity Agent/docs/treatise/EPISTEMIC_SOVEREIGNTY.pdf"

def assemble_master_markdown():
    full_text = []
    full_text.append("# EPISTEMIC SOVEREIGNTY\n")
    full_text.append("## On Market Microstructure, the Collapse of Consensus Reality, and the Autonomous Liquidity Architecture of Macro Civilization\n\n")
    full_text.append("**By Harsha Ghandikota**  \n*PRISM Liquidity Systems — Quantitative Systems & Civilization Architecture*  \n*October 2026*\n\n---\n\n")
    
    for v_path in VOLUMES:
        if os.path.exists(v_path):
            with open(v_path, "r", encoding="utf-8") as f:
                content = f.read()
                full_text.append(content)
                full_text.append("\n\n---\n\n")
    
    combined = "\n".join(full_text)
    with open(MD_OUT, "w", encoding="utf-8") as f:
        f.write(combined)
    print(f"Master markdown assembled at: {MD_OUT}")
    return combined

def assemble_master_html():
    with open(MD_OUT, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # World-class research lab publication styling (DeepMind / Leopold / Stripe Press standard)
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>EPISTEMIC SOVEREIGNTY — PRISM Liquidity Systems</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;800&family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<style>
  @page {{
    size: letter;
    margin: 1.1in 0.95in 1.1in 0.95in;
    @top-right {{
      content: "PRISM LIQUIDITY SYSTEMS  |  EPISTEMIC SOVEREIGNTY";
      font-family: 'Inter', sans-serif;
      font-size: 7pt;
      font-weight: 600;
      letter-spacing: 0.12em;
      color: #94a3b8;
      text-transform: uppercase;
    }}
    @bottom-center {{
      content: counter(page);
      font-family: 'EB Garamond', Georgia, serif;
      font-size: 9.5pt;
      color: #64748b;
    }}
  }}

  *, *::before, *::after {{
    box-sizing: border-box;
  }}

  body {{
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 11.2pt;
    line-height: 1.62;
    color: #1e293b;
    background-color: #ffffff;
    max-width: 820px;
    margin: 0 auto;
    padding: 0;
    -webkit-font-smoothing: antialiased;
  }}

  /* Standout Cover / Title Section */
  .monograph-cover {{
    padding-top: 100px;
    padding-bottom: 80px;
    page-break-after: always;
    border-bottom: 1.5px solid #0f172a;
    margin-bottom: 60px;
  }}

  .cover-eyebrow {{
    font-family: 'Inter', sans-serif;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #0284c7; /* Precision Cyan/Blue */
    margin-bottom: 24px;
  }}

  .cover-title {{
    font-family: 'Cinzel', 'EB Garamond', Georgia, serif;
    font-size: 34pt;
    font-weight: 800;
    line-height: 1.08;
    color: #0f172a;
    letter-spacing: -0.01em;
    margin-bottom: 20px;
    text-transform: uppercase;
  }}

  .cover-subtitle {{
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 14pt;
    font-weight: 400;
    font-style: italic;
    line-height: 1.4;
    color: #475569;
    max-width: 680px;
    margin-bottom: 40px;
  }}

  .cover-divider {{
    width: 60px;
    height: 3px;
    background-color: #0f172a;
    margin-bottom: 40px;
  }}

  .cover-meta {{
    font-family: 'Inter', sans-serif;
    font-size: 9.5pt;
    color: #334155;
    line-height: 1.8;
  }}

  .cover-meta strong {{
    font-weight: 700;
    color: #0f172a;
    letter-spacing: 0.05em;
  }}

  .cover-badge-row {{
    display: flex;
    gap: 16px;
    margin-top: 50px;
  }}

  .cover-badge {{
    border: 1px solid #cbd5e1;
    padding: 6px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 8pt;
    font-weight: 500;
    color: #475569;
    background: #f8fafc;
    border-radius: 2px;
  }}

  /* Editorial Typography */
  h1 {{
    font-family: 'Cinzel', 'EB Garamond', serif;
    font-size: 21pt;
    font-weight: 700;
    line-height: 1.15;
    color: #0f172a;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    margin-top: 48px;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1.5px solid #0f172a;
    page-break-before: always;
  }}

  h1:first-of-type {{
    page-break-before: avoid;
  }}

  h2 {{
    font-family: 'Inter', sans-serif;
    font-size: 13.5pt;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #0f172a;
    margin-top: 32px;
    margin-bottom: 12px;
  }}

  h3 {{
    font-family: 'Inter', sans-serif;
    font-size: 11pt;
    font-weight: 600;
    color: #334155;
    margin-top: 24px;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}

  p {{
    margin-top: 0;
    margin-bottom: 14px;
    text-align: justify;
    text-justify: inter-word;
  }}

  p + p {{
    text-indent: 1.5em;
    margin-top: -14px;
  }}

  blockquote {{
    margin: 24px 0;
    padding: 14px 24px;
    background-color: #f8fafc;
    border-left: 3px solid #0f172a;
    font-style: italic;
    color: #334155;
    font-size: 11pt;
  }}

  blockquote p {{
    text-indent: 0 !important;
    margin-bottom: 6px;
  }}

  pre, code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 8.2pt;
    background-color: #f8fafc;
    color: #0f172a;
  }}

  pre {{
    padding: 14px 18px;
    border: 1px solid #e2e8f0;
    border-radius: 2px;
    overflow-x: auto;
    line-height: 1.4;
    margin: 20px 0;
    page-break-inside: avoid;
  }}

  /* Booktabs Academic Table Styling */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 24px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }}

  th {{
    border-top: 1.5px solid #0f172a;
    border-bottom: 1.5px solid #0f172a;
    padding: 9px 12px;
    text-align: left;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    color: #0f172a;
    background-color: #f8fafc;
    letter-spacing: 0.02em;
  }}

  td {{
    border-bottom: 1px solid #f1f5f9;
    padding: 8px 12px;
    color: #1e293b;
  }}

  tr:last-child td {{
    border-bottom: 1.5px solid #0f172a;
  }}

  hr {{
    border: 0;
    border-top: 1px solid #e2e8f0;
    margin: 36px 0;
  }}

  ul, ol {{
    margin-top: 0;
    margin-bottom: 16px;
    padding-left: 24px;
  }}

  li {{
    margin-bottom: 6px;
    line-height: 1.55;
  }}

  .figure-container {{
    margin: 30px 0;
    text-align: center;
    page-break-inside: avoid;
  }}

  .figure-container img {{
    max-width: 100%;
    height: auto;
    border: 1px solid #e2e8f0;
  }}

  .figure-caption {{
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 9pt;
    font-style: italic;
    color: #64748b;
    margin-top: 8px;
  }}
</style>
</head>
<body>

<!-- Standout Cover Section -->
<div class="monograph-cover">
  <div class="cover-eyebrow">PRISM Liquidity Systems &bull; Macro &amp; Epistemic Architecture</div>
  <div class="cover-title">Epistemic Sovereignty</div>
  <div class="cover-subtitle">On Market Microstructure, the Collapse of Consensus Reality, and the Autonomous Liquidity Architecture of Macro Civilization</div>
  <div class="cover-divider"></div>
  <div class="cover-meta">
    <strong>Author:</strong> Harsha Ghandikota<br>
    <strong>Institution:</strong> PRISM Liquidity Systems<br>
    <strong>Core Engine:</strong> Equinix NY4 Low-Latency Routing &bull; Convex Waterfill Kernel<br>
    <strong>Date:</strong> October 2026 &bull; Publication Edition 1.0<br>
    <strong>Distribution:</strong> Institutional Quantitative Desks &bull; Macro Allocation Funds
  </div>
  <div class="cover-badge-row">
    <div class="cover-badge">NON-CUSTODIAL INFRASTRUCTURE</div>
    <div class="cover-badge">SUB-0.5MS DETERMINISTIC LATENCY</div>
    <div class="cover-badge">CONVEX OPTIMIZATION KERNEL</div>
  </div>
</div>

{html_body}

</body>
</html>
"""
    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print(f"Master HTML written to: {HTML_OUT}")

def generate_master_docx():
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Inches(0.9)
        sec.bottom_margin = Inches(0.9)
        sec.left_margin = Inches(0.9)
        sec.right_margin = Inches(0.9)

    FONT = "Georgia"

    # Title Page
    p_pre = doc.add_paragraph()
    r_pre = p_pre.add_run("PRISM LIQUIDITY SYSTEMS  |  INSTITUTIONAL RESEARCH")
    r_pre.font.name = FONT
    r_pre.font.size = Pt(9)
    r_pre.font.bold = True
    r_pre.font.color.rgb = RGBColor(2, 132, 199) # Sky Blue
    p_pre.paragraph_format.space_before = Pt(36)
    p_pre.paragraph_format.space_after = Pt(6)

    p_title = doc.add_paragraph()
    r_title = p_title.add_run("EPISTEMIC SOVEREIGNTY")
    r_title.font.name = FONT
    r_title.font.size = Pt(26)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)
    p_title.paragraph_format.space_after = Pt(6)

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("On Market Microstructure, the Collapse of Consensus Reality, and the Autonomous Liquidity Architecture of Macro Civilization")
    r_sub.font.name = FONT
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)
    p_sub.paragraph_format.space_after = Pt(14)

    p_meta = doc.add_paragraph()
    r_meta = p_meta.add_run("By Harsha Ghandikota\nPRISM Liquidity Systems  •  October 2026  •  Equinix NY4 Core")
    r_meta.font.name = FONT
    r_meta.font.size = Pt(9.5)
    r_meta.font.bold = True
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    p_meta.paragraph_format.space_after = Pt(24)

    # Divider
    p_div = doc.add_paragraph()
    r_div = p_div.add_run("__________________________________________________________________")
    r_div.font.color.rgb = RGBColor(203, 213, 225)
    p_div.paragraph_format.space_after = Pt(20)

    with open(MD_OUT, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Skip first 10 header lines because we already rendered custom title page
    reading_body = False
    for line in lines:
        line_s = line.strip()
        if not reading_body:
            if "VOLUME I:" in line_s:
                reading_body = True
            else:
                continue
        
        if not line_s:
            continue
            
        if line_s.startswith("# "):
            p = doc.add_paragraph()
            r = p.add_run(line_s[2:])
            r.font.name = FONT
            r.font.size = Pt(18)
            r.font.bold = True
            r.font.color.rgb = RGBColor(15, 23, 42)
            p.paragraph_format.space_before = Pt(24)
            p.paragraph_format.space_after = Pt(8)
        elif line_s.startswith("## "):
            p = doc.add_paragraph()
            r = p.add_run(line_s[3:])
            r.font.name = FONT
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = RGBColor(30, 41, 59)
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
        elif line_s.startswith("### "):
            p = doc.add_paragraph()
            r = p.add_run(line_s[4:])
            r.font.name = FONT
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = RGBColor(51, 65, 85)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
        elif line_s.startswith("> "):
            p = doc.add_paragraph()
            r = p.add_run(line_s[2:])
            r.font.name = FONT
            r.font.size = Pt(9.5)
            r.font.italic = True
            r.font.color.rgb = RGBColor(71, 85, 105)
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.space_after = Pt(6)
        elif line_s.startswith("---"):
            p = doc.add_paragraph()
            r = p.add_run("____________________________________________________")
            r.font.color.rgb = RGBColor(226, 232, 240)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(8)
        elif line_s.startswith("```"):
            continue
        else:
            p = doc.add_paragraph()
            r = p.add_run(line_s)
            r.font.name = FONT
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(30, 41, 59)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.22

    doc.save(DOCX_OUT)
    print(f"Master DOCX saved to: {DOCX_OUT}")

if __name__ == "__main__":
    assemble_master_markdown()
    assemble_master_html()
    generate_master_docx()
