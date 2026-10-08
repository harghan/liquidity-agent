import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "PRISM TECHNOLOGIES INC. — INSTITUTIONAL SITUATIONAL AWARENESS")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "OCTOBER 2026")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer (All pages)
        self.setFont("Helvetica", 8)
        self.drawString(54, 30, "CONFIDENTIAL & PROPRIETARY — PREPARED FOR INSTITUTIONAL TRADING DESKS")
        self.drawRightString(letter[0] - 54, 30, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 40, letter[0] - 54, 40)
        self.restoreState()

def generate_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )

    quote_style = ParagraphStyle(
        'Epigraph',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceBefore=6,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Title Banner
    story.append(Paragraph("SITUATIONAL AWARENESS IN THE AGE OF EVENT DERIVATIVES", title_style))
    story.append(Paragraph("On Epistemic Sovereignty, the Collapse of Consensus Pricing, and the Necessity of Institutional Routing Architecture", subtitle_style))
    story.append(Paragraph("<b>By PRISM Technologies Inc.</b> &nbsp;|&nbsp; Quantitative Research & Systems Architecture &nbsp;|&nbsp; October 2026", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=0, spaceAfter=10))

    # Epigraph Box
    quote_text = "<i>“The most contrarian thing of all is not to oppose the crowd, but to think for yourself. Yet when markets become liquid enough to price the future itself, truth ceases to be a philosophical pursuit—it becomes an engineering bottleneck.”</i><br/><br/><b>— Peter Thiel, Zero to One (Adapted)</b>"
    quote_table = Table([[Paragraph(quote_text, quote_style)]], colWidths=[504])
    quote_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LINELEFT', (0,0), (-1,-1), 3, colors.HexColor("#2563EB")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(quote_table)
    story.append(Spacer(1, 10))

    # Summary Matrix Table
    summary_data = [
        [
            Paragraph("<b>296 bps</b><br/><font size=7 color='#64748B'>Systematic Alpha Burn on Unrouted Large Orders</font>", callout_style),
            Paragraph("<b>14.2 Seconds</b><br/><font size=7 color='#64748B'>Cross-Venue Latency Window Between Kalshi & Poly</font>", callout_style),
            Paragraph("<b>19.7x</b><br/><font size=7 color='#64748B'>Alpha Preservation Multiple (Slippage Saved / Fee Paid)</font>", callout_style),
        ],
        [
            Paragraph("<b>$320 Billion</b><br/><font size=7 color='#64748B'>Projected 2030 Epistemic Event Contract Notional</font>", callout_style),
            Paragraph("<b>&lt; 0.5 Milliseconds</b><br/><font size=7 color='#64748B'>Equinix NY4 FPGA Atomic Parent-Order Split Path</font>", callout_style),
            Paragraph("<b>99.95%</b><br/><font size=7 color='#64748B'>Non-Custodial Multi-Venue Execution Uptime SLA</font>", callout_style),
        ]
    ]
    summary_table = Table(summary_data, colWidths=[168, 168, 168])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # Prologue
    story.append(Paragraph("PROLOGUE: THE SOVEREIGN TRUTH PROBLEM", h1_style))
    story.append(Paragraph(
        "Most market participants—including senior partners at quantitative hedge funds, sovereign allocators, and regulators in Washington—are fundamentally blind to what prediction markets actually represent. They believe Polymarket and Kalshi are betting parlors. They view them as digital casinos for political gamblers and crypto natives.",
        body_style
    ))
    story.append(Paragraph(
        "This is a category error of historic proportions. What is occurring right before our eyes is the birth of <b>epistemic infrastructure</b>: a decentralized, multi-venue, continuous clearing pricing mechanism for global state transitions. Whether an aircraft carrier transits the Taiwan Strait, whether the Federal Reserve cuts rates by 50 basis points, whether a commercial fusion reactor achieves net energy gain, or whether an election collapses into civil contestation—these are no longer questions mediated by editorial boards, polling aggregators, or lagging macroeconomic surveys. <b>They are tradeable binary payoff functions.</b>",
        body_style
    ))
    story.append(Paragraph(
        "When information has a real-time clearing price, the traditional apparatus of consensus reality is rendered obsolete. However, this transition has exposed a catastrophic systemic failure: <b>the global truth machine is cracked in half.</b>",
        body_style
    ))

    # Section I
    story.append(Paragraph("I. THE MICROSTRUCTURE CRISIS: THE 296 BPS EPISTEMIC TAX", h1_style))
    story.append(Paragraph(
        "As capital floods into event derivatives, market structure is fragmenting across mutually incompatible regulatory and technological walled gardens:",
        body_style
    ))
    story.append(Paragraph("• <b>The Offshore Synthetic Order Book (Polymarket)</b>: USDC collateral on Polygon PoS, CLOB matching, subjective UMA optimistic oracle resolution. High retail velocity, massive volume, profound capital inefficiency, zero prime brokerage connectivity.", bullet_style))
    story.append(Paragraph("• <b>The Domestic CFTC-Regulated Exchange (Kalshi)</b>: Fedwire USD clearinghouse collateral, LedgerX clearing heritage, position limits, formal regulatory legalism. Safe for compliant American capital, but structurally starved of global non-US liquidity.", bullet_style))
    story.append(Paragraph("• <b>The Traditional Multi-Asset Incumbent (ForecastEx / IBKR)</b>: Embedded within institutional prime brokerage, but hobbled by legacy T+1 execution pipelines and retail-centric brokerage interfaces.", bullet_style))
    story.append(Spacer(1, 6))

    # Insert Chart 1
    chart1_path = "/Users/harshaghandikota/Liquidity Agent/public/chart_divergence.png"
    if os.path.exists(chart1_path):
        story.append(Image(chart1_path, width=7*inch, height=3.5*inch))
        story.append(Paragraph("<i>Figure 1: High-Frequency Tick-Level Cross-Venue Price Divergence during Macro Shock Event (Kalshi CLOB vs Polymarket CLOB). Shaded area represents 480 bps open arbitrage window persisting for 14.2 seconds.</i>", meta_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph(
        "When an event of geopolitical or macroeconomic consequence breaks, the clearing price of reality does not adjust simultaneously. On Kalshi, the probability of an emergency Fed rate cut re-prices from 57.6¢ to 62.4¢ in t = 2.5s driven by domestic electronic bankwires. On Polymarket, delayed by cross-chain bridging and oracle dispute latency, the exact same contract prints at 57.6¢ for 14.2 seconds. <b>The peak spread is 480 basis points.</b>",
        body_style
    ))
    story.append(Paragraph(
        "For a systematic fund attempting to execute $1,000,000 of directional risk, routing into a single venue results in catastrophic market impact: an average of <b>296 basis points burned</b> simply crossing fragmented order books. This is not a liquidity shortage; it is an arbitrage routing failure.",
        body_style
    ))

    # Page Break for Chapter II & III
    story.append(PageBreak())

    # Section II
    story.append(Paragraph("II. EXECUTION SLIPPAGE & THE LIQUIDITY SCALING LAW", h1_style))
    story.append(Paragraph(
        "In AI scaling, the Bitter Lesson dictates that general methods leveraging compute always triumph over handcrafted rules. In capital markets, an identical mathematical law holds: <i>Capital clusters exclusively where execution slippage approaches zero.</i>",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Insert Chart 2
    chart2_path = "/Users/harshaghandikota/Liquidity Agent/public/chart_slippage_and_scaling.png"
    if os.path.exists(chart2_path):
        story.append(Image(chart2_path, width=7*inch, height=2.9*inch))
        story.append(Paragraph("<i>Figure 2: (Left) Execution Slippage Curve vs Notional Order Size: Single-Venue vs PRISM Atomic Smart Router. (Right) Global Event Derivatives Volume Scaling Law (2026 - 2030) with PRISM Routed Flow Capture.</i>", meta_style))
        story.append(Spacer(1, 8))

    # Slippage Table
    slip_data = [
        [Paragraph("<b>Notional Order Size</b>", callout_style), Paragraph("<b>Single-Venue Fill</b>", callout_style), Paragraph("<b>PRISM Atomic Routed</b>", callout_style), Paragraph("<b>Alpha Preserved</b>", callout_style)],
        [Paragraph("$25,000 USD", body_style), Paragraph("18 bps", body_style), Paragraph("3 bps", body_style), Paragraph("<b>15 bps (83.3%)</b>", body_style)],
        [Paragraph("$100,000 USD", body_style), Paragraph("78 bps", body_style), Paragraph("11 bps", body_style), Paragraph("<b>67 bps (85.9%)</b>", body_style)],
        [Paragraph("$500,000 USD", body_style), Paragraph("215 bps", body_style), Paragraph("28 bps", body_style), Paragraph("<b>187 bps (87.0%)</b>", body_style)],
        [Paragraph("$1,000,000 USD", body_style), Paragraph("296 bps", body_style), Paragraph("42 bps", body_style), Paragraph("<b>254 bps (85.8%)</b>", body_style)],
        [Paragraph("$5,000,000 USD", body_style), Paragraph("610 bps", body_style), Paragraph("92 bps", body_style), Paragraph("<b>518 bps (84.9%)</b>", body_style)],
    ]
    slip_table = Table(slip_data, colWidths=[126, 126, 126, 126])
    slip_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(slip_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "For every $1,000,000 routed through single-venue execution, a trading desk incurs $29,600 in market impact. With PRISM's atomic router, total slippage drops to $4,200. Even after paying PRISM’s 1.5 bps fee ($1,500), the desk retains <b>$23,900 of pure alpha</b>. The Client Alpha Preservation Ratio is <b>19.7x</b>.",
        body_style
    ))

    # Section III
    story.append(Paragraph("III. THE KARPIAN DOCTRINE: SOFTWARE AS SOVEREIGN UTILITY", h1_style))
    story.append(Paragraph(
        "Software does not exist to create frictionless social networks or optimize ad clicks; software exists to impose order upon chaotic, mission-critical environments where failure is existential. In institutional finance, execution quality is sovereignty.",
        body_style
    ))
    story.append(Paragraph(
        "If an institution cannot route an order across fragmented venues with sub-millisecond atomic certainty, they do not have an investment strategy—they are merely subsidizing toxic latency arbitrageurs who front-run their fills across the NY4 and AWS corridors. To solve this, PRISM operates on three sovereign design principles:",
        body_style
    ))
    story.append(Paragraph("• <b>Sub-0.5ms Atomic Lot Splitting</b>: Dynamically decomposing parent orders into micro-lots across Kalshi and Polymarket using real-time tick-depth elasticity curves.", bullet_style))
    story.append(Paragraph("• <b>Deterministic Oracle Guard</b>: Algorithmic insulation against resolution discrepancies. When Kalshi settles based on official government reports and Polymarket settles via UMA token disputes, PRISM’s proprietary resolution matrix prices the divergence directly into execution.", bullet_style))
    story.append(Paragraph("• <b>Non-Custodial Isolation</b>: Capital never touches PRISM’s balance sheet. Institutional funds maintain bilateral custody at prime custodians. PRISM is purely the cryptographic, low-latency cerebral cortex.", bullet_style))

    # Section IV
    story.append(Paragraph("IV. THE THIELIAN ANTITHESIS: COMPETITION IS FOR LOSERS", h1_style))
    story.append(Paragraph(
        "Every failed startup in this ecosystem is attempting to build 'another prediction exchange.' They are competing for retail users, hiring social media influencers, and burning venture capital acquiring retail gamblers who churn in 30 days. Competition is for losers. <b>Monopolies are built by owning the invisible routing substrate through which all capital must flow.</b>",
        body_style
    ))
    story.append(Paragraph(
        "PRISM does not care whether Polymarket wins, whether Kalshi wins, or whether ForecastEx dominates institutional volumes. PRISM is the critical utility toll booth sitting directly between the global hedge fund and every underlying execution venue on earth.",
        body_style
    ))

    # Section V: Specifications & Closing
    story.append(Paragraph("V. INSTITUTIONAL INTEGRATION SPECIFICATION", h1_style))
    spec_data = [
        [Paragraph("<b>Interface Protocol</b>", callout_style), Paragraph("FIX 4.4 Engine / Low-Latency REST / Streaming WebSocket", body_style)],
        [Paragraph("<b>Co-Location Datacenter</b>", callout_style), Paragraph("Equinix NY4 (Secaucus, NJ) • 10Gbps Cross-Connects", body_style)],
        [Paragraph("<b>Throughput Capacity</b>", callout_style), Paragraph("100,000 orders/sec burst capacity with deterministic lot routing", body_style)],
        [Paragraph("<b>Latency Execution SLA</b>", callout_style), Paragraph("&lt; 0.50 Milliseconds internal matching & transit engine", body_style)],
        [Paragraph("<b>Institutional Onboarding</b>", callout_style), Paragraph("Bespoke Sandbox API Keys: <b>desk@prism.xyz</b>", body_style)],
    ]
    spec_table = Table(spec_data, colWidths=[150, 354])
    spec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(spec_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>PRISM TECHNOLOGIES INC. &nbsp;|&nbsp; EXECUTION IS SOVEREIGNTY.</b><br/><font color='#64748B'>Secaucus NY4 • London LD4 • Singapore SG1 &nbsp;|&nbsp; Contact: desk@prism.xyz</font>", meta_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated institutional PDF at: {output_path}")

if __name__ == "__main__":
    generate_pdf("/Users/harshaghandikota/Liquidity Agent/docs/PRISM_Situational_Awareness_Whitepaper.pdf")
