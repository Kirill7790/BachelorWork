import pytest
from datetime import date, timedelta
from DBConnection import DBConnection



class TestClass:
    def test_execute_queries(self):
        # Тест 1: SELECT
        db = DBConnection()
        db.connect()

        try:
            result = db.execute_query("SELECT 1 as test_value", fetch=True)
            print("Запит 1. ")
            print(f"Результат запиту 1: {result}")
            assert result == [(1,)]
        finally:
            db.disconnect()

        # Тест 2: INSERT
        db = DBConnection()
        db.connect()

        try:
            result = db.execute_query(
                "INSERT INTO categories (category_name) VALUES (%s) RETURNING category_id",
                ("Test Category",),
                fetch=True
            )
            print("Запит 2. ")
            assert result is not None
            assert isinstance(result[0][0], int)


            db.execute_query(
                "DELETE FROM categories WHERE category_name = %s",
                ("Test Category",)
            )

        finally:
            db.disconnect()

    def test_rental_status(self):
        def calculate_rental_status(returned_date, end_date, current_date):
            if returned_date is None and end_date < current_date:
                return 'Протерміновано'
            elif returned_date is None:
                return 'В оренді'
            elif returned_date > end_date:
                return 'Повернено з запізненням'
            else:
                return 'Повернено'

        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Активна оренда
        assert calculate_rental_status(None, tomorrow, today) == 'В оренді'
        # Протермінована
        assert calculate_rental_status(None, yesterday, today) == 'Протерміновано'
        # Повернено вчасно
        assert calculate_rental_status(yesterday, yesterday, today) == 'Повернено'
        # Повернено з запізненням
        assert calculate_rental_status(today, yesterday, today) == 'Повернено з запізненням'

    def test_integrity_color(self):
        def get_integrity_color(integrity_percentage):
            if integrity_percentage < 20:
                return "red"
            else:
                return ""

        assert get_integrity_color(15) == "red"
        assert get_integrity_color(19) == "red"
        assert get_integrity_color(80) == ""
        assert get_integrity_color(100) == ""