import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_cmo_model():
    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)

    # ---------------------------------------------------------
    # DESIGN SYSTEM & STYLES (MATCHING CFO MODEL LUXURY AESTHETIC)
    # ---------------------------------------------------------
    FONT_FAMILY = "Arial"

    # Color Palette
    NAVY_DARK = "0F172A"       # Deep Slate Navy (Titles)
    NAVY_HEADER = "1E293B"     # Table headers
    TEXT_WHITE = "FFFFFF"
    BLUE_ACCENT = "2563EB"     # Royal Blue accent
    BLUE_LIGHT = "EFF6FF"      # KPI & highlight background
    GRAY_SECTION = "F1F5F9"    # Section background
    GRAY_BORDER = "CBD5E1"     # Thin borders
    GRAY_TEXT = "64748B"       # Subtitles / notes
    AMBER_BG = "FEF9C3"        # Assumption inputs
    AMBER_TXT = "854D0E"
    EMERALD_BG = "ECFDF5"      # Won / Success metrics
    EMERALD_TXT = "065F46"

    # Fonts
    title_font = Font(name=FONT_FAMILY, size=16, bold=True, color=NAVY_DARK)
    subtitle_font = Font(name=FONT_FAMILY, size=10, italic=True, color=GRAY_TEXT)
    section_font = Font(name=FONT_FAMILY, size=11, bold=True, color=NAVY_DARK)
    table_header_font = Font(name=FONT_FAMILY, size=10, bold=True, color=TEXT_WHITE)
    bold_font = Font(name=FONT_FAMILY, size=10, bold=True, color="000000")
    regular_font = Font(name=FONT_FAMILY, size=10, color="000000")
    italic_font = Font(name=FONT_FAMILY, size=9, italic=True, color=GRAY_TEXT)
    kpi_lbl_font = Font(name=FONT_FAMILY, size=9, bold=True, color=GRAY_TEXT)
    kpi_val_font = Font(name=FONT_FAMILY, size=15, bold=True, color=BLUE_ACCENT)
    input_font = Font(name=FONT_FAMILY, size=10, bold=True, color=AMBER_TXT)

    # Fills
    header_fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    section_fill = PatternFill(start_color=GRAY_SECTION, end_color=GRAY_SECTION, fill_type="solid")
    highlight_fill = PatternFill(start_color=BLUE_LIGHT, end_color=BLUE_LIGHT, fill_type="solid")
    success_fill = PatternFill(start_color=EMERALD_BG, end_color=EMERALD_BG, fill_type="solid")
    input_fill = PatternFill(start_color=AMBER_BG, end_color=AMBER_BG, fill_type="solid")
    kpi_box_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    # Borders
    thin_border_side = Side(border_style="thin", color=GRAY_BORDER)
    double_border_side = Side(border_style="double", color=NAVY_DARK)
    regular_border = Border(top=thin_border_side, bottom=thin_border_side, left=thin_border_side, right=thin_border_side)
    subtotal_border = Border(top=thin_border_side, bottom=thin_border_side)
    top_thin_bottom_double = Border(top=thin_border_side, bottom=double_border_side)

    # Number Formats
    FMT_CURR = "$#,##0"
    FMT_CURR_M = "$#,##0.0"
    FMT_PCT = "0.0%"
    FMT_INT = "#,##0"
    FMT_DEC = "#,##0.0"
    FMT_MULT = '0.0"x"'

    # =========================================================================
    # TAB 1: EXECUTIVE DASHBOARD
    # =========================================================================
    ws1 = wb.create_sheet(title="Executive Dashboard")
    ws1.views.sheetView[0].showGridLines = True

    # Title Block
    ws1["B2"] = "PRISM TECHNOLOGIES INC. — CMO GTM EXECUTIVE DASHBOARD"
    ws1["B2"].font = title_font
    ws1["B3"] = "Institutional Go-To-Market Engine, Demand Gen Funnel Velocity & Channel Economics"
    ws1["B3"].font = Font(name=FONT_FAMILY, size=10, bold=True, color=BLUE_ACCENT)
    ws1["B4"] = "Institutional Cross-Venue Prediction Market Smart Order Router (Series Seed / Series A GTM Plan)"
    ws1["B4"].font = subtitle_font

    # KPI Summary Cards (Row 6 - 8)
    kpis = [
        ("B", "Y1 SOURCED ARR", "='Funnel & Pipeline'!O25", FMT_CURR),
        ("D", "Y1 PIPELINE CREATED", "='Funnel & Pipeline'!O18", FMT_CURR),
        ("F", "PIPELINE COVERAGE", "='Funnel & Pipeline'!O29", FMT_MULT),
        ("H", "BLENDED CAC", "='Channel Economics'!J13", FMT_CURR),
        ("J", "MARKETING MAGIC NO.", "='Marketing Budget'!O33", FMT_MULT),
    ]

    for col, lbl, formula, fmt in kpis:
        c_lbl = ws1[f"{col}6"]
        c_val = ws1[f"{col}7"]
        c_lbl.value = lbl
        c_val.value = formula
        c_lbl.font = kpi_lbl_font
        c_val.font = kpi_val_font
        c_lbl.alignment = Alignment(horizontal="center")
        c_val.alignment = Alignment(horizontal="center")
        c_lbl.fill = kpi_box_fill
        c_val.fill = kpi_box_fill
        c_val.number_format = fmt
        c_lbl.border = Border(top=thin_border_side, left=thin_border_side, right=thin_border_side)
        c_val.border = Border(bottom=thin_border_side, left=thin_border_side, right=thin_border_side)

    # Executive Overview Table (Row 10+)
    ws1["B10"] = "ANNUAL GTM PERFORMANCE ROLLUP & SALES EFFICIENCY (5-YEAR OUTLOOK)"
    ws1["B10"].font = section_font
    ws1["B10"].fill = section_fill
    ws1.merge_cells("B10:G10")

    headers_dash = ["Go-To-Market Metric", "Year 1 (Seed)", "Year 2 (Expansion)", "Year 3 (Scale)", "Year 4 (Institutional)", "Year 5 (Category King)"]
    for col_idx, h in enumerate(headers_dash, start=2):
        cell = ws1.cell(row=11, column=col_idx, value=h)
        cell.font = table_header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="left" if col_idx == 2 else "right")

    # Metrics mapping for executive table
    dash_metrics = [
        ("Institutional MQLs Generated", ["='Funnel & Pipeline'!O15", "=C12*2.8", "=D12*2.5", "=E12*1.9", "=F12*1.6"], FMT_INT),
        ("Sales Qualified Opportunities (SQLs)", ["='Funnel & Pipeline'!O17", "=C13*2.8", "=D13*2.5", "=E13*1.9", "=F13*1.6"], FMT_INT),
        ("Technical Sandbox POCs Launched", ["='Funnel & Pipeline'!O21", "=C14*2.6", "=D14*2.4", "=E14*1.8", "=F14*1.5"], FMT_INT),
        ("New Trading Desks Closed (Won)", ["='Funnel & Pipeline'!O23", "=C15*3.0", "=D15*2.5", "=E15*1.8", "=F15*1.5"], FMT_INT),
        ("Cumulative Marketing-Sourced Desks", ["=C15", "=C16+D15", "=D16+E15", "=E16+F15", "=F16+G15"], FMT_INT),
        ("---", None, None),
        ("Marketing Sourced Pipeline ($M)", ["='Funnel & Pipeline'!O18/1000000", "=C18*3.2", "=D18*2.7", "=E18*2.0", "=F18*1.6"], FMT_CURR_M),
        ("Company Net ARR Quota Target ($M)", [1.663, 7.128, 23.182, 48.361, 82.933], FMT_CURR_M),
        ("Pipeline Coverage Ratio (vs Quota)", ["=C18/C19", "=D18/D19", "=E18/E19", "=F18/F19", "=G18/G19"], FMT_MULT),
        ("Marketing Sourced Net ARR ($)", ["='Funnel & Pipeline'!O25", "=C21*3.8", "=D21*2.9", "=E21*2.0", "=F21*1.6"], FMT_CURR),
        ("Marketing Sourced ARR % of Total", ["=C21/(C19*1000000)", "=D21/(D19*1000000)", "=E21/(E19*1000000)", "=F21/(F19*1000000)", "=G21/(G19*1000000)"], FMT_PCT),
        ("---", None, None),
        ("Total Marketing & GTM Spend ($)", ["='Marketing Budget'!O29", "=C24*2.2", "=D24*1.9", "=E24*1.7", "=F24*1.5"], FMT_CURR),
        ("Marketing Spend as % of Net ARR", ["=C24/C21", "=D24/D21", "=E24/E21", "=F24/F21", "=G24/G21"], FMT_PCT),
        ("Blended Institutional CAC ($)", ["=C24/C15", "=D24/D15", "=E24/E15", "=F24/F15", "=G24/G15"], FMT_CURR),
        ("Average Payback Period (Months)", ["=(C26/(C21/C15))*12", "=(D26/(D21/D15))*12", "=(E26/(E21/E15))*12", "=(F26/(F21/F15))*12", "=(G26/(G21/G15))*12"], FMT_DEC),
        ("Marketing Magic Number (Efficiency)", ["=C21/C24", "=D21/D24", "=E21/E24", "=F21/F24", "=G21/G24"], FMT_MULT),
        ("Institutional LTV / CAC Ratio", ["='Channel Economics'!L13", "=C29*1.2", "=D29*1.3", "=E29*1.1", "=F29*1.05"], FMT_MULT),
    ]

    curr_row = 12
    for item in dash_metrics:
        label = item[0]
        if label == "---":
            curr_row += 1
            continue
        vals = item[1]
        fmt = item[2]
        is_highlight = "Ratio" in label or "Magic" in label or "Sourced Net ARR" in label or "Pipeline Coverage" in label
        c_lbl = ws1.cell(row=curr_row, column=2, value=label)
        c_lbl.font = bold_font if is_highlight else regular_font

        for yr_idx in range(5):
            c = ws1.cell(row=curr_row, column=3 + yr_idx, value=vals[yr_idx])
            c.number_format = fmt
            c.font = bold_font if is_highlight else regular_font
            c.alignment = Alignment(horizontal="right")
            if is_highlight:
                c.fill = highlight_fill
                c.border = subtotal_border
        curr_row += 1

    # =========================================================================
    # TAB 2: GTM ASSUMPTIONS
    # =========================================================================
    ws2 = wb.create_sheet(title="GTM Assumptions")
    ws2.views.sheetView[0].showGridLines = True

    ws2["B2"] = "PRISM GO-TO-MARKET ARCHITECTURE — MASTER ASSUMPTIONS"
    ws2["B2"].font = title_font
    ws2["B3"] = "Institutional Target Accounts, Full-Funnel Conversion Rates, Deal Economics & Benchmarks"
    ws2["B3"].font = subtitle_font

    def write_gtm_assumption_section(start_row, title, headers, rows):
        ws2.cell(row=start_row, column=2, value=title).font = section_font
        ws2.cell(row=start_row, column=2).fill = section_fill
        ws2.merge_cells(start_row=start_row, start_column=2, end_row=start_row, end_column=2 + len(headers) - 1)

        for idx, h in enumerate(headers, start=2):
            cell = ws2.cell(row=start_row + 1, column=idx, value=h)
            cell.font = table_header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="left" if idx == 2 else "right")

        r_idx = start_row + 2
        for r in rows:
            label, val, unit, notes = r[0], r[1], r[2], r[3]
            c_lbl = ws2.cell(row=r_idx, column=2, value=label)
            c_lbl.font = regular_font

            c_val = ws2.cell(row=r_idx, column=3, value=val)
            c_val.font = input_font
            c_val.fill = input_fill
            c_val.alignment = Alignment(horizontal="right")
            if isinstance(val, float):
                if unit == "%":
                    c_val.number_format = FMT_PCT
                elif unit == "$":
                    c_val.number_format = FMT_CURR
                elif unit == "x":
                    c_val.number_format = FMT_MULT
                else:
                    c_val.number_format = FMT_DEC
            elif isinstance(val, int):
                c_val.number_format = FMT_CURR if unit == "$" else FMT_INT

            c_unit = ws2.cell(row=r_idx, column=4, value=unit)
            c_unit.font = regular_font
            c_unit.alignment = Alignment(horizontal="center")

            c_notes = ws2.cell(row=r_idx, column=5, value=notes)
            c_notes.font = italic_font

            r_idx += 1
        return r_idx + 1

    # 1. Target Addressable Accounts
    row_curr = write_gtm_assumption_section(5, "1. IDEAL CUSTOMER PROFILE (ICP) & TARGET ACCOUNT UNIVERSE",
        ["Segment / Tier", "Target Accounts", "Unit", "Institutional Profile & Inclusions"],
        [
            ("Tier 1: Global Market Makers & High-Volume Arbs", 45, "Desks", "Wintermute, Jump, GSR, FalconX, Flow Traders, QCP Capital"),
            ("Tier 2: Systematic Macro & Crypto Hedge Funds", 250, "Funds", "Brevan Howard, Galaxy, Pantera, Polychain, Point72 Crypto, Millennium"),
            ("Tier 3: Quantitative Prop Desks & Multi-Strat Boutiques", 600, "Desks", "Chicago/NYC prop trading firms executing statistical arbitrage"),
            ("Tier 4: Algorithmic Long-Tail Quant API Traders", 2200, "Traders", "Independent quant bots, Python systematic developers, sub-fund desks"),
            ("Total Global Institutional Target Market Universe", 3095, "Accounts", "Total accessible universe of institutions executing prediction flow"),
        ]
    )

    # 2. Funnel Stage Conversion Rates
    row_curr = write_gtm_assumption_section(row_curr, "2. INSTITUTIONAL PIPELINE STAGE CONVERSION BENCHMARKS",
        ["Pipeline Stage Transition", "Conversion Rate", "Unit", "Industry Benchmark / Institutional Validation Criteria"],
        [
            ("Visitor / Viewer to Inbound Inquiry / SDK Clone", 0.045, "%", "4.5% conversion of technical visitors exploring GitHub/docs"),
            ("Engaged Account to Marketing Qualified Account (MQL)", 0.250, "%", "25.0% qualification (verified hedge fund / quant domain, >$10M AUM)"),
            ("MQL to Sales Qualified Opportunity (SQL)", 0.400, "%", "40.0% transition (Head of Trading / CIO demo scheduled)"),
            ("SQL to Technical POC / Sandbox Trial Deployment", 0.600, "%", "60.0% install API keys, run historical paper-arb simulator"),
            ("Technical POC to Compliance, Security & Legal Review", 0.700, "%", "70.0% pass latency SLA (<0.5ms) & slippage proof (>200 bps saved)"),
            ("Compliance / Legal Review to Closed Won Master Contract", 0.800, "%", "80.0% master service agreement (MSA) signed and live trading desk"),
            ("Full-Funnel Cumulative MQL to Closed-Won Win Rate", 0.0672, "%", "MQL to Closed Won compounding rate (0.25*0.40*0.60*0.70*0.80 = 6.72%)"),
        ]
    )

    # 3. Contract Values & Deal Duration
    row_curr = write_gtm_assumption_section(row_curr, "3. CONTRACT VALUES (ACV) & SALES CYCLE DURATION",
        ["Contract Metric", "Value", "Unit", "Strategic Context / Sourced Mix"],
        [
            ("Tier 1 Core Quant API Annual ACV", 30000, "$", "$2,500/mo base systematic API connection"),
            ("Tier 2 Institutional Desk (Flagship) Annual ACV", 144000, "$", "$12,000/mo multi-seat terminal + Parity Radar"),
            ("Tier 3 Prime Direct (Enterprise) Annual ACV", 420000, "$", "$35,000/mo dedicated VPC + custom TWAP algos"),
            ("Blended Average Annual Contract Value (ACV)", 162000, "$", "Weighted average ACV across Tier 1, 2, and 3 contracts"),
            ("Average Institutional Sales Cycle Duration", 45, "Days", "Initial discovery call to live capital deployment"),
            ("Marketing Pipeline Quota Coverage Target", 3.5, "x", "Minimum pipeline generated required to guarantee ARR targets"),
        ]
    )

    # 4. Program Cost Benchmarks
    row_curr = write_gtm_assumption_section(row_curr, "4. MARKETING PROGRAM COSTS & CAMPAIGN BENCHMARKS",
        ["Marketing Program / Asset", "Unit Cost", "Unit", "Scope of Deliverable / Execution Standard"],
        [
            ("Proprietary Quant Alpha Research Whitepaper", 12000, "$", "Deep microstructure data analysis + distribution to 5,000 CIOs"),
            ("Private Executive VIP Salon / Dinner (NYC/London/SG)", 15000, "$", "Exclusive 12-person dinner for Heads of Trading & Macro CIOs"),
            ("Tier-1 Conference Major Presence (FIA Boca, Consensus)", 45000, "$", "Executive meeting suite, stage keynote, VIP networking reception"),
            ("Technical Sales Engineering POC Enablement Cost", 5000, "$", "Dedicated integration engineer hours per trial sandbox"),
            ("Target Inbound Cost per Qualified Lead (CPL)", 850, "$", "Blended paid search, technical newsletters, and retargeting"),
        ]
    )

    # =========================================================================
    # TAB 3: FUNNEL & PIPELINE (12-MONTH WATERFALL)
    # =========================================================================
    ws3 = wb.create_sheet(title="Funnel & Pipeline")
    ws3.views.sheetView[0].showGridLines = True

    ws3["B2"] = "PRISM 12-MONTH INSTITUTIONAL PIPELINE & FUNNEL WATERFALL"
    ws3["B2"].font = title_font
    ws3["B3"] = "Stage-by-Stage Account Progression from Inbound Awareness to Live Trading Desks"
    ws3["B3"].font = subtitle_font

    months = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6",
              "Month 7", "Month 8", "Month 9", "Month 10", "Month 11", "Month 12", "Full Year 1"]

    ws3.cell(row=5, column=2, value="Funnel Stage / Pipeline Metric").font = table_header_font
    ws3.cell(row=5, column=2).fill = header_fill
    for m_idx, m_name in enumerate(months, start=3):
        c = ws3.cell(row=5, column=m_idx, value=m_name)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="right")

    # Funnel rows:
    # Top of funnel
    # Middle of funnel
    # Late funnel
    # Pipeline velocity
    funnel_data = [
        # Top of Funnel
        ("TOP OF FUNNEL (AWARENESS & ENGAGEMENT)", None, None),
        ("Unique Technical Web Visitors", [1200, 1600, 2200, 3100, 4200, 5500, 6800, 8200, 9800, 11500, 13500, 16000], FMT_INT),
        ("Quant Research & Alpha Whitepaper Downloads", [85, 120, 180, 260, 380, 510, 650, 810, 990, 1200, 1450, 1750], FMT_INT),
        ("GitHub Repo Stars & Python/Rust SDK Clones", [45, 70, 110, 165, 240, 330, 430, 550, 680, 830, 1000, 1200], FMT_INT),
        ("Developer Sandbox API Registrations", [18, 26, 38, 54, 76, 102, 132, 168, 208, 254, 306, 368], FMT_INT),
        ("Total Engaged Target Accounts", ["=SUM(C8:C10)", "=SUM(D8:D10)", "=SUM(E8:E10)", "=SUM(F8:F10)", "=SUM(G8:G10)", "=SUM(H8:H10)", "=SUM(I8:I10)", "=SUM(J8:J10)", "=SUM(K8:K10)", "=SUM(L8:L10)", "=SUM(M8:M10)", "=SUM(N8:N10)"], FMT_INT),
        ("---", None, None),
        # Middle of Funnel
        ("MIDDLE OF FUNNEL (QUALIFICATION & DISCOVERY)", None, None),
        ("Inbound Demo Requests & Form Submissions", [12, 16, 24, 32, 42, 55, 68, 82, 98, 115, 135, 160], FMT_INT),
        ("Marketing Qualified Accounts (MQLs)", ["=ROUND(C14*'GTM Assumptions'!C16, 0)", "=ROUND(D14*'GTM Assumptions'!C16, 0)", "=ROUND(E14*'GTM Assumptions'!C16, 0)", "=ROUND(F14*'GTM Assumptions'!C16, 0)", "=ROUND(G14*'GTM Assumptions'!C16, 0)", "=ROUND(H14*'GTM Assumptions'!C16, 0)", "=ROUND(I14*'GTM Assumptions'!C16, 0)", "=ROUND(J14*'GTM Assumptions'!C16, 0)", "=ROUND(K14*'GTM Assumptions'!C16, 0)", "=ROUND(L14*'GTM Assumptions'!C16, 0)", "=ROUND(M14*'GTM Assumptions'!C16, 0)", "=ROUND(N14*'GTM Assumptions'!C16, 0)"], FMT_INT),
        ("Discovery Calls Scheduled (Head of Trading)", [6, 8, 12, 16, 21, 28, 34, 41, 49, 58, 68, 80], FMT_INT),
        ("Sales Qualified Opportunities (SQLs)", ["=ROUND(C16*'GTM Assumptions'!C17, 0)", "=ROUND(D16*'GTM Assumptions'!C17, 0)", "=ROUND(E16*'GTM Assumptions'!C17, 0)", "=ROUND(F16*'GTM Assumptions'!C17, 0)", "=ROUND(G16*'GTM Assumptions'!C17, 0)", "=ROUND(H16*'GTM Assumptions'!C17, 0)", "=ROUND(I16*'GTM Assumptions'!C17, 0)", "=ROUND(J16*'GTM Assumptions'!C17, 0)", "=ROUND(K16*'GTM Assumptions'!C17, 0)", "=ROUND(L16*'GTM Assumptions'!C17, 0)", "=ROUND(M16*'GTM Assumptions'!C17, 0)", "=ROUND(N16*'GTM Assumptions'!C17, 0)"], FMT_INT),
        ("Pipeline Dollar Value Created ($)", ["=C17*'GTM Assumptions'!C28", "=D17*'GTM Assumptions'!C28", "=E17*'GTM Assumptions'!C28", "=F17*'GTM Assumptions'!C28", "=G17*'GTM Assumptions'!C28", "=H17*'GTM Assumptions'!C28", "=I17*'GTM Assumptions'!C28", "=J17*'GTM Assumptions'!C28", "=K17*'GTM Assumptions'!C28", "=L17*'GTM Assumptions'!C28", "=M17*'GTM Assumptions'!C28", "=N17*'GTM Assumptions'!C28"], FMT_CURR),
        ("---", None, None),
        # Late Funnel
        ("LATE FUNNEL (EVALUATION & CLOSING)", None, None),
        ("Technical Sandbox POCs Launched", ["=ROUND(C17*'GTM Assumptions'!C18, 0)", "=ROUND(D17*'GTM Assumptions'!C18, 0)", "=ROUND(E17*'GTM Assumptions'!C18, 0)", "=ROUND(F17*'GTM Assumptions'!C18, 0)", "=ROUND(G17*'GTM Assumptions'!C18, 0)", "=ROUND(H17*'GTM Assumptions'!C18, 0)", "=ROUND(I17*'GTM Assumptions'!C18, 0)", "=ROUND(J17*'GTM Assumptions'!C18, 0)", "=ROUND(K17*'GTM Assumptions'!C18, 0)", "=ROUND(L17*'GTM Assumptions'!C18, 0)", "=ROUND(M17*'GTM Assumptions'!C18, 0)", "=ROUND(N17*'GTM Assumptions'!C18, 0)"], FMT_INT),
        ("Compliance & Security Due Diligence Reviews", ["=ROUND(C21*'GTM Assumptions'!C19, 0)", "=ROUND(D21*'GTM Assumptions'!C19, 0)", "=ROUND(E21*'GTM Assumptions'!C19, 0)", "=ROUND(F21*'GTM Assumptions'!C19, 0)", "=ROUND(G21*'GTM Assumptions'!C19, 0)", "=ROUND(H21*'GTM Assumptions'!C19, 0)", "=ROUND(I21*'GTM Assumptions'!C19, 0)", "=ROUND(J21*'GTM Assumptions'!C19, 0)", "=ROUND(K21*'GTM Assumptions'!C19, 0)", "=ROUND(L21*'GTM Assumptions'!C19, 0)", "=ROUND(M21*'GTM Assumptions'!C19, 0)", "=ROUND(N21*'GTM Assumptions'!C19, 0)"], FMT_INT),
        ("New Closed Won Institutional Desks", [1, 0, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1], FMT_INT),
        ("Cumulative Live Trading Desks", ["=C23", "=C24+D23", "=D24+E23", "=E24+F23", "=F24+G23", "=G24+H23", "=H24+I23", "=I24+J23", "=J24+K23", "=K24+L23", "=L24+M23", "=M24+N23"], FMT_INT),
        ("Monthly Sourced New ARR ($)", ["=C23*'GTM Assumptions'!C28", "=D23*'GTM Assumptions'!C28", "=E23*'GTM Assumptions'!C28", "=F23*'GTM Assumptions'!C28", "=G23*'GTM Assumptions'!C28", "=H23*'GTM Assumptions'!C28", "=I23*'GTM Assumptions'!C28", "=J23*'GTM Assumptions'!C28", "=K23*'GTM Assumptions'!C28", "=L23*'GTM Assumptions'!C28", "=M23*'GTM Assumptions'!C28", "=N23*'GTM Assumptions'!C28"], FMT_CURR),
        ("Cumulative Sourced ARR ($)", ["=C25", "=C26+D25", "=D26+E25", "=E26+F25", "=F26+G25", "=G26+H25", "=H26+I25", "=I26+J25", "=J26+K25", "=K26+L25", "=L26+M25", "=M26+N25"], FMT_CURR),
        ("---", None, None),
        # Pipeline Efficiency
        ("PIPELINE VELOCITY & COVERAGE", None, None),
        ("Monthly Pipeline Coverage Ratio (vs Target)", ["=C18/(C25+1)", "=D18/(D25+1)", "=E18/(E25+1)", "=F18/(F25+1)", "=G18/(G25+1)", "=H18/(H25+1)", "=I18/(I25+1)", "=J18/(J25+1)", "=K18/(K25+1)", "=L18/(L25+1)", "=M18/(M25+1)", "=N18/(N25+1)"], FMT_MULT),
        ("Monthly Pipeline Velocity Index ($/Day)", ["=(C17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(D17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(E17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(F17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(G17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(H17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(I17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(J17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(K17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(L17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(M17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29", "=(N17*'GTM Assumptions'!C21*'GTM Assumptions'!C28)/'GTM Assumptions'!C29"], FMT_CURR),
    ]

    r_idx = 6
    for label, vals, fmt in funnel_data:
        if label == "---":
            r_idx += 1
            continue
        is_header = vals is None
        is_key = "Total" in label or "Closed Won" in label or "Cumulative" in label or "Pipeline Dollar" in label or "Coverage" in label
        c_lbl = ws3.cell(row=r_idx, column=2, value=label)
        c_lbl.font = Font(name=FONT_FAMILY, size=10, bold=True, color=BLUE_ACCENT if is_header else "000000")
        if is_header:
            c_lbl.fill = section_fill
            ws3.merge_cells(start_row=r_idx, start_column=2, end_row=r_idx, end_column=15)
            r_idx += 1
            continue

        for c_offset, v in enumerate(vals):
            c = ws3.cell(row=r_idx, column=3 + c_offset, value=v)
            c.number_format = fmt
            c.font = bold_font if is_key else regular_font
            c.alignment = Alignment(horizontal="right")
            if "Cumulative Sourced ARR" in label or "Closed Won" in label:
                c.fill = success_fill
                c.border = subtotal_border
            elif is_key:
                c.fill = highlight_fill

        # Full Year Column (Col 15 / O)
        if label in ["Unique Technical Web Visitors", "Quant Research & Alpha Whitepaper Downloads", "GitHub Repo Stars & Python/Rust SDK Clones", "Developer Sandbox API Registrations", "Total Engaged Target Accounts", "Inbound Demo Requests & Form Submissions", "Marketing Qualified Accounts (MQLs)", "Discovery Calls Scheduled (Head of Trading)", "Sales Qualified Opportunities (SQLs)", "Pipeline Dollar Value Created ($)", "Technical Sandbox POCs Launched", "Compliance & Security Due Diligence Reviews", "New Closed Won Institutional Desks", "Monthly Sourced New ARR ($)"]:
            c_tot = ws3.cell(row=r_idx, column=15, value=f"=SUM(C{r_idx}:N{r_idx})")
        elif "Cumulative" in label:
            c_tot = ws3.cell(row=r_idx, column=15, value=f"=N{r_idx}")
        elif "Coverage" in label:
            c_tot = ws3.cell(row=r_idx, column=15, value=f"=O18/O25")
        elif "Velocity" in label:
            c_tot = ws3.cell(row=r_idx, column=15, value=f"=AVERAGE(C{r_idx}:N{r_idx})")
        else:
            c_tot = ws3.cell(row=r_idx, column=15, value=f"=SUM(C{r_idx}:N{r_idx})")

        c_tot.number_format = fmt
        c_tot.font = bold_font
        c_tot.alignment = Alignment(horizontal="right")
        c_tot.fill = highlight_fill
        c_tot.border = subtotal_border

        r_idx += 1

    # =========================================================================
    # TAB 4: CHANNEL ECONOMICS & ROI
    # =========================================================================
    ws4 = wb.create_sheet(title="Channel Economics")
    ws4.views.sheetView[0].showGridLines = True

    ws4["B2"] = "PRISM INSTITUTIONAL MARKETING CHANNELS & UNIT ECONOMICS"
    ws4["B2"].font = title_font
    ws4["B3"] = "Comparative Analysis of CAC, LTV/CAC, Payback & Sourced Revenue by Acquisition Channel"
    ws4["B3"].font = subtitle_font

    ws4["B5"] = "ACQUISITION CHANNEL PERFORMANCE MATRIX (YEAR 1 ACTUAL / BUDGET)"
    ws4["B5"].font = section_font
    ws4["B5"].fill = section_fill
    ws4.merge_cells("B5:M5")

    ch_headers = [
        "Marketing Acquisition Channel", "Target Persona / Playbook", "Annual Budget",
        "MQLs", "SQLs", "POC Trials", "Closed Won", "Sourced ARR",
        "Channel CAC", "Channel LTV", "LTV / CAC", "Payback (Mo)"
    ]

    for idx, h in enumerate(ch_headers, start=2):
        c = ws4.cell(row=6, column=idx, value=h)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="left" if idx <= 3 else "right")

    channels_data = [
        ("Account-Based Marketing (ABM) & Outbound", "Top 50 MM & Macro Funds (Wintermute, Jump)", 85000, 32, 14, 8, 4, "=H7*'GTM Assumptions'!C28", "=D7/H7", 3384000, "=K7/J7", "=(J7/(I7/H7))*12"),
        ("Quantitative Research & Alpha Whitepapers", "Systematic PMs, Quant Researchers", 55000, 48, 18, 10, 3, "=H8*'GTM Assumptions'!C28", "=D8/H8", 3384000, "=K8/J8", "=(J8/(I8/H8))*12"),
        ("Developer Relations & Open Source SDKs", "Quant Algo Developers, Python/Rust Bots", 65000, 55, 16, 9, 2, "=H9*'GTM Assumptions'!C28", "=D9/H9", 345000, "=K9/J9", "=(J9/(I9/H9))*12"),
        ("Industry Conferences & Executive VIP Salons", "Heads of Trading, CIOs, Managing Partners", 115000, 24, 12, 7, 2, "=H10*'GTM Assumptions'!C28", "=D10/H10", 3384000, "=K10/J10", "=(J10/(I10/H10))*12"),
        ("Exchange & Venue Ecosystem Co-Marketing", "Polymarket & Kalshi Institutional Flow", 40000, 35, 15, 8, 1, "=H11*'GTM Assumptions'!C28", "=D11/H11", 20160000, "=K11/J11", "=(J11/(I11/H11))*12"),
    ]

    r_idx = 7
    for ch in channels_data:
        ws4.cell(row=r_idx, column=2, value=ch[0]).font = bold_font
        ws4.cell(row=r_idx, column=3, value=ch[1]).font = italic_font

        ws4.cell(row=r_idx, column=4, value=ch[2]).number_format = FMT_CURR
        ws4.cell(row=r_idx, column=5, value=ch[3]).number_format = FMT_INT
        ws4.cell(row=r_idx, column=6, value=ch[4]).number_format = FMT_INT
        ws4.cell(row=r_idx, column=7, value=ch[5]).number_format = FMT_INT
        ws4.cell(row=r_idx, column=8, value=ch[6]).number_format = FMT_INT

        c_arr = ws4.cell(row=r_idx, column=9, value=ch[7])
        c_arr.number_format = FMT_CURR
        c_arr.font = bold_font

        c_cac = ws4.cell(row=r_idx, column=10, value=ch[8])
        c_cac.number_format = FMT_CURR

        c_ltv = ws4.cell(row=r_idx, column=11, value=ch[9])
        c_ltv.number_format = FMT_CURR

        c_ltvcac = ws4.cell(row=r_idx, column=12, value=ch[10])
        c_ltvcac.number_format = FMT_MULT
        c_ltvcac.font = bold_font
        c_ltvcac.fill = highlight_fill

        c_payback = ws4.cell(row=r_idx, column=13, value=ch[11])
        c_payback.number_format = FMT_DEC

        for c_i in range(4, 14):
            ws4.cell(row=r_idx, column=c_i).alignment = Alignment(horizontal="right")

        r_idx += 1

    # Totals Row (Row 13)
    r_idx = 13
    ws4.cell(row=r_idx, column=2, value="TOTAL / BLENDED PORTFOLIO AVERAGE").font = bold_font
    ws4.cell(row=r_idx, column=4, value="=SUM(D7:D11)").number_format = FMT_CURR
    ws4.cell(row=r_idx, column=5, value="=SUM(E7:E11)").number_format = FMT_INT
    ws4.cell(row=r_idx, column=6, value="=SUM(F7:F11)").number_format = FMT_INT
    ws4.cell(row=r_idx, column=7, value="=SUM(G7:G11)").number_format = FMT_INT
    ws4.cell(row=r_idx, column=8, value="=SUM(H7:H11)").number_format = FMT_INT
    ws4.cell(row=r_idx, column=9, value="=SUM(I7:I11)").number_format = FMT_CURR
    ws4.cell(row=r_idx, column=10, value="=D13/H13").number_format = FMT_CURR  # Blended CAC
    ws4.cell(row=r_idx, column=11, value="=AVERAGE(K7:K11)").number_format = FMT_CURR
    ws4.cell(row=r_idx, column=12, value="=K13/J13").number_format = FMT_MULT
    ws4.cell(row=r_idx, column=13, value="=(J13/(I13/H13))*12").number_format = FMT_DEC

    for c_i in range(2, 14):
        cell = ws4.cell(row=r_idx, column=c_i)
        cell.font = bold_font
        cell.fill = highlight_fill
        cell.border = top_thin_bottom_double
        if c_i >= 4:
            cell.alignment = Alignment(horizontal="right")

    # =========================================================================
    # TAB 5: MARKETING BUDGET & OPEX
    # =========================================================================
    ws5 = wb.create_sheet(title="Marketing Budget")
    ws5.views.sheetView[0].showGridLines = True

    ws5["B2"] = "PRISM 12-MONTH MARKETING BUDGET & OPEX ALLOCATION"
    ws5["B2"].font = title_font
    ws5["B3"] = "Headcount, Program Spend, MarTech Infrastructure, and Capital Efficiency Monitoring"
    ws5["B3"].font = subtitle_font

    ws5.cell(row=5, column=2, value="Budget Category / Line Item").font = table_header_font
    ws5.cell(row=5, column=2).fill = header_fill
    for m_idx, m_name in enumerate(months, start=3):
        c = ws5.cell(row=5, column=m_idx, value=m_name)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="right")

    budget_data = [
        # 1. Headcount
        ("1. MARKETING PERSONNEL & HEADCOUNT", None),
        ("VP Marketing / Chief Marketing Officer", [18300, 18300, 18300, 18300, 18300, 18300, 18300, 18300, 18300, 18300, 18300, 18300]),
        ("Quantitative Research & Content Lead", [0, 15250, 15250, 15250, 15250, 15250, 15250, 15250, 15250, 15250, 15250, 15250]),
        ("Developer Relations & Quant Evangelist", [0, 0, 16267, 16267, 16267, 16267, 16267, 16267, 16267, 16267, 16267, 16267]),
        ("Events & Growth Operations Specialist", [0, 0, 0, 11183, 11183, 11183, 11183, 11183, 11183, 11183, 11183, 11183]),
        ("Total Marketing Headcount Cost", ["=SUM(C7:C10)", "=SUM(D7:D10)", "=SUM(E7:E10)", "=SUM(F7:F10)", "=SUM(G7:G10)", "=SUM(H7:H10)", "=SUM(I7:I10)", "=SUM(J7:J10)", "=SUM(K7:K10)", "=SUM(L7:L10)", "=SUM(M7:M10)", "=SUM(N7:N10)"]),
        ("---", None),
        # 2. Programs & Campaigns
        ("2. MARKETING CAMPAIGNS & PROGRAM SPEND", None),
        ("Proprietary Quant Alpha Research Reports", [0, 12000, 0, 12000, 0, 12000, 0, 12000, 0, 12000, 0, 12000]),
        ("Sponsored Technical Media & Retargeting", [3500, 4500, 5000, 5000, 5500, 5500, 6000, 6000, 6500, 6500, 7000, 7000]),
        ("Major Conferences & Executive VIP Salons", [0, 15000, 45000, 0, 15000, 45000, 0, 15000, 0, 30000, 15000, 0]),
        ("DevRel Hackathons, Bug Bounties & Grants", [0, 0, 10000, 0, 0, 15000, 0, 0, 15000, 0, 0, 10000]),
        ("Institutional PR & Communications Agency", [6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000]),
        ("Design, Brand Identity & Motion Assets", [5000, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500]),
        ("Total Marketing Program Spend", ["=SUM(C14:C19)", "=SUM(D14:D19)", "=SUM(E14:E19)", "=SUM(F14:F19)", "=SUM(G14:G19)", "=SUM(H14:H19)", "=SUM(I14:I19)", "=SUM(J14:J19)", "=SUM(K14:K19)", "=SUM(L14:L19)", "=SUM(M14:M19)", "=SUM(N14:N19)"]),
        ("---", None),
        # 3. Technology & Tools
        ("3. MARKETING TECHNOLOGY & SOFTWARE (MARTECH)", None),
        ("HubSpot / Salesforce Enterprise CRM", [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000]),
        ("6sense / Demandbase ABM Intent Data", [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000]),
        ("Apollo / ZoomInfo Verified Contacts", [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]),
        ("Webflow, Segment, Hosting & Analytics", [800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800, 800]),
        ("Total MarTech & Tooling Spend", ["=SUM(C23:C26)", "=SUM(D23:D26)", "=SUM(E23:E26)", "=SUM(F23:F26)", "=SUM(G23:G26)", "=SUM(H23:H26)", "=SUM(I23:I26)", "=SUM(J23:J26)", "=SUM(K23:K26)", "=SUM(L23:L26)", "=SUM(M23:M26)", "=SUM(N23:N26)"]),
        ("---", None),
        # Total Summary
        ("TOTAL MARKETING & GTM OUTFLOW", ["=C11+C20+C27", "=D11+D20+D27", "=E11+E20+E27", "=F11+F20+F27", "=G11+G20+G27", "=H11+H20+H27", "=I11+I20+I27", "=J11+J20+J27", "=K11+K20+K27", "=L11+L20+L27", "=M11+M20+M27", "=N11+N20+N27"]),
        ("Cumulative Marketing Spend ($)", ["=C29", "=C30+D29", "=D30+E29", "=E30+F29", "=F30+G29", "=G30+H29", "=H30+I29", "=I30+J29", "=J30+K29", "=K30+L29", "=L30+M29", "=M30+N29"]),
        ("Monthly Sourced ARR ($)", ["='Funnel & Pipeline'!C25", "='Funnel & Pipeline'!D25", "='Funnel & Pipeline'!E25", "='Funnel & Pipeline'!F25", "='Funnel & Pipeline'!G25", "='Funnel & Pipeline'!H25", "='Funnel & Pipeline'!I25", "='Funnel & Pipeline'!J25", "='Funnel & Pipeline'!K25", "='Funnel & Pipeline'!L25", "='Funnel & Pipeline'!M25", "='Funnel & Pipeline'!N25"]),
        ("Cumulative Sourced ARR ($)", ["='Funnel & Pipeline'!C26", "='Funnel & Pipeline'!D26", "='Funnel & Pipeline'!E26", "='Funnel & Pipeline'!F26", "='Funnel & Pipeline'!G26", "='Funnel & Pipeline'!H26", "='Funnel & Pipeline'!I26", "='Funnel & Pipeline'!J26", "='Funnel & Pipeline'!K26", "='Funnel & Pipeline'!L26", "='Funnel & Pipeline'!M26", "='Funnel & Pipeline'!N26"]),
        ("Marketing Efficiency (Sourced ARR / Spend)", ["=C32/C30", "=D32/D30", "=E32/E30", "=F32/F30", "=G32/G30", "=H32/H30", "=I32/I30", "=J32/J30", "=K32/K30", "=L32/L30", "=M32/M30", "=N32/N30"]),
    ]

    r_idx = 6
    for label, vals in budget_data:
        if label == "---":
            r_idx += 1
            continue
        is_header = vals is None
        is_total = "TOTAL" in label or "Cumulative" in label
        c_lbl = ws5.cell(row=r_idx, column=2, value=label)
        c_lbl.font = Font(name=FONT_FAMILY, size=10, bold=True, color=BLUE_ACCENT if is_header else "000000")
        if is_header:
            c_lbl.fill = section_fill
            ws5.merge_cells(start_row=r_idx, start_column=2, end_row=r_idx, end_column=15)
            r_idx += 1
            continue

        for c_offset, v in enumerate(vals):
            c = ws5.cell(row=r_idx, column=3 + c_offset, value=v)
            c.number_format = FMT_MULT if "Efficiency" in label else FMT_CURR
            c.font = bold_font if is_total else regular_font
            c.alignment = Alignment(horizontal="right")
            if "TOTAL MARKETING" in label:
                c.fill = highlight_fill
                c.border = top_thin_bottom_double
            elif is_total:
                c.fill = highlight_fill

        # Full Year Column (Col 15 / O)
        if "Efficiency" in label:
            c_tot = ws5.cell(row=r_idx, column=15, value=f"=O31/O29")
            c_tot.number_format = FMT_MULT
        elif "Cumulative" in label:
            c_tot = ws5.cell(row=r_idx, column=15, value=f"=N{r_idx}")
            c_tot.number_format = FMT_CURR
        elif label == "Monthly Sourced ARR ($)":
            c_tot = ws5.cell(row=r_idx, column=15, value=f"='Funnel & Pipeline'!O25")
            c_tot.number_format = FMT_CURR
        else:
            c_tot = ws5.cell(row=r_idx, column=15, value=f"=SUM(C{r_idx}:N{r_idx})")
            c_tot.number_format = FMT_CURR

        c_tot.font = bold_font
        c_tot.alignment = Alignment(horizontal="right")
        c_tot.fill = highlight_fill
        c_tot.border = subtotal_border

        r_idx += 1

    # =========================================================================
    # TAB 6: GTM LAUNCH CALENDAR
    # =========================================================================
    ws6 = wb.create_sheet(title="GTM Launch Calendar")
    ws6.views.sheetView[0].showGridLines = True

    ws6["B2"] = "PRISM 12-MONTH GO-TO-MARKET EXECUTION ROADMAP"
    ws6["B2"].font = title_font
    ws6["B3"] = "Chronological Milestones, Campaign Activations, Research Launches, and Field Marketing"
    ws6["B3"].font = subtitle_font

    ws6["B5"] = "ANNUAL GTM EXECUTION CALENDAR & PRODUCT MARKETING ROADMAP"
    ws6["B5"].font = section_font
    ws6["B5"].fill = section_fill
    ws6.merge_cells("B5:H5")

    cal_headers = ["Month", "Quarter", "Campaign / Milestone Initiative", "Category", "Target Audience", "Key Deliverable / Asset", "Primary KPI Target"]
    for idx, h in enumerate(cal_headers, start=2):
        c = ws6.cell(row=6, column=idx, value=h)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="left" if idx > 3 else "center")

    roadmap_data = [
        ("Month 1", "Q1", "Brand & Institutional Website Relaunch", "Brand & Product", "Global Macro & Quant Funds", "Interactive Parity Radar demo & Docs portal", "1,200 unique visitors, 18 API sandboxes"),
        ("Month 2", "Q1", "Research Paper: 'The Cross-Venue Liquidity Gap'", "Quant Research", "Systematic Crypto & Prop Desks", "18-page microstructure whitepaper + dataset", "500 downloads, 15 inbound MQLs"),
        ("Month 3", "Q1", "Consensus & FIA Boca Private Dinner Salon", "Field Marketing", "Top 20 Crypto Market Makers & Arbs", "12-person private VIP dinner in Delray Beach", "4 Technical POCs launched"),
        ("Month 4", "Q2", "PRISM Python & Rust SDK v1.0 Launch", "DevRel & Product", "Systematic Algo Developers", "Open-source GitHub repo, FIX drop-copy guide", "150 stars, 50 git clones, 8 MQLs"),
        ("Month 5", "Q2", "Research Paper: 'Oracle Latency & Resolution Risk'", "Quant Research", "Event-Driven & Macro PMs", "Empirical study on UMA vs Pyth resolution lag", "750 downloads, 20 inbound MQLs"),
        ("Month 6", "Q2", "Tier 2 Institutional Desk Flagship Campaign", "ABM Outbound", "Mid-Tier Multi-Strat Hedge Funds", "Bespoke slippage audit reports per fund", "6 SQLs, 2 live desks signed"),
        ("Month 7", "Q3", "Polymarket & Kalshi Co-Marketing Webinar", "Ecosystem", "Institutional Prediction Market Participants", "Joint technical webinar on order routing efficiency", "800 registrants, 35 MQLs"),
        ("Month 8", "Q3", "London Quant Executive Salon (Mayfair)", "Field Marketing", "UK & European Macro Hedge Funds", "Private salon dinner during London Blockchain Week", "3 Technical POCs launched"),
        ("Month 9", "Q3", "PRISM Quant Trading Hackathon ($50k Prizes)", "DevRel & Community", "Algorithmic Quants & Student Trading Clubs", "Live sandbox paper-arb competition", "250 participating quants, 5 Tier 1 API clients"),
        ("Month 10", "Q4", "Annual 'State of Prediction Markets' Report", "Flagship Content", "Institutional Investors & Industry Media", "Comprehensive 35-page annual market review", "2,500 downloads, Bloomberg/Coindesk press"),
        ("Month 11", "Q4", "Secaucus NY4 Co-Location Expansion Launch", "Enterprise Product", "Tier 1 High-Frequency Market Makers", "Direct 10Gbps cross-connect latency benchmark", "2 Prime Direct / Co-Lo contracts signed"),
        ("Month 12", "Q4", "Annual GTM Retrospective & 2027 Scale Kickoff", "Strategy & Ops", "Internal Executive Team & Board", "Audited cohort CAC, LTV, and ARR attribution deck", "Full Year $1.94M ARR milestone locked"),
    ]

    r_idx = 7
    for row in roadmap_data:
        m, q, init, cat, aud, deliv, kpi = row
        ws6.cell(row=r_idx, column=2, value=m).font = bold_font
        ws6.cell(row=r_idx, column=2).alignment = Alignment(horizontal="center")

        ws6.cell(row=r_idx, column=3, value=q).font = regular_font
        ws6.cell(row=r_idx, column=3).alignment = Alignment(horizontal="center")

        ws6.cell(row=r_idx, column=4, value=init).font = bold_font
        ws6.cell(row=r_idx, column=5, value=cat).font = regular_font
        ws6.cell(row=r_idx, column=6, value=aud).font = regular_font
        ws6.cell(row=r_idx, column=7, value=deliv).font = italic_font
        ws6.cell(row=r_idx, column=8, value=kpi).font = bold_font
        ws6.cell(row=r_idx, column=8).fill = highlight_fill

        r_idx += 1

    # Auto-adjust column widths across all sheets
    for ws in [ws1, ws2, ws3, ws4, ws5, ws6]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row in [2, 3, 4] and col_letter != "B":
                    continue
                val_str = str(cell.value or "")
                if val_str.startswith("="):
                    val_str = "$123,456,789"
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 14)
        ws.column_dimensions["A"].width = 4
        ws.column_dimensions["B"].width = 48

    # Save to project codebase
    output_path = "/Users/harshaghandikota/Liquidity Agent/PRISM_CMO_GoToMarket_Model_v1.xlsx"
    wb.save(output_path)
    print(f"Successfully generated audited CMO model at: {output_path}")

if __name__ == "__main__":
    build_cmo_model()
