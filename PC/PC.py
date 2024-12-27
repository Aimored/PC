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
import random
import pymysql
from pymysql import OperationalError
from PyQt6.QtGui import QFont
logging.basicConfig(level=logging.INFO)

db_user = "db_vgu_student"
db_password = "thasrCt3pKYWAYcK"
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в систему")
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.authenticate)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        self.employee_id = None  # Store employee ID

    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        logging.info(f"Attempting login with username: {username} and password: {password}")  # Debugging output

        if username == "alex" and password == "123":
            self.accept()  # Admin access
            self.role = "Админ"
        else:
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='db_vgu_test'
                )
                with connection.cursor() as cursor:
                    # Use the correct column name for employee_id
                    query = """
                    SELECT u.employee_id, u.login, u.password 
                    FROM users u
                    JOIN sotrudniki s ON u.employee_id = s.id_Sotrudnika
                    WHERE u.login = %s AND u.password = %s
                    """
                    cursor.execute(query, (username, password))
                    result = cursor.fetchone()
                    logging.info(f"Query result: {result}")  # Debugging output
                    if result:
                        self.employee_id = result[0]  # Store employee ID
                        self.accept()  # Employee access
                        self.role = "Сотрудник"
                    else:
                        logging.warning("Invalid credentials provided.")  # Debugging output
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



class EmployeeTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(3)
        self.employee_table.setHorizontalHeaderLabels(["Имя", "Стаж работы", "удалить"])
        self.employee_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("Добавить сотрудника")
        self.add_button.clicked.connect(self.show_add_employee_dialog)
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()

        main_layout.addWidget(self.employee_table)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.load_employees()

    def load_employees(self):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )
            with connection.cursor() as cursor:
                query = "SELECT `id_Sotrudnika`, `FIO`, `stag` FROM `sotrudniki`"
                cursor.execute(query)
                results = cursor.fetchall()
                self.employee_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.employee_table.setItem(row_index, 0, QTableWidgetItem(row_data[1]))
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
                database='db_vgu_test'
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



class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить сотрудника")
        layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")
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
                    database='db_vgu_test'
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
                database='db_vgu_test'
            )
            with connection.cursor() as cursor:
                query = "SELECT idKategorii, Kategoriya FROM kategories"
                cursor.execute(query)
                results = cursor.fetchall()
                self.category_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.category_table.setItem(row_index, 0, QTableWidgetItem(row_data[1]))
                self.category_table.setRowHeight(row_index, 50)
                # Set column widths
                for col in range(self.category_table.columnCount()):
                    self.category_table.setColumnWidth(col, 250)
        except OperationalError as e:
            logging.error(f"Ошибка при загрузке категорий: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

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
                    database='db_vgu_test'
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
                database='db_vgu_test'
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
                    database='db_vgu_test'
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
            self.basket_table.setColumnWidth(col, 150)

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
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )
            with connection.cursor() as cursor:
                # Insert into prodaji table using the stored employee ID
                cursor.execute(
                    "INSERT INTO prodaji (data, sotrudnik_id) VALUES (NOW(), %s)",
                    (self.employee_id,)
                )
                sale_id = cursor.lastrowid

                # Insert each item into sostav table and update product quantity
                for row in range(self.basket_table.rowCount()):
                    product_name = self.basket_table.item(row, 0).text()
                    quantity = int(self.basket_table.item(row, 1).text())

                    # Get product ID and current quantity
                    cursor.execute(
                        "SELECT idTovara, kol FROM tovar WHERE name = %s",
                        (product_name,)
                    )
                    product_id, current_quantity = cursor.fetchone()

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

                connection.commit()
                QMessageBox.information(self, "Продажа", "Товар успешно продан!")
                self.basket_table.setRowCount(0)
                self.total_price_label.setText("Итоговая цена: 0")
        except OperationalError as e:
            logging.error(f"Ошибка при оформлении продажи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при оформлении продажи: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

class ProductTab(QWidget):
    def __init__(self, role):
        super().__init__()
        main_layout = QHBoxLayout()  # Use horizontal layout for main layout
        
        # Product Table
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(["Название товара", "Цена", "Категория", "Наличие", "Удалить"])
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Add product table to the main layout
        main_layout.addWidget(self.product_table)

        if role == "Сотрудник":
            # Arrow Buttons
            arrow_layout = QVBoxLayout()
            self.to_basket_button = QPushButton("→")
            self.to_basket_button.clicked.connect(self.move_to_basket)
            self.from_basket_button = QPushButton("←")
            self.from_basket_button.clicked.connect(self.move_from_basket)
            arrow_layout.addStretch()
            arrow_layout.addWidget(self.to_basket_button)
            arrow_layout.addWidget(self.from_basket_button)
            arrow_layout.addStretch()

            # Basket Section
            basket_layout = QVBoxLayout()  # Vertical layout for basket section
            
            self.basket_table = QTableWidget()
            self.basket_table.setColumnCount(2)
            self.basket_table.setHorizontalHeaderLabels(["Название товара", "Количество"])
            self.basket_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

            # Set column widths for the basket table
            for col in range(self.basket_table.columnCount()):
                self.basket_table.setColumnWidth(col, 150)

            self.total_price_label = QLabel("Итоговая цена: 0")
            self.checkout_button = QPushButton("Оформить")
            self.checkout_button.clicked.connect(self.checkout)

            basket_layout.addWidget(self.basket_table)
            basket_layout.addWidget(self.total_price_label)
            basket_layout.addWidget(self.checkout_button)

            # Add arrow layout and basket layout to the main layout
            main_layout.addLayout(arrow_layout)
            main_layout.addLayout(basket_layout)

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
                database='db_vgu_test'
            )
            with connection.cursor() as cursor:
                query = """
                SELECT tovar.idTovara, tovar.name, tovar.cost, kategories.Kategoriya, tovar.kol
                FROM tovar
                JOIN kategories ON tovar.kategoriya_id = kategories.idKategorii
                """
                cursor.execute(query)
                results = cursor.fetchall()
                self.product_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.product_table.setItem(row_index, 0, QTableWidgetItem(row_data[1]))
                    self.product_table.setItem(row_index, 1, QTableWidgetItem(str(row_data[2])))
                    self.product_table.setItem(row_index, 2, QTableWidgetItem(row_data[3]))
                    self.product_table.setItem(row_index, 3, QTableWidgetItem(str(row_data[4])))
                    
                    delete_button = QPushButton("Удалить")
                    delete_button.clicked.connect(lambda _, id=row_data[0]: self.delete_product(id))
                    self.product_table.setCellWidget(row_index, 4, delete_button)
                    self.product_table.setRowHeight(row_index, 50)
                # Set column widths
                for col in range(self.product_table.columnCount()):
                    self.product_table.setColumnWidth(col, 150)
                    
        except OperationalError as e:
            logging.error(f"Ошибка при загрузке товаров: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

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
                database='db_vgu_test'
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
                    database='db_vgu_test'
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


class SalesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["ID продажи", "Сотрудник", "Товар", "Количество", "Дата"])
        self.sales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.sales_table)
        self.setLayout(layout)
        self.load_sales()

    def load_sales(self):
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
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
            self.tabs.addTab(self.employee_tab, "Сотрудники")
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
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #f0f0f0, stop:1 #d0d0d0);
        }
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
        QTableWidget {
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        QHeaderView::section {
            background-color: #0078d7;
            color: white;
            padding: 5px;
            font-weight: bold;
            border: none;
        }
        QLabel {
            font-size: 16px;
            color: #333;
            font-weight: bold;
        }
        QLineEdit {
            border: 1px solid #ccc;
            padding: 8px;
            border-radius: 5px;
            font-size: 14px;
        }
        QTabBar::tab {
            background: #e0e0e0;
            padding: 10px;
            border: 1px solid #ccc;
            border-bottom: none;
            border-radius: 5px;
            margin: 2px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom: 1px solid #ffffff;
            font-weight: bold;
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
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow(login_dialog.role, login_dialog.employee_id)
        window.showMaximized()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()