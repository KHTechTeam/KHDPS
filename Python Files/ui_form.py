# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QListView,
    QListWidget, QListWidgetItem, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSlider, QStatusBar,
    QTabWidget, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1126, 767)
        MainWindow.setMinimumSize(QSize(1126, 767))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.third_row = QHBoxLayout()
        self.third_row.setObjectName(u"third_row")
        self.add_folder_button = QPushButton(self.centralwidget)
        self.add_folder_button.setObjectName(u"add_folder_button")
        self.add_folder_button.setMaximumSize(QSize(100, 16777215))
        font = QFont()
        font.setPointSize(12)
        self.add_folder_button.setFont(font)

        self.third_row.addWidget(self.add_folder_button)

        self.rm_folder_button = QPushButton(self.centralwidget)
        self.rm_folder_button.setObjectName(u"rm_folder_button")
        self.rm_folder_button.setMaximumSize(QSize(120, 16777215))
        self.rm_folder_button.setFont(font)

        self.third_row.addWidget(self.rm_folder_button)

        self.add_group_button = QPushButton(self.centralwidget)
        self.add_group_button.setObjectName(u"add_group_button")
        self.add_group_button.setMaximumSize(QSize(100, 16777215))
        self.add_group_button.setFont(font)

        self.third_row.addWidget(self.add_group_button)

        self.remove_group_button = QPushButton(self.centralwidget)
        self.remove_group_button.setObjectName(u"remove_group_button")
        self.remove_group_button.setMaximumSize(QSize(120, 16777215))
        self.remove_group_button.setFont(font)

        self.third_row.addWidget(self.remove_group_button)


        self.gridLayout.addLayout(self.third_row, 2, 0, 1, 1)

        self.first_row = QHBoxLayout()
        self.first_row.setSpacing(325)
        self.first_row.setObjectName(u"first_row")
        self.first_row.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.first_row.setContentsMargins(0, -1, 0, -1)
        self.load_def_button = QPushButton(self.centralwidget)
        self.load_def_button.setObjectName(u"load_def_button")
        self.load_def_button.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.load_def_button.sizePolicy().hasHeightForWidth())
        self.load_def_button.setSizePolicy(sizePolicy1)
        self.load_def_button.setMaximumSize(QSize(120, 16777215))
        self.load_def_button.setFont(font)

        self.first_row.addWidget(self.load_def_button)

        self.save_defaults_button = QPushButton(self.centralwidget)
        self.save_defaults_button.setObjectName(u"save_defaults_button")
        self.save_defaults_button.setMinimumSize(QSize(0, 0))
        self.save_defaults_button.setMaximumSize(QSize(120, 16777215))
        self.save_defaults_button.setFont(font)

        self.first_row.addWidget(self.save_defaults_button)

        self.folder_compiler_button = QPushButton(self.centralwidget)
        self.folder_compiler_button.setObjectName(u"folder_compiler_button")
        sizePolicy1.setHeightForWidth(self.folder_compiler_button.sizePolicy().hasHeightForWidth())
        self.folder_compiler_button.setSizePolicy(sizePolicy1)
        self.folder_compiler_button.setMaximumSize(QSize(140, 16777215))
        self.folder_compiler_button.setFont(font)

        self.first_row.addWidget(self.folder_compiler_button)

        self.first_row.setStretch(0, 1)
        self.first_row.setStretch(2, 1)

        self.gridLayout.addLayout(self.first_row, 0, 0, 1, 1)

        self.seventh_row = QHBoxLayout()
        self.seventh_row.setObjectName(u"seventh_row")
        self.add_conc_button = QPushButton(self.centralwidget)
        self.add_conc_button.setObjectName(u"add_conc_button")
        self.add_conc_button.setMaximumSize(QSize(160, 16777215))
        self.add_conc_button.setFont(font)

        self.seventh_row.addWidget(self.add_conc_button)

        self.data_output_loc = QPushButton(self.centralwidget)
        self.data_output_loc.setObjectName(u"data_output_loc")
        self.data_output_loc.setMaximumSize(QSize(200, 16777215))
        self.data_output_loc.setFont(font)

        self.seventh_row.addWidget(self.data_output_loc)

        self.graph_button = QPushButton(self.centralwidget)
        self.graph_button.setObjectName(u"graph_button")
        self.graph_button.setMaximumSize(QSize(100, 16777215))
        self.graph_button.setFont(font)

        self.seventh_row.addWidget(self.graph_button)


        self.gridLayout.addLayout(self.seventh_row, 4, 0, 1, 1)

        self.second_row = QHBoxLayout()
        self.second_row.setSpacing(4)
        self.second_row.setObjectName(u"second_row")
        self.second_row.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.second_row.setContentsMargins(-1, 0, -1, 0)
        self.folder_list = QListView(self.centralwidget)
        self.folder_list.setObjectName(u"folder_list")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.folder_list.sizePolicy().hasHeightForWidth())
        self.folder_list.setSizePolicy(sizePolicy2)
        self.folder_list.setMinimumSize(QSize(0, 100))
        self.folder_list.setMaximumSize(QSize(1070, 200))
        self.folder_list.setFont(font)
        self.folder_list.setStyleSheet(u"QListView {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListView::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")

        self.second_row.addWidget(self.folder_list)

        self.group_names_list = QListWidget(self.centralwidget)
        self.group_names_list.setObjectName(u"group_names_list")
        self.group_names_list.setMinimumSize(QSize(0, 0))
        self.group_names_list.setMaximumSize(QSize(16777215, 200))
        self.group_names_list.setFont(font)
        self.group_names_list.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")

        self.second_row.addWidget(self.group_names_list)


        self.gridLayout.addLayout(self.second_row, 1, 0, 1, 1)

        self.sixth_row = QHBoxLayout()
        self.sixth_row.setObjectName(u"sixth_row")
        self.selection_tabs = QTabWidget(self.centralwidget)
        self.selection_tabs.setObjectName(u"selection_tabs")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.selection_tabs.sizePolicy().hasHeightForWidth())
        self.selection_tabs.setSizePolicy(sizePolicy3)
        self.selection_tabs.setMinimumSize(QSize(0, 440))
        self.selection_tabs.setMaximumSize(QSize(16777215, 16777215))
        self.selection_tabs.setBaseSize(QSize(0, 0))
        self.selection_tabs.setFont(font)
        self.selection_tabs.setStyleSheet(u"QTabBar::tab {\n"
"    width: 550px;\n"
"}\n"
"")
        self.selection_tabs.setUsesScrollButtons(False)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.swv_folder_select = QListWidget(self.tab)
        self.swv_folder_select.setObjectName(u"swv_folder_select")
        self.swv_folder_select.setGeometry(QRect(20, 50, 500, 291))
        self.swv_folder_select.setFont(font)
        self.swv_folder_select.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.swv_electrode_select = QListWidget(self.tab)
        self.swv_electrode_select.setObjectName(u"swv_electrode_select")
        self.swv_electrode_select.setGeometry(QRect(580, 50, 500, 291))
        self.swv_electrode_select.setFont(font)
        self.swv_electrode_select.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.swv_folder_es_group_button = QPushButton(self.tab)
        self.swv_folder_es_group_button.setObjectName(u"swv_folder_es_group_button")
        self.swv_folder_es_group_button.setGeometry(QRect(680, 360, 300, 30))
        self.swv_folder_es_group_button.setFont(font)
        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(160, 10, 200, 35))
        font1 = QFont()
        font1.setPointSize(24)
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(730, 10, 200, 35))
        self.label_2.setFont(font1)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fouriersmooth = QCheckBox(self.tab)
        self.fouriersmooth.setObjectName(u"fouriersmooth")
        self.fouriersmooth.setGeometry(QRect(37, 360, 201, 30))
        self.fouriersmooth.setFont(font)
        self.fouriersmooth.setStyleSheet(u"QCheckBox {\n"
"    outline: none;\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background-color: rgb(45, 101, 163);   /* fill color of checkbox when checked */\n"
"	border-radius: 6px;\n"
"}")
        self.fouriersmooth.setTristate(False)
        self.fouriersmoothslider = QSlider(self.tab)
        self.fouriersmoothslider.setObjectName(u"fouriersmoothslider")
        self.fouriersmoothslider.setGeometry(QRect(280, 380, 180, 20))
        self.fouriersmoothslider.setFont(font)
        self.fouriersmoothslider.setStyleSheet(u"/* the track */\n"
"QSlider::groove:horizontal {\n"
"    background: #e0e0e0;\n"
"    height: 4px;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"/* the filled portion to the left of the handle (Qt 6+) */\n"
"QSlider::sub-page:horizontal {\n"
"    background: rgb(45,101,163);\n"
"    border-radius: 15px;\n"
"}\n"
"\n"
"/* the unfilled portion to the right of the handle (Qt 6+) */\n"
"QSlider::add-page:horizontal {\n"
"    background: #e0e0e0;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"/* the thumb */\n"
"QSlider::handle:horizontal {\n"
"    background: rgb(45,101,163);\n"
"    width: 12px;\n"
"    height: 12px;         /* improves hit area */\n"
"    margin: -4px 0;       /* centers handle on the 8px groove */\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"/* hover/pressed feedback (optional) */\n"
"QSlider::handle:horizontal:hover   { background: rgb(45,101,163); }\n"
"QSlider::handle:horizontal:pressed { background: rgb(45,101,163) }")
        self.fouriersmoothslider.setMaximum(100)
        self.fouriersmoothslider.setSliderPosition(50)
        self.fouriersmoothslider.setOrientation(Qt.Orientation.Horizontal)
        self.fouriersmoothvalue = QLineEdit(self.tab)
        self.fouriersmoothvalue.setObjectName(u"fouriersmoothvalue")
        self.fouriersmoothvalue.setGeometry(QRect(315, 349, 110, 31))
        self.fouriersmoothvalue.setFont(font)
        self.fouriersmoothvalue.setFrame(False)
        self.fouriersmoothvalue.setCursorPosition(2)
        self.fouriersmoothvalue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_6 = QLabel(self.tab)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(310, 349, 61, 31))
        self.label_6.setFont(font)
        self.label_7 = QLabel(self.tab)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(378, 349, 151, 31))
        self.label_7.setFont(font)
        self.selection_tabs.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.cv_folder_select = QListWidget(self.tab_2)
        self.cv_folder_select.setObjectName(u"cv_folder_select")
        self.cv_folder_select.setGeometry(QRect(20, 50, 500, 351))
        self.cv_folder_select.setFont(font)
        self.cv_folder_select.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.cv_electrode_select = QListWidget(self.tab_2)
        self.cv_electrode_select.setObjectName(u"cv_electrode_select")
        self.cv_electrode_select.setGeometry(QRect(870, 50, 211, 291))
        self.cv_electrode_select.setFont(font)
        self.cv_electrode_select.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.cv_folder_es_group_button = QPushButton(self.tab_2)
        self.cv_folder_es_group_button.setObjectName(u"cv_folder_es_group_button")
        self.cv_folder_es_group_button.setGeometry(QRect(680, 360, 300, 30))
        self.cv_folder_es_group_button.setFont(font)
        self.label_3 = QLabel(self.tab_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(160, 10, 200, 35))
        self.label_3.setFont(font1)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_4 = QLabel(self.tab_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(880, 10, 200, 35))
        self.label_4.setFont(font1)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cv_data_type_select = QListWidget(self.tab_2)
        QListWidgetItem(self.cv_data_type_select)
        QListWidgetItem(self.cv_data_type_select)
        QListWidgetItem(self.cv_data_type_select)
        QListWidgetItem(self.cv_data_type_select)
        self.cv_data_type_select.setObjectName(u"cv_data_type_select")
        self.cv_data_type_select.setGeometry(QRect(610, 50, 211, 291))
        self.cv_data_type_select.setFont(font)
        self.cv_data_type_select.setStyleSheet(u"QListWidget {\n"
"    outline: none; /* Removes dotted rectangle focus border */\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(45, 101, 163);\n"
"    color: white;\n"
"	border-radius: 6px;\n"
"}")
        self.label_5 = QLabel(self.tab_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(620, 10, 200, 35))
        self.label_5.setFont(font1)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selection_tabs.addTab(self.tab_2, "")

        self.sixth_row.addWidget(self.selection_tabs)


        self.gridLayout.addLayout(self.sixth_row, 3, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1126, 17))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.selection_tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"KHDPS", None))
        self.add_folder_button.setText(QCoreApplication.translate("MainWindow", u"Add Folder", None))
        self.rm_folder_button.setText(QCoreApplication.translate("MainWindow", u"Remove Folder", None))
        self.add_group_button.setText(QCoreApplication.translate("MainWindow", u"Add Group", None))
        self.remove_group_button.setText(QCoreApplication.translate("MainWindow", u"Remove Group", None))
        self.load_def_button.setText(QCoreApplication.translate("MainWindow", u"Load Defaults", None))
        self.save_defaults_button.setText(QCoreApplication.translate("MainWindow", u"Save Defaults", None))
        self.folder_compiler_button.setText(QCoreApplication.translate("MainWindow", u"Folder Compiler", None))
        self.add_conc_button.setText(QCoreApplication.translate("MainWindow", u"Add Concentrations", None))
        self.data_output_loc.setText(QCoreApplication.translate("MainWindow", u"Data Output Location", None))
        self.graph_button.setText(QCoreApplication.translate("MainWindow", u"Graph", None))
        self.swv_folder_es_group_button.setText(QCoreApplication.translate("MainWindow", u"Save Folder and Electrodes to Group", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Folder:", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Electrodes:", None))
        self.fouriersmooth.setText(QCoreApplication.translate("MainWindow", u"  Fourier Smooth Data?", None))
        self.fouriersmoothvalue.setText(QCoreApplication.translate("MainWindow", u"50", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Keep:", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"% of Frequencies", None))
        self.selection_tabs.setTabText(self.selection_tabs.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"SWV", None))
        self.cv_folder_es_group_button.setText(QCoreApplication.translate("MainWindow", u"Save Folder and Electrodes to Group", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Folder:", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Electrodes:", None))

        __sortingEnabled = self.cv_data_type_select.isSortingEnabled()
        self.cv_data_type_select.setSortingEnabled(False)
        ___qlistwidgetitem = self.cv_data_type_select.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"EASA Before Roughening", None));
        ___qlistwidgetitem1 = self.cv_data_type_select.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"EASA After Roughening", None));
        ___qlistwidgetitem2 = self.cv_data_type_select.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"CVs Without Hydrogel", None));
        ___qlistwidgetitem3 = self.cv_data_type_select.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("MainWindow", u"CVs With Hydrogel", None));
        self.cv_data_type_select.setSortingEnabled(__sortingEnabled)

        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Data Type:", None))
        self.selection_tabs.setTabText(self.selection_tabs.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"CV", None))
    # retranslateUi

