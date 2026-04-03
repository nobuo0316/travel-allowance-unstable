import io
from datetime import date
from decimal import Decimal, InvalidOperation

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from supabase import Client, create_client


# =========================================================
# Page setup
# =========================================================
st.set_page_config(page_title="PNC Travel Forms", page_icon="🧾", layout="centered")

PRIMARY = colors.HexColor("#4E73A8")
BAND = colors.HexColor("#E9F0F8")
LABEL_BG = colors.HexColor("#F8FAFC")
GRID = colors.HexColor("#C8CDD4")
TEXT = colors.HexColor("#1F1F1F")
MUTED = colors.HexColor("#666666")

styles = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "TitleCustom",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=18,
    textColor=TEXT,
    alignment=TA_LEFT,
    spaceAfter=4,
)
SUBTITLE = ParagraphStyle(
    "SubtitleCustom",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=8.5,
    leading=10,
    textColor=MUTED,
    alignment=TA_LEFT,
    spaceAfter=4,
)
CELL = ParagraphStyle(
    "CellCustom",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.8,
    leading=10.2,
    textColor=TEXT,
    alignment=TA_LEFT,
)
CELL_BOLD = ParagraphStyle(
    "CellBoldCustom",
    parent=CELL,
    fontName="Helvetica-Bold",
)
CELL_SMALL = ParagraphStyle(
    "CellSmallCustom",
    parent=CELL,
    fontSize=8.0,
    leading=9.0,
    textColor=MUTED,
)
HEADER = ParagraphStyle(
    "HeaderCustom",
    parent=CELL_BOLD,
    fontSize=8.6,
    textColor=colors.white,
    alignment=TA_CENTER,
)
SECTION = ParagraphStyle(
    "SectionCustom",
    parent=CELL_BOLD,
    fontSize=9.0,
    textColor=TEXT,
)
RIGHT = ParagraphStyle(
    "RightCustom",
    parent=CELL,
    alignment=TA_RIGHT,
)


# =========================================================
# I18N
# =========================================================
I18N = {
    "en": {
        "app_title": "PNC Travel Forms",
        "app_caption": "Login, auto-fill profile data, apply grade allowance rules, and generate A4 PDFs.",
        "language": "Language",
        "login_title": "Login",
        "email": "Email",
        "password": "Password",
        "login_button": "Login",
        "logout_button": "Logout",
        "login_error": "Login failed. Please check your email and password.",
        "profile_missing": "Profile was not found. Please contact the administrator.",
        "tab_request": "Travel Authorization & Cash Advance Request",
        "tab_liquidation": "Travel Expense Liquidation & Trip Report",
        "tab_admin": "Admin",
        "welcome": "Welcome",
        "role": "Role",
        "grade": "Grade",
        "allowance": "Allowance",
        "employee_name": "Employee Name",
        "department": "Department",
        "position": "Position",
        "request_date": "Date of Request",
        "destination": "Destination",
        "departure_date": "Departure Date",
        "return_date": "Return Date",
        "nights": "No. of Nights",
        "purpose": "Purpose of Travel",
        "travel_allowance": "Travel Allowance (TA)",
        "transportation": "Transportation",
        "accommodation": "Accommodation",
        "other_cost": "Other Estimated Cost",
        "cash_advance_requested": "Cash Advance Requested",
        "special_instructions": "Special Instructions",
        "overnight_travel": "Overnight Travel?",
        "provided_transport": "Transportation provided by company / hotel",
        "provided_accommodation": "Accommodation provided by company / hotel",
        "provided_meals": "Meals provided by company / hotel",
        "generate_request_pdf": "Generate Request PDF",
        "save_request": "Save Request",
        "request_saved": "Request saved successfully.",
        "pdf_generated": "PDF generated successfully.",
        "download_request_pdf": "Download Request PDF",
        "trip_summary": "Trip Summary / Accomplishment",
        "travel_completion_date": "Travel Completion Date",
        "reference_form_no": "Reference Approved Travel Form No.",
        "approved_ta": "Approved / Applicable TA",
        "less_meals": "Less: Meals / Benefits Provided",
        "cash_advance_received": "Cash Advance Received",
        "other_expense": "Other Approved Expense",
        "attach_receipts": "Original Receipts / ORs",
        "attach_approved_form": "Approved Travel Form",
        "attach_other_support": "Other Supporting Documents",
        "generate_liquidation_pdf": "Generate Liquidation PDF",
        "save_liquidation": "Save Liquidation",
        "liquidation_saved": "Liquidation saved successfully.",
        "download_liquidation_pdf": "Download Liquidation PDF",
        "required_error": "{} is required.",
        "return_date_error": "Return date cannot be earlier than departure date.",
        "cash_advance_error": "Cash Advance Requested cannot be greater than Total Estimated Cost.",
        "admin_profiles": "Employee Database",
        "admin_allowances": "Grade Allowances",
        "admin_refresh": "Refresh data",
        "admin_only": "Admin only.",
        "not_logged_in": "Please log in.",
        "no_access": "You do not have access to this page.",
        "request_no": "Request No.",
        "liquidation_no": "Liquidation No.",
        "amount_due_employee": "Amount Due to Employee",
        "amount_to_return": "Amount to be Returned by Employee",
        "status": "Status",
    },
    "ja": {
        "app_title": "PNC 出張フォーム",
        "app_caption": "ログイン後にプロフィール自動反映、グレード手当自動反映、A4 PDF 出力ができます。",
        "language": "言語",
        "login_title": "ログイン",
        "email": "メールアドレス",
        "password": "パスワード",
        "login_button": "ログイン",
        "logout_button": "ログアウト",
        "login_error": "ログインに失敗しました。メールアドレスまたはパスワードを確認してください。",
        "profile_missing": "プロフィールが見つかりません。管理者に連絡してください。",
        "tab_request": "出張事前申請書",
        "tab_liquidation": "出張報告・精算書",
        "tab_admin": "管理者",
        "welcome": "ようこそ",
        "role": "権限",
        "grade": "グレード",
        "allowance": "手当額",
        "employee_name": "氏名",
        "department": "部署",
        "position": "役職",
        "request_date": "申請日",
        "destination": "出張先",
        "departure_date": "出発日",
        "return_date": "帰着日",
        "nights": "宿泊数",
        "purpose": "出張目的",
        "travel_allowance": "出張手当（TA）",
        "transportation": "交通費",
        "accommodation": "宿泊費",
        "other_cost": "その他見込費用",
        "cash_advance_requested": "仮払申請額",
        "special_instructions": "備考",
        "overnight_travel": "宿泊を伴う出張ですか？",
        "provided_transport": "交通費を会社 / ホテルが負担",
        "provided_accommodation": "宿泊費を会社 / ホテルが負担",
        "provided_meals": "食事を会社 / ホテルが提供",
        "generate_request_pdf": "事前申請PDFを作成",
        "save_request": "事前申請を保存",
        "request_saved": "事前申請を保存しました。",
        "pdf_generated": "PDFを作成しました。",
        "download_request_pdf": "事前申請PDFをダウンロード",
        "trip_summary": "出張報告 / 成果",
        "travel_completion_date": "出張完了日",
        "reference_form_no": "参照する承認済み申請番号",
        "approved_ta": "適用手当額",
        "less_meals": "食事等提供分の控除",
        "cash_advance_received": "受領済み仮払額",
        "other_expense": "その他承認済み費用",
        "attach_receipts": "領収書 / OR",
        "attach_approved_form": "承認済み申請書",
        "attach_other_support": "その他添付資料",
        "generate_liquidation_pdf": "精算PDFを作成",
        "save_liquidation": "精算書を保存",
        "liquidation_saved": "精算書を保存しました。",
        "download_liquidation_pdf": "精算PDFをダウンロード",
        "required_error": "{} は必須です。",
        "return_date_error": "帰着日は出発日より前にできません。",
        "cash_advance_error": "仮払申請額は概算総額を超えられません。",
        "admin_profiles": "従業員データベース",
        "admin_allowances": "グレード別手当",
        "admin_refresh": "再読み込み",
        "admin_only": "管理者専用です。",
        "not_logged_in": "ログインしてください。",
        "no_access": "このページにアクセスできません。",
        "request_no": "申請番号",
        "liquidation_no": "精算番号",
        "amount_due_employee": "会社から支払う差額",
        "amount_to_return": "従業員が返金する差額",
        "status": "ステータス",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return I18N[lang].get(key, key)


# =========================================================
# Supabase helpers
# =========================================================
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    anon_key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, anon_key)


def p(text: str | None, style=CELL):
    safe = (text or "").replace("\n", "<br/>")
    return Paragraph(safe, style)


def money(value: str | float | int | Decimal | None) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    cleaned = str(value).replace(",", "").strip()
    if not cleaned:
        return Decimal("0")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal("0")


def peso_text(amount: Decimal) -> str:
    return f"PHP {amount:,.2f}"


def yn(flag: bool) -> str:
    return "YES" if flag else "NO"


def section_row(title: str):
    return [p(title, SECTION), "", ""]


PDF_COLS = [48 * mm, 93 * mm, 44 * mm]


def add_table(pdf_story, title: str, subtitle: str, right_text: str, rows: list[list]):
    pdf_story.append(p(title, TITLE))
    if subtitle:
        pdf_story.append(p(subtitle, SUBTITLE))

    top = Table(
        [[p("Philippine Nanogoku Corporation", CELL_SMALL), p(right_text, ParagraphStyle("TopRight", parent=CELL_SMALL, alignment=TA_RIGHT))]],
        colWidths=[120 * mm, 65 * mm],
    )
    top.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, GRID),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, GRID),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    pdf_story.append(top)
    pdf_story.append(Spacer(1, 4))

    data = [[p("Item", HEADER), p("Details / Entry", HEADER), p("Notes", HEADER)]] + rows
    table = Table(data, colWidths=PDF_COLS, repeatRows=1)

    style_cmds = [
        ("BOX", (0, 0), (-1, -1), 0.6, GRID),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, GRID),
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]

    for idx, row in enumerate(data[1:], start=1):
        if isinstance(row[0], Paragraph) and row[0].style.name == SECTION.name:
            style_cmds.extend(
                [
                    ("SPAN", (0, idx), (2, idx)),
                    ("BACKGROUND", (0, idx), (2, idx), BAND),
                    ("BOX", (0, idx), (2, idx), 0.8, colors.HexColor("#7A8CA5")),
                ]
            )
        else:
            style_cmds.append(("BACKGROUND", (0, idx), (0, idx), LABEL_BG))

    table.setStyle(TableStyle(style_cmds))
    pdf_story.append(table)


def build_authorization_pdf(data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=8 * mm,
        title="Travel Authorization & Cash Advance Request",
    )

    rows = [
        section_row("1. EMPLOYEE / TRIP INFORMATION"),
        [p("Employee Name", CELL_BOLD), p(data["employee_name"]), p("")],
        [p("Department / Position", CELL_BOLD), p(f'{data["department"]} / {data["position"]}'), p("")],
        [p("Date of Request", CELL_BOLD), p(data["request_date"]), p("Submit before travel date")],
        [p("Destination", CELL_BOLD), p(data["destination"]), p("Indicate city / province")],
        [
            p("Travel Period", CELL_BOLD),
            p(f'Departure: {data["departure_date"]}    Return: {data["return_date"]}    No. of Nights: {data["nights"]}'),
            p(""),
        ],
        [p("Purpose of Travel", CELL_BOLD), p(data["purpose"]), p("State business purpose clearly", CELL_SMALL)],
        section_row("2. ESTIMATED TRAVEL COST / CASH ADVANCE REQUEST"),
        [p("Travel Allowance (TA)", CELL_BOLD), p(peso_text(data["ta_amount"])), p("Based on company policy", CELL_SMALL)],
        [p("Transportation", CELL_BOLD), p(peso_text(data["transport_amount"])), p("Airfare / bus / fuel / fares", CELL_SMALL)],
        [p("Accommodation", CELL_BOLD), p(peso_text(data["accommodation_amount"])), p("If company-paid, indicate N/A", CELL_SMALL)],
        [p("Other Estimated Cost", CELL_BOLD), p(peso_text(data["other_amount"])), p("Meals / tolls / incidentals if allowed", CELL_SMALL)],
        [p("TOTAL ESTIMATED COST", CELL_BOLD), p(peso_text(data["total_estimated"]), CELL_BOLD), p("")],
        [p("Cash Advance Requested", CELL_BOLD), p(peso_text(data["cash_advance_requested"]), CELL_BOLD), p("Fill if advance is needed", CELL_SMALL)],
        section_row("3. ADMIN / POLICY CHECK"),
        [p("Overnight Travel?", CELL_BOLD), p(yn(data["overnight_travel"])), p("TA usually applies to overnight travel", CELL_SMALL)],
        [
            p("Provided by Company / Hotel", CELL_BOLD),
            p(
                "Transportation: " + yn(data["company_transport"]) +
                "    Accommodation: " + yn(data["company_accommodation"]) +
                "    Meals: " + yn(data["company_meals"])
            ),
            p("Check if already covered", CELL_SMALL),
        ],
        [p("Special Instructions", CELL_BOLD), p(data["special_instructions"] or "-"), p("")],
    ]

    story = []
    add_table(
        story,
        "TRAVEL AUTHORIZATION & CASH ADVANCE REQUEST",
        "For official business travel approval and estimated travel cash advance request.",
        "Form No: PNC-HR-TA-2025",
        rows,
    )
    story.append(Spacer(1, 5))
    sig_data = [
        [p("Approval Line", HEADER), p("Signature / Printed Name", HEADER), p("Date", HEADER)],
        [p("Requested by\n(Employee)", CELL), p("\n\n"), p("\n")],
        [p("Checked by\n(Admin / HR)", CELL), p("\n\n"), p("\n")],
        [p("Approved by\n(Department Head)", CELL), p("\n\n"), p("\n")],
    ]
    sig = Table(sig_data, colWidths=[56 * mm, 92 * mm, 37 * mm])
    sig.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, GRID),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, GRID),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6B7280")),
                ("BACKGROUND", (0, 1), (0, -1), LABEL_BG),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 10),
            ]
        )
    )
    story.append(p("4. APPROVAL", CELL_BOLD))
    story.append(sig)
    story.append(Spacer(1, 3))
    doc.build(story)
    return buffer.getvalue()


def build_liquidation_pdf(data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=8 * mm,
        title="Travel Expense Liquidation & Trip Report",
    )

    settlement_text = (
        f'Amount Due to Employee: {peso_text(data["amount_due_employee"])}'
        if data["amount_due_employee"] > 0
        else f'Amount to be Returned by Employee: {peso_text(data["amount_to_return"])}'
    )

    attachments = []
    if data["attach_receipts"]:
        attachments.append("Original Receipts / ORs")
    if data["attach_approved_form"]:
        attachments.append("Approved Travel Form")
    if data["attach_other_support"]:
        attachments.append("Other Supporting Documents")
    attachment_text = ", ".join(attachments) if attachments else "None indicated"

    rows = [
        section_row("1. GENERAL INFORMATION"),
        [p("Employee Name", CELL_BOLD), p(data["employee_name"]), p("")],
        [p("Department / Position", CELL_BOLD), p(f'{data["department"]} / {data["position"]}'), p("")],
        [p("Travel Completion Date", CELL_BOLD), p(data["travel_completion_date"]), p("")],
        [p("Destination / Area Covered", CELL_BOLD), p(data["destination"]), p("")],
        [p("Trip Summary / Accomplishment", CELL_BOLD), p(data["trip_summary"]), p("Briefly state the result of the trip", CELL_SMALL)],
        section_row("2. TRAVEL ALLOWANCE / ADVANCE SETTLEMENT"),
        [p("No. of Nights", CELL_BOLD), p(f'{data["nights"]} Night(s)'), p("")],
        [p("Approved / Applicable TA", CELL_BOLD), p(peso_text(data["approved_ta"])), p("Based on approved rate", CELL_SMALL)],
        [p("Less: Meals / Benefits Provided", CELL_BOLD), p(peso_text(data["less_meals"])), p("Deduct if company / hotel provided meals", CELL_SMALL)],
        [p("(A) Net TA Due", CELL_BOLD), p(peso_text(data["net_ta_due"]), CELL_BOLD), p("")],
        section_row("3. ACTUAL REIMBURSABLE EXPENSES"),
        [p("Transportation", CELL_BOLD), p(peso_text(data["transportation"])), p("Attach OR if applicable", CELL_SMALL)],
        [p("Accommodation", CELL_BOLD), p(peso_text(data["accommodation"])), p("Attach OR / hotel bill", CELL_SMALL)],
        [p("Other Approved Expense", CELL_BOLD), p(peso_text(data["other_expense"])), p("Tolls / fares / fuel / misc.", CELL_SMALL)],
        [p("(B) Subtotal Reimbursable", CELL_BOLD), p(peso_text(data["subtotal_reimbursable"]), CELL_BOLD), p("")],
        section_row("4. FINAL SETTLEMENT"),
        [p("Cash Advance Received", CELL_BOLD), p(peso_text(data["cash_advance_received"])), p("")],
        [p("TOTAL CLAIM (A + B)", CELL_BOLD), p(peso_text(data["total_claim"]), CELL_BOLD), p("")],
        [p("Settlement Result", CELL_BOLD), p(settlement_text), p("Calculated from Total Claim less Cash Advance", CELL_SMALL)],
        [p("Attachments Submitted", CELL_BOLD), p(attachment_text), p("Check all attached documents", CELL_SMALL)],
    ]

    story = []
    add_table(
        story,
        "TRAVEL EXPENSE LIQUIDATION & TRIP REPORT",
        "For post-travel accomplishment reporting and settlement of travel expenses / cash advance.",
        f'Ref. Approved Travel Form No: {data["reference_form_no"]}',
        rows,
    )
    story.append(Spacer(1, 5))
    sig_data = [
        [p("Line", HEADER), p("Signature / Printed Name / Date", HEADER), p("Purpose", HEADER)],
        [p("Prepared by\n(Employee)", CELL), p("\n\n"), p("I certify this report and expenses are true and correct", CELL_SMALL)],
        [p("Checked by\n(Department Head)", CELL), p("\n\n"), p("Reviewed and verified", CELL_SMALL)],
        [p("Reviewed by\n(Accounting / Finance)", CELL), p("\n\n"), p("Final liquidation review", CELL_SMALL)],
    ]
    sig = Table(sig_data, colWidths=[56 * mm, 88 * mm, 41 * mm])
    sig.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, GRID),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, GRID),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6B7280")),
                ("BACKGROUND", (0, 1), (0, -1), LABEL_BG),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 10),
            ]
        )
    )
    story.append(p("5. SIGNATURES / VERIFICATION", CELL_BOLD))
    story.append(sig)
    doc.build(story)
    return buffer.getvalue()


def ensure_state():
    defaults = {
        "lang": "en",
        "logged_in": False,
        "user": None,
        "profile": None,
        "allowance": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login(email: str, password: str):
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = res.user
        if not user:
            st.error(t("login_error"))
            return

        profile_res = (
            supabase.table("profiles")
            .select("*")
            .eq("id", user.id)
            .single()
            .execute()
        )
        profile = profile_res.data
        if not profile:
            st.error(t("profile_missing"))
            return

        allowance_res = (
            supabase.table("grade_allowances")
            .select("*")
            .eq("grade", profile["grade"])
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
        allowance = allowance_res.data[0] if allowance_res.data else None

        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.profile = profile
        st.session_state.allowance = allowance
        st.rerun()
    except Exception:
        st.error(t("login_error"))


def logout():
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    for key in ["logged_in", "user", "profile", "allowance"]:
        st.session_state[key] = None if key in ["user", "profile", "allowance"] else False
    st.rerun()


def validate_authorization(data: dict) -> list[str]:
    errors = []
    required_text = {
        t("employee_name"): data["employee_name"],
        t("department"): data["department"],
        t("position"): data["position"],
        t("destination"): data["destination"],
        t("purpose"): data["purpose"],
    }
    for label, value in required_text.items():
        if not str(value).strip():
            errors.append(t("required_error").format(label))

    if data["return_date"] < data["departure_date"]:
        errors.append(t("return_date_error"))

    if data["cash_advance_requested"] > data["total_estimated"]:
        errors.append(t("cash_advance_error"))

    return errors


def validate_liquidation(data: dict) -> list[str]:
    errors = []
    required_text = {
        t("reference_form_no"): data["reference_form_no"],
        t("employee_name"): data["employee_name"],
        t("department"): data["department"],
        t("position"): data["position"],
        t("destination"): data["destination"],
        t("trip_summary"): data["trip_summary"],
    }
    for label, value in required_text.items():
        if not str(value).strip():
            errors.append(t("required_error").format(label))
    return errors


def save_request_to_supabase(data: dict):
    supabase = get_supabase()
    payload = {
        "employee_id": st.session_state.profile["id"],
        "employee_name": data["employee_name"],
        "department": data["department"],
        "position_title": data["position"],
        "grade": st.session_state.profile["grade"],
        "destination": data["destination"],
        "purpose": data["purpose"],
        "departure_date": data["departure_date"],
        "return_date": data["return_date"],
        "nights": data["nights"],
        "ta_amount": float(data["ta_amount"]),
        "transport_amount": float(data["transport_amount"]),
        "accommodation_amount": float(data["accommodation_amount"]),
        "other_amount": float(data["other_amount"]),
        "total_estimated": float(data["total_estimated"]),
        "cash_advance_requested": float(data["cash_advance_requested"]),
        "overnight_travel": data["overnight_travel"],
        "company_transport": data["company_transport"],
        "company_accommodation": data["company_accommodation"],
        "company_meals": data["company_meals"],
        "special_instructions": data["special_instructions"],
        "approver1_id": st.session_state.profile.get("approver1_id"),
        "approver2_id": st.session_state.profile.get("approver2_id"),
        "status": "submitted",
        "submitted_at": data["request_date"],
    }
    return supabase.table("travel_requests").insert(payload).execute()


def save_liquidation_to_supabase(data: dict):
    supabase = get_supabase()
    request_lookup = (
        supabase.table("travel_requests")
        .select("id")
        .eq("request_no", data["reference_form_no"])
        .limit(1)
        .execute()
    )
    request_id = request_lookup.data[0]["id"] if request_lookup.data else None

    payload = {
        "travel_request_id": request_id,
        "employee_id": st.session_state.profile["id"],
        "employee_name": data["employee_name"],
        "department": data["department"],
        "position_title": data["position"],
        "grade": st.session_state.profile["grade"],
        "travel_completion_date": data["travel_completion_date"],
        "destination": data["destination"],
        "trip_summary": data["trip_summary"],
        "nights": data["nights"],
        "approved_ta": float(data["approved_ta"]),
        "less_meals": float(data["less_meals"]),
        "net_ta_due": float(data["net_ta_due"]),
        "transportation": float(data["transportation"]),
        "accommodation": float(data["accommodation"]),
        "other_expense": float(data["other_expense"]),
        "subtotal_reimbursable": float(data["subtotal_reimbursable"]),
        "cash_advance_received": float(data["cash_advance_received"]),
        "total_claim": float(data["total_claim"]),
        "amount_due_employee": float(data["amount_due_employee"]),
        "amount_to_return": float(data["amount_to_return"]),
        "attach_receipts": data["attach_receipts"],
        "attach_approved_form": data["attach_approved_form"],
        "attach_other_support": data["attach_other_support"],
        "status": "submitted",
        "submitted_at": data["travel_completion_date"],
    }
    return supabase.table("travel_liquidations").insert(payload).execute()


ensure_state()

st.title(t("app_title"))
st.caption(t("app_caption"))

lang_choice = st.selectbox(t("language"), options=["en", "ja"], format_func=lambda x: "English" if x == "en" else "日本語")
if lang_choice != st.session_state.lang:
    st.session_state.lang = lang_choice
    st.rerun()

if not st.session_state.logged_in:
    st.subheader(t("login_title"))
    with st.form("login_form"):
        email = st.text_input(t("email"))
        password = st.text_input(t("password"), type="password")
        submitted = st.form_submit_button(t("login_button"))
    if submitted:
        login(email, password)
    st.stop()

profile = st.session_state.profile
allowance = st.session_state.allowance

top1, top2 = st.columns([3, 1])
with top1:
    st.write(f'**{t("welcome")}**: {profile["full_name_en"]}')
    st.write(f'**{t("department")}**: {profile["department"]}')
    st.write(f'**{t("position")}**: {profile["position_title"]}')
    st.write(f'**{t("grade")}**: {profile["grade"]}')
    st.write(f'**{t("role")}**: {profile["role"]}')
    if allowance:
        st.write(f'**{t("allowance")} (TA)**: {peso_text(money(allowance["ta_overnight"]))}')
with top2:
    st.button(t("logout_button"), on_click=logout, use_container_width=True)

tabs = [t("tab_request"), t("tab_liquidation")]
if profile["role"] == "admin":
    tabs.append(t("tab_admin"))

tab_objects = st.tabs(tabs)

with tab_objects[0]:
    st.subheader(t("tab_request"))
    default_ta = float(allowance["ta_overnight"]) if allowance else 0.0
    with st.form("request_form"):
        c1, c2 = st.columns(2)
        employee_name = c1.text_input(t("employee_name"), value=profile["full_name_en"], disabled=True)
        department = c1.text_input(t("department"), value=profile["department"], disabled=True)
        position = c2.text_input(t("position"), value=profile["position_title"], disabled=True)
        request_date = c2.date_input(t("request_date"), value=date.today())

        destination = st.text_input(f'{t("destination")} *')
        c3, c4, c5 = st.columns(3)
        departure_date = c3.date_input(t("departure_date"))
        return_date = c4.date_input(t("return_date"))
        nights = c5.number_input(t("nights"), min_value=0, step=1, value=0)

        purpose = st.text_area(f'{t("purpose")} *', height=90)

        st.markdown("**Cost**")
        d1, d2 = st.columns(2)
        ta_amount = d1.number_input(t("travel_allowance"), min_value=0.0, step=100.0, value=default_ta)
        transport_amount = d2.number_input(t("transportation"), min_value=0.0, step=100.0, value=0.0)
        accommodation_amount = d1.number_input(t("accommodation"), min_value=0.0, step=100.0, value=0.0)
        other_amount = d2.number_input(t("other_cost"), min_value=0.0, step=100.0, value=0.0)
        cash_advance_requested = d1.number_input(t("cash_advance_requested"), min_value=0.0, step=100.0, value=0.0)

        st.markdown("**Policy Check**")
        overnight_travel = st.checkbox(t("overnight_travel"))
        e1, e2, e3 = st.columns(3)
        company_transport = e1.checkbox(t("provided_transport"))
        company_accommodation = e2.checkbox(t("provided_accommodation"))
        company_meals = e3.checkbox(t("provided_meals"))
        special_instructions = st.text_area(t("special_instructions"), height=70)

        b1, b2 = st.columns(2)
        generate_request_pdf = b1.form_submit_button(t("generate_request_pdf"), use_container_width=True)
        save_request = b2.form_submit_button(t("save_request"), use_container_width=True)

    total_estimated = money(ta_amount) + money(transport_amount) + money(accommodation_amount) + money(other_amount)
    st.info(f'{t("travel_allowance")}: {peso_text(money(ta_amount))} | Total: {peso_text(total_estimated)}')

    if generate_request_pdf or save_request:
        request_data = {
            "employee_name": employee_name,
            "department": department,
            "position": position,
            "request_date": request_date.strftime("%Y-%m-%d"),
            "destination": destination,
            "departure_date": departure_date.strftime("%Y-%m-%d"),
            "return_date": return_date.strftime("%Y-%m-%d"),
            "nights": int(nights),
            "purpose": purpose,
            "ta_amount": money(ta_amount),
            "transport_amount": money(transport_amount),
            "accommodation_amount": money(accommodation_amount),
            "other_amount": money(other_amount),
            "total_estimated": total_estimated,
            "cash_advance_requested": money(cash_advance_requested),
            "overnight_travel": overnight_travel,
            "company_transport": company_transport,
            "company_accommodation": company_accommodation,
            "company_meals": company_meals,
            "special_instructions": special_instructions,
        }
        errors = validate_authorization(request_data)
        if errors:
            for err in errors:
                st.error(err)
        else:
            if generate_request_pdf:
                pdf_bytes = build_authorization_pdf(request_data)
                st.success(t("pdf_generated"))
                st.download_button(
                    t("download_request_pdf"),
                    data=pdf_bytes,
                    file_name="travel_authorization_request.pdf",
                    mime="application/pdf",
                )
            if save_request:
                try:
                    save_request_to_supabase(request_data)
                    st.success(t("request_saved"))
                except Exception as exc:
                    st.error(str(exc))

with tab_objects[1]:
    st.subheader(t("tab_liquidation"))
    with st.form("liquidation_form"):
        a1, a2 = st.columns(2)
        reference_form_no = a1.text_input(f'{t("reference_form_no")} *')
        travel_completion_date = a2.date_input(t("travel_completion_date"), value=date.today())

        b1, b2 = st.columns(2)
        employee_name2 = b1.text_input(t("employee_name"), value=profile["full_name_en"], disabled=True)
        department2 = b1.text_input(t("department"), value=profile["department"], disabled=True)
        position2 = b2.text_input(t("position"), value=profile["position_title"], disabled=True)
        destination2 = b2.text_input(f'{t("destination")} *')

        c1, c2 = st.columns(2)
        nights2 = c1.number_input(t("nights"), min_value=0, step=1, value=0, key="nights2")
        approved_ta = c2.number_input(t("approved_ta"), min_value=0.0, step=100.0, value=default_ta)
        less_meals = c1.number_input(t("less_meals"), min_value=0.0, step=100.0, value=0.0)
        cash_advance_received = c2.number_input(t("cash_advance_received"), min_value=0.0, step=100.0, value=0.0)

        trip_summary = st.text_area(f'{t("trip_summary")} *', height=90)

        st.markdown("**Expenses**")
        d1, d2, d3 = st.columns(3)
        transportation = d1.number_input(t("transportation"), min_value=0.0, step=100.0, value=0.0)
        accommodation = d2.number_input(t("accommodation"), min_value=0.0, step=100.0, value=0.0)
        other_expense = d3.number_input(t("other_expense"), min_value=0.0, step=100.0, value=0.0)

        st.markdown("**Attachments**")
        e1, e2, e3 = st.columns(3)
        attach_receipts = e1.checkbox(t("attach_receipts"))
        attach_approved_form = e2.checkbox(t("attach_approved_form"))
        attach_other_support = e3.checkbox(t("attach_other_support"))

        f1, f2 = st.columns(2)
        generate_liq_pdf = f1.form_submit_button(t("generate_liquidation_pdf"), use_container_width=True)
        save_liq = f2.form_submit_button(t("save_liquidation"), use_container_width=True)

    net_ta_due = money(approved_ta) - money(less_meals)
    subtotal_reimbursable = money(transportation) + money(accommodation) + money(other_expense)
    total_claim = net_ta_due + subtotal_reimbursable
    difference = total_claim - money(cash_advance_received)
    amount_due_employee = difference if difference > 0 else Decimal("0")
    amount_to_return = abs(difference) if difference < 0 else Decimal("0")

    k1, k2, k3 = st.columns(3)
    k1.metric("Net TA", peso_text(net_ta_due))
    k2.metric("Subtotal", peso_text(subtotal_reimbursable))
    k3.metric("Total", peso_text(total_claim))

    if amount_due_employee > 0:
        st.info(f'{t("amount_due_employee")}: {peso_text(amount_due_employee)}')
    else:
        st.info(f'{t("amount_to_return")}: {peso_text(amount_to_return)}')

    if generate_liq_pdf or save_liq:
        liq_data = {
            "reference_form_no": reference_form_no,
            "employee_name": employee_name2,
            "department": department2,
            "position": position2,
            "travel_completion_date": travel_completion_date.strftime("%Y-%m-%d"),
            "destination": destination2,
            "trip_summary": trip_summary,
            "nights": int(nights2),
            "approved_ta": money(approved_ta),
            "less_meals": money(less_meals),
            "net_ta_due": net_ta_due,
            "transportation": money(transportation),
            "accommodation": money(accommodation),
            "other_expense": money(other_expense),
            "subtotal_reimbursable": subtotal_reimbursable,
            "cash_advance_received": money(cash_advance_received),
            "total_claim": total_claim,
            "amount_due_employee": amount_due_employee,
            "amount_to_return": amount_to_return,
            "attach_receipts": attach_receipts,
            "attach_approved_form": attach_approved_form,
            "attach_other_support": attach_other_support,
        }
        errors = validate_liquidation(liq_data)
        if errors:
            for err in errors:
                st.error(err)
        else:
            if generate_liq_pdf:
                pdf_bytes = build_liquidation_pdf(liq_data)
                st.success(t("pdf_generated"))
                st.download_button(
                    t("download_liquidation_pdf"),
                    data=pdf_bytes,
                    file_name="travel_liquidation_report.pdf",
                    mime="application/pdf",
                )
            if save_liq:
                try:
                    save_liquidation_to_supabase(liq_data)
                    st.success(t("liquidation_saved"))
                except Exception as exc:
                    st.error(str(exc))

if profile["role"] == "admin":
    with tab_objects[2]:
        st.subheader(t("admin_profiles"))
        if st.button(t("admin_refresh")):
            st.cache_data.clear()
            st.rerun()

        try:
            supabase = get_supabase()
            profiles = supabase.table("profiles").select("email,employee_code,full_name_en,department,position_title,grade,role,is_active").order("full_name_en").execute()
            allowances = supabase.table("grade_allowances").select("grade,ta_overnight,transport_limit,accommodation_limit,is_active").order("grade").execute()
            st.dataframe(profiles.data, use_container_width=True)
            st.subheader(t("admin_allowances"))
            st.dataframe(allowances.data, use_container_width=True)
        except Exception as exc:
            st.error(str(exc))
