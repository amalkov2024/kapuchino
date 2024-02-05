import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QTableWidgetItem


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.pushButton.clicked.connect(self.update_result)
        self.pushButton_2.clicked.connect(self.onClicked)
        self.titles = None
        self.modified = {}

    def update_result(self):
        cur = self.con.cursor()
        # Получили результат запроса, который ввели в текстовое поле
        result = cur.execute("SELECT * FROM Coffee").fetchall()
        # Заполнили размеры таблицы
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(
            len(result[0])
        )  # столбцы и их количество в таблице
        self.titles = [description[0] for description in cur.description]
        self.tableWidget.setHorizontalHeaderLabels(self.titles)
        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()
        self.modified = {}

    def onClicked(self):
        self.redactor = MyRedactor()
        self.redactor.show()
        self.modified = {}


class MyRedactor(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("addEditCoffeeForm.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.pushButton.clicked.connect(self.update_result)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.pushButton_2.clicked.connect(self.save_result)
        self.titles = None
        cur = self.con.cursor()
        self.zap = [
            int(x[0]) for x in list(cur.execute("SELECT * FROM Coffee").fetchall())
        ]
        self.plainTextEdit.setPlainText(
            "Количество редактируемых записей в таблице: " + str(len(self.zap))
        )
        self.modified = {}
        print(self.zap)

    def update_result(self):
        cur = self.con.cursor()
        self.item_id = self.spinBox.text()
        # Получили результат запроса, который ввели в текстовое поле
        result = cur.execute(
            "SELECT * FROM Coffee WHERE id=?", (self.item_id,)
        ).fetchall()
        if not result:
            self.plainTextEdit.setPlainText(
                "Такой записи не существует. Заполните поля и нажмите сохранить для добавления записи"
            )
            nul_zap = (self.item_id, "_", 0, "_", "_", 0, 0)
            self.tableWidget.clear()
            self.tableWidget.setRowCount(1)
            self.tableWidget.setColumnCount(7)  # столбцы и их количество в таблице
            self.titles = [description[0] for description in cur.description]
            self.tableWidget.setHorizontalHeaderLabels(self.titles)
            for j, val in enumerate(nul_zap):
                self.tableWidget.setItem(1, j, QTableWidgetItem(str(val)))
        else:
            # Заполнили размеры таблицы
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setColumnCount(
                len(result[0])
            )  # столбцы и их количество в таблице
            self.titles = [description[0] for description in cur.description]
            self.tableWidget.setHorizontalHeaderLabels(self.titles)
            # Заполнили таблицу полученными элементами
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            # self.tableWidget.resizeColumnsToContents()
            self.modified = {}
            self.zap = [
                int(x[0]) for x in list(cur.execute("SELECT * FROM Coffee").fetchall())
            ]
            self.plainTextEdit.setPlainText(
                "Количество редактируемых записей в таблице: " + str(len(self.zap))
            )

    def item_changed(self, item):
        # Если значение в ячейке было изменено,
        # то в словарь записывается пара: название поля, новое значение
        self.modified[self.titles[item.column()]] = item.text()
        print(self.modified)

    def save_result(self):
        # Добавить записи если нет такого id
        if self.modified and int(self.item_id) not in self.zap:
            mod = (
                int(self.item_id),
                self.modified["category"],
                int(self.modified["roasting"]),
                self.modified["zerno"],
                self.modified["vkus"],
                int(self.modified["price"]),
                int(self.modified["volume"]),
            )
            cur = self.con.cursor()
            cur.execute("INSERT INTO Coffee VALUES(?, ?, ?, ?, ?, ?, ?)", mod)
        elif self.modified:
            cur = self.con.cursor()
            que = "UPDATE Coffee SET\n"
            que += ", ".join(
                [f"{key}='{self.modified.get(key)}'" for key in self.modified.keys()]
            )
            que += "WHERE id = ?"
            cur.execute(que, (self.spinBox.text(),))
        self.con.commit()
        self.modified.clear()
        self.zap = [
            int(x[0]) for x in list(cur.execute("SELECT * FROM Coffee").fetchall())
        ]
        self.plainTextEdit.setPlainText(
            "Количество редактируемых записей в таблице: " + str(len(self.zap))
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
