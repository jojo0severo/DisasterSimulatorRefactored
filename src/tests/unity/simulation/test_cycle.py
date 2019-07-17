import sys
import pathlib

file_path = pathlib.Path(__file__).parents[4]
if str(file_path.absolute) not in sys.path:
    sys.path.insert(0, str(file_path.absolute()))

engine_path = pathlib.Path(__file__).parents[3] / 'execution'
if str(engine_path.absolute()) not in sys.path:
    sys.path.insert(1, str(engine_path.absolute()))

import json
from src.execution.simulation_engine.simulation_helpers.cycle import Cycle

config_path = pathlib.Path(__file__).parent / 'simulation_tests_config.json'
config_json = json.load(open(config_path, 'r'))
cycle = Cycle(config_json)


def test_connect_agent():
    assert cycle.connect_agent('token_agent')
    assert not cycle.connect_agent('token_agent')


def test_connect_asset():
    assert cycle.connect_social_asset('token')
    assert not cycle.connect_social_asset('token')


def test_disconnect_agent():
    assert cycle.disconnect_agent('token_agent')
    assert not cycle.disconnect_agent('token_agent')


def test_disconnect_asset():
    assert cycle.disconnect_social_asset('token')
    assert not cycle.disconnect_social_asset('token')


def test_get_agents_info():
    assert len(cycle.get_agents_info()) == 1

    cycle.connect_agent('token_agent1')

    assert len(cycle.get_agents_info()) == 2


def test_get_assets_info():
    assert len(cycle.get_assets_info()) == 1

    cycle.connect_social_asset('token1')
    assert len(cycle.get_assets_info()) == 2


def test_get_step():
    assert cycle.get_step()


def test_activate_step():
    old = cycle.get_step()
    assert not old['flood'].active

    cycle.activate_step()
    new = cycle.get_step()

    assert new['flood'].active


def test_get_previous_steps():
    for i in range(1, 5):
        cycle.current_step = i
        cycle.activate_step()

    assert cycle.get_previous_steps()


def test_check_steps():
    assert not cycle.check_steps()
    cycle.current_step = 10
    assert cycle.check_steps()
    cycle.current_step = 4


def test_update_steps():
    old_period = cycle.steps[0]['flood'].period
    cycle.update_steps()
    new_period = cycle.steps[0]['flood'].period

    assert old_period != new_period


def test_nothing_just_setup_for_pytest():
    cycle.restart(config_json)
    for i in range(10):
        cycle.current_step = i
        cycle.activate_step()
        cycle.update_steps()


def test_check_abilities_and_resources():
    assert cycle._check_abilities_and_resources('token_agent', 'move')

    for i in range(1, 4):
        cycle.connect_agent(f'token{i+1}_agent')

    cycle.connect_agent('agent_without_abilities')
    assert not cycle._check_abilities_and_resources('agent_without_abilities', 'move')

    cycle.connect_agent('agent_without_resources')
    assert not cycle._check_abilities_and_resources('agent_without_resources', 'charge')


if __name__ == '__main__':
    test_connect_agent()
    test_connect_asset()
    test_disconnect_agent()
    test_disconnect_asset()
    test_get_agents_info()
    test_get_assets_info()
    test_get_step()
    test_activate_step()
    test_get_previous_steps()
    test_check_steps()
    test_update_steps()
    test_nothing_just_setup_for_pytest()
    test_check_abilities_and_resources()