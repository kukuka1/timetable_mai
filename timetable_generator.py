from bs4 import BeautifulSoup
import datetime
import requests
import uuid

group_name = 'М1О-101С-20'
year = str(datetime.datetime.now().year)
with open(group_name + '.ics', 'w', encoding='utf8') as calendar:
    calendar.write('BEGIN:VCALENDAR\n'
                   'PRODID:-//Google Inc//Google Calendar 70.9054//EN\n'
                   'VERSION:2.0\n'
                   'CALSCALE:GREGORIAN\n'
                   'METHOD:PUBLISH\n'
                   'X-WR-CALNAME:МАИ\n'
                   'X-WR-TIMEZONE:Europe/Moscow\n'
                   'X-WR-CALDESC:{}\n'
                   'BEGIN:VTIMEZONE\n'
                   'TZID:Europe/Moscow\n'
                   'X-LIC-LOCATION:Europe/Moscow\n'
                   'BEGIN:STANDARD\n'
                   'TZOFFSETFROM:+0300\n'
                   'TZOFFSETTO:+0300\n'
                   'TZNAME:MSK\n'
                   'DTSTART:19700101T000000\n'
                   'END:STANDARD\n'
                   'END:VTIMEZONE\n'.format(group_name))
    days = []
    for i in range(18):
        data_group = requests.get('https://mai.ru/education/schedule/detail.php?group={}&week={}'.format(group_name, i))
        if data_group.status_code != requests.codes.ok:
            data_group.raise_for_status()

        soup = BeautifulSoup(data_group.content, 'html.parser')
        soup_data_days = soup.find_all("div", "sc-container")
        for soup_day in soup_data_days:
            day = soup_day.find('div', 'sc-day-header').contents[0].strip()
            if day not in days:
                days.append(day)
            else:
                continue
            item_time = soup_day.find_all('div', 'sc-item-time')
            item_type = soup_day.find_all('div', 'sc-item-type')
            item_title = soup_day.find_all('span', 'sc-title')
            lecturer = soup_day.find_all('span', 'sc-lecturer')
            item_location = soup_day.find_all('div', 'sc-item-location')
            for info in zip(item_time, item_type, item_title, lecturer, item_location):
                lesson = []
                id = uuid.uuid1()
                for inf in info:
                    lesson.append(inf.get_text().strip())
                if 'Военная подготовка' in lesson:
                    continue
                calendar.write('BEGIN:VEVENT\n')
                calendar.write('DTSTART;TZID=Europe/Moscow:{}{}T{}00\n'.format(
                    year, day[-2:] + day[0:2], lesson[0][:5].replace(':', '')))
                calendar.write('DTEND;TZID=Europe/Moscow:{}{}T{}00\n'.format(
                    year, day[-2:] + day[0:2], lesson[0][-5:].replace(':', '')))
                calendar.write('DTSTAMP:20190901T000000\n')
                calendar.write('UID:{}@google.com\n'.format(id.hex))
                calendar.write('DESCRIPTION:{}\n'.format(lesson[3]))
                calendar.write('LOCATION:{}\n'.format(lesson[4]))
                calendar.write('SEQUENCE:0\n')
                calendar.write('STATUS:CONFIRMED\n')
                calendar.write('SUMMARY:{}\n'.format(lesson[1] + ' ' + lesson[2]))
                # calendar.write('COLOR:{}\n'.format(choice([''])))
                calendar.write('TRANSP:OPAQUE\n')
                calendar.write('END:VEVENT\n')
    calendar.write('END:VCALENDAR\n')
