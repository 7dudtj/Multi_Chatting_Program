import socket
import threading
import socket as sc
import sys
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox, QApplication
from PyQt5.QtCore import QThread, pyqtSlot, QCoreApplication
from PyQt5 import QtCore
from PyQt5 import uic
import os

ui_form = uic.loadUiType("test.ui")[0]

class QtWindow(QMainWindow, ui_form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.socket = None
        self.userName = None
        self.isRun = False
        self.allChat = ''

        self.sendButton.clicked.connect(self.sendMessage)
        self.accessButton.clicked.connect(self.connect)
        self.exitButton.clicked.connect(self.quit)
        self.sendFileButton.clicked.connect(self.sendFile)

    def connect(self):
        if self.isRun:
            QMessageBox.question(self, 'Message', self.userName + '님, 이미 연결중입니다.', QMessageBox.Yes,
                                 QMessageBox.NoButton)

        else:
            try:
                ip = str(self.inputIp.toPlainText()).strip()
                port = int(str(self.inputPort.toPlainText()).strip())
                self.userName = self.inputName.toPlainText().strip()
                self.socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
                self.socket.connect((ip, port))
                self.socket.sendall(self.userName.encode(encoding='utf-8'))
                self.isRun = True

                thread = threading.Thread(target=self.receive())
                thread.daemon = True
                thread.start()
                print("서버와 연결했습니다")
            except socket.gaierror:
                QMessageBox.question(self, 'Message', "잘못된 IP와 PORT입니다.", QMessageBox.Yes,
                                     QMessageBox.NoButton)
            except Exception as e:

                QMessageBox.question(self, 'Message', str(e) + " " + str(e.__class__), QMessageBox.Yes,
                                     QMessageBox.NoButton)

    def receive(self):
        try:
            print('수신 thread 가동')
            while True:
                print('수신 대기중')
                message = self.socket.recv(1024).decode()
                if message == "/text":
                    self.readMessage()
                elif message == "/file":
                    self.readFile()
        except Exception as e:
            self.isRun = False
            QMessageBox.question(self, 'Message', str(e), QMessageBox.Yes,
                                 QMessageBox.NoButton)

    def readMessage(self):
        message = self.socket.recv(1024).decode()
        self.chatBox.append(str(message) + "\n")

    def recieveFile(self):
        try:
            nowdir = os.getcwd()
            fileName = self.socket.recv(1024).decode()
            data = self.socket.recv(1024).decode()
            with open(nowdir + "\\" + fileName, 'wb') as f:
                f.write(data)
                while data:
                    data = self.socket.recv(1024).decode()

        except FileNotFoundError:
            QMessageBox.question(self, 'Message', '작성하신 파일명과 일치하는 파일이 존재하지 않습니다.', QMessageBox.Yes,
                                 QMessageBox.NoButton)
            self.inputFileName.setPlainText("")
        except Exception as e:
            QMessageBox.question(self, 'Message', "파일 수신 실패: " + str(e), QMessageBox.Yes,
                                 QMessageBox.NoButton)
            print(e.__class__)
            print(e)

    def sendMessage(self, e):
        if self.isRun:
            message = self.inputMsg.toPlainText()
            self.inputMsg.setPlainText("")
            message = message.encode(encoding='utf-8')
            try:
                self.socket.sendall("/text".encode(encoding='utf-8'))
                self.socket.sendall(message)
                print("메시지 전송")
            except Exception as e:
                self.isRun = False
                QMessageBox.question(self, 'Message', str(e), QMessageBox.Yes,
                                     QMessageBox.NoButton)
        else:
            QMessageBox.question(self, 'Message', '먼저 서버의 IP, PORT, 그리고 사용자 이름을 입력하고 접속해주세요.', QMessageBox.Yes,
                                 QMessageBox.NoButton)
            self.inputMsg.setPlainText("")

    def sendFile(self):
        if self.isRun:
            try:
                nowdir = os.getcwd()
                fileName = self.inputFileName.toPlainText().strip()

                message = "/file".encode(encoding='utf-8')
                self.socket.sendall(message)

                with open(nowdir + "\\" + fileName, 'r') as f:
                    data = f.read(1024)
                    while data:
                        self.socket.sendMessage(data.encode(encoding="utf-8"))
                        data = f.read(1024)

            except FileNotFoundError:
                QMessageBox.question(self, 'Message', '작성하신 파일명과 일치하는 파일이 존재하지 않습니다.', QMessageBox.Yes,
                                     QMessageBox.NoButton)
                self.inputFileName.setPlainText("")
            except Exception as e:
                QMessageBox.question(self, 'Message', str(e), QMessageBox.Yes,
                                     QMessageBox.NoButton)
                print(e.__class__)
                print(e)

        else:
            QMessageBox.question(self, 'Message', '먼저 서버의 IP, PORT, 그리고 사용자 이름을 입력하고 접속해주세요.', QMessageBox.Yes,
                                 QMessageBox.NoButton)
            self.inputFileName.setPlainText("")

    def quit(self):
        # 서버에 접속 종료를 알림
        if self.isRun:
            message = "/stop".encode(encoding='utf-8')
            self.socket.sendall(message)

        # 서버와의 연결 종료
        if self.socket:
            self.socket.close()

        # 윈도우 종료
        QCoreApplication.instance().quit()
        sys.exit(1)


def main():
    # conn = UiChatClient()
    # conn.run()
    app = QApplication(sys.argv)
    window = QtWindow()
    window.setWindowTitle("채팅")
    window.show()
    app.exec_()

main()