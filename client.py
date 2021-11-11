import threading
import socket as sc
import sys
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox, QApplication
from PyQt5.QtCore import QThread, pyqtSlot, QCoreApplication
from PyQt5 import QtCore
from PyQt5 import uic

ui_form = uic.loadUiType("test.ui")[0]

class QtWindow(QMainWindow, ui_form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.socket = None
        self.userName = None
        self.isRun = False
        self.allChat = ''


        self.sendButton.clicked.connect(self.send)
        self.accessButton.clicked.connect(self.connect)
        self.exitButton.clicked.connect(self.quit)

    def quit(self):

        if self.socket:
            self.socket.close()

        QCoreApplication.instance().quit()
        sys.exit(1)

    def send(self, e):
        if self.isRun:
            message = self.inputMsg.toPlainText()
            # self.addChat(message)
            self.inputMsg.setPlainText("")
            message = message.encode(encoding='utf-8')
            try:
                self.socket.sendall(message)
                print("메시지 전송")
            except Exception as e:
                self.isRun = False
                QMessageBox.question(self, 'Message', str(e), QMessageBox.Yes,
                                     QMessageBox.NoButton)
        else:
            QMessageBox.question(self, 'Message', '먼저 서버의 IP와, PORT 그리고 사용자 이름을 입력하고 접속해주세요.', QMessageBox.Yes,
                                 QMessageBox.NoButton)
            self.inputMsg.setPlainText("")

    def recieveMessage(self):  # 상대방이 보낸 메시지 읽어서 화면에 출력
        try:
            print('수신 thread 가동')
            while True:
                print('수신 대기중')
                message = self.socket.recv(1024).decode()

                print("서버에서 전송받은 메세지: \"" + str(message) + "\"")

                self.chatBox.append(str(message) + "\n")
        except Exception as e:
            self.isRun = False
            QMessageBox.question(self, 'Message', str(e), QMessageBox.Yes,
                                 QMessageBox.NoButton)
            # self.addChat(message)
            # if msg == '/stop':Z
            #     self.close()
            #     break


    def addChat(self, msg):
        self.chatBox.appendPlainText(msg)

    def connect(self):
        if self.isRun:
            QMessageBox.question(self, 'Message', self.userName + '님, 이미 연결중입니다.', QMessageBox.Yes, QMessageBox.NoButton)

        else:
            try:
                ip = str(self.inputIp.toPlainText()).strip()
                port = int(str(self.inputPort.toPlainText()).strip())
                self.userName = self.inputName.toPlainText().strip()
                self.socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
                self.socket.connect((ip, port))
                self.socket.sendall(self.userName.encode(encoding='utf-8'))
                self.isRun = True

                thread = threading.Thread(target=self.recieveMessage)
                thread.daemon = True
                thread.start()
                print("서버와 연결했습니다")
            except Exception as e:
                QMessageBox.question(self, 'Message', str(e), QMessageBox.Yes,
                                     QMessageBox.NoButton)

def main():
    # conn = UiChatClient()
    # conn.run()
    app = QApplication(sys.argv)
    window = QtWindow()
    window.setWindowTitle("쵀팅")
    window.show()
    app.exec_()

main()