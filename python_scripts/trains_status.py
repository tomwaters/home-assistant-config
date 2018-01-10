# notify the status of trains in a window
time_format = '%H:%M'
entity_id = data.get('entity_id')
notify_target = data.get('notify_target')
throttle_mins = data.get('throttle_mins') or 1
late_only = data.get('late_only') == 'True'
window_start = time.strptime(data.get('window_start', '08:00'), time_format)
window_end = time.strptime(data.get('window_end', '08:30'), time_format)
attributes = hass.states.get(entity_id).attributes

response = ''
for train in attributes['next_trains']:
    train_scheduled = time.strptime(train['scheduled'], time_format)
    if train_scheduled >= window_start and train_scheduled <= window_end:
        train_estimated = time.strptime(train['estimated'], time_format)
        if late_only != True or train_estimated > train_scheduled:
            response = '{0}{1} to {2} estimated {3} ({4})\r\n'.format(
                response,
                train['scheduled'],
                train['destination_name'],
                train['estimated'],
                train['status']
            )

if late_only != True or response != '':
    response = response or 'No trains within window'
    last_sent = hass.states.get('trains_status.last_sent').state or 0
    if time.time() > float(last_sent) + (float(throttle_mins) * 60):
        hass.services.call(
            'notify',
            notify_target,
            {'title': 'Train Status Update', 'message': response})
        hass.states.set('trains_status.last_sent', time.time())
