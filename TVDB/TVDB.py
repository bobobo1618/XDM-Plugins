from xdm.plugins import *

from tvdb_api import tvdb_api

import xml.etree.ElementTree as etree
import requests
import re

class TVDB(Provider):
    version = '0.1'
    identifier = 'com.github.bobobo1618.tvdb'
    _tag = 'tvdb'

    types = ['de.lad1337.tv']
    _config = {
        'usexem': True,
        'apikey': '',
        'language':'en'
    }
    config_meta = {
        'plugin_desc': 'TheTVDB provider.'
    }

    base_url = 'http://thetvdb.com/api/'

    def searchForElement(self, term='', id=0):
        self.progress.reset()

        mt = MediaType.get(MediaType.identifier == 'de.lad1337.tv')
        mtm = mt.manager
        root = mtm.getFakeRoot(term)

        t = tvdb_api.Tvdb(banners=True, apikey=self._config.get('apikey') or None)
        shows = t.search(term)

        self.progress.total = len(shows)
        for show in shows:
            newElement = self.getElement(show['seriesid'], new_root=root, lang=show['language'])
            self.progress.addItem()

        return root

        
    def getElement(self, series_id, element=None, new_root=None, lang='en'):
        mt = MediaType.get(MediaType.identifier == 'de.lad1337.tv')
        mtm = mt.manager
        root = new_root or mtm.getFakeRoot(term)
        series_id = str(series_id)

        t = tvdb_api.Tvdb(banners=True, apikey=self._config.get('apikey') or None)
        t._getShowData(series_id, lang)
        s = t.shows[series_id]

        show = Element()
        show.mediaType = mt
        show.parent = root
        show.type = 'Show'

        show.setField("title", s['seriesname'], self._tag)
        show.setField("overview", s['overview'], self._tag)
        show.setField("id", int(s['id']), self._tag)

        show.setField("poster_image", s['poster'], self._tag)
        show.setField("banner_image", s['banner'], self._tag)
        show.setField("fanart_image", s['fanart'], self._tag)

        show.setField("show_status", s['status'], self._tag)

        show.setField("year", s['firstaired'].split('-')[0], self._tag)

        show.setField("genres", ", ".join(s['genre'].strip('|').split('|')), self._tag)

        show.setField("runtime", s['runtime'], self._tag)

        show.setField("airs", s['airs_dayofweek'] + ' ' + s['airs_time'])

        for (x, season) in show.items():
            newSeason = Element()
            newSeason.mediaType = mt
            newSeason.parent = show
            newSeason.type = 'Season'

            newSeason.setField('number', x, self._tag)

            for (y, episode) in season.items():
                newEpisode = Element()
                newEpisode.mediaType = mt
                newEpisode.parent = newSeason
                newEpisode.type = 'Episode'

                newEpisode.setField("title", episode['episodename'], self._tag)
                newEpisode.setField("airdate", episode['firstaired'], self._tag)
                newEpisode.setField("season", x, self._tag)
                newEpisode.setField("number", y, self._tag)
                newEpisode.setField("overview", episode['overview'], self._tag)

                newEpisode.saveTemp()

            newSeason.saveTemp()

        show.saveTemp()









        