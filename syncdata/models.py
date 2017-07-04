# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, String, Integer, Text, Boolean


class _Base(object):

    table_prefix = 'sd_'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True, name="id")

    @declared_attr
    def __tablename__(self):
        name = self.__name__

        return (
            self.table_prefix + name[0].lower() + re.sub(r'([A-Z])', lambda m: "_" + m.group(0).lower(), name[1:])
        )

Base = declarative_base(cls=_Base)


class ExecuteLog(Base):
    gid = Column(Integer, server_default='0', index=True, nullable=False)
    log = Column(Text, server_default='', nullable=False)


class SyncData(Base):
    gid = Column(Integer, server_default='0', index=True, nullable=False)
    hash = Column(String(255), unique=True, server_default='', nullable=False)
    data = Column(Text, server_default='', nullable=False)
    deleted = Column(Boolean, server_default='FALSE', nullable=False)
