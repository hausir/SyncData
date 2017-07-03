# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from sqlalchemy.sql import func
from ..models import ExecuteLog


class ExecuteLogService(object):
    def __init__(self, session):
        self.session = session

    def get_max_id(self):
        log = self.session.query(
            func.max(ExecuteLog.id).label('max_id')
        ).first()

        return log.max_id if log.max_id else 0

    def get_unexecute_logs(self, log_id, to_dict=True):
        logs = self.session.query(ExecuteLog).filter(
            ExecuteLog.id > log_id,
        ).all()

        if to_dict:
            data = []
            for log in logs:
                data.append({
                    'id': log.id,
                    'log': json.loads(log.log),
                })
            return data

        return logs

    def add(self, log):
        execute_log = ExecuteLog(
            log=json.dumps(log),
        )
        self.session.add(execute_log)
        self.session.flush()

        return execute_log.id
