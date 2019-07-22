def simulation_started_format(response, token):
    info = {'status': 0, 'result': False, 'event': {}, 'message': ''}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

            for actor in response['actors']:
                if actor['token'] == token:
                    if 'role' in actor:
                        info['agent'] = actor
                    else:
                        info['social_asset'] = actor
                    break

            if 'agent' not in info and 'social_asset' not in info:
                return event_error_format('Actor not found in response. ')

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
    info = {'status': 0, 'result': False, 'event': {}, 'message': ''}

    if response:
        if response['status']:
            info['status'] = response['status']
            info['result'] = True

            for actor in response['actors']:
                if 'agent' in actor:
                    if actor['agent']['token'] == token:
                        info['agent'] = actor['agent']
                        info['message'] = actor['message']
                        break
                else:
                    if actor['social_asset']['token'] == token:
                        info['social_asset'] = actor['social_asset']
                        info['message'] = actor['message']
                        break

            if 'agent' not in info and 'social_asset' not in info:
                return event_error_format('Actor not found in response. ')

            info['event'] = response['event']

        else:
            info['message'] = response['message']

        return info

    else:
        return event_error_format('Empty simulation response. ')


def event_error_format(message):
    return {'status': 0, 'result': False, 'actor': {}, 'event': {}, 'message': f'{message}Possible internal error.'}
