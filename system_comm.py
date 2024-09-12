from requests import get
from loguru import logger
import json
from config import headers
from messages import ErrorText
from messages import countrie_flags, is_active
from aiogram import html
from classes import MixNode


def new_user(file: str, username: str = "", lang: str = "") -> bool:
    file = str(file)
    with open(f'users/{file}.json', 'w') as f:
        empy_user = {
            "telegram" : {
                "username" : username,
                "lang" : lang,
                "currency" : ""
                },
            "mixnodes" : [],
        }
        json.dump(empy_user, f, indent=4, ensure_ascii=False)
        logger.info(f"{file} started|restarted")
        return True

def validate_comma(comma: list) -> str:
    if len(comma.text.split()) > 1:
        if comma.text.split()[1].isdigit():
            return True
        else:
            return ErrorText.NOT_NUMBER
    else:
        return ErrorText.EMPTY_COMMAND


def get_mixnode_info(user_id:str, mix_node_id: str) -> str:
    with open(f'users/{user_id}.json', 'r') as f:
        data_from_file = json.load(f)
    out_info = {}
    # cur_version = get('https://api.github.com/repos/nymtech/nym/releases/latest', headers).json()['tag_name']
    # current_version = get(f'https://github.com/nymtech/nym/releases/download/{cur_version}/hashes.json').json()['assets']['nym-node']['details']['build_version']
    for i in data_from_file['mixnodes']:
        if i['info']['mix_id'] == int(mix_node_id):
            out_info = i['info']
            out_stats = i['stats']
            out_deleg = i['delegations']
        else:
            continue
        return (f"\
    {html.italic(html.underline('mixnode info'))} explorer №:{html.link(mix_node_id, 'https://explorer.nymtech.net/network-components/mixnode/'+mix_node_id)}\n\
    {html.italic('ip')}: {html.bold(out_info['mix_node']['host'])}\n\
    {html.italic('country')}: {html.bold(out_info['location']['country_name'])} {next((_['emoji'] for _ in countrie_flags if out_info['location']['country_name'] == _['name']), None)}\n\
    {html.italic('status')}: {html.bold(out_info['status'])} {is_active[0]if out_info['status'] == 'active' else is_active[1]}\n\
    {html.italic('blacklist')}: {html.bold('no' if out_info['blacklisted'] is False else 'yes!!!')}\n\
    {html.italic('version')}: {html.bold(out_info['mix_node']['version'])} (current: {html.bold(current_version)})\n\
    {html.italic('saturation')}: {html.bold(round(float(out_info['stake_saturation'])*100, 5))}%\n\
    {html.italic('performance 24h')}: {html.bold(float(out_info['node_performance']['last_24h'])*100)}%\n\
    {html.italic('op.cost')}: {html.bold(float(out_info['operating_cost']['amount'])/1000000)} NYM   {html.italic('profit')}: {html.bold(round(float(out_info['profit_margin_percent'])*100))}%\n\
    {html.italic('delegators')}: {html.bold(len(out_deleg))}\n\
    {html.italic('delegation')}: {html.bold(float(out_info['total_delegation']['amount'])/1000000)} NYM\n\
    {html.italic('    received')}: {html.bold('{:,d}'.format(out_stats['packets_received_since_startup']))}\n\
        {html.italic('           sent')}: {html.bold('{:,d}'.format(out_stats['packets_sent_since_startup']))}\n\
        {html.italic('    dropped')}: {html.bold('{:,d}'.format(out_stats['packets_explicitly_dropped_since_startup']))}\n\
    {html.italic('bond')}: {html.bold(float(out_info['pledge_amount']['amount'])/1000000)} NYM\n\
    {html.italic('NYM price')}: {html.bold(nym_price)}\n\
    ")

    
def get_explorer_mixnode_json(mix_node_id: str, endpoint: str) -> None or dict:
    API = 'https://explorer.nymtech.net/api/v1/mix-node/'
    url = f'{API}{str(mix_node_id)}{endpoint}'
    if get(url, headers=headers).status_code == 200:
        return get(url, headers=headers).json()
    else:
        return False

def get_nym_price():
    response = get('https://iapi.kraken.com/api/internal/markets/all/assets', headers=headers_krack)
    if response.status_code == 200:
        for key in response.json()["result"]["data"]:
            if key["symbol"] == "NYM":
                return str(key["price"])
    else: return "Nope!"

def add_mixnode(user_id: int, node_id: str) -> bool:
    user_id = str(user_id)
    mix_node = MixNode(node_id)
    with open(f"users/{user_id}.json", "r") as file:
        data_from_json = json.load(file)
    mix_list = [i['info']["mix_id"] for i in data_from_json["mixnodes"]]
    if int(node_id) not in mix_list and mix_node.get_mixnode_info() is not False:
        data_from_json["mixnodes"].append({
            'info':mix_node.get_mixnode_info(),
            'delegations':mix_node.get_mixnode_delegations(),
            'stats':mix_node.get_mixnode_stats()
        })
        try:
            with open(f"users/{user_id}.json", "w") as file:
                json.dump(data_from_json, file, indent=4, ensure_ascii=False)
        except Exception:
            logger.error(f"Error while adding mixnode {node_id} to {user_id}")
        return True
    else:
        return False

def del_mixnode(user_id: int, node_id: int) -> bool:
    user_id = str(user_id)
    node_id = str(node_id)
    with open(f"users/{user_id}.json", "r") as file:
        data_from_json = json.load(file)
    if len(data_from_json["mixnodes"]) > 0:
        for key in data_from_json["mixnodes"]:
            if key['info']['mix_id'] == int(node_id):
                data_from_json["mixnodes"].remove(key)
    else:
        return False
    with open(f"users/{user_id}.json", "w") as file:
        json.dump(data_from_json, file, indent=4, ensure_ascii=False)
    return True



