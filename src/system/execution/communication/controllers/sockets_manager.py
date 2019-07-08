

class SocketsManager:
    def __init__(self):
        self.socket_clients = {}

    def add_socket(self, token, socket_id):
        self.socket_clients[token] = socket_id

    def get_socket(self, token):
        return self.socket_clients.get(token)

    def get_sockets(self):
        return list(self.socket_clients.values())

    def remove_socket(self, token):
        del self.socket_clients[token]
