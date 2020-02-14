from argparse import ArgumentParser
from datetime import datetime

from requests import get

availabilities = {}

parser = ArgumentParser(description='Schedule rehearsals based on provided whenufree links.')
parser.add_argument('urls', metavar='ID', type=str, nargs='+', help='an ID of a whenufree')

args = parser.parse_args()

for url in args.urls:
    response = get('https://whenufree.io/api/events/{}'.format(url))
    json = response.json()
    found = False
    for person in json['availabilities']:
        if len(person['cells']):
            print("Using {}'s data for URL {}".format(person['name'], url))
            found = True
            break
    if not found:
        print('Could not find a user for URL {}'.format(url))
        exit(1)
    for entry in person['cells']:
        availabilities[entry['date']] = availabilities.get(entry['date'], {})
        availabilities[entry['date']][entry['hour']] = availabilities[entry['date']].get(entry['hour'], [0, 0])
        availabilities[entry['date']][entry['hour']][entry['block']] += 1

for date in sorted(availabilities.keys()):
    tracking = False
    start_time = 0
    start_block = 0
    for time in sorted(availabilities[date].keys()):
        for block, count in enumerate(availabilities[date][time]):
            if count == len(args.urls) and not tracking:
                tracking = True
                start_time = time
                start_block = block
            elif count != len(args.urls) and tracking:
                tracking = False
                print('Available on {} from {}:{} to {}:{}'.format(datetime.strptime(date, '%Y-%m-%dT00:00:00.000Z').strftime('%A %Y-%m-%d'), start_time, '30' if start_block else '00', time, '30' if block else '00'))
    if tracking:
        tracking = False
        print('Available on {} from {}:{} to 0:00'.format(datetime.strptime(date, '%Y-%m-%dT00:00:00.000Z').strftime('%A %Y-%m-%d'), start_time, '30' if start_block else '00'))
