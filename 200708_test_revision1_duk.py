import datetime
import sys

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas_datareader.data as web
import pandas as pd
import numpy as np

from pandas import Series, DataFrame

#-get code----------------------------------------------------------------------------------------------------
def get_code(table, firm):
    code = table[table["name"] == firm]["code"].values[0]
    return "{:06d}".format(int(code))

#-클래스 정의 ------------------------------------------------------------------------------------------------------
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

#-윈도우 창 셋팅----------------------------------------------------------------------------------------------------
    def setupUI(self):
        self.setGeometry(150, 100, 1500, 800)
        self.setWindowTitle("Trading Simulator")
        self.setWindowIcon(QIcon('icon.png'))

#-콤포박스 셋팅-----------------------------------------------------------------------------------------------------
        self.firmCombobox = QComboBox()
        self.firmCombobox.setEditable(True)

        self.firmdf = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]
        self.firmdf = self.firmdf[['회사명', '종목코드']]
        self.firmdf = self.firmdf.rename(columns={'회사명': 'name', '종목코드': 'code'})
        for firm in self.firmdf['name']:
            self.firmCombobox.addItem(firm)
        self.firmCombobox.setEditText('삼성전자')

#-종목 조희 입력 셋팅---------------------------------------------------------------------------------------------------
        self.startEdit = QDateEdit()
        self.startEdit.setDate(QDate(2016, 1, 1))
        self.endEdit = QDateEdit()
        self.endEdit.setDate(QDate(2020, 3, 15))

        self.pushButton = QPushButton("Launch")
        self.pushButton.clicked.connect(self.pushButtonClicked)

#-계산기 입력 셋팅(buy & sell)---------------------------------------------------------------------------------------------
        self.fundEdit = QLineEdit()
        self.fundEdit.setText('10000000')
        self.buyDateEdit=QDateEdit()
        self.buyLineEdit=QLineEdit()
        self.pushBuyButton = QPushButton("Buy")
        self.pushBuyButton.clicked.connect(self.pushBuyButtonClicked)

        self.sellDateEdit=QDateEdit()
        self.sellLineEdit=QLineEdit()
        self.pushSellButton = QPushButton("Sell")
        self.pushSellButton.clicked.connect(self.pushSellButtonClicked)

#-Right Layout (종목 조회 버튼들 수직 나열) -----------------------------------------------------------------------------
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.firmCombobox)
        rightLayout.addWidget(self.startEdit)
        rightLayout.addWidget(self.endEdit)
        rightLayout.addWidget(self.pushButton)

#-초기 자본금 Edit Layoyt ---------------------------------------------------------------------------------------------
        groupLayout = QHBoxLayout()
        groupLayout.addWidget(QLabel("Init Fund : "))
        groupLayout.addWidget(self.fundEdit)

        rightLayout.addLayout(groupLayout)

#-Right Layout (Buy 버튼들 수평 나열)-----------------------------------------------------------------------------------
        groupLayout = QHBoxLayout()
        groupLayout.addWidget(self.buyDateEdit)
        groupLayout.addWidget(self.buyLineEdit)
        groupLayout.addWidget(self.pushBuyButton)

        rightLayout.addLayout(groupLayout)

#-Right Layout (Sell 버튼들 수평 나열)----------------------------------------------------------------------------------
        groupLayout = QHBoxLayout()
        groupLayout.addWidget(self.sellDateEdit)
        groupLayout.addWidget(self.sellLineEdit)
        groupLayout.addWidget(self.pushSellButton)

        rightLayout.addLayout(groupLayout)

#-Right Layout 크기 조절가능 셋팅--------------------------------------------------------------------------------------
        rightLayout.addStretch(1)

#-플롯 생성 및 설정----------------------------------------------------------------------------------------------------
        #plt.style.use('ggplot')
        self.fig = plt.Figure(tight_layout=True)
        #self.fig.subplot(1, 1, 1)
        self.canvas = FigureCanvas(self.fig)
        #self.canvas.setSizePolicy(QSizePolicy.Expanding,
        #                          QSizePolicy.Expanding)
        #self.fig.tight_layout()

#-테이블 생성(종목 조회 테이블, 계산기 테이블)---------------------------------------------------------------------------------
        self.seriestableWidget = QTableWidget()
        self.simultableWidget = QTableWidget()
        self.dailyEstiTable = QTableWidget()

#-upleft layout에 플롯, 종목 조회 테이블 담기-----------------------------------------------------------------------------
        upleftLayout = QHBoxLayout()
        upleftLayout.addWidget(self.canvas)
        upleftLayout.addWidget(self.seriestableWidget)

#-upleft layout 창 크기 설정-------------------------------------------------------------------------------------------
        self.seriestableWidget.setFixedWidth(500)

        upleftLayout.setStretchFactor(self.canvas, 1)
        upleftLayout.setStretchFactor(self.seriestableWidget, 0)
        #leftLayout.addStretch(1)

#-left layout에 uoleft layout과 계산기 테이블 수직으로 담기----------------------------------------------------------------
        summaryLayout = QFormLayout()
        self.fundValueLabel = QLabel("-")
        self.estiStockLabel = QLabel("-")
        self.remainCashLabel = QLabel("-")
        self.assetLabel = QLabel("-")
        self.returnValue = QLabel("-")
        self.returnRatio = QLabel("-")
        self.varLabel = QLabel("-")

        summaryLayout.addRow("FUND : ", self.fundValueLabel)
        summaryLayout.addRow("Esti. Stock : ", self.estiStockLabel)
        summaryLayout.addRow("Cash : ", self.remainCashLabel)
        summaryLayout.addRow("Esti, Asset : ", self.assetLabel)
        summaryLayout.addRow("Return Value : ", self.returnValue)
        summaryLayout.addRow("Return Ratio : ", self.returnRatio)
        summaryLayout.addRow("std. Return Ratio : ", self.varLabel)

        dividendLayout = QFormLayout()
        self.dividendRate = QLabel("-")
        self.twoTimeScale = QLabel("-")
        self.fourTimeScale = QLabel("-")
        self.eightTimeScale = QLabel("-")
        self.sixteenTimeScale = QLabel("-")

        dividendLayout.addRow("Dividend Rate : ", self.dividendRate)
        dividendLayout.addRow("Two times for Init : ", self.twoTimeScale)
        dividendLayout.addRow("Four times for Init : ", self.fourTimeScale)
        dividendLayout.addRow("Eight times for Init : ", self.eightTimeScale)
        dividendLayout.addRow("Sixteen times for Init : ", self.sixteenTimeScale)

        groupLayout = QVBoxLayout()
        groupLayout2 = QVBoxLayout()
        simLayout = QHBoxLayout()

        groupLayout.addWidget(self.simultableWidget)
        groupLayout.addWidget(self.dailyEstiTable)
        groupLayout2.addLayout(summaryLayout)
        groupLayout2.addLayout(dividendLayout)
        simLayout.addLayout(groupLayout)
        simLayout.addLayout(groupLayout2)

        self.simultableWidget.setFixedWidth(720)
        self.dailyEstiTable.setFixedWidth(720)
        simLayout.setStretchFactor(self.simultableWidget, 1)

        leftLayout = QVBoxLayout()
        leftLayout.addLayout(simLayout)
        leftLayout.addLayout(upleftLayout)

#-전체 layout에 left layout과 right layout 합치기---------------------------------------------------------------------
        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)
        layout.setStretchFactor(leftLayout, 1)
        layout.setStretchFactor(rightLayout, 0)

        self.setLayout(layout)

#-종목 조회 테이블 내용물 생성하기---------------------------------------------------------------------------------------
    def showDataTable(self, gs):
        self.seriestableWidget.setRowCount(len(gs.index))
        self.seriestableWidget.setColumnCount(3)
        self.seriestableWidget.setHorizontalHeaderLabels(['Date', 'Close', 'Volume'])

        #labels = ['Volumn', 'Close'];
        for row in range(len(gs.index)) :
            #for col in labels:
            self.seriestableWidget.setItem(row, 0, QTableWidgetItem(gs.index[row].strftime("%Y/%m/%d")))
            self.seriestableWidget.setItem(row, 1, QTableWidgetItem("{0}".format(gs.loc[gs.index[row], 'Close'])))
            self.seriestableWidget.setItem(row, 2, QTableWidgetItem("{0}".format(gs.loc[gs.index[row], 'Volume'])))

        #self.tableWidget.setItem(0, 0, QTableWidgetItem("Name"))
        #self.tableWidget.setItem(0, 1, QTableWidgetItem("Email"))
        #self.tableWidget.setItem(0, 2, QTableWidgetItem("Phone No"))

# - Daily Estimate Table 에 일별 로그수익률을 보여준다
    def showDailyEstiTable(self, gs, simdf):
        self.dailyEstiTable.setRowCount(len(gs.index))
        self.dailyEstiTable.setColumnCount(5)
        self.dailyEstiTable.setHorizontalHeaderLabels(['Date', 'Close', 'Esti. Stock', 'Asset', 'return(log)'])

        logReturnData = []

        # labels = ['Volumn', 'Close'];
        initCash = int(self.fundEdit.text())
        oldAssetValue = initCash
        for row in range(0, len(gs.index)):
            data = gs.iloc[row]
            index = gs.index[row]
            temp = simdf[simdf['Date'] <= index]

            # row 시점의 주식평가금액
            buyStockQuantity = temp['Quantity'].loc[temp['Position'] == 'Buy'].sum()
            sellStockQuantity = temp['Quantity'].loc[temp['Position'] == 'Sell'].sum()
            stockQuantity = buyStockQuantity - sellStockQuantity
            estiStockValue = stockQuantity * data['Close']

            # row 시점의 현금평가금액
            buyPQ = temp['PQ'].loc[temp['Position'] == 'Buy'].sum()
            sellPQ = temp['PQ'].loc[temp['Position'] == 'Sell'].sum()

            remainCash = initCash - buyPQ + sellPQ
            assetValue = remainCash + estiStockValue
            logReturnRatio = np.log(assetValue / oldAssetValue) * 100
            logReturnData.append(logReturnRatio)

            # for col in labels:
            self.dailyEstiTable.setItem(row, 0, QTableWidgetItem(index.strftime("%Y/%m/%d")))
            self.dailyEstiTable.setItem(row, 1, QTableWidgetItem("{0:,d}".format(int(data['Close']))))
            self.dailyEstiTable.setItem(row, 2, QTableWidgetItem("{0:,d}".format(int(estiStockValue))))
            self.dailyEstiTable.setItem(row, 3, QTableWidgetItem("{0:,d}".format(int(assetValue))))
            self.dailyEstiTable.setItem(row, 4, QTableWidgetItem("{0:.2f}%".format(logReturnRatio)))
            oldAssetValue = assetValue

        stdLogReturn = np.std(logReturnData)
        stdLogReturnByYear = stdLogReturn * 365
        #self.varLabel.setText("{0:.2f}%".format(stdLogReturn))
        self.varLabel.setText("{0:.2f}% ({1:.2f}% per year)".format(stdLogReturn, stdLogReturnByYear))
        LogReturnYear = (np.array(logReturnData) * 365).tolist()
        plt.cla()
        plt.plot(gs.index, LogReturnYear, color='#052962', linewidth=1, alpha=.4)
        plt.plot(gs.index, [np.mean(logReturnData) * 365] * len(gs.index), color='#cc0a11', linewidth=1, alpha=.8)
        plt.plot(gs.index, [(np.mean(logReturnData) + stdLogReturn * 1.96) * 365] * len(gs.index), linewidth=1,
                 color="gray", alpha=.8)
        plt.plot(gs.index, [(np.mean(logReturnData) - stdLogReturn * 1.96) * 365] * len(gs.index), linewidth=1,
                 color="gray", alpha=.8)
        plt.show()

#-종목 조회 버튼 클릭 이벤트 생성----------------------------------------------------------------------------------------
    def pushButtonClicked(self):
        firm = self.firmCombobox.currentText()
        startDate = self.startEdit.date()
        endDate = self.endEdit.date()

        start = datetime.datetime(startDate.year(), startDate.month(), startDate.day())
        end = datetime.datetime(endDate.year(), endDate.month(), endDate.day())

        #----- gs 데이터프레임 생성-------------------------------------------------------------------------------
        codename = get_code(self.firmdf, firm)
        codename = codename + ".KS"

        gs = web.DataReader(codename, "yahoo", start, end)
        gs = gs[["Close", "Volume"]]
        self.gs = gs

        #--------gs 플롯 만들기--------------------------------------------------------------------------------
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(gs["Close"], color='#052962')
        ax.grid(True, axis='y', color='gray', alpha=0.25, linestyle='--')

        #-------gs플롯과 테이블 보여주기----------------------------------------------------------------------
        self.canvas.draw()
        self.showDataTable(gs)

        #-------시뮬 데이터 프레임 생성---------------------------------------------------------------------------
        self.simuldf = pd.DataFrame(data=[], columns=["Position", "Date", "Price", "Quantity", "PQ"])

        #------buy, sell 데이트 초기값 자동으로 조정해주기---------------------------------------------------------
        gsStartDate = self.gs.index[0]
        self.buyDateEdit.setDate(QDate(gsStartDate.year, gsStartDate.month, gsStartDate.day))
        self.sellDateEdit.setDate(QDate(gsStartDate.year, gsStartDate.month, gsStartDate.day))

#-buy 버튼 클릭 이벤트 생성---------------------------------------------------------------------------------------------
    def pushBuyButtonClicked(self):
        buyquantity = int(self.buyLineEdit.text())
        qBuydate = self.buyDateEdit.date()
        buyDatetime = datetime.datetime(qBuydate.year(), qBuydate.month(), qBuydate.day())

        #if (buyDatetime in self.gs.index.values) == False:
        #    QMessageBox.critical(self, "Error", "No buy date in data frame")
        #    return

        #buyprice = self.gs
        price = self.gs.loc[buyDatetime].values[0]
        buycost = price * buyquantity
        new_row = {'Position': 'Buy', 'Date': buyDatetime, 'Price': price, 'Quantity': buyquantity, 'PQ' : buycost}
        rowcount = len(self.simuldf.index) + 1
        self.simuldf.loc[rowcount - 1] = new_row

        self.simultableWidget.setRowCount(rowcount)
        self.simultableWidget.setColumnCount(5)
        self.simultableWidget.setHorizontalHeaderLabels(['Buy/Sell', 'Date', 'Price', 'Quantity', 'PQ'])
        self.simultableWidget.setItem(rowcount - 1, 0, QTableWidgetItem("{0}".format("Buy")))
        self.simultableWidget.setItem(rowcount - 1, 1, QTableWidgetItem(buyDatetime.strftime("%Y/%m/%d")))
        self.simultableWidget.setItem(rowcount - 1, 2, QTableWidgetItem("{0}".format(price)))
        self.simultableWidget.setItem(rowcount - 1, 3, QTableWidgetItem("{0:d}".format(buyquantity)))
        self.simultableWidget.setItem(rowcount - 1, 4, QTableWidgetItem("{0}".format(buycost)))

        self.estimateAsset()

# -sell 버튼 클릭 이벤트 생성---------------------------------------------------------------------------------------------
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
        self.simultableWidget.setHorizontalHeaderLabels(['Buy/Sell', 'Date', 'Price', 'Quantity', 'PQ'])
        self.simultableWidget.setItem(rowcount - 1, 0, QTableWidgetItem("{0}".format("Sell")))
        self.simultableWidget.setItem(rowcount - 1, 1, QTableWidgetItem(sellDatetime.strftime("%Y/%m/%d")))
        self.simultableWidget.setItem(rowcount - 1, 2, QTableWidgetItem("{0}".format(price)))
        self.simultableWidget.setItem(rowcount - 1, 3, QTableWidgetItem("{0:d}".format(sellquantity)))
        self.simultableWidget.setItem(rowcount - 1, 4, QTableWidgetItem("{0}".format(sellpq)))

        self.estimateAsset()

    def estimateAsset(self):
        # 초기자본금
        self.fundValueLabel.setText("{0:,d}".format(int(self.fundEdit.text())))

        # 주식평가금액
        buyStockQuantity = self.simuldf['Quantity'].loc[self.simuldf['Position'] == 'Buy'].sum()
        sellStockQuantity = self.simuldf['Quantity'].loc[self.simuldf['Position'] == 'Sell'].sum()
        stockQuantity = buyStockQuantity - sellStockQuantity

        estiStockValue = stockQuantity * self.gs.iloc[-1]['Close']
        self.estiStockLabel.setText("{0:,.0f}".format(estiStockValue))

        # 현금
        buyPQ = self.simuldf['PQ'].loc[self.simuldf['Position'] == 'Buy'].sum()
        sellPQ = self.simuldf['PQ'].loc[self.simuldf['Position'] == 'Sell'].sum()
        initCash = int(self.fundEdit.text())
        remainCash =  initCash - buyPQ + sellPQ
        self.remainCashLabel.setText("{0:,.0f}".format(remainCash))

        # 자산
        assetValue = remainCash + estiStockValue
        self.assetLabel.setText("{0:,.0f}".format(assetValue))

        # 수익금액
        returnValue = assetValue - initCash
        self.returnValue.setText("{0:,.0f}".format(returnValue))

        # 수익률
        duration = (self.gs.index[-1] - self.gs.index[0]).days + 1
        returnRatio = (assetValue / initCash - 1.0) * 100
        returnRatioByYear = (assetValue / initCash - 1.0) * 100 / duration * 365
        self.returnRatio.setText("{0:.2f}% ({1:.2f}% per year)".format(returnRatio, returnRatioByYear))

        # Daily 수익률 표를 업데이트
        self.showDailyEstiTable(self.gs, self.simuldf)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()