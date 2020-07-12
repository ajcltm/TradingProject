import datetime
import sys

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas_datareader.data as web
import pandas as pd
from pandas import Series, DataFrame


def get_code(table, firm):
    code = table[table["name"] == firm]["code"].values[0]
    return "{:06d}".format(int(code))

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(600, 200, 1200, 600)
        self.setWindowTitle("PyChart Viewer v0.1")
        self.setWindowIcon(QIcon('icon.png'))

        self.lineEdit = QLineEdit()
        self.startEdit = QDateEdit()

        self.startEdit.setDate(QDate(2016, 1, 1))
        self.endEdit = QDateEdit()
        self.endEdit.setDate(QDate(2020, 3, 15))

        self.pushButton = QPushButton("차트그리기")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.canvas)

        # Right Layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.lineEdit)
        rightLayout.addWidget(self.startEdit)
        rightLayout.addWidget(self.endEdit)
        rightLayout.addWidget(self.pushButton)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def pushButtonClicked(self):
        firm = self.lineEdit.text()
        startDate = self.startEdit.date()
        endDate = self.endEdit.date()

        start = datetime.datetime(startDate.year(), startDate.month(), startDate.day())
        end = datetime.datetime(endDate.year(), endDate.month(), endDate.day())

        df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
        df = df[['회사명', '종목코드']]
        df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})

        codename = get_code(df, "삼성전자")
        codename = codename + ".KS"



        gs = web.DataReader(codename, "yahoo", start, end)
        gs = gs["Close"]

        #df['MA20'] = df['Adj Close'].rolling(window=20).mean()
        #df['MA60'] = df['Adj Close'].rolling(window=60).mean()

        ax = self.fig.add_subplot(111)
        ax.plot(gs)
        #ax.plot(df.index, df['Adj Close'], label='Adj Close')
        #ax.plot(df.index, df['MA20'], label='MA20')
        #ax.plot(df.index, df['MA60'], label='MA60')
        ax.legend(loc='upper right')
        ax.grid()

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()