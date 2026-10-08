import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_docx(output_path):
    doc = Document()
    
    # 0.75 in margins
    for sec in doc.sections:
        sec.top_margin = Inches(0.75)
        sec.bottom_margin = Inches(0.75)
        sec.left_margin = Inches(0.75)
        sec.right_margin = Inches(0.75)

    # Document Header / Title
    title = doc.add_paragraph()
    r_title = title.add_run("SITUATIONAL AWARENESS IN THE AGE OF EVENT DERIVATIVES")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42) # Slate 900
    title.paragraph_format.space_after = Pt(4)

    sub = doc.add_paragraph()
    r_sub = sub.add_run("On Epistemic Sovereignty, the Collapse of Consensus Pricing, and the Necessity of Institutional Routing Architecture")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.color.rgb = RGBColor(37, 99, 235) # Blue 600
    r_sub.font.bold = True
    sub.paragraph_format.space_after = Pt(6)

    meta = doc.add_paragraph()
    r_meta = meta.add_run("By PRISM Technologies Inc.  |  Quantitative Research & Systems Architecture  |  October 2026")
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(9)
    r_meta.font.color.rgb = RGBColor(100, 116, 139) # Slate 500
    r_meta.font.bold = True
    meta.paragraph_format.space_after = Pt(12)

    # Epigraph Quote Box
    q_table = doc.add_table(rows=1, cols=1)
    q_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    q_cell = q_table.cell(0, 0)
    set_cell_background(q_cell, "F8FAFC")
    set_cell_margins(q_cell, top=140, bottom=140, left=200, right=200)
    
    qp = q_cell.paragraphs[0]
    qr = qp.add_run('“The most contrarian thing of all is not to oppose the crowd, but to think for yourself. Yet when markets become liquid enough to price the future itself, truth ceases to be a philosophical pursuit—it becomes an engineering bottleneck.”\n\n— Peter Thiel, Zero to One (Adapted)')
    qr.font.name = "Arial"
    qr.font.size = Pt(9.5)
    qr.font.italic = True
    qr.font.color.rgb = RGBColor(51, 65, 85)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Executive Summary Metric Cards Table
    m_table = doc.add_table(rows=2, cols=3)
    m_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    metrics = [
        ("296 bps", "Systematic Alpha Burn on Unrouted Large Orders"),
        ("14.2 Seconds", "Cross-Venue Latency Window Between Kalshi & Poly"),
        ("19.7x", "Alpha Preservation Multiple (Slippage Saved / Fee Paid)"),
        ("$320 Billion", "Projected 2030 Epistemic Event Contract Notional"),
        ("< 0.5 Milliseconds", "Equinix NY4 FPGA Atomic Parent-Order Split Path"),
        ("99.95%", "Non-Custodial Multi-Venue Execution Uptime SLA"),
    ]

    for idx, (val, desc) in enumerate(metrics):
        r_i, c_i = divmod(idx, 3)
        cell = m_table.cell(r_i, c_i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        r1 = p.add_run(val + "\n")
        r1.font.name = "Arial"
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(15, 23, 42)
        
        r2 = p.add_run(desc)
        r2.font.name = "Arial"
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Helper for Headings
    def add_h1(text):
        h = doc.add_paragraph()
        r = h.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)

    def add_p(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        r_bold = p.add_run(bold_prefix + ": ")
        r_bold.font.name = "Arial"
        r_bold.font.size = Pt(9.5)
        r_bold.font.bold = True
        r_bold.font.color.rgb = RGBColor(15, 23, 42)

        r_body = p.add_run(text)
        r_body.font.name = "Arial"
        r_body.font.size = Pt(9.5)
        r_body.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.space_after = Pt(4)

    # Prologue
    add_h1("PROLOGUE: THE SOVEREIGN TRUTH PROBLEM")
    add_p("Most market participants—including senior partners at quantitative hedge funds, sovereign allocators, and regulators in Washington—are fundamentally blind to what prediction markets actually represent. They believe Polymarket and Kalshi are betting parlors. They view them as digital casinos for political gamblers and crypto natives.")
    add_p("This is a category error of historic proportions. What is occurring right before our eyes is the birth of epistemic infrastructure: a decentralized, multi-venue, continuous clearing pricing mechanism for global state transitions. Whether an aircraft carrier transits the Taiwan Strait, whether the Federal Reserve cuts rates by 50 basis points, whether a commercial fusion reactor achieves net energy gain, or whether an election collapses into civil contestation—these are no longer questions mediated by editorial boards, polling aggregators, or lagging macroeconomic surveys. They are tradeable binary payoff functions.")
    add_p("When information has a real-time clearing price, the traditional apparatus of consensus reality is rendered obsolete. However, this transition has exposed a catastrophic systemic failure: the global truth machine is cracked in half.")

    # Section I
    add_h1("I. THE MICROSTRUCTURE CRISIS: THE 296 BPS EPISTEMIC TAX")
    add_p("As capital floods into event derivatives, market structure is fragmenting across mutually incompatible regulatory and technological walled gardens:")
    add_bullet("The Offshore Synthetic Order Book (Polymarket)", "USDC collateral on Polygon PoS, CLOB matching, subjective UMA optimistic oracle resolution. High retail velocity, massive volume, profound capital inefficiency, zero prime brokerage connectivity.")
    add_bullet("The Domestic CFTC-Regulated Exchange (Kalshi)", "Fedwire USD clearinghouse collateral, LedgerX clearing heritage, position limits, formal regulatory legalism. Safe for compliant American capital, but structurally starved of global non-US liquidity.")
    add_bullet("The Traditional Multi-Asset Incumbent (ForecastEx / IBKR)", "Embedded within institutional prime brokerage, but hobbled by legacy T+1 execution pipelines and retail-centric brokerage interfaces.")

    # Image 1
    chart1_path = "/Users/harshaghandikota/Liquidity Agent/public/chart_divergence.png"
    if os.path.exists(chart1_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(chart1_path, width=Inches(6.8))
        
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c_r = cap.add_run("Figure 1: High-Frequency Tick-Level Cross-Venue Price Divergence during Macro Shock Event (Kalshi CLOB vs Polymarket CLOB). Shaded area represents 480 bps open arbitrage window persisting for 14.2 seconds.")
        c_r.font.name = "Arial"
        c_r.font.size = Pt(8)
        c_r.font.italic = True
        c_r.font.color.rgb = RGBColor(100, 116, 139)
        cap.paragraph_format.space_after = Pt(10)

    add_p("When an event of geopolitical or macroeconomic consequence breaks, the clearing price of reality does not adjust simultaneously. On Kalshi, the probability of an emergency Fed rate cut re-prices from 57.6¢ to 62.4¢ in t = 2.5s driven by domestic electronic bankwires. On Polymarket, delayed by cross-chain bridging and oracle dispute latency, the exact same contract prints at 57.6¢ for 14.2 seconds. The peak spread is 480 basis points.")
    add_p("For a systematic fund attempting to execute $1,000,000 of directional risk, routing into a single venue results in catastrophic market impact: an average of 296 basis points burned simply crossing fragmented order books. This is not a liquidity shortage; it is an arbitrage routing failure.")

    # Section II
    add_h1("II. EXECUTION SLIPPAGE & THE LIQUIDITY SCALING LAW")
    add_p("In AI scaling, the Bitter Lesson dictates that general methods leveraging compute always triumph over handcrafted rules. In capital markets, an identical mathematical law holds: Capital clusters exclusively where execution slippage approaches zero.")

    # Image 2
    chart2_path = "/Users/harshaghandikota/Liquidity Agent/public/chart_slippage_and_scaling.png"
    if os.path.exists(chart2_path):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(8)
        p_img2.paragraph_format.space_after = Pt(2)
        doc.add_picture(chart2_path, width=Inches(6.8))
        
        cap2 = doc.add_paragraph()
        cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c_r2 = cap2.add_run("Figure 2: (Left) Execution Slippage Curve vs Notional Order Size: Single-Venue vs PRISM Atomic Smart Router. (Right) Global Event Derivatives Volume Scaling Law (2026 - 2030) with PRISM Routed Flow Capture.")
        c_r2.font.name = "Arial"
        c_r2.font.size = Pt(8)
        c_r2.font.italic = True
        c_r2.font.color.rgb = RGBColor(100, 116, 139)
        cap2.paragraph_format.space_after = Pt(10)

    # Slippage Matrix Table
    s_table = doc.add_table(rows=6, cols=4)
    s_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers = ["Notional Order Size", "Single-Venue Fill", "PRISM Atomic Routed", "Net Alpha Preserved"]
    for c_i, h in enumerate(s_headers):
        cell = s_table.cell(0, c_i)
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    s_rows = [
        ("$25,000 USD", "18 bps", "3 bps", "15 bps (83.3%)"),
        ("$100,000 USD", "78 bps", "11 bps", "67 bps (85.9%)"),
        ("$500,000 USD", "215 bps", "28 bps", "187 bps (87.0%)"),
        ("$1,000,000 USD", "296 bps", "42 bps", "254 bps (85.8%)"),
        ("$5,000,000 USD", "610 bps", "92 bps", "518 bps (84.9%)"),
    ]

    for r_i, row in enumerate(s_rows, start=1):
        for c_i, val in enumerate(row):
            cell = s_table.cell(r_i, c_i)
            bg = "F8FAFC" if r_i % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            r.font.bold = (c_i == 3)
            r.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    add_p("For every $1,000,000 routed through single-venue execution, a trading desk incurs $29,600 in market impact. With PRISM's atomic router, total slippage drops to $4,200. Even after paying PRISM’s 1.5 bps fee ($1,500), the desk retains $23,900 of pure alpha. The Client Alpha Preservation Ratio is 19.7x.")

    # Section III
    add_h1("III. THE KARPIAN DOCTRINE: SOFTWARE AS SOVEREIGN UTILITY")
    add_p("Software does not exist to create frictionless social networks or optimize ad clicks; software exists to impose order upon chaotic, mission-critical environments where failure is existential. In institutional finance, execution quality is sovereignty.")
    add_p("If an institution cannot route an order across fragmented venues with sub-millisecond atomic certainty, they do not have an investment strategy—they are merely subsidizing toxic latency arbitrageurs who front-run their fills across the NY4 and AWS corridors. To solve this, PRISM operates on three sovereign design principles:")
    add_bullet("Sub-0.5ms Atomic Lot Splitting", "Dynamically decomposing parent orders into micro-lots across Kalshi and Polymarket using real-time tick-depth elasticity curves.")
    add_bullet("Deterministic Oracle Guard", "Algorithmic insulation against resolution discrepancies. When Kalshi settles based on official government reports and Polymarket settles via UMA token disputes, PRISM’s proprietary resolution matrix prices the divergence directly into execution.")
    add_bullet("Non-Custodial Isolation", "Capital never touches PRISM’s balance sheet. Institutional funds maintain bilateral custody at prime custodians. PRISM is purely the cryptographic, low-latency cerebral cortex.")

    # Section IV
    add_h1("IV. THE THIELIAN ANTITHESIS: COMPETITION IS FOR LOSERS")
    add_p("Every failed startup in this ecosystem is attempting to build 'another prediction exchange.' They are competing for retail users, hiring social media influencers, and burning venture capital acquiring retail gamblers who churn in 30 days. Competition is for losers. Monopolies are built by owning the invisible routing substrate through which all capital must flow.")
    add_p("PRISM does not care whether Polymarket wins, whether Kalshi wins, or whether ForecastEx dominates institutional volumes. PRISM is the critical utility toll booth sitting directly between the global hedge fund and every underlying execution venue on earth.")

    # Integration Spec Table
    add_h1("V. INSTITUTIONAL INTEGRATION SPECIFICATION")
    spec_table = doc.add_table(rows=5, cols=2)
    spec_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    specs = [
        ("Interface Protocol", "FIX 4.4 Engine / Low-Latency REST / Streaming WebSocket"),
        ("Co-Location Datacenter", "Equinix NY4 (Secaucus, NJ) • 10Gbps Cross-Connects"),
        ("Throughput Capacity", "100,000 orders/sec burst capacity with deterministic lot routing"),
        ("Latency Execution SLA", "< 0.50 Milliseconds internal matching & transit engine"),
        ("Institutional Onboarding", "Bespoke Sandbox API Keys: desk@prism.xyz"),
    ]
    for r_i, (k, v) in enumerate(specs):
        c1 = spec_table.cell(r_i, 0)
        c2 = spec_table.cell(r_i, 1)
        set_cell_background(c1, "F1F5F9")
        set_cell_background(c2, "FFFFFF")
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c2, top=60, bottom=60, left=100, right=100)
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(k)
        r1.font.name = "Arial"
        r1.font.size = Pt(8.5)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(15, 23, 42)

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(v)
        r2.font.name = "Arial"
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)
    fin = doc.add_paragraph()
    r_fin = fin.add_run("PRISM TECHNOLOGIES INC.  |  EXECUTION IS SOVEREIGNTY.\nSecaucus NY4 • London LD4 • Singapore SG1  |  Contact: desk@prism.xyz")
    r_fin.font.name = "Arial"
    r_fin.font.size = Pt(8.5)
    r_fin.font.bold = True
    r_fin.font.color.rgb = RGBColor(100, 116, 139)

    doc.save(output_path)
    print(f"Successfully generated institutional DOCX at: {output_path}")

if __name__ == "__main__":
    generate_docx("/Users/harshaghandikota/Liquidity Agent/docs/PRISM_Situational_Awareness_Whitepaper.docx")
