from communication.controllers.agents_manager import AgentsManager
from communication.controllers.social_assets_manager import SocialAssetsManager
from communication.controllers.sockets_manager import SocketsManager


class Manager:
    def __init__(self):
        self.agents_manager = AgentsManager()
        self.social_assets_manager = SocialAssetsManager()
        self.agents_sockets_manager = SocketsManager()
        self.assets_sockets_manager = SocketsManager()

    def add(self, token, obj_info, kind):
        if kind == 'agent':
            self.agents_manager.add_agent(token, obj_info)

        elif kind == 'social_asset':
            self.social_assets_manager.add_social_asset(token, obj_info)

        elif kind == 'socket':
            if self.agents_manager.get_agent(token) is None:
                self.assets_sockets_manager.add_socket(token, obj_info)

            else:
                self.agents_sockets_manager.add_socket(token, obj_info)

        else:
            return False

        return True

    def get(self, token, kind):
        if kind == 'agent':
            return self.agents_manager.get_agent(token)

        elif kind == 'social_asset':
            return self.social_assets_manager.get_social_asset(token)

        elif kind == 'socket':
            if self.agents_manager.get_agent(token) is None:
                return self.assets_sockets_manager.get_socket(token)

            else:
                return self.agents_sockets_manager.get_socket(token)

        else:
            return None

    def get_all(self, kind):
        if kind == 'agent':
            return self.agents_manager.get_agents()

        elif kind == 'social_asset':
            return self.social_assets_manager.get_social_assets()

        elif kind == 'socket':
            return self.agents_sockets_manager.get_sockets(), self.assets_sockets_manager.get_sockets()

        else:
            return None

    def get_actions(self, kind):
        if kind == 'agent':
            return self.agents_manager.get_actions()

        elif kind == 'social_asset':
            return self.social_assets_manager.get_actions()

        else:
            return None

    def get_workers(self, kind):
        if kind == 'agent':
            return self.agents_manager.get_workers()

        elif kind == 'social_asset':
            return self.social_assets_manager.get_workers()

        else:
            return None

    def get_kind(self, token):
        if self.get(token, 'agent') is None:
            if self.get(token, 'social_asset') is None:
                return None
            return 'social_asset'
        return 'agent'

    def edit(self, token, attribute, new_value, kind):
        if kind == 'agent':
            self.agents_manager.edit_agent(token, attribute, new_value)

        elif kind == 'social_asset':
            self.social_assets_manager.edit_social_asset(token, attribute, new_value)

        else:
            return False

        return True

    def clear_workers(self):
        self.agents_manager.clear_workers()
        self.social_assets_manager.clear_workers()
        return True

    def remove(self, token, kind):
        if kind == 'agent':
            self.agents_manager.remove_agent(token)
            self.agents_sockets_manager.remove_socket(token)

        elif kind == 'social_asset':
            self.social_assets_manager.remove_social_asset(token)
            self.assets_sockets_manager.remove_socket(token)

        else:
            return False

        return True
