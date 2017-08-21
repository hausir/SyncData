# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from ..models import SyncData


class SyncDataService(object):
    def __init__(self, session, gid=0):
        self.session = session
        self.gid = gid

    def get(self, _hash):
        data = self.session.query(SyncData).filter(
            SyncData.hash == _hash,
        ).filter(
            SyncData.gid == self.gid,
        ).first()
        return data

    def get_all(self, to_dict=True):
        sync_datas = self.session.query(SyncData).filter(
            SyncData.deleted == False,
        ).filter(
            SyncData.gid == self.gid,
        ).all()

        if to_dict:
            data = []
            for sync_data in sync_datas:
                data.append({
                    'id': sync_data.id,
                    'hash': sync_data.hash,
                    'data': json.loads(sync_data.data),
                })
            return data

        return sync_datas

    def add(self, data):
        sync_data = SyncData(
            gid=self.gid,
            hash=data.get('hash'),
            data=json.dumps(data.get('data')),
        )
        self.session.add(sync_data)

    def delete(self, data):
        data = self.get(data.get('hash'))
        data.deleted = True
        self.session.flush()

    def update(self, kwargs):
        data = self.get(kwargs.get('hash'))
        data.data = json.dumps(kwargs.get('data'))
        self.session.flush()
