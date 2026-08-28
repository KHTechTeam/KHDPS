# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_conc.ui'
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
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(300, 400)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        palette = QPalette()
        brush = QBrush(QColor(31, 31, 31, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        self.label.setPalette(palette)
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setWordWrap(True)

        self.verticalLayout.addWidget(self.label)

        self.conc_table = QTableWidget(Dialog)
        self.conc_table.setObjectName(u"conc_table")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(50)
        sizePolicy.setHeightForWidth(self.conc_table.sizePolicy().hasHeightForWidth())
        self.conc_table.setSizePolicy(sizePolicy)
        self.conc_table.setStyleSheet(u"QTableWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")

        self.verticalLayout.addWidget(self.conc_table)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.importconc = QPushButton(Dialog)
        self.importconc.setObjectName(u"importconc")
        self.importconc.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout.addWidget(self.importconc)

        self.saveconc = QPushButton(Dialog)
        self.saveconc.setObjectName(u"saveconc")
        self.saveconc.setMaximumSize(QSize(125, 16777215))

        self.horizontalLayout.addWidget(self.saveconc)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        font1 = QFont()
        font1.setPointSize(12)
        self.label_2.setFont(font1)
        self.label_2.setWordWrap(True)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.conc_unit = QLineEdit(Dialog)
        self.conc_unit.setObjectName(u"conc_unit")
        self.conc_unit.setFont(font1)

        self.horizontalLayout_2.addWidget(self.conc_unit)

        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)
        self.label_3.setWordWrap(True)

        self.horizontalLayout_2.addWidget(self.label_3)

        self.norm_point = QLineEdit(Dialog)
        self.norm_point.setObjectName(u"norm_point")
        self.norm_point.setFont(font1)

        self.horizontalLayout_2.addWidget(self.norm_point)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        palette1 = QPalette()
        brush1 = QBrush(QColor(255, 255, 255, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush1)
        brush2 = QBrush(QColor(42, 42, 42, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush2)
        brush3 = QBrush(QColor(46, 46, 46, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, brush3)
        brush4 = QBrush(QColor(38, 38, 38, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, brush4)
        brush5 = QBrush(QColor(15, 15, 15, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush5)
        brush6 = QBrush(QColor(21, 21, 21, 255))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush6)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush1)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush1)
        brush7 = QBrush(QColor(0, 0, 0, 255))
        brush7.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush7)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush7)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush5)
        brush8 = QBrush(QColor(255, 255, 220, 255))
        brush8.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, brush8)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, brush7)
        brush9 = QBrush(QColor(255, 255, 255, 127))
        brush9.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush9)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Accent, brush7)
#endif
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, brush3)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, brush4)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush5)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush7)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush7)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush5)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, brush8)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, brush7)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush9)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Accent, brush7)
#endif
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush5)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush2)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, brush3)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush5)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush6)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush5)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush5)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush7)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, brush8)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush7)
        brush10 = QBrush(QColor(15, 15, 15, 127))
        brush10.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush10)
#endif
        brush11 = QBrush(QColor(22, 22, 22, 255))
        brush11.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Accent, brush11)
#endif
        self.buttonBox.setPalette(palette1)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Add All Concentrations/Points:", None))
        self.importconc.setText(QCoreApplication.translate("Dialog", u"Import Concentrations", None))
        self.saveconc.setText(QCoreApplication.translate("Dialog", u"Save Concentrations", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Concentration Units:", None))
        self.conc_unit.setText(QCoreApplication.translate("Dialog", u"uM", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Normalization Point:", None))
        self.norm_point.setText(QCoreApplication.translate("Dialog", u"1", None))
    # retranslateUi

