""" Before running the ChatRoom through main.py, run this file first (server.py). This file ensures
    that the host laptop becomes a socket that starts listening for connections.

    @author Daniel Burrell
"""


import threading
import socket
import pickle
import datetime



class Server(object):
    """Creates a server object that handles client connections. The Server class is also in charge of
       keeping track of who is connected and receiving messages from a client and sending it back to
       other clients.
    """

    __BUFFER = 4000 #Can be changed if wanted to.
    __PORT = 5050 #Can be changed if wanted to.
    __HOST = socket.gethostbyname(socket.gethostname())
    __ADDR = (__HOST, __PORT)
    __FORMAT = "utf-8"
    __connected_clients = {} #Dictionary to map key/value pairs of connected clients.
    __connected_usernames = [] #List to store usernames to show to all clients.

  

    def __init__(self):
        try:
            self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__server.bind(self.__ADDR)
        
        except socket.error as ex:
            print("Error in creating the server.")
            self.__server.close()
      
        
        
    def start(self):
        """Makes the server socket start listening for incoming connections from other sockets.
           When a connection is made, the username of the client is first validated. If they are
           valid, they are added to the dictionary and list. A separate thread is started for each connected
           client to send messages to the server.
           
        """

        print("[STARTING SERVER]")
        try:
            self.__server.listen()

            while True:
                sock, addr = self.__server.accept()
                print(f"[CONNECTION SUCCESS] {addr} has connected to the SERVER.")
                username = sock.recv(self.__BUFFER).decode(self.__FORMAT)
                if self.__validate_username(username):
                    sock.send("Valid".encode(self.__FORMAT))
                    new_user = dict(user = username, address = addr, client = sock) #Creates a new dictionary value
                    self.__connected_clients[username] = new_user #Creating a new key/value pair in the dictionary.
                    self.__connected_usernames.append(username)
                    self.__broadcast(username, "[*] " + username + " has joined the room. ") #Sends a message to all currently connected clients that someone new has joined.
                    self.__list_of_users()
                    client_thread = threading.Thread(target=self.__message_handler,args=(username, addr, sock))
                    client_thread.start()  

                else:
                    sock.send("Invalid".encode(self.__FORMAT))
                

        except socket.error as ex:
            print("Error while listening for client connections.")
            



    def __validate_username(self, username):
        """Checks if the username that just connected to the server is valid.
           The method searches through the Server class' dictionary and tries to retrieve the key/value pair
           using the username. If nothing is retrieved, then the username is valid and can be used.

           :param str username: The username of the client who just connected to the server. 
           :return: If the username is valid to be used.
           :rtype: bool 
        
        """

        if self.__connected_clients.get(username) == None: #Checks if the username given maps to a dictionary in connected clients
            return True #The key was not found so the username is valid.

        else:
            return False



    def __list_of_users(self):
        """Sends the list of current users of the system to each client. This method makes use of the 
           pickle module to convert the usernames list into bytes in order to be sent through a socket.
        
        """

        user_list = pickle.dumps(self.__connected_usernames)
        for _, values in self.__connected_clients.items():
            values['client'].send(user_list)



    def __broadcast(self, username, message):
        """Sends a message to all the other clients currently connected to the server.
           
           :param str username: The username of the client who just connected to the server.
           :param str message: The message that is to broadcasted to the other clients.

        """

        for key, values in self.__connected_clients.items():
            if key == username:
                continue  #Exclude the current client.
            else:
                values['client'].send(message.encode(self.__FORMAT))




    def __message_handler(self, username, address, client):
        """Handles receiving messages from a certain client. If the client disconnects from the server
           they are removed from the dictionary and a message is sent to all other clients that they have left
           the room.

           :param str username: The username of the client who just connected to the server.
           :param AddressFamily address: The address of the client who just connected to the server.
           :param socket client: The socket of the client who just connected to the server.
           :raises ConnectionResetError: The client forcibly closed the ChatRoom which interrupted the message listening process.

        """

        connected = True

        while connected:
            try:
                message = client.recv(self.__BUFFER).decode(self.__FORMAT)
                if message: #If message is not empty
                    if message == "DISCONNECT":
                        connected = False
                        continue 
                    else:
                        message_date = datetime.datetime.now()
                        self.__broadcast(username, ">" + username + ": " + message + " - " + message_date.strftime(" %x %I:%M %p"))
                        
            except ConnectionResetError: #client forcibly closes application
                break

        client.close()
        self.__remove_user(username)




    def __remove_user(self,username):
        """Removes a user from the server.

           :param str username: The username of the client that just connected to the server.

        """

        del self.__connected_clients[username]
        self.__connected_usernames.remove(username)

        if len(self.__connected_usernames) != 0: #If the last person has disconnected, do not broadcast the message. 
            self.__list_of_users()  
            self.__broadcast(username, "[*] " + username + " has disconnected from the server.")




def main():
    SERVER = Server()
    SERVER.start()



if __name__ == "__main__":
    main()