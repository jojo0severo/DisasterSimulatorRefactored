import time
from communication.objects.social_asset import SocialAsset


class SocialAssetsManager:
    def __init__(self):
        self.social_assets = {}

    def add_social_asset(self, token, agent_info):
        self.social_assets[token] = SocialAsset(token, agent_info)

    def get_social_asset(self, token):
        return self.social_assets.get(token)

    def get_social_assets(self):
        return list(self.social_assets.values())

    def get_actions(self):
        actions = []
        try:
            for token in self.social_assets:
                if self.social_assets[token].worker:
                    action_name = self.social_assets[token].action_name
                    action_params = self.social_assets[token].action_params

                    actions.append({'token': token, 'action': action_name, 'parameters': action_params})

        except RuntimeError:
            time.sleep(1)
            actions = []
            for token in self.social_assets:
                if self.social_assets[token].worker:
                    action_name = self.social_assets[token].action_name
                    action_params = self.social_assets[token].action_params

                    actions.append({'token': token, 'action': action_name, 'parameters': action_params})

        return actions

    def get_workers(self):
        return [self.social_assets[token] for token in self.social_assets if self.social_assets[token].worker]

    def edit_social_asset(self, token, attribute, new_value):
        exec(f'self.social_assets[token].{attribute} = new_value')

    def clear_workers(self):
        for token in self.social_assets:
            self.social_assets[token].worker = False

    def remove_social_asset(self, token):
        del self.social_assets[token]
