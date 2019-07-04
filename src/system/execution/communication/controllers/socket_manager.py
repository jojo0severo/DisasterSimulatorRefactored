

class SocketManager:
    def __init__(self):
        self.socket_clients = {}

    def add_socket(self, token, socket_id):
        self.socket_clients[token] = socket_id

    def remove_socket(self, token):
        del self.socket_clients[token]

    def get_sockets(self):
        return list(self.socket_clients.values())

    def get_tokens(self):
        return list(self.socket_clients.keys())

    def get_socket(self, token):
        return self.socket_clients.get(token)

    def clear(self):
        self.socket_clients.clear()

    def burn(self):
        self.socket_clients.clear()
        del self.socket_clients
