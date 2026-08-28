# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'graphing.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHeaderView,
    QLabel, QListWidget, QListWidgetItem, QMdiArea,
    QPushButton, QSizePolicy, QTabWidget, QTableView,
    QWidget)

class Ui_Graphing(object):
    def setupUi(self, Graphing):
        if not Graphing.objectName():
            Graphing.setObjectName(u"Graphing")
        Graphing.resize(1084, 720)
        Graphing.setMinimumSize(QSize(1084, 720))
        self.gridLayout = QGridLayout(Graphing)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(Graphing)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMinimumSize(QSize(270, 0))
        self.tabWidget.setMaximumSize(QSize(270, 16777215))
        self.tabWidget.setStyleSheet(u"QTabBar::tab {\n"
"	width: 55px;\n"
"    background: rgb(60, 60, 60);\n"
"    padding: 6px;\n"
"    border-top-left-radius: 6px;\n"
"    border-top-right-radius: 6px;\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    background: rgb(45, 101, 163);     /* Color for selected tab */\n"
"    color: white;            /* Text color for selected tab */\n"
"}")
        self.tabWidget.setUsesScrollButtons(False)
        self.graph_1 = QWidget()
        self.graph_1.setObjectName(u"graph_1")
        self.label = QLabel(self.graph_1)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 211, 41))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.graph1_groups_list = QListWidget(self.graph_1)
        self.graph1_groups_list.setObjectName(u"graph1_groups_list")
        self.graph1_groups_list.setGeometry(QRect(10, 70, 231, 61))
        self.graph1_groups_list.setFont(font)
        self.graph1_groups_list.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_13 = QLabel(self.graph_1)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(10, 140, 121, 21))
        self.label_13.setFont(font)
        self.graph1_average = QCheckBox(self.graph_1)
        self.graph1_average.setObjectName(u"graph1_average")
        self.graph1_average.setGeometry(QRect(150, 142, 21, 21))
        self.graph1_average.setFont(font)
        self.graph1_average.setStyleSheet(u"QCheckBox {\n"
"    outline: none;\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background-color: rgb(45, 101, 163);   /* fill color of checkbox when checked */\n"
"	border-radius: 6px;\n"
"}")
        self.label_5 = QLabel(self.graph_1)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(180, 140, 71, 21))
        self.label_5.setFont(font)
        self.label_5.setWordWrap(True)
        self.graph1_electrodes_table = QTableView(self.graph_1)
        self.graph1_electrodes_table.setObjectName(u"graph1_electrodes_table")
        self.graph1_electrodes_table.setGeometry(QRect(5, 170, 251, 101))
        self.graph1_electrodes_table.setFont(font)
        self.graph1_electrodes_table.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.graph1_electrodes_table.horizontalHeader().setVisible(True)
        self.graph1_electrodes_table.verticalHeader().setVisible(True)
        self.label_17 = QLabel(self.graph_1)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(10, 280, 141, 21))
        self.label_17.setFont(font)
        self.graph1_freq_table = QTableView(self.graph_1)
        self.graph1_freq_table.setObjectName(u"graph1_freq_table")
        self.graph1_freq_table.setGeometry(QRect(5, 300, 251, 101))
        self.graph1_freq_table.setFont(font)
        self.graph1_freq_table.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_29 = QLabel(self.graph_1)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setGeometry(QRect(40, 395, 41, 31))
        self.label_29.setFont(font)
        self.conc_table_graph1 = QTableView(self.graph_1)
        self.conc_table_graph1.setObjectName(u"conc_table_graph1")
        self.conc_table_graph1.setGeometry(QRect(5, 540, 251, 101))
        font1 = QFont()
        font1.setPointSize(9)
        self.conc_table_graph1.setFont(font1)
        self.conc_table_graph1.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.graph1_plot_button = QPushButton(self.graph_1)
        self.graph1_plot_button.setObjectName(u"graph1_plot_button")
        self.graph1_plot_button.setGeometry(QRect(10, 650, 90, 30))
        self.graph1_plot_button.setFont(font)
        self.graph1_back = QPushButton(self.graph_1)
        self.graph1_back.setObjectName(u"graph1_back")
        self.graph1_back.setGeometry(QRect(170, 650, 90, 30))
        self.graph1_back.setFont(font)
        self.label_22 = QLabel(self.graph_1)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setGeometry(QRect(180, 395, 61, 31))
        self.label_22.setFont(font)
        self.label_22.setWordWrap(False)
        self.label_21 = QLabel(self.graph_1)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setGeometry(QRect(10, 510, 161, 30))
        self.label_21.setFont(font)
        self.graph1_xax = QListWidget(self.graph_1)
        QListWidgetItem(self.graph1_xax)
        QListWidgetItem(self.graph1_xax)
        QListWidgetItem(self.graph1_xax)
        QListWidgetItem(self.graph1_xax)
        self.graph1_xax.setObjectName(u"graph1_xax")
        self.graph1_xax.setGeometry(QRect(5, 420, 111, 91))
        self.graph1_xax.setFont(font)
        self.graph1_xax.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.graph1_yax = QListWidget(self.graph_1)
        QListWidgetItem(self.graph1_yax)
        QListWidgetItem(self.graph1_yax)
        QListWidgetItem(self.graph1_yax)
        QListWidgetItem(self.graph1_yax)
        QListWidgetItem(self.graph1_yax)
        QListWidgetItem(self.graph1_yax)
        QListWidgetItem(self.graph1_yax)
        QListWidgetItem(self.graph1_yax)
        QListWidgetItem(self.graph1_yax)
        self.graph1_yax.setObjectName(u"graph1_yax")
        self.graph1_yax.setGeometry(QRect(135, 420, 121, 91))
        self.graph1_yax.setFont(font)
        self.graph1_yax.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.tabWidget.addTab(self.graph_1, "")
        self.graph_2 = QWidget()
        self.graph_2.setObjectName(u"graph_2")
        self.label_2 = QLabel(self.graph_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 10, 211, 41))
        self.label_2.setFont(font)
        self.label_2.setWordWrap(True)
        self.graph2_groups_list = QListWidget(self.graph_2)
        self.graph2_groups_list.setObjectName(u"graph2_groups_list")
        self.graph2_groups_list.setGeometry(QRect(10, 70, 231, 61))
        self.graph2_groups_list.setFont(font)
        self.graph2_groups_list.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.graph2_average = QCheckBox(self.graph_2)
        self.graph2_average.setObjectName(u"graph2_average")
        self.graph2_average.setGeometry(QRect(150, 142, 21, 21))
        self.graph2_average.setFont(font)
        self.graph2_average.setStyleSheet(u"QCheckBox {\n"
"    outline: none;\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background-color: rgb(45, 101, 163);   /* fill color of checkbox when checked */\n"
"	border-radius: 6px;\n"
"}")
        self.label_6 = QLabel(self.graph_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(180, 140, 71, 21))
        self.label_6.setFont(font)
        self.label_6.setWordWrap(True)
        self.label_14 = QLabel(self.graph_2)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(10, 140, 121, 21))
        self.label_14.setFont(font)
        self.graph2_electrodes_table = QTableView(self.graph_2)
        self.graph2_electrodes_table.setObjectName(u"graph2_electrodes_table")
        self.graph2_electrodes_table.setGeometry(QRect(5, 170, 251, 101))
        self.graph2_electrodes_table.setFont(font)
        self.graph2_electrodes_table.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_18 = QLabel(self.graph_2)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(10, 280, 141, 21))
        self.label_18.setFont(font)
        self.graph2_freq_table = QTableView(self.graph_2)
        self.graph2_freq_table.setObjectName(u"graph2_freq_table")
        self.graph2_freq_table.setGeometry(QRect(5, 300, 251, 101))
        self.graph2_freq_table.setFont(font)
        self.graph2_freq_table.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_26 = QLabel(self.graph_2)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(10, 510, 161, 30))
        self.label_26.setFont(font)
        self.graph2_plot_button = QPushButton(self.graph_2)
        self.graph2_plot_button.setObjectName(u"graph2_plot_button")
        self.graph2_plot_button.setGeometry(QRect(10, 650, 90, 30))
        self.graph2_plot_button.setFont(font)
        self.graph2_back = QPushButton(self.graph_2)
        self.graph2_back.setObjectName(u"graph2_back")
        self.graph2_back.setGeometry(QRect(170, 650, 90, 30))
        self.graph2_back.setFont(font)
        self.conc_table_graph2 = QTableView(self.graph_2)
        self.conc_table_graph2.setObjectName(u"conc_table_graph2")
        self.conc_table_graph2.setGeometry(QRect(5, 540, 251, 101))
        self.conc_table_graph2.setFont(font1)
        self.conc_table_graph2.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_30 = QLabel(self.graph_2)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setGeometry(QRect(40, 395, 51, 31))
        self.label_30.setFont(font)
        self.label_23 = QLabel(self.graph_2)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setGeometry(QRect(180, 395, 61, 31))
        self.label_23.setFont(font)
        self.label_23.setWordWrap(False)
        self.graph2_xax = QListWidget(self.graph_2)
        QListWidgetItem(self.graph2_xax)
        QListWidgetItem(self.graph2_xax)
        QListWidgetItem(self.graph2_xax)
        QListWidgetItem(self.graph2_xax)
        self.graph2_xax.setObjectName(u"graph2_xax")
        self.graph2_xax.setGeometry(QRect(5, 420, 111, 91))
        self.graph2_xax.setFont(font)
        self.graph2_xax.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.graph2_yax = QListWidget(self.graph_2)
        QListWidgetItem(self.graph2_yax)
        QListWidgetItem(self.graph2_yax)
        QListWidgetItem(self.graph2_yax)
        QListWidgetItem(self.graph2_yax)
        QListWidgetItem(self.graph2_yax)
        QListWidgetItem(self.graph2_yax)
        QListWidgetItem(self.graph2_yax)
        QListWidgetItem(self.graph2_yax)
        QListWidgetItem(self.graph2_yax)
        self.graph2_yax.setObjectName(u"graph2_yax")
        self.graph2_yax.setGeometry(QRect(135, 420, 121, 91))
        self.graph2_yax.setFont(font)
        self.graph2_yax.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.tabWidget.addTab(self.graph_2, "")
        self.graph_3 = QWidget()
        self.graph_3.setObjectName(u"graph_3")
        self.label_3 = QLabel(self.graph_3)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 10, 211, 41))
        self.label_3.setFont(font)
        self.label_3.setWordWrap(True)
        self.graph3_groups_list = QListWidget(self.graph_3)
        self.graph3_groups_list.setObjectName(u"graph3_groups_list")
        self.graph3_groups_list.setGeometry(QRect(10, 70, 231, 61))
        self.graph3_groups_list.setFont(font)
        self.graph3_groups_list.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.graph3_average = QCheckBox(self.graph_3)
        self.graph3_average.setObjectName(u"graph3_average")
        self.graph3_average.setGeometry(QRect(150, 142, 21, 21))
        self.graph3_average.setFont(font)
        self.graph3_average.setStyleSheet(u"QCheckBox {\n"
"    outline: none;\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background-color: rgb(45, 101, 163);   /* fill color of checkbox when checked */\n"
"	border-radius: 6px;\n"
"}")
        self.label_7 = QLabel(self.graph_3)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(180, 140, 71, 21))
        self.label_7.setFont(font)
        self.label_7.setWordWrap(True)
        self.label_15 = QLabel(self.graph_3)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(10, 140, 121, 21))
        self.label_15.setFont(font)
        self.graph3_electrodes_table = QTableView(self.graph_3)
        self.graph3_electrodes_table.setObjectName(u"graph3_electrodes_table")
        self.graph3_electrodes_table.setGeometry(QRect(5, 170, 251, 101))
        self.graph3_electrodes_table.setFont(font)
        self.graph3_electrodes_table.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_19 = QLabel(self.graph_3)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setGeometry(QRect(10, 280, 141, 21))
        self.label_19.setFont(font)
        self.graph3_freq_table = QTableView(self.graph_3)
        self.graph3_freq_table.setObjectName(u"graph3_freq_table")
        self.graph3_freq_table.setGeometry(QRect(5, 300, 251, 101))
        self.graph3_freq_table.setFont(font)
        self.graph3_freq_table.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_27 = QLabel(self.graph_3)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(10, 510, 161, 30))
        self.label_27.setFont(font)
        self.graph3_plot_button = QPushButton(self.graph_3)
        self.graph3_plot_button.setObjectName(u"graph3_plot_button")
        self.graph3_plot_button.setGeometry(QRect(10, 650, 90, 30))
        self.graph3_plot_button.setFont(font)
        self.graph3_back = QPushButton(self.graph_3)
        self.graph3_back.setObjectName(u"graph3_back")
        self.graph3_back.setGeometry(QRect(170, 650, 90, 30))
        self.graph3_back.setFont(font)
        self.conc_table_graph3 = QTableView(self.graph_3)
        self.conc_table_graph3.setObjectName(u"conc_table_graph3")
        self.conc_table_graph3.setGeometry(QRect(5, 540, 251, 101))
        self.conc_table_graph3.setFont(font1)
        self.conc_table_graph3.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_31 = QLabel(self.graph_3)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setGeometry(QRect(40, 395, 61, 31))
        self.label_31.setFont(font)
        self.label_24 = QLabel(self.graph_3)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setGeometry(QRect(180, 395, 51, 31))
        self.label_24.setFont(font)
        self.label_24.setWordWrap(False)
        self.graph3_xax = QListWidget(self.graph_3)
        QListWidgetItem(self.graph3_xax)
        QListWidgetItem(self.graph3_xax)
        QListWidgetItem(self.graph3_xax)
        QListWidgetItem(self.graph3_xax)
        self.graph3_xax.setObjectName(u"graph3_xax")
        self.graph3_xax.setGeometry(QRect(5, 420, 111, 91))
        self.graph3_xax.setFont(font)
        self.graph3_xax.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.graph3_yax = QListWidget(self.graph_3)
        QListWidgetItem(self.graph3_yax)
        QListWidgetItem(self.graph3_yax)
        QListWidgetItem(self.graph3_yax)
        QListWidgetItem(self.graph3_yax)
        QListWidgetItem(self.graph3_yax)
        QListWidgetItem(self.graph3_yax)
        QListWidgetItem(self.graph3_yax)
        QListWidgetItem(self.graph3_yax)
        QListWidgetItem(self.graph3_yax)
        self.graph3_yax.setObjectName(u"graph3_yax")
        self.graph3_yax.setGeometry(QRect(135, 420, 121, 91))
        self.graph3_yax.setFont(font)
        self.graph3_yax.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.tabWidget.addTab(self.graph_3, "")
        self.graph_4 = QWidget()
        self.graph_4.setObjectName(u"graph_4")
        self.label_4 = QLabel(self.graph_4)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 10, 211, 41))
        self.label_4.setFont(font)
        self.label_4.setWordWrap(True)
        self.graph4_groups_list = QListWidget(self.graph_4)
        self.graph4_groups_list.setObjectName(u"graph4_groups_list")
        self.graph4_groups_list.setGeometry(QRect(10, 70, 231, 61))
        self.graph4_groups_list.setFont(font)
        self.graph4_groups_list.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.graph4_average = QCheckBox(self.graph_4)
        self.graph4_average.setObjectName(u"graph4_average")
        self.graph4_average.setGeometry(QRect(150, 142, 21, 21))
        self.graph4_average.setFont(font)
        self.graph4_average.setStyleSheet(u"QCheckBox {\n"
"    outline: none;\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background-color: rgb(45, 101, 163);   /* fill color of checkbox when checked */\n"
"	border-radius: 6px;\n"
"}")
        self.label_8 = QLabel(self.graph_4)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(180, 140, 71, 21))
        self.label_8.setFont(font)
        self.label_8.setWordWrap(True)
        self.label_16 = QLabel(self.graph_4)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setGeometry(QRect(10, 140, 121, 21))
        self.label_16.setFont(font)
        self.graph4_electrodes_table = QTableView(self.graph_4)
        self.graph4_electrodes_table.setObjectName(u"graph4_electrodes_table")
        self.graph4_electrodes_table.setGeometry(QRect(5, 170, 251, 101))
        self.graph4_electrodes_table.setFont(font)
        self.graph4_electrodes_table.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_20 = QLabel(self.graph_4)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setGeometry(QRect(10, 280, 141, 21))
        self.label_20.setFont(font)
        self.graph4_freq_table = QTableView(self.graph_4)
        self.graph4_freq_table.setObjectName(u"graph4_freq_table")
        self.graph4_freq_table.setGeometry(QRect(5, 300, 251, 101))
        self.graph4_freq_table.setFont(font)
        self.graph4_freq_table.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_28 = QLabel(self.graph_4)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setGeometry(QRect(10, 510, 161, 30))
        self.label_28.setFont(font)
        self.graph4_plot_button = QPushButton(self.graph_4)
        self.graph4_plot_button.setObjectName(u"graph4_plot_button")
        self.graph4_plot_button.setGeometry(QRect(10, 650, 90, 30))
        self.graph4_plot_button.setFont(font)
        self.graph4_back = QPushButton(self.graph_4)
        self.graph4_back.setObjectName(u"graph4_back")
        self.graph4_back.setGeometry(QRect(170, 650, 90, 30))
        self.graph4_back.setFont(font)
        self.conc_table_graph4 = QTableView(self.graph_4)
        self.conc_table_graph4.setObjectName(u"conc_table_graph4")
        self.conc_table_graph4.setGeometry(QRect(5, 540, 251, 101))
        self.conc_table_graph4.setFont(font1)
        self.conc_table_graph4.setStyleSheet(u"QTableView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QTableView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_32 = QLabel(self.graph_4)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setGeometry(QRect(40, 395, 61, 31))
        self.label_32.setFont(font)
        self.label_25 = QLabel(self.graph_4)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setGeometry(QRect(180, 395, 51, 31))
        self.label_25.setFont(font)
        self.label_25.setWordWrap(False)
        self.graph4_xax = QListWidget(self.graph_4)
        QListWidgetItem(self.graph4_xax)
        QListWidgetItem(self.graph4_xax)
        QListWidgetItem(self.graph4_xax)
        QListWidgetItem(self.graph4_xax)
        self.graph4_xax.setObjectName(u"graph4_xax")
        self.graph4_xax.setGeometry(QRect(5, 420, 111, 91))
        self.graph4_xax.setFont(font)
        self.graph4_xax.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.graph4_yax = QListWidget(self.graph_4)
        QListWidgetItem(self.graph4_yax)
        QListWidgetItem(self.graph4_yax)
        QListWidgetItem(self.graph4_yax)
        QListWidgetItem(self.graph4_yax)
        QListWidgetItem(self.graph4_yax)
        QListWidgetItem(self.graph4_yax)
        QListWidgetItem(self.graph4_yax)
        QListWidgetItem(self.graph4_yax)
        QListWidgetItem(self.graph4_yax)
        self.graph4_yax.setObjectName(u"graph4_yax")
        self.graph4_yax.setGeometry(QRect(135, 420, 121, 91))
        self.graph4_yax.setFont(font)
        self.graph4_yax.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.tabWidget.addTab(self.graph_4, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.mdiArea = QMdiArea(Graphing)
        self.mdiArea.setObjectName(u"mdiArea")
        self.mdiArea.setMinimumSize(QSize(770, 680))
        self.mdiArea.setFont(font1)
        self.mdiArea.setToolTipDuration(3)
        self.mdiArea.setActivationOrder(QMdiArea.WindowOrder.CreationOrder)
        self.mdiArea.setTabsClosable(False)
        self.graph_window4 = QWidget()
        self.graph_window4.setObjectName(u"graph_window4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graph_window4.sizePolicy().hasHeightForWidth())
        self.graph_window4.setSizePolicy(sizePolicy)
        self.graph_window4.setMinimumSize(QSize(200, 300))
        self.label_12 = QLabel(self.graph_window4)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(160, 0, 81, 31))
        font2 = QFont()
        font2.setPointSize(15)
        font2.setBold(True)
        self.label_12.setFont(font2)
        self.label_12.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.calib_graph4 = QPushButton(self.graph_window4)
        self.calib_graph4.setObjectName(u"calib_graph4")
        self.calib_graph4.setGeometry(QRect(260, 10, 141, 51))
        self.calib_graph4.setFont(font)
        self.mdiArea.addSubWindow(self.graph_window4)
        self.graph_window3 = QWidget()
        self.graph_window3.setObjectName(u"graph_window3")
        sizePolicy.setHeightForWidth(self.graph_window3.sizePolicy().hasHeightForWidth())
        self.graph_window3.setSizePolicy(sizePolicy)
        self.graph_window3.setMinimumSize(QSize(200, 300))
        self.label_11 = QLabel(self.graph_window3)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(160, 0, 81, 31))
        self.label_11.setFont(font2)
        self.label_11.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.calib_graph3 = QPushButton(self.graph_window3)
        self.calib_graph3.setObjectName(u"calib_graph3")
        self.calib_graph3.setGeometry(QRect(260, 10, 141, 51))
        self.calib_graph3.setFont(font)
        self.mdiArea.addSubWindow(self.graph_window3)
        self.graph_window2 = QWidget()
        self.graph_window2.setObjectName(u"graph_window2")
        sizePolicy.setHeightForWidth(self.graph_window2.sizePolicy().hasHeightForWidth())
        self.graph_window2.setSizePolicy(sizePolicy)
        self.graph_window2.setMinimumSize(QSize(200, 300))
        self.label_10 = QLabel(self.graph_window2)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(160, 0, 81, 31))
        self.label_10.setFont(font2)
        self.label_10.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.calib_graph2 = QPushButton(self.graph_window2)
        self.calib_graph2.setObjectName(u"calib_graph2")
        self.calib_graph2.setGeometry(QRect(260, 10, 141, 51))
        self.calib_graph2.setFont(font)
        self.mdiArea.addSubWindow(self.graph_window2)
        self.graph_window1 = QWidget()
        self.graph_window1.setObjectName(u"graph_window1")
        sizePolicy.setHeightForWidth(self.graph_window1.sizePolicy().hasHeightForWidth())
        self.graph_window1.setSizePolicy(sizePolicy)
        self.graph_window1.setMinimumSize(QSize(200, 300))
        self.graph_window1.setFont(font1)
        self.label_9 = QLabel(self.graph_window1)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(160, 0, 81, 31))
        self.label_9.setFont(font2)
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.calib_graph1 = QPushButton(self.graph_window1)
        self.calib_graph1.setObjectName(u"calib_graph1")
        self.calib_graph1.setGeometry(QRect(260, 10, 141, 51))
        self.calib_graph1.setFont(font)
        self.mdiArea.addSubWindow(self.graph_window1)

        self.gridLayout.addWidget(self.mdiArea, 0, 1, 1, 1)


        self.retranslateUi(Graphing)

        self.tabWidget.setCurrentIndex(0)
        self.graph1_xax.setCurrentRow(0)
        self.graph1_yax.setCurrentRow(2)
        self.graph2_xax.setCurrentRow(0)
        self.graph2_yax.setCurrentRow(2)
        self.graph3_xax.setCurrentRow(0)
        self.graph3_yax.setCurrentRow(2)
        self.graph4_xax.setCurrentRow(0)
        self.graph4_yax.setCurrentRow(2)


        QMetaObject.connectSlotsByName(Graphing)
    # setupUi

    def retranslateUi(self, Graphing):
        Graphing.setWindowTitle(QCoreApplication.translate("Graphing", u"Form", None))
        self.label.setText(QCoreApplication.translate("Graphing", u"Select which group(s) to display on Graph 1:", None))
        self.label_13.setText(QCoreApplication.translate("Graphing", u"Select Electrodes:", None))
        self.graph1_average.setText("")
        self.label_5.setText(QCoreApplication.translate("Graphing", u"Average?", None))
        self.label_17.setText(QCoreApplication.translate("Graphing", u"Select Frequencies:", None))
        self.label_29.setText(QCoreApplication.translate("Graphing", u"x-axis", None))
        self.graph1_plot_button.setText(QCoreApplication.translate("Graphing", u"Plot", None))
        self.graph1_back.setText(QCoreApplication.translate("Graphing", u"Back", None))
        self.label_22.setText(QCoreApplication.translate("Graphing", u"y-axis", None))
        self.label_21.setText(QCoreApplication.translate("Graphing", u"Select Concentrations:", None))

        __sortingEnabled = self.graph1_xax.isSortingEnabled()
        self.graph1_xax.setSortingEnabled(False)
        ___qlistwidgetitem = self.graph1_xax.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("Graphing", u"Scan Number", None));
        ___qlistwidgetitem1 = self.graph1_xax.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("Graphing", u"Concentration", None));
        ___qlistwidgetitem2 = self.graph1_xax.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("Graphing", u"Time", None));
        ___qlistwidgetitem3 = self.graph1_xax.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("Graphing", u"Frequency", None));
        self.graph1_xax.setSortingEnabled(__sortingEnabled)


        __sortingEnabled1 = self.graph1_yax.isSortingEnabled()
        self.graph1_yax.setSortingEnabled(False)
        ___qlistwidgetitem4 = self.graph1_yax.item(0)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("Graphing", u"Peak Height", None));
        ___qlistwidgetitem5 = self.graph1_yax.item(1)
        ___qlistwidgetitem5.setText(QCoreApplication.translate("Graphing", u"i max", None));
        ___qlistwidgetitem6 = self.graph1_yax.item(2)
        ___qlistwidgetitem6.setText(QCoreApplication.translate("Graphing", u"Signal Change (%)", None));
        ___qlistwidgetitem7 = self.graph1_yax.item(3)
        ___qlistwidgetitem7.setText(QCoreApplication.translate("Graphing", u"AUC", None));
        ___qlistwidgetitem8 = self.graph1_yax.item(4)
        ___qlistwidgetitem8.setText(QCoreApplication.translate("Graphing", u"Peak Position", None));
        ___qlistwidgetitem9 = self.graph1_yax.item(5)
        ___qlistwidgetitem9.setText(QCoreApplication.translate("Graphing", u"i max/cm\u00b2", None));
        ___qlistwidgetitem10 = self.graph1_yax.item(6)
        ___qlistwidgetitem10.setText(QCoreApplication.translate("Graphing", u"Peak Height/cm\u00b2", None));
        ___qlistwidgetitem11 = self.graph1_yax.item(7)
        ___qlistwidgetitem11.setText(QCoreApplication.translate("Graphing", u"AUC/cm\u00b2", None));
        ___qlistwidgetitem12 = self.graph1_yax.item(8)
        ___qlistwidgetitem12.setText(QCoreApplication.translate("Graphing", u"Concentration", None));
        self.graph1_yax.setSortingEnabled(__sortingEnabled1)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.graph_1), QCoreApplication.translate("Graphing", u"Graph 1", None))
        self.label_2.setText(QCoreApplication.translate("Graphing", u"Select which group(s) to display on Graph 2:", None))
        self.graph2_average.setText("")
        self.label_6.setText(QCoreApplication.translate("Graphing", u"Average?", None))
        self.label_14.setText(QCoreApplication.translate("Graphing", u"Select Electrodes:", None))
        self.label_18.setText(QCoreApplication.translate("Graphing", u"Select Frequencies:", None))
        self.label_26.setText(QCoreApplication.translate("Graphing", u"Select Concentrations:", None))
        self.graph2_plot_button.setText(QCoreApplication.translate("Graphing", u"Plot", None))
        self.graph2_back.setText(QCoreApplication.translate("Graphing", u"Back", None))
        self.label_30.setText(QCoreApplication.translate("Graphing", u"x-axis", None))
        self.label_23.setText(QCoreApplication.translate("Graphing", u"y-axis", None))

        __sortingEnabled2 = self.graph2_xax.isSortingEnabled()
        self.graph2_xax.setSortingEnabled(False)
        ___qlistwidgetitem13 = self.graph2_xax.item(0)
        ___qlistwidgetitem13.setText(QCoreApplication.translate("Graphing", u"Scan Number", None));
        ___qlistwidgetitem14 = self.graph2_xax.item(1)
        ___qlistwidgetitem14.setText(QCoreApplication.translate("Graphing", u"Concentration", None));
        ___qlistwidgetitem15 = self.graph2_xax.item(2)
        ___qlistwidgetitem15.setText(QCoreApplication.translate("Graphing", u"Time", None));
        ___qlistwidgetitem16 = self.graph2_xax.item(3)
        ___qlistwidgetitem16.setText(QCoreApplication.translate("Graphing", u"Frequency", None));
        self.graph2_xax.setSortingEnabled(__sortingEnabled2)


        __sortingEnabled3 = self.graph2_yax.isSortingEnabled()
        self.graph2_yax.setSortingEnabled(False)
        ___qlistwidgetitem17 = self.graph2_yax.item(0)
        ___qlistwidgetitem17.setText(QCoreApplication.translate("Graphing", u"Peak Height", None));
        ___qlistwidgetitem18 = self.graph2_yax.item(1)
        ___qlistwidgetitem18.setText(QCoreApplication.translate("Graphing", u"i max", None));
        ___qlistwidgetitem19 = self.graph2_yax.item(2)
        ___qlistwidgetitem19.setText(QCoreApplication.translate("Graphing", u"Signal Change (%)", None));
        ___qlistwidgetitem20 = self.graph2_yax.item(3)
        ___qlistwidgetitem20.setText(QCoreApplication.translate("Graphing", u"AUC", None));
        ___qlistwidgetitem21 = self.graph2_yax.item(4)
        ___qlistwidgetitem21.setText(QCoreApplication.translate("Graphing", u"Peak Position", None));
        ___qlistwidgetitem22 = self.graph2_yax.item(5)
        ___qlistwidgetitem22.setText(QCoreApplication.translate("Graphing", u"i max/cm\u00b2", None));
        ___qlistwidgetitem23 = self.graph2_yax.item(6)
        ___qlistwidgetitem23.setText(QCoreApplication.translate("Graphing", u"Peak Height/cm\u00b2", None));
        ___qlistwidgetitem24 = self.graph2_yax.item(7)
        ___qlistwidgetitem24.setText(QCoreApplication.translate("Graphing", u"AUC/cm\u00b2", None));
        ___qlistwidgetitem25 = self.graph2_yax.item(8)
        ___qlistwidgetitem25.setText(QCoreApplication.translate("Graphing", u"Concentration", None));
        self.graph2_yax.setSortingEnabled(__sortingEnabled3)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.graph_2), QCoreApplication.translate("Graphing", u"Graph 2", None))
        self.label_3.setText(QCoreApplication.translate("Graphing", u"Select which group(s) to display on Graph 3:", None))
        self.graph3_average.setText("")
        self.label_7.setText(QCoreApplication.translate("Graphing", u"Average?", None))
        self.label_15.setText(QCoreApplication.translate("Graphing", u"Select Electrodes:", None))
        self.label_19.setText(QCoreApplication.translate("Graphing", u"Select Frequencies:", None))
        self.label_27.setText(QCoreApplication.translate("Graphing", u"Select Concentrations:", None))
        self.graph3_plot_button.setText(QCoreApplication.translate("Graphing", u"Plot", None))
        self.graph3_back.setText(QCoreApplication.translate("Graphing", u"Back", None))
        self.label_31.setText(QCoreApplication.translate("Graphing", u"x-axis", None))
        self.label_24.setText(QCoreApplication.translate("Graphing", u"y-axis", None))

        __sortingEnabled4 = self.graph3_xax.isSortingEnabled()
        self.graph3_xax.setSortingEnabled(False)
        ___qlistwidgetitem26 = self.graph3_xax.item(0)
        ___qlistwidgetitem26.setText(QCoreApplication.translate("Graphing", u"Scan Number", None));
        ___qlistwidgetitem27 = self.graph3_xax.item(1)
        ___qlistwidgetitem27.setText(QCoreApplication.translate("Graphing", u"Concentration", None));
        ___qlistwidgetitem28 = self.graph3_xax.item(2)
        ___qlistwidgetitem28.setText(QCoreApplication.translate("Graphing", u"Time", None));
        ___qlistwidgetitem29 = self.graph3_xax.item(3)
        ___qlistwidgetitem29.setText(QCoreApplication.translate("Graphing", u"Frequency", None));
        self.graph3_xax.setSortingEnabled(__sortingEnabled4)


        __sortingEnabled5 = self.graph3_yax.isSortingEnabled()
        self.graph3_yax.setSortingEnabled(False)
        ___qlistwidgetitem30 = self.graph3_yax.item(0)
        ___qlistwidgetitem30.setText(QCoreApplication.translate("Graphing", u"Peak Height", None));
        ___qlistwidgetitem31 = self.graph3_yax.item(1)
        ___qlistwidgetitem31.setText(QCoreApplication.translate("Graphing", u"i max", None));
        ___qlistwidgetitem32 = self.graph3_yax.item(2)
        ___qlistwidgetitem32.setText(QCoreApplication.translate("Graphing", u"Signal Change (%)", None));
        ___qlistwidgetitem33 = self.graph3_yax.item(3)
        ___qlistwidgetitem33.setText(QCoreApplication.translate("Graphing", u"AUC", None));
        ___qlistwidgetitem34 = self.graph3_yax.item(4)
        ___qlistwidgetitem34.setText(QCoreApplication.translate("Graphing", u"Peak Position", None));
        ___qlistwidgetitem35 = self.graph3_yax.item(5)
        ___qlistwidgetitem35.setText(QCoreApplication.translate("Graphing", u"i max/cm\u00b2", None));
        ___qlistwidgetitem36 = self.graph3_yax.item(6)
        ___qlistwidgetitem36.setText(QCoreApplication.translate("Graphing", u"Peak Height/cm\u00b2", None));
        ___qlistwidgetitem37 = self.graph3_yax.item(7)
        ___qlistwidgetitem37.setText(QCoreApplication.translate("Graphing", u"AUC/cm\u00b2", None));
        ___qlistwidgetitem38 = self.graph3_yax.item(8)
        ___qlistwidgetitem38.setText(QCoreApplication.translate("Graphing", u"Concentration", None));
        self.graph3_yax.setSortingEnabled(__sortingEnabled5)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.graph_3), QCoreApplication.translate("Graphing", u"Graph 3", None))
        self.label_4.setText(QCoreApplication.translate("Graphing", u"Select which group(s) to display on Graph 4:", None))
        self.graph4_average.setText("")
        self.label_8.setText(QCoreApplication.translate("Graphing", u"Average?", None))
        self.label_16.setText(QCoreApplication.translate("Graphing", u"Select Electrodes:", None))
        self.label_20.setText(QCoreApplication.translate("Graphing", u"Select Frequencies:", None))
        self.label_28.setText(QCoreApplication.translate("Graphing", u"Select Concentrations:", None))
        self.graph4_plot_button.setText(QCoreApplication.translate("Graphing", u"Plot", None))
        self.graph4_back.setText(QCoreApplication.translate("Graphing", u"Back", None))
        self.label_32.setText(QCoreApplication.translate("Graphing", u"x-axis", None))
        self.label_25.setText(QCoreApplication.translate("Graphing", u"y-axis", None))

        __sortingEnabled6 = self.graph4_xax.isSortingEnabled()
        self.graph4_xax.setSortingEnabled(False)
        ___qlistwidgetitem39 = self.graph4_xax.item(0)
        ___qlistwidgetitem39.setText(QCoreApplication.translate("Graphing", u"Scan Number", None));
        ___qlistwidgetitem40 = self.graph4_xax.item(1)
        ___qlistwidgetitem40.setText(QCoreApplication.translate("Graphing", u"Concentration", None));
        ___qlistwidgetitem41 = self.graph4_xax.item(2)
        ___qlistwidgetitem41.setText(QCoreApplication.translate("Graphing", u"Time", None));
        ___qlistwidgetitem42 = self.graph4_xax.item(3)
        ___qlistwidgetitem42.setText(QCoreApplication.translate("Graphing", u"Frequency", None));
        self.graph4_xax.setSortingEnabled(__sortingEnabled6)


        __sortingEnabled7 = self.graph4_yax.isSortingEnabled()
        self.graph4_yax.setSortingEnabled(False)
        ___qlistwidgetitem43 = self.graph4_yax.item(0)
        ___qlistwidgetitem43.setText(QCoreApplication.translate("Graphing", u"Peak Height", None));
        ___qlistwidgetitem44 = self.graph4_yax.item(1)
        ___qlistwidgetitem44.setText(QCoreApplication.translate("Graphing", u"i max", None));
        ___qlistwidgetitem45 = self.graph4_yax.item(2)
        ___qlistwidgetitem45.setText(QCoreApplication.translate("Graphing", u"Signal Change (%)", None));
        ___qlistwidgetitem46 = self.graph4_yax.item(3)
        ___qlistwidgetitem46.setText(QCoreApplication.translate("Graphing", u"AUC", None));
        ___qlistwidgetitem47 = self.graph4_yax.item(4)
        ___qlistwidgetitem47.setText(QCoreApplication.translate("Graphing", u"Peak Position", None));
        ___qlistwidgetitem48 = self.graph4_yax.item(5)
        ___qlistwidgetitem48.setText(QCoreApplication.translate("Graphing", u"i max/cm\u00b2", None));
        ___qlistwidgetitem49 = self.graph4_yax.item(6)
        ___qlistwidgetitem49.setText(QCoreApplication.translate("Graphing", u"Peak Height/cm\u00b2", None));
        ___qlistwidgetitem50 = self.graph4_yax.item(7)
        ___qlistwidgetitem50.setText(QCoreApplication.translate("Graphing", u"AUC/cm\u00b2", None));
        ___qlistwidgetitem51 = self.graph4_yax.item(8)
        ___qlistwidgetitem51.setText(QCoreApplication.translate("Graphing", u"Concentration", None));
        self.graph4_yax.setSortingEnabled(__sortingEnabled7)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.graph_4), QCoreApplication.translate("Graphing", u"Graph 4", None))
        self.graph_window4.setWindowTitle(QCoreApplication.translate("Graphing", u"Graph 4", None))
        self.label_12.setText(QCoreApplication.translate("Graphing", u"Graph 4", None))
        self.calib_graph4.setText(QCoreApplication.translate("Graphing", u"Graph 4 \n"
"Calibration Panel", None))
        self.graph_window3.setWindowTitle(QCoreApplication.translate("Graphing", u"Graph 3", None))
        self.label_11.setText(QCoreApplication.translate("Graphing", u"Graph 3", None))
        self.calib_graph3.setText(QCoreApplication.translate("Graphing", u"Graph 3 \n"
"Calibration Panel", None))
        self.graph_window2.setWindowTitle(QCoreApplication.translate("Graphing", u"Graph 2", None))
        self.label_10.setText(QCoreApplication.translate("Graphing", u"Graph 2", None))
        self.calib_graph2.setText(QCoreApplication.translate("Graphing", u"Graph 2 \n"
"Calibration Panel", None))
        self.graph_window1.setWindowTitle(QCoreApplication.translate("Graphing", u"Graph 1", None))
        self.label_9.setText(QCoreApplication.translate("Graphing", u"Graph 1", None))
        self.calib_graph1.setText(QCoreApplication.translate("Graphing", u"Graph 1 \n"
"Calibration Panel", None))
    # retranslateUi

