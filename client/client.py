import socket
import threading
import socket as sc
import sys
import PyQt5.QtWidgets
from PyQt5.QtCore import QCoreApplication
from PyQt5 import uic
import os

ui_form = uic.loadUiType("client.ui")[0]

class QtWindow(PyQt5.QtWidgets.QMainWindow, ui_form):

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
            PyQt5.QtWidgets.QMessageBox.question(self, 'Message', self.userName + '님, 이미 연결중입니다.', PyQt5.QtWidgets.QMessageBox.Yes,
                                                 PyQt5.QtWidgets.QMessageBox.NoButton)

        else:
            try:
                ip = str(self.inputIp.toPlainText()).strip()
                port = int(str(self.inputPort.toPlainText()).strip())
                self.userName = self.inputName.toPlainText().strip()
                self.socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
                self.socket.connect((ip, port))
                self.socket.sendall(self.userName.encode(encoding='utf-8'))
                self.isRun = True

                thread = threading.Thread(target=self.receive)
                thread.daemon = True
                thread.start() 
                print("서버와 연결했습니다")
            except socket.gaierror:
                PyQt5.QtWidgets.QMessageBox.question(self, 'Message', "잘못된 IP와 PORT입니다.", PyQt5.QtWidgets.QMessageBox.Yes,
                                                     PyQt5.QtWidgets.QMessageBox.NoButton)
            except Exception as e:

                PyQt5.QtWidgets.QMessageBox.question(self, 'Message', str(e) + " " + str(e.__class__), PyQt5.QtWidgets.QMessageBox.Yes,
                                                     PyQt5.QtWidgets.QMessageBox.NoButton)

    def receive(self):
        try:
            print('수신 thread 가동')
            while True:
                print('수신 대기중')
                message = self.socket.recv(1024).decode()
                if message == "/text":
                    message = self.socket.recv(1024).decode()
                    self.chatBox.append(str(message) + "\n")
                elif message == "/file":
                    print("서버가 파일 보냄")
                    try:
                        nowdir = os.getcwd()
                        fileName = self.socket.recv(1024).decode()
                        print("받은 파일이름: "+str(fileName))
                        fileName = "To"+self.userName+"_"+fileName
                        data = self.socket.recv(1024).decode()
                        print("파일 내용: "+str(data))
                        with open(nowdir + "\\" + fileName, 'w') as f:
                            f.write(str(data))
                        f.close()
                        print("파일 저장 완료")

                    except FileNotFoundError:
                        PyQt5.QtWidgets.QMessageBox.question(self, 'Message', '작성하신 파일명과 일치하는 파일이 존재하지 않습니다.',
                                                             PyQt5.QtWidgets.QMessageBox.Yes,
                                                             PyQt5.QtWidgets.QMessageBox.NoButton)
                        self.inputFileName.setPlainText("")
                    except Exception as e:
                        PyQt5.QtWidgets.QMessageBox.question(self, 'Message', "파일 수신 실패: " + str(e),
                                                             PyQt5.QtWidgets.QMessageBox.Yes,
                                                             PyQt5.QtWidgets.QMessageBox.NoButton)
                        print(e.__class__)
                        print(e)
                else:
                    message = self.socket.recv(1024).decode()
                    self.chatBox.append(str(message) + "\n")

        except Exception as e:
            self.isRun = False
            PyQt5.QtWidgets.QMessageBox.question(self, 'Message', str(e), PyQt5.QtWidgets.QMessageBox.Yes,
                                                 PyQt5.QtWidgets.QMessageBox.NoButton)

    def sendMessage(self, e):
        if self.isRun:
            message = self.inputMsg.toPlainText()
            # 메세지 입력 없이 전송버튼 누를때 예외처리
            if message == "":
                return
            self.inputMsg.setPlainText("")
            message = message.encode(encoding='utf-8')
            try:
                self.socket.sendall("/text".encode(encoding='utf-8'))
                self.socket.sendall(message)
                print("메시지 전송")
            except Exception as e:
                self.isRun = False
                PyQt5.QtWidgets.QMessageBox.question(self, 'Message', str(e), PyQt5.QtWidgets.QMessageBox.Yes,
                                                     PyQt5.QtWidgets.QMessageBox.NoButton)
        else:
            PyQt5.QtWidgets.QMessageBox.question(self, 'Message', '먼저 서버의 IP, PORT, 그리고 사용자 이름을 입력하고 접속해주세요.', PyQt5.QtWidgets.QMessageBox.Yes,
                                                 PyQt5.QtWidgets.QMessageBox.NoButton)
            self.inputMsg.setPlainText("")

    def sendFile(self):
        if self.isRun:
            try:
                nowdir = os.getcwd()
                fileName = self.inputFileName.toPlainText().strip()
                newfileName = "From"+self.userName+"_"+fileName

                self.socket.sendall("/file".encode(encoding='utf-8'))
                self.socket.sendall(newfileName.encode(encoding='utf-8'))

                with open(nowdir + "\\" + fileName, 'r') as f:
                    data = f.read(1024)
                f.close()
                self.socket.sendall(data.encode(encoding="utf-8"))
                print("파일 전송 완료")

            except FileNotFoundError:
                PyQt5.QtWidgets.QMessageBox.question(self, 'Message', '작성하신 파일명과 일치하는 파일이 존재하지 않습니다.', PyQt5.QtWidgets.QMessageBox.Yes,
                                                     PyQt5.QtWidgets.QMessageBox.NoButton)
                self.inputFileName.setPlainText("")
            except Exception as e:
                PyQt5.QtWidgets.QMessageBox.question(self, 'Message', str(e), PyQt5.QtWidgets.QMessageBox.Yes,
                                                     PyQt5.QtWidgets.QMessageBox.NoButton)
                print(e.__class__)
                print(e)

        else:
            PyQt5.QtWidgets.QMessageBox.question(self, 'Message', '먼저 서버의 IP, PORT, 그리고 사용자 이름을 입력하고 접속해주세요.', PyQt5.QtWidgets.QMessageBox.Yes,
                                                 PyQt5.QtWidgets.QMessageBox.NoButton)
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

    def closeEvent(self, event):
        self.deleteLater()

def main():
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    window = QtWindow()
    window.setWindowTitle("채팅")
    window.show()
    app.exec_()

main()