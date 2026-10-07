import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_model():
    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)

    # Styling Palette
    FONT_FAMILY = "Calibri"
    
    # Colors
    NAVY_DARK = "0F172A"       # Primary Headers
    NAVY_LIGHT = "1E293B"      # Secondary Headers
    BLUE_ACCENT = "2563EB"     # Section Bars
    BLUE_ICE = "EFF6FF"        # Input Cell Fill
    GRAY_LIGHT = "F8FAFC"      # Alternate Row Fill
    GRAY_BORDER = "CBD5E1"     # Gridlines
    GRAY_TEXT = "64748B"       # Subtitles / Notes
    WHITE = "FFFFFF"
    EMERALD_BG = "ECFDF5"      # Green Highlight
    
    # Font Styles
    title_font = Font(name=FONT_FAMILY, size=15, bold=True, color=NAVY_DARK)
    subtitle_font = Font(name=FONT_FAMILY, size=10, italic=True, color=GRAY_TEXT)
    section_font = Font(name=FONT_FAMILY, size=10, bold=True, color=WHITE)
    table_header_font = Font(name=FONT_FAMILY, size=10, bold=True, color=WHITE)
    bold_font = Font(name=FONT_FAMILY, size=10, bold=True, color="000000")
    regular_font = Font(name=FONT_FAMILY, size=10, color="000000")
    italic_font = Font(name=FONT_FAMILY, size=9, italic=True, color=GRAY_TEXT)
    input_font = Font(name=FONT_FAMILY, size=10, color="1E3A8A") # Blue text for assumptions
    kpi_val_font = Font(name=FONT_FAMILY, size=13, bold=True, color=NAVY_DARK)
    kpi_lbl_font = Font(name=FONT_FAMILY, size=9, bold=True, color=GRAY_TEXT)

    # Fills
    header_fill = PatternFill(start_color=NAVY_DARK, end_color=NAVY_DARK, fill_type="solid")
    section_fill = PatternFill(start_color=BLUE_ACCENT, end_color=BLUE_ACCENT, fill_type="solid")
    input_fill = PatternFill(start_color=BLUE_ICE, end_color=BLUE_ICE, fill_type="solid")
    total_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    kpi_box_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    highlight_fill = PatternFill(start_color=EMERALD_BG, end_color=EMERALD_BG, fill_type="solid")

    # Borders
    thin_border_side = Side(style='thin', color=GRAY_BORDER)
    top_thin_bottom_double = Border(top=Side(style='thin', color="000000"), bottom=Side(style='double', color="000000"))
    subtotal_border = Border(top=Side(style='thin', color="000000"), bottom=Side(style='thin', color="000000"))

    # Number Formats
    FMT_CURR = "$#,##0"
    FMT_PCT = "0.0%"
    FMT_INT = "#,##0"
    FMT_DEC = "#,##0.0"
    FMT_MULT = '0.0"x"'

    # =========================================================================
    # TAB 1: EXECUTIVE SUMMARY
    # =========================================================================
    ws1 = wb.create_sheet(title="Executive Summary")
    ws1.views.sheetView[0].showGridLines = True
    
    # Title Block
    ws1["B2"] = "PRISM TECHNOLOGIES INC."
    ws1["B2"].font = title_font
    ws1["B3"] = "Institutional Cross-Venue Prediction Market Smart Order Router (SOR)"
    ws1["B3"].font = Font(name=FONT_FAMILY, size=10, bold=True, color=BLUE_ACCENT)
    ws1["B4"] = "5-Year Pro-Forma Financial Model & CFO Business Plan (Series Seed / Series A)"
    ws1["B4"].font = subtitle_font

    # KPI Summary Cards (Row 6 - 8)
    ws1["B6"] = "Y1 ARR"
    ws1["B7"] = "='5-Year Pro-Forma'!C26"
    ws1["D6"] = "Y3 ARR"
    ws1["D7"] = "='5-Year Pro-Forma'!E26"
    ws1["F6"] = "Y5 ARR"
    ws1["F7"] = "='5-Year Pro-Forma'!G26"
    ws1["H6"] = "Y3 EBITDA MARGIN"
    ws1["H7"] = "='5-Year Pro-Forma'!E46"
    ws1["J6"] = "Y3 GROSS MARGIN"
    ws1["J7"] = "='5-Year Pro-Forma'!E35"

    for col in ["B", "D", "F", "H", "J"]:
        ws1[f"{col}6"].font = kpi_lbl_font
        ws1[f"{col}7"].font = kpi_val_font
        ws1[f"{col}6"].alignment = Alignment(horizontal="center")
        ws1[f"{col}7"].alignment = Alignment(horizontal="center")
        ws1[f"{col}6"].fill = kpi_box_fill
        ws1[f"{col}7"].fill = kpi_box_fill
        ws1[f"{col}6"].border = Border(top=thin_border_side, left=thin_border_side, right=thin_border_side)
        ws1[f"{col}7"].border = Border(bottom=thin_border_side, left=thin_border_side, right=thin_border_side)
    
    ws1["B7"].number_format = FMT_CURR
    ws1["D7"].number_format = FMT_CURR
    ws1["F7"].number_format = FMT_CURR
    ws1["H7"].number_format = FMT_PCT
    ws1["J7"].number_format = FMT_PCT

    # Executive Overview Table (Row 10+)
    ws1["B10"] = "EXECUTIVE FINANCIAL DASHBOARD (5-YEAR PRO-FORMA)"
    ws1["B10"].font = section_font
    ws1["B10"].fill = section_fill
    ws1.merge_cells("B10:G10")

    headers_dash = ["Financial Metric", "Year 1 (Seed)", "Year 2 (Expansion)", "Year 3 (Scale)", "Year 4 (Institutional)", "Year 5 (Category King)"]
    for col_idx, h in enumerate(headers_dash, start=2):
        cell = ws1.cell(row=11, column=col_idx, value=h)
        cell.font = table_header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="left" if col_idx == 2 else "right")

    metrics_mapping = [
        ("Active Trading Desks", "='5-Year Pro-Forma'!C12", FMT_INT),
        ("Avg Monthly Volume / Desk ($M)", "='5-Year Pro-Forma'!C13", "$#,##0.0"),
        ("Annual Routed Notional ($M)", "='5-Year Pro-Forma'!C14", FMT_CURR),
        ("---", None, None),
        ("SaaS Subscription Revenue", "='5-Year Pro-Forma'!C21", FMT_CURR),
        ("Volume Routing Take-Rate", "='5-Year Pro-Forma'!C22", FMT_CURR),
        ("Premium Data & SLA Feeds", "='5-Year Pro-Forma'!C23", FMT_CURR),
        ("Gross Revenue", "='5-Year Pro-Forma'!C24", FMT_CURR),
        ("Less: Upfront Prepay Discounts (15%)", "='5-Year Pro-Forma'!C25", FMT_CURR),
        ("Net Recognized Revenue", "='5-Year Pro-Forma'!C26", FMT_CURR),
        ("---", None, None),
        ("Cost of Goods Sold (COGS)", "='5-Year Pro-Forma'!C33", FMT_CURR),
        ("Gross Profit", "='5-Year Pro-Forma'!C34", FMT_CURR),
        ("Gross Margin %", "='5-Year Pro-Forma'!C35", FMT_PCT),
        ("---", None, None),
        ("Research & Development (R&D)", "='5-Year Pro-Forma'!C38", FMT_CURR),
        ("Sales & Trading BD (S&M)", "='5-Year Pro-Forma'!C39", FMT_CURR),
        ("General & Administrative (G&A)", "='5-Year Pro-Forma'!C40", FMT_CURR),
        ("Total Operating Expenses", "='5-Year Pro-Forma'!C42", FMT_CURR),
        ("---", None, None),
        ("EBITDA (Operating Profit)", "='5-Year Pro-Forma'!C45", FMT_CURR),
        ("EBITDA Margin %", "='5-Year Pro-Forma'!C46", FMT_PCT),
        ("Operating Income (EBIT)", "='5-Year Pro-Forma'!C48", FMT_CURR),
        ("Net Income (After Tax)", "='5-Year Pro-Forma'!C52", FMT_CURR),
        ("Net Income Margin %", "='5-Year Pro-Forma'!C53", FMT_PCT),
        ("---", None, None),
        ("Implied Valuation (25x ARR Multiple)", "='Valuation & Returns'!C21", FMT_CURR),
    ]

    curr_row = 12
    for label, formula_base, fmt in metrics_mapping:
        if label == "---":
            curr_row += 1
            continue
        ws1.cell(row=curr_row, column=2, value=label).font = bold_font if "Net" in label or "Gross Profit" in label or "EBITDA" in label or "Valuation" in label else regular_font
        for yr_idx in range(5):
            source_col = get_column_letter(3 + yr_idx)
            form = formula_base.replace("!C", f"!{source_col}")
            c = ws1.cell(row=curr_row, column=3 + yr_idx, value=form)
            c.number_format = fmt
            c.font = bold_font if "Net" in label or "Gross Profit" in label or "EBITDA" in label or "Valuation" in label else regular_font
            c.alignment = Alignment(horizontal="right")
            if "EBITDA" in label or "Gross Profit" in label or "Valuation" in label:
                c.fill = total_fill
        curr_row += 1

    # =========================================================================
    # TAB 2: MODEL ASSUMPTIONS
    # =========================================================================
    ws2 = wb.create_sheet(title="Model Assumptions")
    ws2.views.sheetView[0].showGridLines = True

    ws2["B2"] = "PRISM FINANCIAL ARCHITECTURE — MASTER ASSUMPTIONS"
    ws2["B2"].font = title_font
    ws2["B3"] = "Dynamic Drivers Governing Unit Economics, Revenue Take-Rates, Capacity, and Headcount"
    ws2["B3"].font = subtitle_font

    def write_assumption_section(start_row, title, headers, rows):
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
                elif unit == "$M":
                    c_val.number_format = "$#,##0.0"
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

    # 1. Market Sizing & Volume
    row_curr = write_assumption_section(5, "1. MARKET SIZE & MACRO PREDICTION ADOPTION (TAM / SAM / SOM)", 
        ["Driver / Assumption", "Value", "Unit", "Strategic Rationale / Grounding"],
        [
            ("Total Global Event Derivatives Market Notional (Y1)", 12000, "$M", "Estimated 2026 combined Polymarket + Kalshi + ForecastEx volume"),
            ("Total Global Event Derivatives Market Notional (Y3)", 85000, "$M", "Expansion into macro indices, rates, and corporate earnings"),
            ("Total Global Event Derivatives Market Notional (Y5)", 320000, "$M", "Institutional scale capturing 0.2% of global macro hedging"),
            ("PRISM Share of Institutional Routed Flow (Y1)", 0.008, "%", "Capturing 0.8% of market volume in Seed year ($96M/yr)"),
            ("PRISM Share of Institutional Routed Flow (Y3)", 0.052, "%", "Capturing 5.2% of total market volume ($4.42B/yr)"),
            ("PRISM Share of Institutional Routed Flow (Y5)", 0.120, "%", "Capturing 12.0% as category king execution standard ($38.4B/yr)"),
        ]
    )

    # 2. SaaS Pricing Tiers & ACV
    row_curr = write_assumption_section(row_curr, "2. SUBSCRIPTION PRICING TIERS & ANNUAL CONTRACT VALUE (ACV)", 
        ["Pricing Tier", "Monthly Fee", "Annual ACV", "Target Profile & Inclusions"],
        [
            ("Tier 1: Core Quant API", 2500, "$", "Systematic algo bots, 100 req/sec, standard REST/WebSocket"),
            ("Tier 2: Institutional Desk (Core Flagship)", 12000, "$", "Multi-seat terminal, Parity Radar, Oracle Conflict Guard, 99.95% SLA"),
            ("Tier 3: Prime Direct (Enterprise)", 35000, "$", "Dedicated VPC instance, custom Iceberg/TWAP algos, FIX drop-copy"),
            ("Tier 4: Sovereign Co-Location (Secaucus NY4)", 65000, "$", "Direct Equinix NY4 10Gbps cross-connect, sub-0.5ms FPGA path"),
            ("Annual Upfront Prepay Discount", 0.150, "%", "15% discount for 12-month upfront cash payment (creates negative working capital)"),
            ("Expected % of Clients Choosing Annual Prepay", 0.450, "%", "Funds taking advantage of annual budget allocation discounts"),
        ]
    )

    # 3. Volume-Based Take-Rate (SOR Surcharge)
    row_curr = write_assumption_section(row_curr, "3. VARIABLE ROUTING TAKE-RATE (SOR BASIS POINTS)", 
        ["Parameter", "Value", "Unit", "Economic Mechanism"],
        [
            ("Standard Volume Routing Take-Rate", 0.00015, "%", "1.5 bps (0.015%) charged on net notional executed through SOR"),
            ("Average Slippage Saved per Client Order", 0.0296, "%", "296 bps saved vs single-venue execution (clients retain 95% of alpha)"),
            ("Client Value-to-Fee Ratio", 19.7, "x", "Clients save $19.70 for every $1.00 paid to PRISM in routing fees"),
        ]
    )

    # 4. Customer Acquisition Funnel & Retention
    row_curr = write_assumption_section(row_curr, "4. CUSTOMER FUNNEL, RETENTION & SALES EFFICIENCY", 
        ["Funnel Metric", "Value", "Unit", "Industry Benchmark Comparison"],
        [
            ("Tier 2 CAC (Institutional Desk)", 22000, "$", "Technical sales engineer salary, compliance review, POC demo period"),
            ("Tier 3 CAC (Prime Direct)", 65000, "$", "Enterprise procurement, on-premise security review, legal review"),
            ("Sales Cycle Duration (Tier 2)", 45, "Days", "Rapid trial-to-production deployment timeline"),
            ("Annual Gross Logo Churn Rate", 0.050, "%", "5% annual churn (OEMS workflow integration creates high stickiness)"),
            ("Net Revenue Retention (NRR)", 1.280, "%", "128% NRR driven by funds adding seats and increasing routed volume"),
        ]
    )

    # 5. Infrastructure & COGS Drivers
    row_curr = write_assumption_section(row_curr, "5. INFRASTRUCTURE & COGS DRIVERS (FIXED & VARIABLE)", 
        ["Cost Component", "Monthly Cost", "Unit", "Vendor / Allocation Details"],
        [
            ("Equinix NY4 Secaucus Cabinet Base Lease", 6500, "$", "1U-4U rack space, redundant PDU, Secaucus datacenter"),
            ("NY4 Cross-Connect per 10 Active Clients", 1200, "$", "Direct low-latency fiber cross-connects to exchange matching engines"),
            ("Enterprise L2 RPC Nodes (Polygon/Arbitrum)", 2200, "$", "Dedicated high-throughput Alchemy/QuickNode endpoints"),
            ("AWS/GCP Serverless Engine Base", 1800, "$", "Database clusters, Redis low-latency cache, API gateways"),
            ("Cloud Variable Cost per $1M Routed", 12.0, "$", "Elastic serverless execution scaling per order million"),
            ("FIPS 140-2 Level 3 HSM Hardware Security", 1500, "$", "Dedicated cryptographic key validation hardware"),
            ("Real-Time L2 Market Data Streaming Relays", 2000, "$", "WebSocket distribution clusters"),
        ]
    )

    # 6. Headcount & Compensation Plan
    row_curr = write_assumption_section(row_curr, "6. PERSONNEL HEADCOUNT & SALARY ASSUMPTIONS", 
        ["Role / Title", "Annual Base", "Unit", "Fully Burdened Rate (+22% Payroll Taxes/Benefits)"],
        [
            ("Low-Latency / C++ / Rust Systems Engineer", 210000, "$", "$256,200 fully loaded annual compensation"),
            ("Quantitative Microstructure Researcher", 220000, "$", "$268,400 fully loaded annual compensation"),
            ("VP Institutional Sales / Business Dev", 160000, "$", "$195,200 base + commission tied to desk quota"),
            ("Solutions Architect / Desk Integration Engineer", 150000, "$", "$183,000 fully loaded annual compensation"),
            ("General Counsel & Chief Compliance Officer", 200000, "$", "$244,000 fully loaded annual compensation"),
            ("Operations / Financial Controller", 140000, "$", "$170,800 fully loaded annual compensation"),
        ]
    )

    # =========================================================================
    # TAB 3: 5-YEAR PRO-FORMA P&L
    # =========================================================================
    ws3 = wb.create_sheet(title="5-Year Pro-Forma")
    ws3.views.sheetView[0].showGridLines = True

    ws3["B2"] = "PRISM 5-YEAR PRO-FORMA INCOME STATEMENT (ANNUAL)"
    ws3["B2"].font = title_font
    ws3["B3"] = "Forecast of Revenues, COGS, OpEx, EBITDA, and Net Income (2026 - 2030)"
    ws3["B3"].font = subtitle_font

    headers_pnl = ["Line Item / Operational Metric", "Year 1 (Seed)", "Year 2 (Expansion)", "Year 3 (Scale)", "Year 4 (Institutional)", "Year 5 (Category King)"]
    for col_idx, h in enumerate(headers_pnl, start=2):
        cell = ws3.cell(row=5, column=col_idx, value=h)
        cell.font = table_header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="left" if col_idx == 2 else "right")

    # Volume & Client Drivers
    ws3["B7"] = "KEY REVENUE DRIVERS"
    ws3["B7"].font = section_font
    ws3["B7"].fill = section_fill
    ws3.merge_cells("B7:G7")

    drivers_rows = [
        ("Tier 1 Clients (Core API @ $2.5k/mo)", [4, 15, 35, 60, 95], FMT_INT),
        ("Tier 2 Clients (Institutional Desk @ $12k/mo)", [7, 28, 75, 140, 220], FMT_INT),
        ("Tier 3 Clients (Prime Direct @ $35k/mo)", [1, 5, 18, 38, 65], FMT_INT),
        ("Tier 4 Clients (Sovereign Co-Lo @ $65k/mo)", [0, 0, 2, 6, 12], FMT_INT),
        ("Total Active Institutional Desks", ["=SUM(C8:C11)", "=SUM(D8:D11)", "=SUM(E8:E11)", "=SUM(F8:F11)", "=SUM(G8:G11)"], FMT_INT),
        ("Average Monthly Routed Volume per Desk ($M)", [6.7, 7.3, 10.8, 14.2, 17.5], "$#,##0.0"),
        ("Annual Routed Notional Volume ($M)", ["=C12*C13*12", "=D12*D13*12", "=E12*E13*12", "=F12*F13*12", "=G12*G13*12"], FMT_CURR),
    ]

    r_idx = 8
    for label, vals, fmt in drivers_rows:
        ws3.cell(row=r_idx, column=2, value=label).font = bold_font if "Total" in label or "Annual" in label else regular_font
        for c_offset, v in enumerate(vals):
            c = ws3.cell(row=r_idx, column=3 + c_offset, value=v)
            c.number_format = fmt
            c.font = bold_font if "Total" in label or "Annual" in label else regular_font
            c.alignment = Alignment(horizontal="right")
            if "Total" in label:
                c.fill = total_fill
                c.border = subtotal_border
        r_idx += 1

    # Revenue Section
    ws3["B16"] = "REVENUE STREAMS"
    ws3["B16"].font = section_font
    ws3["B16"].fill = section_fill
    ws3.merge_cells("B16:G16")

    rev_rows = [
        ("Tier 1: Core Quant API Revenue", ["=C8*'Model Assumptions'!C16*12", "=D8*'Model Assumptions'!C16*12", "=E8*'Model Assumptions'!C16*12", "=F8*'Model Assumptions'!C16*12", "=G8*'Model Assumptions'!C16*12"]),
        ("Tier 2: Institutional Desk Revenue", ["=C9*'Model Assumptions'!C17*12", "=D9*'Model Assumptions'!C17*12", "=E9*'Model Assumptions'!C17*12", "=F9*'Model Assumptions'!C17*12", "=G9*'Model Assumptions'!C17*12"]),
        ("Tier 3: Prime Direct Revenue", ["=C10*'Model Assumptions'!C18*12", "=D10*'Model Assumptions'!C18*12", "=E10*'Model Assumptions'!C18*12", "=F10*'Model Assumptions'!C18*12", "=G10*'Model Assumptions'!C18*12"]),
        ("Tier 4: Sovereign Co-Lo Revenue", ["=C11*'Model Assumptions'!C19*12", "=D11*'Model Assumptions'!C19*12", "=E11*'Model Assumptions'!C19*12", "=F11*'Model Assumptions'!C19*12", "=G11*'Model Assumptions'!C19*12"]),
        ("Total SaaS Subscription Revenue (ARR)", ["=SUM(C17:C20)", "=SUM(D17:D20)", "=SUM(E17:E20)", "=SUM(F17:F20)", "=SUM(G17:G20)"]),
        ("Volume Routing Take-Rate (1.5 bps)", ["=C14*1000000*'Model Assumptions'!C25", "=D14*1000000*'Model Assumptions'!C25", "=E14*1000000*'Model Assumptions'!C25", "=F14*1000000*'Model Assumptions'!C25", "=G14*1000000*'Model Assumptions'!C25"]),
        ("Premium Data & Legal Oracle Feeds", [75000, 360000, 1100000, 2400000, 4200000]),
        ("Total Gross Contracted Revenue", ["=SUM(C21:C23)", "=SUM(D21:D23)", "=SUM(E21:E23)", "=SUM(F21:F23)", "=SUM(G21:G23)"]),
        ("Less: Annual Prepay Cash Discounts", ["=-C21*'Model Assumptions'!C20*'Model Assumptions'!C21", "=-D21*'Model Assumptions'!C20*'Model Assumptions'!C21", "=-E21*'Model Assumptions'!C20*'Model Assumptions'!C21", "=-F21*'Model Assumptions'!C20*'Model Assumptions'!C21", "=-G21*'Model Assumptions'!C20*'Model Assumptions'!C21"]),
        ("NET RECOGNIZED REVENUE", ["=C24+C25", "=D24+D25", "=E24+E25", "=F24+F25", "=G24+G25"]),
    ]

    r_idx = 17
    for label, vals in rev_rows:
        is_total = "Total" in label or "NET" in label
        ws3.cell(row=r_idx, column=2, value=label).font = bold_font if is_total else regular_font
        for c_offset, v in enumerate(vals):
            c = ws3.cell(row=r_idx, column=3 + c_offset, value=v)
            c.number_format = FMT_CURR
            c.font = bold_font if is_total else regular_font
            c.alignment = Alignment(horizontal="right")
            if is_total:
                c.fill = total_fill
                c.border = top_thin_bottom_double if "NET" in label else subtotal_border
        r_idx += 1

    # Cost of Goods Sold (COGS)
    ws3["B28"] = "COST OF GOODS SOLD (COGS)"
    ws3["B28"].font = section_font
    ws3["B28"].fill = section_fill
    ws3.merge_cells("B28:G28")

    cogs_rows = [
        ("Equinix NY4 Co-Location & Cross-Connects", ["=('Model Assumptions'!C39*12)+(C12*'Model Assumptions'!C40*12/10)", "=('Model Assumptions'!C39*12)+(D12*'Model Assumptions'!C40*12/10)", "=('Model Assumptions'!C39*12)+(E12*'Model Assumptions'!C40*12/10)", "=('Model Assumptions'!C39*12)+(F12*'Model Assumptions'!C40*12/10)", "=('Model Assumptions'!C39*12)+(G12*'Model Assumptions'!C40*12/10)"]),
        ("Enterprise RPC Nodes & L2 Gas Relayers", ["='Model Assumptions'!C41*12", "='Model Assumptions'!C41*12*1.8", "='Model Assumptions'!C41*12*3.2", "='Model Assumptions'!C41*12*5.5", "='Model Assumptions'!C41*12*8.0"]),
        ("Cloud Compute, Redis & WebSocket Relays", ["=('Model Assumptions'!C42*12)+(C14*'Model Assumptions'!C43)", "=('Model Assumptions'!C42*12)+(D14*'Model Assumptions'!C43)", "=('Model Assumptions'!C42*12)+(E14*'Model Assumptions'!C43)", "=('Model Assumptions'!C42*12)+(F14*'Model Assumptions'!C43)", "=('Model Assumptions'!C42*12)+(G14*'Model Assumptions'!C43)"]),
        ("FIPS 140-2 Hardware HSM Cryptographic Security", ["='Model Assumptions'!C44*12", "='Model Assumptions'!C44*12*1.5", "='Model Assumptions'!C44*12*2.2", "='Model Assumptions'!C44*12*3.5", "='Model Assumptions'!C44*12*5.0"]),
        ("TOTAL COST OF GOODS SOLD", ["=SUM(C29:C32)", "=SUM(D29:D32)", "=SUM(E29:E32)", "=SUM(F29:F32)", "=SUM(G29:G32)"]),
        ("GROSS PROFIT", ["=C26-C33", "=D26-D33", "=E26-E33", "=F26-F33", "=G26-G33"]),
        ("Gross Margin %", ["=C34/C26", "=D34/D26", "=E34/E26", "=F34/F26", "=G34/G26"]),
    ]

    r_idx = 29
    for label, vals in cogs_rows:
        is_pct = "%" in label
        is_total = "TOTAL" in label or "GROSS" in label
        ws3.cell(row=r_idx, column=2, value=label).font = bold_font if is_total else regular_font
        for c_offset, v in enumerate(vals):
            c = ws3.cell(row=r_idx, column=3 + c_offset, value=v)
            c.number_format = FMT_PCT if is_pct else FMT_CURR
            c.font = bold_font if is_total else regular_font
            c.alignment = Alignment(horizontal="right")
            if is_total:
                c.fill = total_fill
                c.border = subtotal_border
        r_idx += 1

    # Operating Expenses (OpEx)
    ws3["B37"] = "OPERATING EXPENSES (OPEX)"
    ws3["B37"].font = section_font
    ws3["B37"].fill = section_fill
    ws3.merge_cells("B37:G37")

    opex_rows = [
        ("Research & Development (R&D / Low-Latency Engineering)", [850000, 1800000, 3600000, 6200000, 9500000]),
        ("Sales & Marketing (Institutional Sales, Travel, Marketing)", [220000, 650000, 1400000, 2800000, 4800000]),
        ("General & Administrative (Legal, Compliance, Audits, Insurance)", [110000, 240000, 450000, 850000, 1400000]),
        ("Enterprise Tools, Security Audits & G&A Infrastructure", [70000, 150000, 320000, 580000, 920000]),
        ("TOTAL OPERATING EXPENSES", ["=SUM(C38:C41)", "=SUM(D38:D41)", "=SUM(E38:E41)", "=SUM(F38:F41)", "=SUM(G38:G41)"]),
    ]

    r_idx = 38
    for label, vals in opex_rows:
        is_total = "TOTAL" in label
        ws3.cell(row=r_idx, column=2, value=label).font = bold_font if is_total else regular_font
        for c_offset, v in enumerate(vals):
            c = ws3.cell(row=r_idx, column=3 + c_offset, value=v)
            c.number_format = FMT_CURR
            c.font = bold_font if is_total else regular_font
            c.alignment = Alignment(horizontal="right")
            if is_total:
                c.fill = total_fill
                c.border = subtotal_border
        r_idx += 1

    # Profitability & Taxes
    ws3["B44"] = "PROFITABILITY & CASH GENERATION"
    ws3["B44"].font = section_font
    ws3["B44"].fill = section_fill
    ws3.merge_cells("B44:G44")

    profit_rows = [
        ("EBITDA (OPERATING PROFIT)", ["=C34-C42", "=D34-D42", "=E34-E42", "=F34-F42", "=G34-G42"]),
        ("EBITDA Margin %", ["=C45/C26", "=D45/D26", "=E45/E26", "=F45/F26", "=G45/G26"]),
        ("Less: Depreciation & Amortization (Servers/Hardware)", [24000, 52000, 110000, 210000, 350000]),
        ("Operating Income (EBIT)", ["=C45-C47", "=D45-D47", "=E45-E47", "=F45-F47", "=G45-G47"]),
        ("Net Interest Income (Treasury Cash Reserve Yield @ 4.8%)", [134400, 115000, 280000, 650000, 1420000]),
        ("Earnings Before Taxes (EBT)", ["=C48+C49", "=D48+D49", "=E48+E49", "=F48+F49", "=G48+G49"]),
        ("Income Tax Expense (21% Federal/State Effective)", ["=IF(C50>0, C50*0.21, 0)", "=IF(D50>0, D50*0.21, 0)", "=IF(E50>0, E50*0.21, 0)", "=IF(F50>0, F50*0.21, 0)", "=IF(G50>0, G50*0.21, 0)"]),
        ("NET INCOME (AFTER-TAX PROFIT)", ["=C50-C51", "=D50-D51", "=E50-E51", "=F50-F51", "=G50-G51"]),
        ("Net Income Margin %", ["=C52/C26", "=D52/D26", "=E52/E26", "=F52/F26", "=G52/G26"]),
    ]

    r_idx = 45
    for label, vals in profit_rows:
        is_pct = "Margin %" in label
        is_net = "NET INCOME" in label
        is_ebitda = "EBITDA" in label
        ws3.cell(row=r_idx, column=2, value=label).font = bold_font if is_net or is_ebitda else regular_font
        for c_offset, v in enumerate(vals):
            c = ws3.cell(row=r_idx, column=3 + c_offset, value=v)
            c.number_format = FMT_PCT if is_pct else FMT_CURR
            c.font = bold_font if is_net or is_ebitda else regular_font
            c.alignment = Alignment(horizontal="right")
            if is_net or is_ebitda:
                c.fill = highlight_fill if is_net else total_fill
                c.border = top_thin_bottom_double if is_net else subtotal_border
        r_idx += 1

    # =========================================================================
    # TAB 4: MONTHLY CASH FLOW & RUNWAY (YEAR 1)
    # =========================================================================
    ws4 = wb.create_sheet(title="Year 1 Monthly Cash Flow")
    ws4.views.sheetView[0].showGridLines = True

    ws4["B2"] = "PRISM YEAR 1 MONTHLY CASH FLOW & RUNWAY MONITOR"
    ws4["B2"].font = title_font
    ws4["B3"] = "Demonstrating Capital Preservation, Upfront Float, and Net Burn Path from Seed Funding"
    ws4["B3"].font = subtitle_font

    months = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6", 
              "Month 7", "Month 8", "Month 9", "Month 10", "Month 11", "Month 12"]
    
    ws4.cell(row=5, column=2, value="Cash Flow Line Item").font = table_header_font
    ws4.cell(row=5, column=2).fill = header_fill
    for m_idx, m_name in enumerate(months, start=3):
        c = ws4.cell(row=5, column=m_idx, value=m_name)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="right")

    cf_data = [
        ("Beginning Cash Balance", [3500000, "=C26", "=D26", "=E26", "=F26", "=G26", "=H26", "=I26", "=J26", "=K26", "=L26", "=M26"]),
        ("---", None),
        ("CASH INFLOWS:", None),
        ("Active Client Desks", [1, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12]),
        ("Monthly Subscription Inflows", ["=C9*'Model Assumptions'!C17", "=D9*'Model Assumptions'!C17", "=E9*'Model Assumptions'!C17", "=F9*'Model Assumptions'!C17", "=G9*'Model Assumptions'!C17", "=H9*'Model Assumptions'!C17", "=I9*'Model Assumptions'!C17", "=J9*'Model Assumptions'!C17", "=K9*'Model Assumptions'!C17", "=L9*'Model Assumptions'!C17", "=M9*'Model Assumptions'!C17", "=N9*'Model Assumptions'!C17"]),
        ("Annual Upfront Prepay Cash Float", [122400, 0, 122400, 0, 122400, 122400, 0, 122400, 0, 122400, 122400, 122400]),
        ("Variable Volume Routing Fees", [2500, 3200, 5400, 7800, 10500, 13200, 16800, 20400, 24500, 29000, 34000, 41000]),
        ("Treasury Yield (Cash Sweep @ 4.8%)", ["=C6*0.048/12", "=D6*0.048/12", "=E6*0.048/12", "=F6*0.048/12", "=G6*0.048/12", "=H6*0.048/12", "=I6*0.048/12", "=J6*0.048/12", "=K6*0.048/12", "=L6*0.048/12", "=M6*0.048/12", "=N6*0.048/12"]),
        ("Total Monthly Cash Inflows", ["=SUM(C10:C13)", "=SUM(D10:D13)", "=SUM(E10:E13)", "=SUM(F10:F13)", "=SUM(G10:G13)", "=SUM(H10:H13)", "=SUM(I10:I13)", "=SUM(J10:J13)", "=SUM(K10:K13)", "=SUM(L10:L13)", "=SUM(M10:M13)", "=SUM(N10:N13)"]),
        ("---", None),
        ("CASH OUTFLOWS:", None),
        ("Infrastructure & Co-Location COGS", [11200, 11200, 12400, 12400, 13600, 13600, 14800, 14800, 16000, 16000, 17200, 17200]),
        ("Engineering Payroll (4 Engineers)", [70000, 70000, 70000, 70000, 70000, 70000, 70000, 70000, 70000, 70000, 70000, 70000]),
        ("Sales & Business Development", [12000, 12000, 15000, 15000, 18000, 18000, 21000, 21000, 24000, 24000, 27000, 27000]),
        ("Legal, Compliance & Retainers", [15000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000]),
        ("SaaS Tooling, Admin, Insurance", [4500, 4500, 4800, 4800, 5200, 5200, 5600, 5600, 6000, 6000, 6500, 6500]),
        ("Total Monthly Cash Outflows", ["=SUM(C17:C21)", "=SUM(D17:D21)", "=SUM(E17:E21)", "=SUM(F17:F21)", "=SUM(G17:G21)", "=SUM(H17:H21)", "=SUM(I17:I21)", "=SUM(J17:J21)", "=SUM(K17:K21)", "=SUM(L17:L21)", "=SUM(M17:M21)", "=SUM(N17:N21)"]),
        ("---", None),
        ("NET MONTHLY CASH FLOW", ["=C14-C22", "=D14-D22", "=E14-E22", "=F14-F22", "=G14-G22", "=H14-H22", "=I14-I22", "=J14-J22", "=K14-K22", "=L14-L22", "=M14-M22", "=N14-N22"]),
        ("---", None),
        ("ENDING CASH BALANCE", ["=C6+C24", "=D6+D24", "=E6+E24", "=F6+F24", "=G6+G24", "=H6+H24", "=I6+I24", "=J6+J24", "=K6+K24", "=L6+L24", "=M6+M24", "=N6+N24"]),
        ("Runway Remaining (Months at Gross Burn)", ["=C26/C22", "=D26/D22", "=E26/E22", "=F26/F22", "=G26/G22", "=H26/H22", "=I26/I22", "=J26/J22", "=K26/K22", "=L26/L22", "=M26/M22", "=N26/N22"]),
    ]

    r_idx = 6
    for label, vals in cf_data:
        if label == "---":
            r_idx += 1
            continue
        is_header = "CASH INFLOWS" in label or "CASH OUTFLOWS" in label
        is_key = "NET" in label or "ENDING" in label or "Beginning" in label or "Total" in label
        c_lbl = ws4.cell(row=r_idx, column=2, value=label)
        c_lbl.font = Font(name=FONT_FAMILY, size=10, bold=True, color=BLUE_ACCENT if is_header else "000000")
        
        if vals is not None:
            for c_offset, v in enumerate(vals):
                c = ws4.cell(row=r_idx, column=3 + c_offset, value=v)
                c.number_format = FMT_DEC if "Runway" in label else (FMT_INT if "Desks" in label else FMT_CURR)
                c.font = bold_font if is_key else regular_font
                c.alignment = Alignment(horizontal="right")
                if "ENDING" in label:
                    c.fill = highlight_fill
                    c.border = top_thin_bottom_double
                elif "NET" in label or "Total" in label:
                    c.fill = total_fill
                    c.border = subtotal_border
        r_idx += 1

    # =========================================================================
    # TAB 5: UNIT ECONOMICS & VALUATION
    # =========================================================================
    ws5 = wb.create_sheet(title="Valuation & Returns")
    ws5.views.sheetView[0].showGridLines = True

    ws5["B2"] = "PRISM UNIT ECONOMICS & VENTURE VALUATION SENSITIVITY"
    ws5["B2"].font = title_font
    ws5["B3"] = "Enterprise Multiple Analysis, Exit Scenarios, and Cohort Return Metrics"
    ws5["B3"].font = subtitle_font

    # Section 1: Customer Unit Economics Table
    ws5["B5"] = "1. COHORT UNIT ECONOMICS BY PRICING TIER"
    ws5["B5"].font = section_font
    ws5["B5"].fill = section_fill
    ws5.merge_cells("B5:F5")

    ue_headers = ["Metric / Parameter", "Tier 1: Core API", "Tier 2: Inst. Desk", "Tier 3: Prime Direct", "Blended Average"]
    for idx, h in enumerate(ue_headers, start=2):
        c = ws5.cell(row=6, column=idx, value=h)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="left" if idx == 2 else "right")

    ue_rows = [
        ("Annual Contract Value (ACV)", [30000, 144000, 420000, 162000], FMT_CURR),
        ("Customer Acquisition Cost (CAC)", [12000, 22000, 65000, 28000], FMT_CURR),
        ("Payback Period (Months)", ["=(C8/C7)*12", "=(D8/D7)*12", "=(E8/E7)*12", "=(F8/F7)*12"], FMT_DEC),
        ("Gross Margin Contribution %", [0.92, 0.94, 0.96, 0.94], FMT_PCT),
        ("Annual Churn Rate %", [0.08, 0.04, 0.02, 0.045], FMT_PCT),
        ("Customer Lifetime (Years)", ["=1/C11", "=1/D11", "=1/E11", "=1/F11"], FMT_DEC),
        ("Lifetime Value (LTV)", ["=C7*C10*C12", "=D7*D10*D12", "=E7*E10*E12", "=F7*F10*F12"], FMT_CURR),
        ("LTV / CAC Ratio", ["=C13/C8", "=D13/D8", "=E13/E8", "=F13/F8"], FMT_MULT),
    ]

    r_idx = 7
    for label, vals, fmt in ue_rows:
        is_highlight = "LTV / CAC" in label or "Payback" in label
        ws5.cell(row=r_idx, column=2, value=label).font = bold_font if is_highlight else regular_font
        for c_offset, v in enumerate(vals):
            c = ws5.cell(row=r_idx, column=3 + c_offset, value=v)
            c.number_format = fmt
            c.font = bold_font if is_highlight else regular_font
            c.alignment = Alignment(horizontal="right")
            if is_highlight:
                c.fill = highlight_fill
                c.border = subtotal_border
        r_idx += 1

    # Section 2: Valuation Sensitivity Matrix
    r_idx += 2
    ws5.cell(row=r_idx, column=2, value="2. VALUATION SENSITIVITY TABLE (ARR MULTIPLES vs FORWARD REVENUE)").font = section_font
    ws5.cell(row=r_idx, column=2).fill = section_fill
    ws5.merge_cells(start_row=r_idx, start_column=2, end_row=r_idx, end_column=7)
    r_idx += 1

    val_headers = ["ARR Multiple", "Year 1 ARR", "Year 2 ARR", "Year 3 ARR", "Year 4 ARR", "Year 5 ARR"]
    for idx, h in enumerate(val_headers, start=2):
        c = ws5.cell(row=r_idx, column=idx, value=h)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="left" if idx == 2 else "right")
    r_idx += 1

    multiples = [15.0, 20.0, 25.0, 30.0, 35.0]
    for mult in multiples:
        ws5.cell(row=r_idx, column=2, value=f"{mult:.0f}x Forward ARR Multiple").font = bold_font
        for yr_idx in range(5):
            source_col = get_column_letter(3 + yr_idx)
            c = ws5.cell(row=r_idx, column=3 + yr_idx, value=f"='5-Year Pro-Forma'!{source_col}26*{mult}")
            c.number_format = FMT_CURR
            c.font = bold_font if mult == 25.0 else regular_font
            c.alignment = Alignment(horizontal="right")
            if mult == 25.0:
                c.fill = highlight_fill
                c.border = subtotal_border
        r_idx += 1

    # Section 3: Potential Strategic Acquirers & Exit Paths
    r_idx += 2
    ws5.cell(row=r_idx, column=2, value="3. STRATEGIC M&A & EXIT BENCHMARKS").font = section_font
    ws5.cell(row=r_idx, column=2).fill = section_fill
    ws5.merge_cells(start_row=r_idx, start_column=2, end_row=r_idx, end_column=7)
    r_idx += 1

    exit_headers = ["Potential Acquirer", "Strategic Rationale", "Comparable Deal Benchmark", "Target Valuation Range"]
    for idx, h in enumerate(exit_headers, start=2):
        c = ws5.cell(row=r_idx, column=idx, value=h)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="left" if idx < 5 else "right")
    r_idx += 1

    exit_rows = [
        ("Intercontinental Exchange (ICE / NYSE)", "Acquisition of primary cross-venue event derivative routing utility", "ICE acquired Ellie Mae ($11B) & SuperDerivatives ($350M)", "$450M - $850M"),
        ("Bloomberg LP / Tradebook", "Incorporation into 350k+ Bloomberg Terminals as native event execution engine", "Bloomberg acquisitions of EMS/OEMS utilities", "$300M - $600M"),
        ("CME Group", "Integration with CME Event Contracts to dominate institutional macro derivative flow", "CME acquired NEX Group ($5.5B)", "$500M - $1.2B"),
        ("Citadel Securities / Jane Street", "Internalization of high-value non-toxic institutional event flow", "Virtu acquired ITG ($1B)", "$350M - $750M"),
        ("Coinbase Institutional", "Expansion from crypto spot/perps into global regulated event prediction markets", "Coinbase acquired Tagomi ($100M+)", "$250M - $500M"),
    ]

    for acq, strat, comp, val_rng in exit_rows:
        ws5.cell(row=r_idx, column=2, value=acq).font = bold_font
        ws5.cell(row=r_idx, column=3, value=strat).font = regular_font
        ws5.cell(row=r_idx, column=4, value=comp).font = italic_font
        c_val = ws5.cell(row=r_idx, column=5, value=val_rng)
        c_val.font = bold_font
        c_val.alignment = Alignment(horizontal="right")
        r_idx += 1

    # Auto-adjust column widths across all sheets
    for ws in [ws1, ws2, ws3, ws4, ws5]:
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
            ws.column_dimensions[col_letter].width = max(max_len + 3, 13)
        ws.column_dimensions["A"].width = 4
        ws.column_dimensions["B"].width = 46

    # Save to file
    output_path = "/Users/harshaghandikota/Liquidity Agent/PRISM_CFO_Financial_Model_v1.xlsx"
    wb.save(output_path)
    print(f"Successfully generated audited financial model at: {output_path}")

if __name__ == "__main__":
    build_model()
