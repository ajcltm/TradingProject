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
        self.setGeometry(150, 100, 1500, 800)
        self.setWindowTitle("Trading Simulator")
        self.setWindowIcon(QIcon('icon.png'))

        self.firmCombobox = QComboBox()
        self.firmCombobox.setEditable(True)
        self.firmdf = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
        self.firmdf = self.firmdf[['회사명', '종목코드']]
        self.firmdf = self.firmdf.rename(columns={'회사명': 'name', '종목코드': 'code'})
        for firm in self.firmdf['name']:
            self.firmCombobox.addItem(firm)


        self.startEdit = QDateEdit()

        self.startEdit.setDate(QDate(2016, 1, 1))
        self.endEdit = QDateEdit()
        self.endEdit.setDate(QDate(2020, 3, 15))

        self.pushButton = QPushButton("Launch")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.buyDateEdit=QDateEdit()
        self.buyLineEdit=QLineEdit()
        self.pushBuyButton = QPushButton("Buy")
        self.pushBuyButton.clicked.connect(self.pushBuyButtonClicked)
        self.sellDateEdit=QDateEdit()
        self.sellLineEdit=QLineEdit()
        self.pushSellButton = QPushButton("Sell")
        self.pushSellButton.clicked.connect(self.pushSellButtonClicked)

        # Right Layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.firmCombobox)
        rightLayout.addWidget(self.startEdit)
        rightLayout.addWidget(self.endEdit)
        rightLayout.addWidget(self.pushButton)
        groupLayout = QHBoxLayout()
        groupLayout.addWidget(self.buyDateEdit)
        groupLayout.addWidget(self.buyLineEdit)
        groupLayout.addWidget(self.pushBuyButton)
        rightLayout.addLayout(groupLayout)
        groupLayout = QHBoxLayout()
        groupLayout.addWidget(self.sellDateEdit)
        groupLayout.addWidget(self.sellLineEdit)
        groupLayout.addWidget(self.pushSellButton)
        rightLayout.addLayout(groupLayout)
        rightLayout.addStretch(1)

        plt.style.use('ggplot')
        self.fig = plt.Figure(tight_layout=True)
        #self.fig.subplot(1, 1, 1)
        self.canvas = FigureCanvas(self.fig)
        #self.canvas.setSizePolicy(QSizePolicy.Expanding,
        #                          QSizePolicy.Expanding)
        #self.fig.tight_layout()

        self.seriestableWidget = QTableWidget()
        self.simultableWidget = QTableWidget()

        upleftLayout = QHBoxLayout()
        upleftLayout.addWidget(self.canvas)
        upleftLayout.addWidget(self.seriestableWidget)
        self.seriestableWidget.setFixedWidth(500)
        upleftLayout.setStretchFactor(self.canvas, 1)
        upleftLayout.setStretchFactor(self.seriestableWidget, 0)
        #leftLayout.addStretch(1)

        leftLayout = QVBoxLayout()
        leftLayout.addLayout(upleftLayout)
        leftLayout.addWidget(self.simultableWidget)


        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

    def showDataTable(self, gs):
        self.seriestableWidget.setRowCount(len(gs.index))
        self.seriestableWidget.setColumnCount(3)

        #labels = ['Volumn', 'Close'];
        for row in range(len(gs.index)) :
            #for col in labels:
            self.seriestableWidget.setItem(row, 0, QTableWidgetItem(gs.index[row].strftime("%Y/%m/%d")))
            self.seriestableWidget.setItem(row, 1, QTableWidgetItem("{0}".format(gs.loc[gs.index[row], 'Close'])))
            self.seriestableWidget.setItem(row, 2, QTableWidgetItem("{0}".format(gs.loc[gs.index[row], 'Volume'])))

        #self.tableWidget.setItem(0, 0, QTableWidgetItem("Name"))
        #self.tableWidget.setItem(0, 1, QTableWidgetItem("Email"))
        #self.tableWidget.setItem(0, 2, QTableWidgetItem("Phone No"))

    def pushButtonClicked(self):
        firm = self.firmCombobox.currentText()
        startDate = self.startEdit.date()
        endDate = self.endEdit.date()

        start = datetime.datetime(startDate.year(), startDate.month(), startDate.day())
        end = datetime.datetime(endDate.year(), endDate.month(), endDate.day())

        codename = get_code(self.firmdf, firm)
        codename = codename + ".KS"

        gs = web.DataReader(codename, "yahoo", start, end)
        gs = gs[["Close", "Volume"]]

        #df['MA20'] = df['Adj Close'].rolling(window=20).mean()
        #df['MA60'] = df['Adj Close'].rolling(window=60).mean()
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(gs["Close"])
        #ax.plot(df.index, df['Adj Close'], label='Adj Close')
        #ax.plot(df.index, df['MA20'], label='MA20')
        #ax.plot(df.index, df['MA60'], label='MA60')
        ax.grid()

        self.canvas.draw()
        self.showDataTable(gs)
        self.gs = gs

        self.simuldf = pd.DataFrame(data=[], columns=["Position", "Date", "Price", "Quantity", "PQ"])

        gsStartDate = self.gs.index[0]
        self.buyDateEdit.setDate(QDate(gsStartDate.year, gsStartDate.month, gsStartDate.day))
        self.sellDateEdit.setDate(QDate(gsStartDate.year, gsStartDate.month, gsStartDate.day))

    def pushBuyButtonClicked(self):
        buyquantity = int(self.buyLineEdit.text())
        qBuydate = self.buyDateEdit.date()
        buyDatetime = datetime.datetime(qBuydate.year(), qBuydate.month(), qBuydate.day())

        if (buyDatetime in self.gs.index.values) == False:
            QMessageBox.critical(self, "Error", "No buy date in data frame")
            return
        #buyprice = self.gs
        price = self.gs.loc[buyDatetime].values[0]
        buycost = price * buyquantity
        new_row = {'Position': 'Buy', 'Date': buyDatetime, 'Price': price, 'Quantity': buyquantity, 'PQ' : buycost}
        rowcount = len(self.simuldf.index) + 1
        self.simuldf.loc[rowcount - 1] = new_row

        self.simultableWidget.setRowCount(rowcount)
        self.simultableWidget.setColumnCount(5)
        self.simultableWidget.setItem(rowcount - 1, 0, QTableWidgetItem("{0}".format("Buy")))
        self.simultableWidget.setItem(rowcount - 1, 1, QTableWidgetItem(buyDatetime.strftime("%Y/%m/%d")))
        self.simultableWidget.setItem(rowcount - 1, 2, QTableWidgetItem("{0}".format(price)))
        self.simultableWidget.setItem(rowcount - 1, 3, QTableWidgetItem("{0:d}".format(buyquantity)))
        self.simultableWidget.setItem(rowcount - 1, 4, QTableWidgetItem("{0}".format(buycost)))

    def pushSellButtonClicked(self):
        sellquantity = int(self.sellLineEdit.text())
        selldate = self.sellDateEdit.date()
        sellDatetime = datetime.datetime(selldate.year(), selldate.month(), selldate.day())
        #buyprice = self.gs
        price = self.gs.loc[sellDatetime].values[0]
        sellpq = price * sellquantity
        new_row = {'Position': 'Sell', 'Date': sellDatetime, 'Price': price, 'Quantity': sellquantity, 'PQ' : sellpq}
        rowcount = len(self.simuldf.index) + 1
        self.simuldf.loc[rowcount - 1] = new_row

        self.simultableWidget.setRowCount(rowcount)
        self.simultableWidget.setColumnCount(5)
        self.simultableWidget.setItem(rowcount - 1, 0, QTableWidgetItem("{0}".format("Sell")))
        self.simultableWidget.setItem(rowcount - 1, 1, QTableWidgetItem(sellDatetime.strftime("%Y/%m/%d")))
        self.simultableWidget.setItem(rowcount - 1, 2, QTableWidgetItem("{0}".format(price)))
        self.simultableWidget.setItem(rowcount - 1, 3, QTableWidgetItem("{0:d}".format(sellquantity)))
        self.simultableWidget.setItem(rowcount - 1, 4, QTableWidgetItem("{0}".format(sellpq)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()