# styles.py
from openpyxl.styles import Font, Border, Side, Alignment


class ExcelStyles:
    """Centralized style definitions"""

    # Border definitions
    THIN = Side(border_style="thin", color="000000")
    MEDIUM = Side(border_style="medium", color="000000")

    # Alignments
    LEFT_CENTER = Alignment(horizontal="left", vertical="center")
    CENTER_CENTER = Alignment(horizontal="center", vertical="center")
    RIGHT_CENTER = Alignment(horizontal="right", vertical="center")

    @staticmethod
    def pattern_1_header():
        """Bold + Full Border (Table Headers)"""
        return {
            "font": Font(name="Calibri", size=14, bold=True),
            "border": Border(
                top=ExcelStyles.THIN,
                bottom=ExcelStyles.THIN,
                left=ExcelStyles.THIN,
                right=ExcelStyles.THIN,
            ),
            "alignment": ExcelStyles.CENTER_CENTER,
        }

    @staticmethod
    def pattern_2_plain():
        """Plain Text, No Border (Spacers)"""
        return {
            "font": Font(name="Calibri", size=11),
            "border": Border(),
            "alignment": ExcelStyles.LEFT_CENTER,
        }

    @staticmethod
    def pattern_3_data():
        """Normal Text + Thin Border (Data Cells)"""
        return {
            "font": Font(name="Calibri", size=11),
            "border": Border(
                top=ExcelStyles.THIN,
                bottom=ExcelStyles.THIN,
                left=ExcelStyles.THIN,
                right=ExcelStyles.THIN,
            ),
            "alignment": ExcelStyles.LEFT_CENTER,
        }

    @staticmethod
    def pattern_3_data_right():
        """Data cell with right alignment (for numbers)"""
        style = ExcelStyles.pattern_3_data()
        style["alignment"] = ExcelStyles.RIGHT_CENTER
        return style

    @staticmethod
    def pattern_4_section():
        """Bold + Left Medium Border (Section Headers)"""
        return {
            "font": Font(name="Calibri", size=13, bold=True),
            "border": Border(
                top=ExcelStyles.THIN,
                bottom=ExcelStyles.THIN,
                left=ExcelStyles.MEDIUM,
                right=ExcelStyles.THIN,
            ),
            "alignment": ExcelStyles.LEFT_CENTER,
        }

    @staticmethod
    def pattern_5_totals():
        """Plain Text + Top/Bottom Border (Totals)"""
        return {
            "font": Font(name="Calibri", size=12),
            "border": Border(top=ExcelStyles.THIN, bottom=ExcelStyles.THIN),
            "alignment": ExcelStyles.LEFT_CENTER,
        }

    @staticmethod
    def pattern_5_totals_bold():
        """Bold variant for total labels"""
        style = ExcelStyles.pattern_5_totals()
        style["font"] = Font(name="Calibri", size=13, bold=True)
        return style

    @staticmethod
    def apply_style(cell, style_dict):
        """Apply a style dictionary to a cell"""
        for attr, value in style_dict.items():
            setattr(cell, attr, value)
