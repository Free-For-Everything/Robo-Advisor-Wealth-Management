"""PDF report generator using fpdf2 for daily portfolio reports."""

from datetime import date
from pathlib import Path

from fpdf import FPDF


class PDFReportGenerator:
    """Generates daily portfolio PDF reports with market summary, forecasts, and recommendations."""

    def __init__(self, output_dir: str = "reports/"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_report(
        self,
        report_date: date,
        macro_data: dict,
        forecast_data: dict,
        recommendations: list[dict],
    ) -> str:
        """Generate a daily PDF report with 4 sections.

        Args:
            report_date: Date of the report.
            macro_data: Dict with macro indicators e.g. {'vn_index': 1250.5, 'volume': 450_000_000}.
            forecast_data: Dict with forecast values e.g. {'direction': 'up', 'target': 1270.0, 'confidence': 0.75}.
            recommendations: List of dicts with keys: symbol, action, weight, rationale.

        Returns:
            Absolute path to the generated PDF file.
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        self._add_header(pdf, report_date)
        self._add_market_summary(pdf, macro_data)
        self._add_forecast(pdf, forecast_data)
        self._add_recommendations(pdf, recommendations)
        self._add_risk_snapshot(pdf, macro_data, forecast_data)

        filename = f"daily_report_{report_date.strftime('%Y%m%d')}.pdf"
        filepath = self.output_dir / filename
        pdf.output(str(filepath))
        return str(filepath.resolve())

    # ── Private section builders ──────────────────────────────────────────────

    def _add_header(self, pdf: FPDF, report_date: date) -> None:
        """Title and date header."""
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, "Robo-Advisor Daily Report", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, f"Date: {report_date.strftime('%d %B %Y')}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(6)

    def _add_market_summary(self, pdf: FPDF, macro_data: dict) -> None:
        """Section 1: Market Summary."""
        self._section_title(pdf, "1. Market Summary")
        pdf.set_font("Helvetica", "", 10)
        for key, value in macro_data.items():
            label = key.replace("_", " ").title()
            formatted = f"{value:,.2f}" if isinstance(value, float) else str(value)
            pdf.cell(60, 7, f"{label}:", border=0)
            pdf.cell(0, 7, formatted, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    def _add_forecast(self, pdf: FPDF, forecast_data: dict) -> None:
        """Section 2: VN-Index Forecast."""
        self._section_title(pdf, "2. VN-Index Forecast")
        pdf.set_font("Helvetica", "", 10)
        direction = forecast_data.get("direction", "neutral").upper()
        target = forecast_data.get("target", 0.0)
        confidence = forecast_data.get("confidence", 0.0)
        pdf.cell(60, 7, "Direction:", border=0)
        pdf.cell(0, 7, direction, new_x="LMARGIN", new_y="NEXT")
        pdf.cell(60, 7, "Target Price:", border=0)
        pdf.cell(0, 7, f"{target:,.2f}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(60, 7, "Confidence:", border=0)
        pdf.cell(0, 7, f"{confidence * 100:.1f}%", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    def _add_recommendations(self, pdf: FPDF, recommendations: list[dict]) -> None:
        """Section 3: Recommendations table."""
        self._section_title(pdf, "3. Recommendations")
        if not recommendations:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 7, "No recommendations today.", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
            return

        # Table header
        pdf.set_font("Helvetica", "B", 9)
        col_widths = [25, 20, 20, 0]  # symbol, action, weight, rationale (fills remainder)
        headers = ["Symbol", "Action", "Weight", "Rationale"]
        usable_w = pdf.w - pdf.l_margin - pdf.r_margin
        col_widths[-1] = usable_w - sum(col_widths[:-1])

        for header, w in zip(headers, col_widths):
            pdf.cell(w, 7, header, border=1, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 9)
        for rec in recommendations:
            pdf.cell(col_widths[0], 6, str(rec.get("symbol", "")), border=1, align="C")
            pdf.cell(col_widths[1], 6, str(rec.get("action", "")), border=1, align="C")
            weight = rec.get("weight", 0.0)
            pdf.cell(col_widths[2], 6, f"{weight:.1%}" if isinstance(weight, float) else str(weight), border=1, align="C")
            pdf.cell(col_widths[3], 6, str(rec.get("rationale", ""))[:60], border=1)
            pdf.ln()
        pdf.ln(4)

    def _add_risk_snapshot(self, pdf: FPDF, macro_data: dict, forecast_data: dict) -> None:
        """Section 4: Risk Snapshot (VaR, drawdown, confidence band)."""
        self._section_title(pdf, "4. Risk Snapshot")
        pdf.set_font("Helvetica", "", 10)
        var_95 = macro_data.get("var_95", "N/A")
        max_dd = macro_data.get("max_drawdown", "N/A")
        confidence = forecast_data.get("confidence", 0.0)
        risk_level = "LOW" if confidence > 0.7 else "MEDIUM" if confidence > 0.5 else "HIGH"

        for label, value in [
            ("VaR (95%)", f"{var_95:.2%}" if isinstance(var_95, float) else str(var_95)),
            ("Max Drawdown", f"{max_dd:.2%}" if isinstance(max_dd, float) else str(max_dd)),
            ("Model Risk Level", risk_level),
        ]:
            pdf.cell(60, 7, f"{label}:", border=0)
            pdf.cell(0, 7, value, new_x="LMARGIN", new_y="NEXT")

    def _section_title(self, pdf: FPDF, title: str) -> None:
        """Render a bold underlined section title."""
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(180, 180, 180)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(3)
