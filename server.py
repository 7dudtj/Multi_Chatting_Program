import socket, threading

class Room:  # 채팅방 클래스.
    def __init__(self):
        self.clients = []
        self.allChat=None

    def addClient(self, c):  # c: 텔레마케터 . 클라이언트 1명씩 전담하는 쓰레드
        self.clients.append(c)

    def delClient(self, c):
        self.clients.remove(c)

    def sendMsgAll(self, msg):  # 채팅방에 있는 모든 사람한테 메시지 전송
        for i in self.clients:
            print(i.id+"에게 전송")
            i.sendMsg(msg)


class ChatClient:  # 텔레마케터
    def __init__(self, r, soc):
        self.room = r  # 채팅방. Room 객체
        self.id = None  # 사용자 id
        self.soc = soc  # 사용자와 1:1 통신할 소켓

    def readMsg(self):
        self.id = self.soc.recv(1024).decode()
        msg = self.id + '님이 입장하셨습니다'
        self.room.sendMsgAll(msg)

        while True:
            try:
                msg = self.soc.recv(1024).decode()  # 사용자가 전송한 메시지 읽음
                if msg == '/stop':  # 종료 메시지이면 루프 종료
                    self.soc.sendall(msg.encode(encoding='utf-8'))  # 이 메시지를 보낸 한명에게만 전송
                    self.room.delClient(self)
                    break
                msg = self.id+': '+ msg
                self.room.sendMsgAll(msg)  # 모든 사용자에 메시지 전송
            except ConnectionResetError as e:
                print(self.id+"가 강제로 종료되었습니다.\n"+str(e))
                break

    def sendMsg(self, msg):
        print("\""+msg+"\"")
        self.soc.sendall(msg.encode(encoding='utf-8'))


class ChatServer:
    ip = 'localhost'
    port = 8080

    def __init__(self):
        self.server_soc = None  # 서버 소켓(대문)
        self.room = Room()

    def open(self):
        self.server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_soc.bind((ChatServer.ip, ChatServer.port))
        self.server_soc.listen()

    def run(self):
        self.open()
        print('서버 시작11')

        while True:
            client_soc, addr = self.server_soc.accept()
            print(addr, '접속')
            c = ChatClient(self.room, client_soc)
            self.room.addClient(c)
            # print('클라:',self.room.clients)
            th = threading.Thread(target=c.readMsg)
            th.start()

        self.server_soc.close()


def main():
    cs = ChatServer()
    cs.run()


main()