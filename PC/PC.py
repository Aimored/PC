import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QComboBox
)
import pymysql
from pymysql import OperationalError

logging.basicConfig(level=logging.INFO)


class JobPositionTab(QWidget):
    def __init__(self):
        super().__init__()

        # Создаем макет для вкладки
        layout = QVBoxLayout()

        # Метка и поле ввода для должности
        self.position_label = QLabel("Должность:")
        self.position_input = QLineEdit()

        # Кнопка для добавления должности
        self.add_button = QPushButton("Добавить должность")
        self.add_button.clicked.connect(self.add_position)

        # Таблица для отображения должностей
        self.position_table = QTableWidget()
        self.position_table.setColumnCount(2)
        self.position_table.setHorizontalHeaderLabels(["ID Должности", "Должности"])

        # Добавляем виджеты в макет
        layout.addWidget(self.position_label)
        layout.addWidget(self.position_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.position_table)

        # Устанавливаем макет для вкладки
        self.setLayout(layout)

        # Загружаем должности из базы данных
        self.load_positions()

    def add_position(self):
        position = self.position_input.text()
        if position:
            # Явное указание данных для подключения
            db_user = "Aimor"
            db_password = "Alex25122005"

            try:
                logging.info("Подключение к базе данных...")
                connection = pymysql.connect(
                    host='localhost',
                    user=db_user,
                    password=db_password,
                    database='pcpc'
                )

                with connection.cursor() as cursor:
                    # Вставляем новую запись
                    query = "INSERT INTO Должности (Должность) VALUES (%s)"
                    cursor.execute(query, (position,))
                    connection.commit()

                QMessageBox.information(self, "Успех", "Должность успешно добавлена.")
                self.load_positions()  # Обновляем таблицу после добавления

            except OperationalError as e:
                logging.error(f"Ошибка добавления должности: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления должности: {e}")

            finally:
                if 'connection' in locals():
                    connection.close()
                    logging.info("Соединение закрыто.")
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите должность.")

    def load_positions(self):
        try:
            # Явное указание данных для подключения
            db_user = "Aimor"
            db_password = "Alex25122005"

            logging.info("Подключение к базе данных для загрузки должностей...")
            connection = pymysql.connect(
                host='localhost',
                user=db_user,
                password=db_password,
                database='pcpc'
            )

            with connection.cursor() as cursor:
                # Получаем список должностей
                query = "SELECT `id Должности`, Должность FROM Должности"
                cursor.execute(query)
                results = cursor.fetchall()

                # Заполняем таблицу данными
                self.position_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.position_table.setItem(row_index, 0, QTableWidgetItem(str(row_data[0])))
                    self.position_table.setItem(row_index, 1, QTableWidgetItem(row_data[1]))

        except OperationalError as e:
            logging.error(f"Ошибка загрузки должностей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки должностей: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после загрузки должностей.")


class EmployeeTab(QWidget):
    def __init__(self):
        super().__init__()

        # Создаем макет для вкладки
        layout = QVBoxLayout()

        # Метки и поля ввода для сотрудника
        self.name_label = QLabel("ФИО:")
        self.name_input = QLineEdit()

        self.experience_label = QLabel("Стаж работы:")
        self.experience_input = QLineEdit()

        self.position_label = QLabel("Должность:")
        self.position_combo = QComboBox()

        # Кнопка для добавления сотрудника
        self.add_button = QPushButton("Добавить сотрудника")
        self.add_button.clicked.connect(self.add_employee)

        # Таблица для отображения сотрудников
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(4)
        self.employee_table.setHorizontalHeaderLabels(["ID Сотрудника", "ФИО", "Должность","Стаж работы"])

        # Добавляем виджеты в макет
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.experience_label)
        layout.addWidget(self.experience_input)
        layout.addWidget(self.position_label)
        layout.addWidget(self.position_combo)
        layout.addWidget(self.add_button)
        layout.addWidget(self.employee_table)

        # Устанавливаем макет для вкладки
        self.setLayout(layout)

        # Загружаем данные
        self.load_positions()
        self.load_employees()

    def load_positions(self):
        """Загружает список должностей для выпадающего списка."""
        try:
            db_user = "Aimor"
            db_password = "Alex25122005"

            connection = pymysql.connect(
                host='localhost',
                user=db_user,
                password=db_password,
                database='pcpc'
            )

            with connection.cursor() as cursor:
                query = "SELECT `id Должности`, Должность FROM Должности"
                cursor.execute(query)
                results = cursor.fetchall()

                # Заполняем выпадающий список
                self.position_combo.clear()
                for row in results:
                    self.position_combo.addItem(row[1], userData=row[0])

        except OperationalError as e:
            logging.error(f"Ошибка загрузки должностей: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def load_employees(self):
        """Загружает список сотрудников для таблицы."""
        try:
            db_user = "Aimor"
            db_password = "Alex25122005"

            connection = pymysql.connect(
                host='localhost',
                user=db_user,
                password=db_password,
                database='pcpc'
            )

            with connection.cursor() as cursor:
                query = """
                SELECT 
                    `id Сотрудника`, 
                    `ФИО`, 
                    `Должности`.`Должность`, 
                    `Стаж работы`
                FROM 
                    `Сотрудники`
                JOIN 
                    `Должности` 
                ON 
                    `Сотрудники`.`Должность` = `Должности`.`id Должности`
                """
                cursor.execute(query)
                results = cursor.fetchall()

                # Заполняем таблицу данными
                self.employee_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.employee_table.setItem(row_index, 0, QTableWidgetItem(str(row_data[0])))
                    self.employee_table.setItem(row_index, 1, QTableWidgetItem(row_data[1]))
                    self.employee_table.setItem(row_index, 2, QTableWidgetItem(row_data[2]))
                    self.employee_table.setItem(row_index, 3, QTableWidgetItem(str(row_data[3])))

        except OperationalError as e:
            logging.error(f"Ошибка загрузки сотрудников: {e}")
        finally:
            if 'connection' in locals():
                connection.close()


    def add_employee(self):
        """Добавляет нового сотрудника в базу данных."""
        name = self.name_input.text()
        position_id = self.position_combo.currentData()
        experience = self.experience_input.text()

        if name and position_id and experience.isdigit():
            db_user = "Aimor"
            db_password = "Alex25122005"

            try:
                connection = pymysql.connect(
                    host='localhost',
                    user=db_user,
                    password=db_password,
                    database='pcpc'
                )

                with connection.cursor() as cursor:
                    query = "INSERT INTO `Сотрудники` (`ФИО`, `Должность`, `Стаж`) VALUES (%s, %s, %s)"
                    cursor.execute(query, (name, position_id, experience))
                    connection.commit()

                QMessageBox.information(self, "Успех", "Сотрудник успешно добавлен.")
                self.load_employees()  # Обновляем таблицу после добавления

            except OperationalError as e:
                logging.error(f"Ошибка добавления сотрудника: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления сотрудника: {e}")

            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля корректно.")

class CategoryTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create layout for the tab
        layout = QVBoxLayout()

        # Label and input field for category
        self.category_label = QLabel("Категория:")
        self.category_input = QLineEdit()

        # Button to add category
        self.add_button = QPushButton("Добавить категорию")
        self.add_button.clicked.connect(self.add_category)

        # Table to display categories
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(1)  # Only show the category name
        self.category_table.setHorizontalHeaderLabels(["Категория"])

        # Add widgets to layout
        layout.addWidget(self.category_label)
        layout.addWidget(self.category_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.category_table)

        # Set layout for the tab
        self.setLayout(layout)

        # Load categories from the database
        self.load_categories()

    def add_category(self):
        category = self.category_input.text()
        if category:
            db_user = "Aimor"
            db_password = "Alex25122005"

            try:
                logging.info("Подключение к базе данных...")
                connection = pymysql.connect(
                    host='localhost',
                    user=db_user,
                    password=db_password,
                    database='pcpc'
                )

                with connection.cursor() as cursor:
                    # Insert new category
                    query = "INSERT INTO Категории (Категория) VALUES (%s)"
                    cursor.execute(query, (category,))
                    connection.commit()

                QMessageBox.information(self, "Успех", "Категория успешно добавлена.")
                self.load_categories()  # Refresh the table after adding

            except OperationalError as e:
                logging.error(f"Ошибка добавления категории: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления категории: {e}")

            finally:
                if 'connection' in locals():
                    connection.close()
                    logging.info("Соединение закрыто.")
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите категорию.")

    def load_categories(self):
        try:
            db_user = "Aimor"
            db_password = "Alex25122005"

            logging.info("Подключение к базе данных для загрузки категорий...")
            connection = pymysql.connect(
                host='localhost',
                user=db_user,
                password=db_password,
                database='pcpc'
            )

            with connection.cursor() as cursor:
                # Get list of categories
                query = "SELECT Категория FROM Категории"
                cursor.execute(query)
                results = cursor.fetchall()

                # Fill the table with data
                self.category_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.category_table.setItem(row_index, 0, QTableWidgetItem(row_data[0]))

        except OperationalError as e:
            logging.error(f"Ошибка загрузки категорий: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки категорий: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после загрузки категорий.")

class ProductTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create layout for the tab
        layout = QVBoxLayout()

        # Label and input field for product name
        self.name_label = QLabel("Наименование:")
        self.name_input = QLineEdit()

        # Label and input field for product price
        self.price_label = QLabel("Цена:")
        self.price_input = QLineEdit()

        # Label and dropdown for category
        self.category_label = QLabel("Категория:")
        self.category_dropdown = QComboBox()

        # Button to add product
        self.add_button = QPushButton("Добавить товар")
        self.add_button.clicked.connect(self.add_product)

        # Table to display products
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(3)  # Show only name, price, and category
        self.product_table.setHorizontalHeaderLabels(["Наименование", "Цена", "Категория"])

        # Add widgets to layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)
        layout.addWidget(self.category_label)
        layout.addWidget(self.category_dropdown)
        layout.addWidget(self.add_button)
        layout.addWidget(self.product_table)

        # Set layout for the tab
        self.setLayout(layout)

        # Load categories and products from the database
        self.load_categories()
        self.load_products()

    def load_categories(self):
        try:
            db_user = "Aimor"
            db_password = "Alex25122005"

            logging.info("Подключение к базе данных для загрузки категорий...")
            connection = pymysql.connect(
                host='localhost',
                user=db_user,
                password=db_password,
                database='pcpc'
            )

            with connection.cursor() as cursor:
                # Get list of categories
                query = "SELECT `id категории`, Категория FROM Категории"
                cursor.execute(query)
                results = cursor.fetchall()

                # Populate the dropdown with categories
                self.category_dropdown.clear()
                for category_id, category_name in results:
                    self.category_dropdown.addItem(category_name, category_id)

        except OperationalError as e:
            logging.error(f"Ошибка загрузки категорий: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки категорий: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после загрузки категорий.")

    def add_product(self):
        name = self.name_input.text()
        price = self.price_input.text()
        category_id = self.category_dropdown.currentData()

        if name and price and category_id is not None:
            db_user = "Aimor"
            db_password = "Alex25122005"

            try:
                logging.info("Подключение к базе данных...")
                connection = pymysql.connect(
                    host='localhost',
                    user=db_user,
                    password=db_password,
                    database='pcpc'
                )

                with connection.cursor() as cursor:
                    # Insert new product
                    query = "INSERT INTO Товар (Наименование, Цена, `id категории`) VALUES (%s, %s, %s)"
                    cursor.execute(query, (name, price, category_id))
                    connection.commit()

                QMessageBox.information(self, "Успех", "Товар успешно добавлен.")
                self.load_products()  # Refresh the table after adding

            except OperationalError as e:
                logging.error(f"Ошибка добавления товара: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления товара: {e}")

            finally:
                if 'connection' in locals():
                    connection.close()
                    logging.info("Соединение закрыто.")
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля.")

    def load_products(self):
        try:
            db_user = "Aimor"
            db_password = "Alex25122005"

            logging.info("Подключение к базе данных для загрузки товаров...")
            connection = pymysql.connect(
                host='localhost',
                user=db_user,
                password=db_password,
                database='pcpc'
            )

            with connection.cursor() as cursor:
                # Correct the SQL query to match the actual column names in your database
                query = """
                SELECT Наименование, Цена, Категории.Категория
                FROM Товар
                JOIN Категории ON Товар.`категория` = Категории.`id категории`
                """
                cursor.execute(query)
                results = cursor.fetchall()

                # Fill the table with data
                self.product_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.product_table.setItem(row_index, 0, QTableWidgetItem(row_data[0]))
                    self.product_table.setItem(row_index, 1, QTableWidgetItem(str(row_data[1])))
                    self.product_table.setItem(row_index, 2, QTableWidgetItem(row_data[2]))

        except OperationalError as e:
            logging.error(f"Ошибка загрузки товаров: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки товаров: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после загрузки товаров.")
class SalesTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Поля для ввода данных
        self.employee_label = QLabel("Сотрудник:")
        self.employee_combo = QComboBox()

        self.product_label = QLabel("Товар:")
        self.product_combo = QComboBox()

        self.quantity_label = QLabel("Количество:")
        self.quantity_input = QLineEdit()

        self.date_label = QLabel("Дата продажи:")
        self.date_input = QLineEdit()

        # Кнопка для добавления продажи
        self.add_button = QPushButton("Добавить продажу")
        self.add_button.clicked.connect(self.add_sale)

        # Таблица для отображения продаж
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(
            ["№ Продажи", "Сотрудник", "Товар", "Количество", "Дата"]
        )

        # Добавляем виджеты в макет
        layout.addWidget(self.employee_label)
        layout.addWidget(self.employee_combo)
        layout.addWidget(self.product_label)
        layout.addWidget(self.product_combo)
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.sales_table)

        # Устанавливаем макет для вкладки
        self.setLayout(layout)

        # Загружаем данные
        self.load_employees()
        self.load_products()
        self.load_sales()

    def load_employees(self):
        """Загружает список сотрудников для выпадающего списка."""
        try:
            connection = pymysql.connect(
                host="localhost",
                user="Aimor",
                password="Alex25122005",
                database="pcpc",
            )
            with connection.cursor() as cursor:
                query = "SELECT `id Сотрудника`, ФИО FROM Сотрудники"
                cursor.execute(query)
                results = cursor.fetchall()
                self.employee_combo.clear()
                for row in results:
                    self.employee_combo.addItem(row[1], userData=row[0])
        except OperationalError as e:
            logging.error(f"Ошибка загрузки сотрудников: {e}")
        finally:
            if "connection" in locals():
                connection.close()

    def load_products(self):
        """Загружает список товаров для выпадающего списка."""
        try:
            connection = pymysql.connect(
                host="localhost",
                user="Aimor",
                password="Alex25122005",
                database="pcpc",
            )
            with connection.cursor() as cursor:
                query = "SELECT `id Товара`, Наименование FROM Товар"
                cursor.execute(query)
                results = cursor.fetchall()
                self.product_combo.clear()
                for row in results:
                    self.product_combo.addItem(row[1], userData=row[0])
        except OperationalError as e:
            logging.error(f"Ошибка загрузки товаров: {e}")
        finally:
            if "connection" in locals():
                connection.close()

    def load_sales(self):
        """Загружает список продаж для таблицы."""
        try:
            connection = pymysql.connect(
                host="localhost",
                user="Aimor",
                password="Alex25122005",
                database="pcpc",
            )
            with connection.cursor() as cursor:
                query = """
                SELECT Продажи.`№ Продажи`, Сотрудники.ФИО, Товар.Наименование, Составпродажи.Количество, Продажи.Дата
                FROM Составпродажи
                JOIN Продажи ON Составпродажи.Продажа = Продажи.`№ Продажи`
                JOIN Сотрудники ON Продажи.Сотрудник = Сотрудники.`id Сотрудника`
                JOIN Товар ON Составпродажи.Товар = Товар.`id Товара`
                """
                cursor.execute(query)
                results = cursor.fetchall()

                self.sales_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    for col_index, value in enumerate(row_data):
                        self.sales_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
        except OperationalError as e:
            logging.error(f"Ошибка загрузки продаж: {e}")
        finally:
            if "connection" in locals():
                connection.close()

    def add_sale(self):
        """Добавляет новую продажу в базу данных."""
        employee_id = self.employee_combo.currentData()
        product_id = self.product_combo.currentData()
        quantity = self.quantity_input.text()
        sale_date = self.date_input.text()

        if employee_id and product_id and quantity and sale_date:
            try:
                connection = pymysql.connect(
                    host="localhost",
                    user="Aimor",
                    password="Alex25122005",
                    database="pcpc",
                )
                with connection.cursor() as cursor:
                    # Добавляем продажу
                    query_sale = "INSERT INTO Продажи (Дата, Сотрудник) VALUES (%s, %s)"
                    cursor.execute(query_sale, (sale_date, employee_id))
                    sale_id = cursor.lastrowid

                    # Добавляем состав продажи
                    query_composition = """
                    INSERT INTO СоставПродажи (Продажа, Товар, Количество)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(query_composition, (sale_id, product_id, quantity))
                    connection.commit()

                QMessageBox.information(self, "Успех", "Продажа успешно добавлена.")
                self.load_sales()
            except OperationalError as e:
                logging.error(f"Ошибка добавления продажи: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления продажи: {e}")
            finally:
                if "connection" in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Менеджер компании")

        # Create tab widget
        self.tabs = QTabWidget()

        # Create tabs
        self.job_position_tab = JobPositionTab()
        self.employee_tab = EmployeeTab()
        self.category_tab = CategoryTab()
        self.product_tab = ProductTab()  # New product tab
        self.sales_tab = SalesTab()

        self.tabs.addTab(self.sales_tab, "Продажи")
        self.tabs.addTab(self.job_position_tab, "Должности")
        self.tabs.addTab(self.employee_tab, "Сотрудники")
        self.tabs.addTab(self.category_tab, "Категории")
        self.tabs.addTab(self.product_tab, "Товары")  # Add the new tab

        # Set central widget
        self.setCentralWidget(self.tabs)

    def on_tab_changed(self, index):
        if index == 1:  # Index of the "Сотрудники" tab
            self.employee_tab.load_positions()



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
