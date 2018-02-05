# -*- coding: utf-8 -*-

from resources.lib import kodilogging
from resources.lib import plugin

import logging
import xbmcaddon

import operator

import routing
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory, setResolvedUrl, getSetting, setContent

import xml.etree.ElementTree as ET

# Keep this file to a minimum, as Kodi
# doesn't keep a compiled copy of this
ADDON = xbmcaddon.Addon()
kodilogging.config()

import requests

URL = 'https://fosdem.org/2018/schedule/xml'

plugin = routing.Plugin()

def fetch_root():
    r = requests.get(URL)
    return ET.fromstring(r.text.encode('utf-8'))


root = fetch_root()


@plugin.route('/')
@plugin.route('/dir/<path:subdir>')
def show_dir(subdir=''):
    if subdir == '':
        addDirectoryItem(plugin.handle, plugin.url_for(show_dir,
                         subdir='2018'), ListItem('2018'), True)
    else:
        for day in root.findall('day'):
            number = day.attrib['index']
            text = 'Day {}'.format(number)
            url = plugin.url_for(show_day, day=number)
            addDirectoryItem(plugin.handle, url,
                             ListItem(text), True)
    endOfDirectory(plugin.handle)


@plugin.route('/day/<day>')
def show_day(day):
    exp = './day[@index="{}"]/room'.format(day)
    for room in root.findall(exp):
        name = room.attrib['name']
        addDirectoryItem(plugin.handle, plugin.url_for(show_room,
                         day=day, room=name), ListItem(name), True)
    endOfDirectory(plugin.handle)


@plugin.route('/room/<day>/<room>')
def show_room(day, room):
    exp = './day[@index="{}"]/room[@name="{}"]/event'.format(day, room)
    for event in root.findall(exp):
        links = [link.attrib['href'] for link in event.findall('./links/link') if 'video.fosdem.org' in link.attrib['href']]
        if not links:
            continue

        event_id = event.attrib['id']
        title = event.find('title').text
        track = event.find('track').text
        subtitle = event.find('subtitle').text
        persons = [p.text for p in event.find('./persons/person')]
        abstract = event.find('abstract').text
        if abstract:
            abstract = abstract.replace('<p>', '').replace('</p>', '')

        item = ListItem(title)
        item.setProperty('IsPlayable', 'true')
        item.setInfo('video', {
            'cast': persons,
            'genre': track,
            'plot': abstract,
            'tagline': subtitle,
        })
        #item.setArt({'thumb': event['logo_url']})
        url = plugin.url_for(show_event,
                             event_id=event_id)
        addDirectoryItem(plugin.handle, url, item, False)



    endOfDirectory(plugin.handle)


@plugin.route('/event/<event_id>')
def show_event(event_id):
    event = root.find('.//event[@id="{}"]'.format(event_id))
    links = [link.attrib['href'] for link in event.findall('./links/link')]
    print(links)
    videos = [link for link in links if 'video.fosdem.org' in link]
    print(videos)
    if videos:
        print(videos)
        url = videos[0]
        setResolvedUrl(plugin.handle, True, ListItem(path=url))




if __name__ == '__main__':
    plugin.run()

