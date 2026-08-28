# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calibwindow.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QFrame, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QRadioButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_calib_window(object):
    def setupUi(self, calib_window):
        if not calib_window.objectName():
            calib_window.setObjectName(u"calib_window")
        calib_window.resize(600, 600)
        calib_window.setMinimumSize(QSize(600, 400))
        self.horizontalLayout = QHBoxLayout(calib_window)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_2 = QFrame(calib_window)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(250, 0))
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.label = QLabel(self.frame_2)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 5, 45, 15))
        font = QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.calib_group = QListWidget(self.frame_2)
        self.calib_group.setObjectName(u"calib_group")
        self.calib_group.setGeometry(QRect(10, 20, 100, 90))
        self.calib_group.setFont(font)
        self.calib_group.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.calib_elec = QListWidget(self.frame_2)
        self.calib_elec.setObjectName(u"calib_elec")
        self.calib_elec.setGeometry(QRect(140, 20, 100, 90))
        self.calib_elec.setFont(font)
        self.calib_elec.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_2 = QLabel(self.frame_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(140, 5, 65, 15))
        self.label_2.setFont(font)
        self.calib_yaxis = QListWidget(self.frame_2)
        QListWidgetItem(self.calib_yaxis)
        QListWidgetItem(self.calib_yaxis)
        QListWidgetItem(self.calib_yaxis)
        QListWidgetItem(self.calib_yaxis)
        self.calib_yaxis.setObjectName(u"calib_yaxis")
        self.calib_yaxis.setGeometry(QRect(140, 130, 100, 75))
        self.calib_yaxis.setFont(font)
        self.calib_yaxis.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(140, 110, 45, 15))
        self.label_3.setFont(font)
        self.calib_freq = QListWidget(self.frame_2)
        self.calib_freq.setObjectName(u"calib_freq")
        self.calib_freq.setGeometry(QRect(10, 130, 100, 75))
        self.calib_freq.setFont(font)
        self.calib_freq.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_4 = QLabel(self.frame_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 110, 65, 15))
        self.label_4.setFont(font)
        self.groupBox = QGroupBox(self.frame_2)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 380, 231, 191))
        self.model_dropdown = QComboBox(self.groupBox)
        self.model_dropdown.addItem("")
        self.model_dropdown.addItem("")
        self.model_dropdown.addItem("")
        self.model_dropdown.addItem("")
        self.model_dropdown.setObjectName(u"model_dropdown")
        self.model_dropdown.setGeometry(QRect(10, 20, 211, 22))
        self.formLayoutWidget = QWidget(self.groupBox)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 50, 211, 131))
        self.param_form = QFormLayout(self.formLayoutWidget)
        self.param_form.setObjectName(u"param_form")
        self.param_form.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 0, 131, 21))
        self.label_5.setFont(font)
        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 210, 231, 41))
        self.avg_elec = QRadioButton(self.groupBox_2)
        self.avg_elec.setObjectName(u"avg_elec")
        self.avg_elec.setGeometry(QRect(10, 0, 111, 41))
        self.avg_elec.setFont(font)
        self.avg_lines = QRadioButton(self.groupBox_2)
        self.avg_lines.setObjectName(u"avg_lines")
        self.avg_lines.setGeometry(QRect(140, 0, 101, 41))
        self.avg_lines.setFont(font)
        self.calib_conc = QTableWidget(self.frame_2)
        self.calib_conc.setObjectName(u"calib_conc")
        self.calib_conc.setGeometry(QRect(10, 270, 231, 101))
        self.calib_conc.setStyleSheet(u"QTableWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_6 = QLabel(self.frame_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 250, 131, 21))
        self.label_6.setFont(font)

        self.horizontalLayout.addWidget(self.frame_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.calib_graph = QFrame(calib_window)
        self.calib_graph.setObjectName(u"calib_graph")
        self.calib_graph.setMinimumSize(QSize(125, 250))
        self.calib_graph.setFrameShape(QFrame.Shape.StyledPanel)
        self.calib_graph.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.calib_graph)

        self.calib_outputs = QFrame(calib_window)
        self.calib_outputs.setObjectName(u"calib_outputs")
        self.calib_outputs.setMinimumSize(QSize(125, 0))
        self.calib_outputs.setFrameShape(QFrame.Shape.StyledPanel)
        self.calib_outputs.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.calib_outputs)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.fit_button = QPushButton(calib_window)
        self.fit_button.setObjectName(u"fit_button")
        self.fit_button.setFont(font)

        self.horizontalLayout_2.addWidget(self.fit_button)

        self.calib_window_ok = QDialogButtonBox(calib_window)
        self.calib_window_ok.setObjectName(u"calib_window_ok")
        self.calib_window_ok.setOrientation(Qt.Orientation.Horizontal)
        self.calib_window_ok.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.calib_window_ok.setCenterButtons(False)

        self.horizontalLayout_2.addWidget(self.calib_window_ok)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.retranslateUi(calib_window)
        self.calib_window_ok.accepted.connect(calib_window.accept)
        self.calib_window_ok.rejected.connect(calib_window.reject)

        self.calib_yaxis.setCurrentRow(0)


        QMetaObject.connectSlotsByName(calib_window)
    # setupUi

    def retranslateUi(self, calib_window):
        calib_window.setWindowTitle(QCoreApplication.translate("calib_window", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("calib_window", u"Group:", None))
        self.label_2.setText(QCoreApplication.translate("calib_window", u"Electrode:", None))

        __sortingEnabled = self.calib_yaxis.isSortingEnabled()
        self.calib_yaxis.setSortingEnabled(False)
        ___qlistwidgetitem = self.calib_yaxis.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("calib_window", u"Signal Change %", None));
        ___qlistwidgetitem1 = self.calib_yaxis.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("calib_window", u"Peak Position", None));
        ___qlistwidgetitem2 = self.calib_yaxis.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("calib_window", u"i max", None));
        ___qlistwidgetitem3 = self.calib_yaxis.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("calib_window", u"Peak Height", None));
        self.calib_yaxis.setSortingEnabled(__sortingEnabled)

        self.label_3.setText(QCoreApplication.translate("calib_window", u"Y-axis:", None))
        self.label_4.setText(QCoreApplication.translate("calib_window", u"Frequency:", None))
        self.groupBox.setTitle("")
        self.model_dropdown.setItemText(0, QCoreApplication.translate("calib_window", u"Linear", None))
        self.model_dropdown.setItemText(1, QCoreApplication.translate("calib_window", u"Langmuir (1:1)", None))
        self.model_dropdown.setItemText(2, QCoreApplication.translate("calib_window", u"Hill Equation", None))
        self.model_dropdown.setItemText(3, QCoreApplication.translate("calib_window", u"4-Parameter Logistic (4PL)", None))

        self.label_5.setText(QCoreApplication.translate("calib_window", u"Select Model Type:", None))
        self.groupBox_2.setTitle("")
        self.avg_elec.setText(QCoreApplication.translate("calib_window", u"Average \n"
"Electrodes", None))
        self.avg_lines.setText(QCoreApplication.translate("calib_window", u"Average \n"
"Lines", None))
        self.label_6.setText(QCoreApplication.translate("calib_window", u"Select Concentrations:", None))
        self.fit_button.setText(QCoreApplication.translate("calib_window", u"Fit Data", None))
    # retranslateUi

