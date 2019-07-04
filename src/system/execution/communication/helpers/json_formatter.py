def simulation_started_format(response, token):
    info = {'status': 0, 'result': False, 'agent': {}, 'event': {}, 'message': 'Possible internal error'}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

            for agent in response['agents']:
                if agent['token'] == token:
                    info['agent'] = agent
                    break

            if not info['agent']:
                return event_error_format('Agent not found in response. ')

            info['event'] = response['event']

        info['message'] = response['message']

        return info

    else:
        return event_error_format('Empty simulation response. ')


def simulation_ended_format(response):
    info = {'status': 0, 'result': False, 'agent': {}, 'event': {}, 'message': 'Possible internal error'}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

        info['message'] = response['message']

        return info

    else:
        return event_error_format('Empty response. ')


def action_results_format(response, token):
    info = {'status': 0, 'result': False, 'agent': {}, 'event': {}, 'message': 'Possible internal error'}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

            for agent in response['agents']:
                if agent['agent']['token'] == token:
                    info['agent'] = agent['agent']
                    info['message'] = agent['message']
                    break

            if not info['agent']:
                return event_error_format('Agent not found in response. ')

            info['event'] = response['event']

        else:
            info['message'] = response['message']

        return info

    else:
        return event_error_format('Empty simulation response. ')


def event_error_format(message):
    return {'status': 0, 'result': False, 'agent': {}, 'event': {}, 'message': f'{message}Possible internal error'}
