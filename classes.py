from requests import get
from config import headers


class MixNode:
    def __init__(self, node_id: str):
        self.node_id = node_id

    @staticmethod
    def get_url(url: str) -> str:
        if get(url, headers=headers).status_code == 200:
            return get(url, headers=headers).json()
        else:
            return False

    @staticmethod
    def get_explorer_mixnode_json(self, endpoint: str) -> None:
        mixnode_endpoints = 'https://explorer.nymtech.net/api/v1/mix-node/'
        url = mixnode_endpoints + self.node_id + endpoint
        return self.get_url(url)

    @staticmethod
    def get_validator_mixnode_json(self, endpoint: str) -> None:
        validator_endpoints = 'https://validator.nymtech.net/api/v1/status/mixnode/'
        url = validator_endpoints + self.node_id + endpoint
        return self.get_url(url)

    def get_mixnode_info(self) -> dict:
        return self.get_explorer_mixnode_json(self, '/')

    def get_mixnode_stats(self) -> str:
        return self.get_explorer_mixnode_json(self, '/stats')

    def get_mixnode_delegations(self) -> str:
        return self.get_explorer_mixnode_json(self, '/delegations')

    def get_mixnode_summed(self) -> str:
        return self.get_explorer_mixnode_json(self, '/summed')

    def get_mixnode_history(self) -> list:
        return self.get_validator_mixnode_json(self, '/history')

    def get_mixnode_economic_dynamics_stats(self) -> str:
        return self.get_explorer_mixnode_json(self, '/economic-dynamics-stats')


