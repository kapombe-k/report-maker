from flask_restful import Resource
from flask import send_file
from models import Expense
from datetime import datetime
from report_builder import DailyReportBuilder


class ReportResource(Resource):
    def get(self, type, param):
        if type == "day":
            try:
                target_date = datetime.strptime(param, "%Y-%m-%d").date()
                day_data = Expense.get_day_tallies(target_date)
                return day_data, 200
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD"}, 400

        elif type == "daily":
            try:
                target_date = datetime.strptime(param, "%Y-%m-%d").date()
                day_data = Expense.get_day_tallies(target_date)

                # Use builder to generate Excel
                builder = DailyReportBuilder(param, day_data)
                excel_file = builder.build()

                return send_file(
                    excel_file,
                    as_attachment=True,
                    download_name=f"daily_report_{param}.xlsx",
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD"}, 400

        elif type == "monthly":
            try:
                year, month_num = map(int, param.split("-"))
                month_data = Expense.get_month_tallies(month_num, year)
                return month_data, 200
            except ValueError:
                return {"error": "Invalid month format. Use YYYY-MM"}, 400
        else:
            return {"error": "Invalid type. Use day, daily, or monthly"}, 400