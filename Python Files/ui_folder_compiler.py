# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'folder_compiler.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QWidget)

class Ui_Compiler(object):
    def setupUi(self, Compiler):
        if not Compiler.objectName():
            Compiler.setObjectName(u"Compiler")
        Compiler.resize(300, 400)
        self.buttonBox = QDialogButtonBox(Compiler)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(-110, 360, 341, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.compile_folder_list = QListWidget(Compiler)
        self.compile_folder_list.setObjectName(u"compile_folder_list")
        self.compile_folder_list.setGeometry(QRect(20, 50, 251, 201))
        self.compile_folder_list.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.add_folder_comp_button = QPushButton(Compiler)
        self.add_folder_comp_button.setObjectName(u"add_folder_comp_button")
        self.add_folder_comp_button.setGeometry(QRect(20, 260, 80, 24))
        self.rm_folder_comp_button = QPushButton(Compiler)
        self.rm_folder_comp_button.setObjectName(u"rm_folder_comp_button")
        self.rm_folder_comp_button.setGeometry(QRect(170, 260, 101, 24))
        self.label = QLabel(Compiler)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 300, 131, 41))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label_2 = QLabel(Compiler)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 10, 261, 31))
        self.label_2.setFont(font)
        self.select_folder_comp_button = QPushButton(Compiler)
        self.select_folder_comp_button.setObjectName(u"select_folder_comp_button")
        self.select_folder_comp_button.setGeometry(QRect(170, 310, 101, 24))

        self.retranslateUi(Compiler)
        self.buttonBox.accepted.connect(Compiler.accept)
        self.buttonBox.rejected.connect(Compiler.reject)

        QMetaObject.connectSlotsByName(Compiler)
    # setupUi

    def retranslateUi(self, Compiler):
        Compiler.setWindowTitle(QCoreApplication.translate("Compiler", u"Dialog", None))
        self.add_folder_comp_button.setText(QCoreApplication.translate("Compiler", u"Add Folder", None))
        self.rm_folder_comp_button.setText(QCoreApplication.translate("Compiler", u"Remove Folder", None))
        self.label.setText(QCoreApplication.translate("Compiler", u"Select New Data Folder Location:", None))
        self.label_2.setText(QCoreApplication.translate("Compiler", u"Input Folders in Order:", None))
        self.select_folder_comp_button.setText(QCoreApplication.translate("Compiler", u"Select Folder", None))
    # retranslateUi

