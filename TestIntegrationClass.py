import pytest
from datetime import date, timedelta
from DBConnection import DBConnection


class TestIntegrationClass:

    def setup_method(self):
        """Підготовка до кожного тесту"""
        self.db = DBConnection()
        self.db.connect()

    def clean_method(self):
        """Очищення після кожного тесту"""
        if hasattr(self, 'db'):
            self.db.disconnect()

    def test_add_item(self):
        """Додавання тестового предмету в інвентар"""
        try:
            item_data = {
                "item_name": "Тестовий предмет",
                "category_id": 1,
                "status_id": 1,
                "integrity_percentage": 100,
                "purchase_date": date.today(),
                "item_notes": "Тестовий запис для перевірки роботи функції додавання предмету"
            }

            print(f"\n=== ДОДАВАННЯ ПРЕДМЕТУ ===")
            print(f"Дані предмету: {item_data}")

            item_id = self.db.add_inventory_item(item_data)
            assert item_id is not None, "Не вдалося додати предмет"
            print(f"Предмет додано з ID: {item_id}")

            inventory = self.db.get_inventory_details()
            test_item = inventory[inventory['Назва предмету'] == item_data["item_name"]]
            assert not test_item.empty, "Предмет не знайдено в інвентарі"
            print("Предмет знайдено в інвентарі")

            return {
                "item_id": item_id,
                "item_data": item_data,
                "inventory_record": test_item.iloc[0].to_dict()
            }
        except Exception as e:
            pytest.fail(f"Помилка при додаванні предмету: {str(e)}")
            return None

    def test_rent_item(self):
        """Оренда тестового предмету"""
        try:
            add_result = self.test_add_item()
            item_id = add_result["item_id"]
            print(f"Створено новий предмет для оренди з ID: {item_id}")

            rental_data = {
                "user_name": "Василь Петрович",
                "start_date": date.today(),
                "end_date": date.today() + timedelta(days=14),
                "notes": "Тестова оренда для тестування функції оренди предмету"
            }

            print(f"\n=== ОРЕНДА ПРЕДМЕТУ ===")
            print(f"ID предмету: {item_id}")
            print(f"Дані оренди: {rental_data}")

            rental_id = self.db.rent_item(item_id, **rental_data)
            assert rental_id is not None, "Не вдалося оформити оренду"
            print(f"Оренду оформлено з ID: {rental_id}")

            updated_inventory = self.db.get_inventory_details()
            updated_item = updated_inventory[updated_inventory['ID предмету'] == item_id]
            assert not updated_item.empty, "Предмет не знайдено після оренди"
            print("Статус предмету оновлено після оренди")

            return {
                "rental_id": rental_id,
                "item_id": item_id,
                "rental_data": rental_data,
                "updated_item": updated_item.iloc[0].to_dict()
            }
        except Exception as e:
            pytest.fail(f"Помилка при оренді предмету: {str(e)}")
            return None

    def test_return_item(self):
        """Повернення тестового предмету"""
        try:
            rent_result = self.test_rent_item()
            rental_id = rent_result["rental_id"]
            item_id = rent_result["item_id"]
            print(f"Створено нову оренду для повернення: rental_id={rental_id}, item_id={item_id}")

            return_data = {
                "return_date": date.today() + timedelta(days=10),
                "integrity_percentage": 92,
                "notes": "Повернення для тестування функції повернення"
            }

            print(f"\n=== ПОВЕРНЕННЯ ПРЕДМЕТУ ===")
            print(f"ID оренди: {rental_id}")
            print(f"ID предмету: {item_id}")
            print(f"Дані повернення: {return_data}")

            return_result = self.db.return_item(
                rental_id,
                return_data["return_date"],
                return_data["integrity_percentage"],
                return_data["notes"]
            )

            assert return_result, "Не вдалося зафіксувати повернення"
            print("Повернення успішно зафіксовано")

            final_inventory = self.db.get_inventory_details()
            final_item = final_inventory[final_inventory['ID предмету'] == item_id]
            assert not final_item.empty, "Предмет не знайдено після повернення"

            integrity = final_item.iloc[0]['Цілісність (%)']
            assert integrity == return_data["integrity_percentage"], f"Цілісність не оновилась правильно: {integrity}"
            print(f"Цілісність предмету оновлено правильно: {integrity}%")

            return {
                "success": True,
                "rental_id": rental_id,
                "item_id": item_id,
                "return_data": return_data,
                "final_item": final_item.iloc[0].to_dict()
            }
        except Exception as e:
            pytest.fail(f"Помилка при поверненні предмету: {str(e)}")
            return {"success": False}

    def test_delete_item(self):
        """Видалення тестового предмету"""
        try:
            add_result = self.test_add_item()
            item_id = add_result["item_id"]
            print(f"Створено новий предмет для видалення з ID: {item_id}")

            print(f"\n=== ВИДАЛЕННЯ ПРЕДМЕТУ ===")
            print(f"ID предмету для видалення: {item_id}")

            delete_result = self.db.delete_inventory_item(item_id)
            if delete_result:
                print("Предмет успішно видалено")

                inventory = self.db.get_inventory_details()
                deleted_item = inventory[inventory['ID предмету'] == item_id]
                assert deleted_item.empty, "Предмет все ще знаходиться в інвентарі після видалення"
                print("Предмет успішно видалено з інвентарю")

                return {
                    "success": True,
                    "item_id": item_id
                }
            else:
                print("Не вдалося видалити предмет")
                return {
                    "success": False,
                    "item_id": item_id
                }
        except Exception as delete_error:
            print(f"Помилка при видаленні предмету: {delete_error}")
            return {
                "success": False,
                "error": str(delete_error)
            }
