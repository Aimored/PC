import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QTabWidget,
    QTabBar, QStylePainter, QStyleOptionTab, QStyleOptionTabWidgetFrame, QStyle, QDialog,
    QLabel, QInputDialog,QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor  # Correct import for QColor
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt 
import random
import pymysql
from pymysql import OperationalError
from PyQt6.QtGui import QFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta  # Import timedelta
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import calendar
logging.basicConfig(level=logging.INFO)
font_dir = os.path.join(os.path.dirname(__file__), 'fonts')  # Assuming fonts are in a 'fonts' directory
arial_bold_path = os.path.join(font_dir, 'Arial-Bold.ttf')
arial_path = os.path.join(font_dir, 'Arial.ttf')

# Register the Arial and Arial-Bold fonts
pdfmetrics.registerFont(TTFont('Arial', arial_path))
pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
db_user = "2024_mysql_l_usr"
db_password = "gh1JLEUiTvTdCsjq"
class IntroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добро пожаловать")
        self.setFixedSize(600, 400)

        # Main layout
        main_layout = QVBoxLayout()

        # Label
        self.intro_label = QLabel("Продажа комплектующих для ПК")
        self.intro_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.intro_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        # Button
        self.login_button = QPushButton("Вход")
        self.login_button.setFixedSize(150, 50)
        self.login_button.clicked.connect(self.open_login_dialog)

        # Add widgets to the layout
        main_layout.addStretch()
        main_layout.addWidget(self.intro_label)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.login_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def open_login_dialog(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            logging.info("Login successful, closing intro dialog")
            self.role = login_dialog.role
            self.employee_id = login_dialog.employee_id
            self.accept()  # Close the IntroDialog if login is successful
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(800, 600)

        # Initialize role and employee_id
        self.role = None
        self.employee_id = None
        # Main layout to center everything vertically
        main_layout = QVBoxLayout()
        main_layout.addStretch()  # Add stretchable space at the top

        # Input fields
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        self.username_input.setFixedSize(250, 50)  # Set input field size to 250x50

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedSize(250, 50)  # Set input field size to 250x50

        # Button
        self.login_button = QPushButton("Войти")
        self.login_button.setFixedSize(150, 50)  # Set button size to 150x50

        # Layout for input fields
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)  # Set spacing between input fields
        input_layout.addWidget(self.username_input)
        input_layout.addWidget(self.password_input)

        # Center the input fields using a horizontal layout
        centered_input_layout = QHBoxLayout()
        centered_input_layout.addStretch()
        centered_input_layout.addLayout(input_layout)
        centered_input_layout.addStretch()

        # Center the button using a horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()

        # Add centered layouts to the main layout
        main_layout.addLayout(centered_input_layout)
        main_layout.addSpacing(20)  # Adjust spacing between input fields and button
        main_layout.addLayout(button_layout)
        main_layout.addStretch()  # Add stretchable space at the bottom

        self.setLayout(main_layout)

        self.login_button.clicked.connect(self.authenticate)

        self.employee_id = None  # Store employee ID


    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        logging.info(f"Attempting login with username: {username} and password: {password}")

        if username == "alex" and password == "123":
            logging.info("Admin login successful")
            self.role = "Админ"
            self.accept()
        else:
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='2024_mysql_alex'
                )
                with connection.cursor() as cursor:
                    query = """
                    SELECT u.employee_id, u.login, u.password 
                    FROM users u
                    JOIN sotrudniki s ON u.employee_id = s.id_Sotrudnika
                    WHERE u.login = %s AND u.password = %s
                    """
                    cursor.execute(query, (username, password))
                    result = cursor.fetchone()
                    logging.info(f"Query result: {result}")
                    if result:
                        self.employee_id = result[0]
                        self.role = "Сотрудник"
                        logging.info("Employee login successful")
                        self.accept()
                    else:
                        logging.warning("Invalid credentials provided.")
                        QMessageBox.warning(self, "Ошибка", "Неверные учетные данные.")
            except OperationalError as e:
                logging.error(f"Ошибка подключения к базе данных: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {e}")
            finally:
                if 'connection' in locals():
                    connection.close()
class VerticalQTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabBar(VerticalQTabBar())
        self.setTabPosition(QTabWidget.TabPosition.West)
        self.setFont(QFont("Arial", 10))

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTabWidgetFrame()
        self.initStyleOption(option)
        option.rect = QtCore.QRect(QtCore.QPoint(self.tabBar().geometry().width(), 0), QtCore.QSize(option.rect.width(), option.rect.height()))
        painter.drawPrimitive(QStyle.PrimitiveElement.PE_FrameTabWidget, option)

class VerticalQTabBar(QTabBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setElideMode(QtCore.Qt.TextElideMode.ElideNone)
        self.setFont(QFont("Arial", 10))

    def tabSizeHint(self, index):
        size_hint = super().tabSizeHint(index)
        size_hint.transpose()
        return size_hint

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            if QApplication.style().objectName() == "macos":
                option.shape = QTabBar.Shape.RoundedNorth
                option.position = QStyleOptionTab.TabPosition.Beginning
            else:
                option.shape = QTabBar.Shape.RoundedWest
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, option)
            option.shape = QTabBar.Shape.RoundedNorth
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabLabel, option)

def make_table_uneditable(table: QTableWidget):
    """Set all items in the given QTableWidget to be uneditable."""
    for row in range(table.rowCount()):
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if item is not None:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)


class EmployeeTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(3)
        self.employee_table.setHorizontalHeaderLabels(["ФИО", "Стаж работы", "Удалить"])
        self.employee_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employee_table.cellDoubleClicked.connect(self.open_edit_employee_dialog)

        button_layout = QVBoxLayout()
        self.add_button = QPushButton("Добавить сотрудника")
        self.add_button.clicked.connect(self.show_add_employee_dialog)
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()

        main_layout.addWidget(self.employee_table)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.load_employees()
        make_table_uneditable(self.employee_table)

    def open_edit_employee_dialog(self, row, column):
        employee_id = self.employee_table.item(row, 0).data(QtCore.Qt.ItemDataRole.UserRole)
        name = self.employee_table.item(row, 0).text()
        experience = self.employee_table.item(row, 1).text()

        dialog = EditEmployeeDialog(employee_id, name, experience, self)
        if dialog.exec():
            self.load_employees()

    def load_employees(self):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                query = "SELECT `id_Sotrudnika`, `FIO`, `stag` FROM `sotrudniki`"
                cursor.execute(query)
                results = cursor.fetchall()
                self.employee_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    item = QTableWidgetItem(row_data[1])
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, row_data[0])  # Store employee ID
                    self.employee_table.setItem(row_index, 0, item)
                    self.employee_table.setItem(row_index, 1, QTableWidgetItem(str(row_data[2])))

                    delete_button = QPushButton("Удалить")
                    delete_button.setFixedSize(250, 50)
                    delete_button.clicked.connect(lambda _, id=row_data[0]: self.delete_employee(id))

                    button_widget = QWidget()
                    button_layout = QHBoxLayout(button_widget)
                    button_layout.addWidget(delete_button)
                    button_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    button_layout.setContentsMargins(0, 0, 0, 0)

                    self.employee_table.setCellWidget(row_index, 2, button_widget)

                    # Set the row height
                    self.employee_table.setRowHeight(row_index, 50)  # Adjust the height as needed

                for col in range(self.employee_table.columnCount()):
                    self.employee_table.setColumnWidth(col, 250)
        except OperationalError as e:
            logging.error(f"Ошибка при загрузке сотрудников: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
    def delete_employee(self, employee_id):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                query = "DELETE FROM `sotrudniki` WHERE `id_Sotrudnika` = %s"
                cursor.execute(query, (employee_id,))
                connection.commit()
            QMessageBox.information(self, "Успех", "Сотрудник успешно удален.")
            self.load_employees()
        except OperationalError as e:
            logging.error(f"Ошибка при удалении сотрудника: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении сотрудника: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def show_add_employee_dialog(self):
        dialog = AddEmployeeDialog(self)
        if dialog.exec():
            self.load_employees()

class EditEmployeeDialog(QDialog):
    def __init__(self, employee_id, name, experience, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать сотрудника")
        self.employee_id = employee_id

        layout = QVBoxLayout()

        self.name_input = QLineEdit(name)
        self.experience_input = QLineEdit(str(experience))

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_employee)

        layout.addWidget(QLabel("ФИО"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Стаж работы"))
        layout.addWidget(self.experience_input)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_employee(self):
        name = self.name_input.text().strip()
        experience = self.experience_input.text().strip()

        if name and experience.isdigit():
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='2024_mysql_alex'
                )
                with connection.cursor() as cursor:
                    query = """
                    UPDATE sotrudniki SET FIO = %s, stag = %s
                    WHERE id_Sotrudnika = %s
                    """
                    cursor.execute(query, (name, experience, self.employee_id))
                    connection.commit()
                QMessageBox.information(self, "Успех", "Сотрудник успешно обновлен.")
                self.accept()
            except OperationalError as e:
                logging.error(f"Ошибка при обновлении сотрудника: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении сотрудника: {e}")
            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля корректно.")

class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить продавца")
        layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ФИО")
        self.experience_input = QLineEdit()
        self.experience_input.setPlaceholderText("Стаж работы")
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_employee)
        layout.addWidget(self.name_input)
        layout.addWidget(self.experience_input)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def generate_login(self, name):
        parts = name.split()
        if len(parts) >= 2:
            return parts[0][0].lower() + parts[1].lower()
        return name.lower()

    def generate_password(self):
        return ''.join(random.choices('0123456789', k=2))

    def add_employee(self):
        name = self.name_input.text()
        experience = self.experience_input.text()
        if name and experience.isdigit():
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='2024_mysql_alex'
                )
                with connection.cursor() as cursor:
                    # Добавляем сотрудника в таблицу sotrudniki
                    query = "INSERT INTO `sotrudniki` (`FIO`, `stag`) VALUES (%s, %s)"
                    cursor.execute(query, (name, experience))
                    employee_id = cursor.lastrowid

                    # Генерируем логин и пароль
                    login = self.generate_login(name)
                    password = self.generate_password()

                    # Добавляем данные в таблицу users
                    query = "INSERT INTO `users` (`employee_id`, `login`, `password`) VALUES (%s, %s, %s)"
                    cursor.execute(query, (employee_id, login, password))
                    connection.commit()

                QMessageBox.information(self, "Успех", f"Сотрудник успешно добавлен.\nЛогин: {login}\nПароль: {password}")
                self.accept()
            except OperationalError as e:
                logging.error(f"Ошибка при добавлении сотрудника: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении сотрудника: {e}")
            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля корректно.")


class CategoryTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(1)
        self.category_table.setHorizontalHeaderLabels(["Категория"])
        self.category_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        button_layout = QVBoxLayout()
        self.add_button = QPushButton("Добавить категорию")
        self.add_button.clicked.connect(self.show_add_category_dialog)
        self.delete_button = QPushButton("Удалить категорию")
        self.delete_button.clicked.connect(self.show_delete_category_dialog)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        main_layout.addWidget(self.category_table)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.load_categories()

    def load_categories(self):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                query = "SELECT idKategorii, Kategoriya FROM kategories"
                cursor.execute(query)
                results = cursor.fetchall()
                self.category_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.category_table.setItem(row_index, 0, QTableWidgetItem(row_data[1]))
                    self.category_table.setRowHeight(row_index, 50)  # Move this line inside the loop
                # Set column widths
                for col in range(self.category_table.columnCount()):
                    self.category_table.setColumnWidth(col, 250)
        except OperationalError as e:
            logging.error(f"Ошибка при загрузке категорий: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        make_table_uneditable(self.category_table)
    def show_add_category_dialog(self):
        dialog = AddCategoryDialog(self)
        if dialog.exec():
            self.load_categories()

    def show_delete_category_dialog(self):
        dialog = DeleteCategoryDialog(self)
        if dialog.exec():
            self.load_categories()

class AddCategoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить категорию")
        layout = QVBoxLayout()
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Категория")
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_category)
        layout.addWidget(self.category_input)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def add_category(self):
        category = self.category_input.text()
        if category:
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='2024_mysql_alex'
                )
                with connection.cursor() as cursor:
                    query = "INSERT INTO kategories (Kategoriya) VALUES (%s)"
                    cursor.execute(query, (category,))
                    connection.commit()
                QMessageBox.information(self, "Успех", "Категория успешно добавлена.")
                self.accept()
            except OperationalError as e:
                logging.error(f"Ошибка при добавлении категории: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении категории: {e}")
            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите категорию.")

class DeleteCategoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удалить категорию")
        layout = QVBoxLayout()
        self.category_combo = QComboBox()
        self.load_categories()
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_category)
        layout.addWidget(self.category_combo)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

    def load_categories(self):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                query = "SELECT idKategorii, Kategoriya FROM kategories"
                cursor.execute(query)
                results = cursor.fetchall()
                self.category_combo.clear()
                for row in results:
                    self.category_combo.addItem(row[1], userData=row[0])
        except OperationalError as e:
            logging.error(f"Ошибка при загрузке категорий: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def delete_category(self):
        category_id = self.category_combo.currentData()
        if category_id is not None:
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='2024_mysql_alex'
                )
                with connection.cursor() as cursor:
                    query = "DELETE FROM kategories WHERE idKategorii = %s"
                    cursor.execute(query, (category_id,))
                    connection.commit()
                QMessageBox.information(self, "Успех", "Категория успешно удалена.")
                self.accept()
            except OperationalError as e:
                logging.error(f"Ошибка при удалении категории: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении категории: {e}")
            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите категорию для удаления.")
class SellProductTab(QWidget):
    def __init__(self, employee_id):
        super().__init__()
        self.employee_id = employee_id  # Store employee ID
        main_layout = QHBoxLayout()
        
        # Basket Table
        self.basket_table = QTableWidget()
        self.basket_table.setColumnCount(2)
        self.basket_table.setHorizontalHeaderLabels(["Название товара", "Количество"])
        self.basket_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Set column widths for the basket table
        for col in range(self.basket_table.columnCount()):
            self.basket_table.setColumnWidth(col, 200)  # Set column width to 200

        # Set row height for the basket table
        self.basket_table.verticalHeader().setDefaultSectionSize(50)  # Set row height to 50

        # Total Price and Checkout Button
        right_layout = QVBoxLayout()
        self.total_price_label = QLabel("Итоговая цена: 0")
        self.checkout_button = QPushButton("Оформить")
        self.checkout_button.clicked.connect(self.finalize_sale)

        right_layout.addWidget(self.total_price_label)
        right_layout.addWidget(self.checkout_button)
        right_layout.addStretch()

        # Add widgets to the main layout
        main_layout.addWidget(self.basket_table)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    def finalize_sale(self):
        if self.basket_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста. Пожалуйста, добавьте товары перед оформлением.")
            return

        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                # Retrieve employee name
                cursor.execute(
                    "SELECT FIO FROM sotrudniki WHERE id_Sotrudnika = %s",
                    (self.employee_id,)
                )
                employee_name = cursor.fetchone()[0]

                # Insert into prodaji table using the stored employee ID
                cursor.execute(
                    "INSERT INTO prodaji (data, sotrudnik_id) VALUES (NOW(), %s)",
                    (self.employee_id,)
                )
                sale_id = cursor.lastrowid

                # Insert each item into sostav table and update product quantity
                items = []
                total_price = 0
                for row in range(self.basket_table.rowCount()):
                    product_name = self.basket_table.item(row, 0).text()
                    quantity = int(self.basket_table.item(row, 1).text())

                    # Get product ID, current quantity, and price
                    cursor.execute(
                        "SELECT idTovara, kol, cost FROM tovar WHERE name = %s",
                        (product_name,)
                    )
                    product_id, current_quantity, price = cursor.fetchone()

                    # Insert into sostav table
                    cursor.execute(
                        "INSERT INTO sostav (Kol, tovar_id, prodaji_id) VALUES (%s, %s, %s)",
                        (quantity, product_id, sale_id)
                    )

                    # Update product quantity in tovar table
                    new_quantity = current_quantity - quantity
                    cursor.execute(
                        "UPDATE tovar SET kol = %s WHERE idTovara = %s",
                        (new_quantity, product_id)
                    )

                    # Calculate total price
                    total_price += price * quantity

                    # Collect item details for the receipt
                    items.append((product_name, quantity, price))

                connection.commit()
                QMessageBox.information(self, "Продажа", "Товар успешно продан!")
                self.basket_table.setRowCount(0)
                self.total_price_label.setText("Итоговая цена: 0")

                # Generate PDF receipt
                self.generate_pdf_receipt(sale_id, items, employee_name, total_price)

        except OperationalError as e:
            logging.error(f"Ошибка при оформлении продажи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при оформлении продажи: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def generate_pdf_receipt(self, sale_id, items, employee_name, total_price):
        filename = f"receipt_{sale_id}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Set the font to Arial-Bold for the header
        c.setFont("Arial-Bold", 16)
        c.drawString(100, height - 50, "Чек продажи")

        # Sale ID, Date, and Employee
        c.setFont("Arial", 12)
        c.drawString(100, height - 80, f"ID продажи: {sale_id}")
        c.drawString(100, height - 100, f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, height - 120, f"Продавец: {employee_name}")

        # Table Header
        c.drawString(100, height - 160, "Товар")
        c.drawString(300, height - 160, "Количество")
        c.drawString(400, height - 160, "Цена")

        # Items
        y_position = height - 180
        for product_name, quantity, price in items:
            c.drawString(100, y_position, product_name)
            c.drawString(300, y_position, str(quantity))
            c.drawString(400, y_position, f"{price} руб.")
            y_position -= 20

        # Total Price
        c.drawString(100, y_position - 40, f"Итоговая цена: {total_price} руб.")
        c.drawString(100, y_position - 60, "Спасибо за покупку!")

        c.save()
        QMessageBox.information(self, "Чек", f"Чек сохранен как {filename}")
class ProductTab(QWidget):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.products = []  # Store products for filtering

        # Main layout
        main_layout = QHBoxLayout()  # Use horizontal layout for main layout

        # Left side: Search input and Product Table
        left_layout = QVBoxLayout()

        # Search input and Add Product Button for Admin
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск товаров...")
        self.search_input.setFixedWidth(800)  # Adjust the width to 400 pixels
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_input)

        if role == "Админ":
            self.add_product_button = QPushButton("Добавить товар")
            self.add_product_button.setFixedWidth(150)  # Set the button width to 150 pixels
            self.add_product_button.clicked.connect(self.show_add_product_dialog)
            search_layout.addWidget(self.add_product_button)

        # Add search layout to the left layout
        left_layout.addLayout(search_layout)

        # Product Table
        self.product_table = QTableWidget()
        if role == "Админ":
            self.product_table.setColumnCount(5)
            self.product_table.setHorizontalHeaderLabels(["Название товара", "Цена", "Категория", "Наличие", "Удалить"])
        else:
            self.product_table.setColumnCount(4)
            self.product_table.setHorizontalHeaderLabels(["Название товара", "Цена", "Категория", "Наличие"])

        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Only connect the double-click signal if the user is an admin
        if role == "Админ":
            self.product_table.cellDoubleClicked.connect(self.open_edit_product_dialog)

        # Add product table to the left layout
        left_layout.addWidget(self.product_table)

        # Arrow Buttons Layout
        if role == "Сотрудник":
            arrow_layout = QVBoxLayout()
            self.to_basket_button = QPushButton("→")
            self.to_basket_button.clicked.connect(self.move_to_basket)
            self.from_basket_button = QPushButton("←")
            self.from_basket_button.clicked.connect(self.move_from_basket)
            arrow_layout.addStretch()
            arrow_layout.addWidget(self.to_basket_button)
            arrow_layout.addWidget(self.from_basket_button)
            arrow_layout.addStretch()

        # Right side: Basket and controls
        right_layout = QVBoxLayout()
        right_layout.addStretch()  # Add stretchable space at the top

        # Basket Section
        if role == "Сотрудник":
            self.basket_table = QTableWidget()
            self.basket_table.setColumnCount(2)
            self.basket_table.setHorizontalHeaderLabels(["Название товара", "Количество"])
            self.basket_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.basket_table.setFixedHeight(800)  # Set the height to 800 pixels

            # Set column widths for the basket table
            for col in range(self.basket_table.columnCount()):
                self.basket_table.setColumnWidth(col, 200)  # Set column width to 200

            # Set row height for the basket table
            self.basket_table.verticalHeader().setDefaultSectionSize(50)  # Set row height to 50

            self.total_price_label = QLabel("Итоговая цена: 0")
            self.checkout_button = QPushButton("Оформить")
            self.checkout_button.clicked.connect(self.checkout)

            # Center the basket and controls
            basket_layout = QVBoxLayout()
            basket_layout.addWidget(self.basket_table)
            basket_layout.addWidget(self.total_price_label)
            basket_layout.addWidget(self.checkout_button)
            basket_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            right_layout.addLayout(basket_layout)
            right_layout.addStretch()  # Add stretchable space at the bottom

        # Add left, arrow, and right layouts to the main layout
        main_layout.addLayout(left_layout)
        if role == "Сотрудник":
            main_layout.addLayout(arrow_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.load_products()

    def move_to_basket(self):
        selected_rows = self.product_table.selectionModel().selectedRows()
        for index in selected_rows:
            product_name = self.product_table.item(index.row(), 0).text()
            available_quantity = int(self.product_table.item(index.row(), 3).text())
            if available_quantity > 0:
                quantity, ok = QInputDialog.getInt(self, "Количество", f"Введите количество для {product_name}:", 1, 1, available_quantity)
                if ok and quantity <= available_quantity:
                    row_count = self.basket_table.rowCount()
                    self.basket_table.insertRow(row_count)
                    self.basket_table.setItem(row_count, 0, QTableWidgetItem(product_name))
                    
                    # Create a widget for quantity adjustment
                    quantity_widget = QWidget()
                    quantity_layout = QHBoxLayout()
                    
                    minus_button = QPushButton("-")
                    minus_button.setFixedSize(30, 30)
                    minus_button.clicked.connect(lambda _, row=row_count: self.change_quantity(row, -1))
                    
                    quantity_input = QLineEdit(str(quantity))
                    quantity_input.setFixedWidth(50)
                    quantity_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    quantity_input.setValidator(QtGui.QIntValidator(1, 999))
                    quantity_input.textChanged.connect(lambda text, row=row_count: self.manual_quantity_change(row, text))
                    
                    plus_button = QPushButton("+")
                    plus_button.setFixedSize(30, 30)
                    plus_button.clicked.connect(lambda _, row=row_count: self.change_quantity(row, 1))
                    
                    quantity_layout.addWidget(minus_button)
                    quantity_layout.addWidget(quantity_input)
                    quantity_layout.addWidget(plus_button)
                    quantity_widget.setLayout(quantity_layout)
                    
                    self.basket_table.setCellWidget(row_count, 1, quantity_widget)
                    self.update_total_price()

                    # Update product table quantity
                    new_quantity = available_quantity - quantity
                    self.product_table.setItem(index.row(), 3, QTableWidgetItem(str(new_quantity)))
            else:
                QMessageBox.warning(self, "Ошибка", f"Товар {product_name} недоступен для перемещения.")

    def move_from_basket(self):
        selected_rows = self.basket_table.selectionModel().selectedRows()
        for index in sorted(selected_rows, reverse=True):
            product_name = self.basket_table.item(index.row(), 0).text()
            quantity_widget = self.basket_table.cellWidget(index.row(), 1)
            quantity_input = quantity_widget.findChild(QLineEdit)
            quantity = int(quantity_input.text())

            # Revert quantity in product table
            for row in range(self.product_table.rowCount()):
                if self.product_table.item(row, 0).text() == product_name:
                    available_quantity = int(self.product_table.item(row, 3).text())
                    new_quantity = available_quantity + quantity
                    self.product_table.setItem(row, 3, QTableWidgetItem(str(new_quantity)))
                    break

            self.basket_table.removeRow(index.row())
        self.update_total_price()

    def change_quantity(self, row, change):
        quantity_widget = self.basket_table.cellWidget(row, 1)
        quantity_input = quantity_widget.findChild(QLineEdit)
        current_quantity = int(quantity_input.text())
        new_quantity = current_quantity + change
        if new_quantity > 0:
            quantity_input.setText(str(new_quantity))
            self.update_total_price()

            # Update product table quantity
            product_name = self.basket_table.item(row, 0).text()
            for product_row in range(self.product_table.rowCount()):
                if self.product_table.item(product_row, 0).text() == product_name:
                    available_quantity = int(self.product_table.item(product_row, 3).text())
                    self.product_table.setItem(product_row, 3, QTableWidgetItem(str(available_quantity - change)))
                    break

    def manual_quantity_change(self, row, text):
        if text.isdigit() and int(text) > 0:
            self.update_total_price()

    def update_total_price(self):
        total_price = 0
        for row in range(self.basket_table.rowCount()):
            product_name = self.basket_table.item(row, 0).text()
            quantity_widget = self.basket_table.cellWidget(row, 1)
            quantity_input = quantity_widget.findChild(QLineEdit)
            quantity = int(quantity_input.text())
            price = float(self.get_product_price(product_name))
            total_price += price * quantity
        self.total_price_label.setText(f"Итоговая цена: {total_price}")

    def get_product_price(self, product_name):
        for row in range(self.product_table.rowCount()):
            if self.product_table.item(row, 0).text() == product_name:
                return self.product_table.item(row, 1).text()
        return 0

    def checkout(self):
        if self.basket_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста. Пожалуйста, добавьте товары перед оформлением.")
            return

        # Access the MainWindow instance to get the sell_product_tab
        main_window = self.window()  # Get the top-level window, which is MainWindow
        sell_tab = main_window.sell_product_tab  # Access the sell_product_tab directly from MainWindow

        # Transfer items to the SellProductTab
        sell_tab.basket_table.setRowCount(self.basket_table.rowCount())
        for row in range(self.basket_table.rowCount()):
            product_name = self.basket_table.item(row, 0).text()
            quantity_widget = self.basket_table.cellWidget(row, 1)
            quantity_input = quantity_widget.findChild(QLineEdit)
            quantity = quantity_input.text()

            # Set product name and quantity in the SellProductTab
            sell_tab.basket_table.setItem(row, 0, QTableWidgetItem(product_name))
            sell_tab.basket_table.setItem(row, 1, QTableWidgetItem(quantity))

        # Set the total price in the SellProductTab
        sell_tab.total_price_label.setText(self.total_price_label.text())

        # Clear the current basket
        self.basket_table.setRowCount(0)
        self.total_price_label.setText("Итоговая цена: 0")

        # Switch to the SellProductTab
        main_window.tabs.setCurrentWidget(sell_tab)



    def load_products(self):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                query = """
                SELECT tovar.idTovara, tovar.name, tovar.cost, kategories.Kategoriya, tovar.kol
                FROM tovar
                JOIN kategories ON tovar.kategoriya_id = kategories.idKategorii
                """
                cursor.execute(query)
                self.products = cursor.fetchall()  # Store products for filtering
                self.display_products(self.products)
        except OperationalError as e:
            logging.error(f"Ошибка при загрузке товаров: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        make_table_uneditable(self.product_table)


    def delete_product(self, product_id):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                query = "DELETE FROM tovar WHERE idTovara = %s"
                cursor.execute(query, (product_id,))
                connection.commit()
            QMessageBox.information(self, "Успех", "Товар успешно удален.")
            self.load_products()
        except OperationalError as e:
            logging.error(f"Ошибка при удалении товара: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении товара: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
    def display_products(self, products):
        self.product_table.setRowCount(0)  # Clear the table
        for row_index, row_data in enumerate(products):
            item = QTableWidgetItem(row_data[1])
            item.setData(QtCore.Qt.ItemDataRole.UserRole, row_data[0])  # Store product ID
            self.product_table.insertRow(row_index)
            self.product_table.setItem(row_index, 0, item)
            self.product_table.setItem(row_index, 1, QTableWidgetItem(str(row_data[2])))
            self.product_table.setItem(row_index, 2, QTableWidgetItem(row_data[3]))
            self.product_table.setItem(row_index, 3, QTableWidgetItem(str(row_data[4])))

            if self.role == "Админ":
                delete_button = QPushButton("Удалить")
                delete_button.clicked.connect(lambda _, id=row_data[0]: self.delete_product(id))
                self.product_table.setCellWidget(row_index, 4, delete_button)

            self.product_table.setRowHeight(row_index, 50)
        # Set column widths
        for col in range(self.product_table.columnCount()):
            self.product_table.setColumnWidth(col, 150)

    def filter_products(self):
        search_query = self.search_input.text().lower()
        filtered_products = [product for product in self.products if search_query in product[1].lower()]
        self.display_products(filtered_products)

    def open_edit_product_dialog(self, row, column):
        product_id = self.product_table.item(row, 0).data(QtCore.Qt.ItemDataRole.UserRole)
        name = self.product_table.item(row, 0).text()
        price = self.product_table.item(row, 1).text()
        category = self.product_table.item(row, 2).text()
        quantity = self.product_table.item(row, 3).text()

        dialog = EditProductDialog(product_id, name, price, quantity, category, self)
        if dialog.exec():
            self.load_products()
    def show_add_product_dialog(self):
        dialog = AddProductDialog(self)
        if dialog.exec():
            self.load_products()

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить товар")
        layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название товара")
        
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Цена")
        
        self.availability_input = QLineEdit()
        self.availability_input.setPlaceholderText("Наличие")
        
        self.category_combo = QComboBox()
        self.load_categories()
        
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_product)
        
        layout.addWidget(self.name_input)
        layout.addWidget(self.price_input)
        layout.addWidget(self.availability_input)
        layout.addWidget(self.category_combo)
        layout.addWidget(self.add_button)
        
        self.setLayout(layout)

    def load_categories(self):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                query = "SELECT idKategorii, Kategoriya FROM kategories"
                cursor.execute(query)
                results = cursor.fetchall()
                self.category_combo.clear()
                for row in results:
                    self.category_combo.addItem(row[1], userData=row[0])
        except OperationalError as e:
            logging.error(f"Ошибка при загрузке категорий: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def add_product(self):
        name = self.name_input.text()
        price = self.price_input.text()
        availability = self.availability_input.text()
        category_id = self.category_combo.currentData()
        
        if name and price.isdigit() and availability.isdigit() and category_id is not None:
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='2024_mysql_alex'
                )
                with connection.cursor() as cursor:
                    query = "INSERT INTO tovar (name, cost, kategoriya_id, kol) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (name, price, category_id, availability))
                    connection.commit()
                QMessageBox.information(self, "Успех", "Товар успешно добавлен.")
                self.accept()
            except OperationalError as e:
                logging.error(f"Ошибка при добавлении товара: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении товара: {e}")
            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля.")

class EditProductDialog(QDialog):
    def __init__(self, product_id, name, price, quantity, category_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать товар")
        self.product_id = product_id

        layout = QVBoxLayout()

        self.name_input = QLineEdit(name)
        self.price_input = QLineEdit(str(price))
        self.quantity_input = QLineEdit(str(quantity))
        self.category_combo = QComboBox()
        self.load_categories(category_id)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_product)

        layout.addWidget(QLabel("Название товара"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Цена"))
        layout.addWidget(self.price_input)
        layout.addWidget(QLabel("Наличие"))
        layout.addWidget(self.quantity_input)
        layout.addWidget(QLabel("Категория"))
        layout.addWidget(self.category_combo)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def load_categories(self, current_category_id):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                query = "SELECT idKategorii, Kategoriya FROM kategories"
                cursor.execute(query)
                results = cursor.fetchall()
                self.category_combo.clear()
                for row in results:
                    self.category_combo.addItem(row[1], userData=row[0])
                    if row[0] == current_category_id:
                        self.category_combo.setCurrentIndex(self.category_combo.count() - 1)
        except OperationalError as e:
            logging.error(f"Ошибка при загрузке категорий: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def save_product(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        quantity = self.quantity_input.text().strip()
        category_id = self.category_combo.currentData()

        if name and price.isdigit() and quantity.isdigit():
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='2024_mysql_alex'
                )
                with connection.cursor() as cursor:
                    logging.info(f"Updating product ID {self.product_id} with name: {name}, price: {price}, quantity: {quantity}, category_id: {category_id}")
                    query = """
                    UPDATE tovar SET name = %s, cost = %s, kol = %s, kategoriya_id = %s
                    WHERE idTovara = %s
                    """
                    cursor.execute(query, (name, price, quantity, category_id, self.product_id))
                    connection.commit()  # Ensure the transaction is committed
                QMessageBox.information(self, "Успех", "Товар успешно обновлен.")
                self.accept()
            except OperationalError as e:
                logging.error(f"Ошибка при обновлении товара: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении товара: {e}")
            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля корректно.")


class SalesTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()  # Use horizontal layout for main layout

        # Sales Table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["ID продажи", "Продавец", "Товар", "Количество", "Дата"])
        self.sales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Create Report Button
        self.create_report_button = QPushButton("Создать отчет")
        self.create_report_button.clicked.connect(self.create_report)

        # Right layout for the button
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.create_report_button)
        right_layout.addStretch()

        # Add widgets to main layout
        main_layout.addWidget(self.sales_table)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        self.load_sales()

    def load_sales(self):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                query = """
                SELECT prodaji.idProdaji, sotrudniki.FIO, tovar.name, sostav.Kol, prodaji.data
                FROM sostav
                JOIN prodaji ON sostav.prodaji_id = prodaji.idProdaji
                JOIN sotrudniki ON prodaji.sotrudnik_id = sotrudniki.id_Sotrudnika
                JOIN tovar ON sostav.tovar_id = tovar.idTovara
                """
                cursor.execute(query)
                results = cursor.fetchall()
                self.sales_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    for col_index, value in enumerate(row_data):
                        self.sales_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
                        self.sales_table.setRowHeight(row_index, 50)
                # Set column widths
                for col in range(self.sales_table.columnCount()):
                    self.sales_table.setColumnWidth(col, 250)
        except OperationalError as e:
            logging.error(f"Ошибка при загрузке продаж: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
        make_table_uneditable(self.sales_table)

    def create_report(self):
        try:
            # Establish a connection to the database
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='2024_mysql_alex'
            )
            with connection.cursor() as cursor:
                # Get the current month and year
                now = datetime.now()
                first_day = now.replace(day=1)
                last_day = now.replace(day=calendar.monthrange(now.year, now.month)[1])

                # SQL query to fetch sales data for the current month
                query = """
                SELECT prodaji.idProdaji, sotrudniki.FIO, tovar.name, sostav.Kol, prodaji.data, tovar.cost
                FROM sostav
                JOIN prodaji ON sostav.prodaji_id = prodaji.idProdaji
                JOIN sotrudniki ON prodaji.sotrudnik_id = sotrudniki.id_Sotrudnika
                JOIN tovar ON sostav.tovar_id = tovar.idTovara
                WHERE prodaji.data BETWEEN %s AND %s
                """
                cursor.execute(query, (first_day, last_day))
                results = cursor.fetchall()

                # Calculate the total sales amount
                total_sales = sum(row[3] * row[5] for row in results)

                # Generate the PDF report
                filename = f"monthly_report_{now.strftime('%Y_%m')}.pdf"
                logging.info(f"Saving report to {filename}")
                c = canvas.Canvas(filename, pagesize=A4)
                width, height = A4

                # Set the font and draw the report header
                c.setFont("Arial-Bold", 16)
                c.drawString(100, height - 50, "Отчет по продажам за месяц")

                # Draw the month and total sales amount
                c.setFont("Arial", 12)
                c.drawString(100, height - 80, f"Месяц: {now.strftime('%B %Y')}")
                c.drawString(100, height - 100, f"Итоговая сумма: {total_sales} руб.")

                # Draw the table header
                c.drawString(100, height - 140, "ID продажи")
                c.drawString(200, height - 140, "Продавец")
                c.drawString(300, height - 140, "Товар")
                c.drawString(400, height - 140, "Количество")
                c.drawString(500, height - 140, "Дата")

                # Draw each sale item
                y_position = height - 160
                for sale_id, employee_name, product_name, quantity, sale_date, price in results:
                    c.drawString(100, y_position, str(sale_id))
                    c.drawString(200, y_position, employee_name)
                    c.drawString(300, y_position, product_name)
                    c.drawString(400, y_position, str(quantity))
                    c.drawString(500, y_position, sale_date.strftime('%Y-%m-%d'))
                    y_position -= 20
                    if y_position < 50:  # Check if we need a new page
                        c.showPage()
                        c.setFont("Arial", 12)
                        y_position = height - 50

                # Save the PDF
                c.save()
                QMessageBox.information(self, "Отчет", f"Отчет сохранен как {filename}")

        except OperationalError as e:
            logging.error(f"Ошибка при создании отчета: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании отчета: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during report creation: {e}")
            QMessageBox.critical(self, "Ошибка", f"Unexpected error: {e}")
        finally:
            if 'connection' in locals():
                connection.close()
class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)

    def enterEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(-5, -5, 5, 5))
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(5, 5, -5, -5))
        self.animation.start()
        super().leaveEvent(event)
class MainWindow(QMainWindow):
    def __init__(self, role, employee_id=None):
        super().__init__()
        self.setWindowTitle("Менеджер компании")
        self.tabs = VerticalQTabWidget()
        self.employee_tab = EmployeeTab()
        self.category_tab = CategoryTab()
        self.product_tab = ProductTab(role)
        self.sales_tab = SalesTab()
        self.sell_product_tab = SellProductTab(employee_id)  # Pass employee ID

        if role == "Админ":
            self.tabs.addTab(self.employee_tab, "Продавцы")
            self.tabs.addTab(self.category_tab, "Категории")
            self.tabs.addTab(self.product_tab, "Товары")
            self.tabs.addTab(self.sales_tab, "Продажи")
            # Do not add the "Продать товар" tab for admin
        elif role == "Сотрудник":
            self.tabs.addTab(self.product_tab, "Товары")
            self.tabs.addTab(self.sell_product_tab, "Продать товар")

        self.setCentralWidget(self.tabs)

def apply_advanced_stylesheet(app):
    app.setStyleSheet("""
        QMainWindow {
            background-color: rgba(88, 88, 88, 0.84);  /* Gray background */
        }
        QWidget {
            background-color: rgba(83, 78, 78, 0.4);  /* Gray background for all widgets */
        }
        QPushButton {
            background-color: #800080;  /* Purple background */
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #660066;  /* Darker purple on hover */
        }
        QTableWidget {
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            color: black;  /* Set text color to white */
        }
        QHeaderView::section {
            background-color: #800080;  /* Purple header */
            color: White;
            padding: 5px;
            font-weight: bold;
            border: none;
        }
        QLabel {
            font-size: 16px;
            color: white;  /* Set text color to white */
            font-weight: bold;
        }
        QLineEdit {
            border: 1px solid #ccc;
            padding: 8px;
            border-radius: 5px;
            font-size: 14px;
            color: white;  /* Set text color to white */
        }
        QTabBar::tab {
            background: #e0e0e0;
            padding: 10px;
            border: 1px solid #ccc;
            border-bottom: none;
            border-radius: 5px;
            margin: 2px;
            color: Black;  /* Set text color to white */
        }
        QTabBar::tab:selected {
            background: rgb(230, 225, 225);
            border-bottom: 1px solid rgb(238, 237, 237);
            font-weight: bold;
            color: black;  /* Set text color to white */
        }
    """)



class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)

        # Create and apply shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)

    def enterEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(-5, -5, 5, 5))
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(5, 5, -5, -5))
        self.animation.start()
        super().leaveEvent(event)
def main():
    app = QApplication(sys.argv)
    apply_advanced_stylesheet(app)

    intro_dialog = IntroDialog()
    if intro_dialog.exec() == QDialog.DialogCode.Accepted:
        logging.info("Intro dialog accepted, opening main window")
        window = MainWindow(intro_dialog.role, intro_dialog.employee_id)
        window.showMaximized()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()