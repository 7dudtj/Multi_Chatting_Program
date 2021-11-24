import socket
import threading
import os

################################################################
class Room:  # Room class
    def __init__(self):
        self.chatUsers = [] # 채팅방 접속 유저 리스트 (채팅방)
        self.waitUsers = [] # 재접속을 기다리는 유저 리스트 (대기열)

    def add_chatUser(self, c): # 채팅방에 유저 추가
        self.chatUsers.append(c)

    def add_waitUser(self, c): # 대기열에 유저 추가
        self.waitUsers.append(c)

    def del_chatUser(self, c): # 채팅방에 유저 삭제 (정상 종료)
        c.soc.close()
        self.chatUsers.remove(c)

    def del_waitUser(self, c): # 대기열에서 유저 삭제
        c.soc.close()
        self.waitUsers.remove(c)

    def sendMsgAll(self, msg):  # 채팅방에 있는 모든 유저한테 메시지 전송
        for i in self.chatUsers:
            print(str(i.userName)+"에게 전송")
            i.sendMsg(msg)
################################################################


################################################################
class chatClient:  # 채팅 유저 클래스
    def __init__(self, r, soc):
        self.room = r  # 채팅방(Room) 객체
        self.userName = None  # user name
        self.soc = soc  # 유저와 1:1로 통신할 소켓

    def readMsg(self):
        # 유저의 닉네임 받아오기
        self.userName = self.soc.recv(1024).decode()
        print(str(self.userName) + "한테서 받은 메세지: " + str(self.userName))

        # 재접속 유저인지 확인
        reconnect = False
        for i in self.room.waitUsers: # 'i'는 대기열의 유저
            if (i.userName == self.userName):
                reconnect = True
                self.room.del_waitUser(i) # 대기열에서 삭제

        # 채팅방 재입장
        if (reconnect):
            msg = self.userName + '님이 재접속했습니다'
        # 채팅방 신규입장
        else:
            msg = self.userName + '님이 입장하셨습니다'
        self.room.sendMsgAll('/text')
        self.room.sendMsgAll(msg)

        # 유저의 채팅을 받아오는 부분
        while True:
            try:
                msg = self.soc.recv(1024).decode()  # 유저가 전송한 채팅 읽기
                print(str(self.userName)+"한테서 받은 메세지: "+str(msg))
                # 종료 메시지이면 루프 종료
                if msg == '/stop':
                    outmember = self.userName
                    self.room.del_chatUser(self) # 채팅방에서 퇴장
                    self.room.sendMsgAll('/text')
                    self.room.sendMsgAll(str(outmember)+"님이 퇴장하셨습니다.")
                    break
                # 텍스트 수신
                elif msg == '/text':
                    msg = self.soc.recv(1024).decode()
                    msg = self.userName + ': ' + msg
                    self.room.sendMsgAll('/text')
                    self.room.sendMsgAll(msg)  # 모든 사용자에 메시지 전송
                # 파일 수신
                elif msg == '/file':
                    # 유저로부터 파일 수신
                    nowdir = os.getcwd()
                    fileName = self.soc.recv(1024).decode() # 파일 이름 받기
                    data = self.soc.recv(1024).decode() # 파일 내용 받기
                    print("파일 수신 완료")
                    with open(nowdir + "\\" + fileName, 'w') as f:
                        f.write(str(data))
                    f.close()
                    print("파일 저장 완료")

                    # 모든 유저들에게 파일 전송
                    self.room.sendMsgAll('/text')
                    self.room.sendMsgAll(self.userName+"님이 파일을 보냈습니다")
                    with open(nowdir + "\\" + fileName, 'r') as f:
                        data = f.read(1024)
                    f.close()
                    self.room.sendMsgAll('/file')
                    self.room.sendMsgAll(fileName)
                    self.room.sendMsgAll(data)
                    print("파일 전송 완료")
                    os.remove(nowdir + "\\" + fileName)
                    print("서버측 파일 삭제 완료")

            except Exception as e: # 에러가 발생할 경우
                outuserName = self.userName # 퇴장 유저의 아이디
                self.room.del_chatUser(self) # 채팅방에서 퇴장
                self.room.add_waitUser(self) # 대기열으로 진입
                self.room.sendMsgAll('/text')
                self.room.sendMsgAll(str(outuserName)+"님이 접속이 끊겼습니다.")
                print(str(self.userName)+": 접속이 끊겼습니다.\n"+str(e))
                break

    def sendMsg(self, msg):
        print("\""+msg+"\"")
        self.soc.sendall(msg.encode(encoding='utf-8'))
################################################################


################################################################
class ChatServer:
    ip = 'localhost'
    port = 8080

    def __init__(self):
        self.server_soc = None  # 서버 소켓(대문)
        self.room = Room() # 채팅방. 모든 유저와 공유됨

    def open(self):
        self.server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_soc.bind((ChatServer.ip, ChatServer.port))
        self.server_soc.listen()

    def run(self):
        self.open()
        print('서버 시작')

        while True: # 유저 접속 대기중
            print('client 접속 대기중')
            client_soc, addr = self.server_soc.accept()
            print(addr, '접속 성공')
            c = chatClient(self.room, client_soc) # 유저 객체 생성
            self.room.add_chatUser(c) # 채팅방에 유저 추가
            th = threading.Thread(target=c.readMsg)
            th.start()



        # 서버는 종료되지 않기에
        # 소켓을 닫지 않고 계속 가동
################################################################


def main():
    cs = ChatServer() # 서버 생성
    cs.run() # 서버 가동


main()