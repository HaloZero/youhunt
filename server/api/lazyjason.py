# api.lazyjason

import json

class LazyJason(object):
    _lazy_defaults = {}

    def laze(self):
        self._orig_db_attrs = self.db_attrs
        if hasattr(self, '_jdict'):
            return
        #print 'trying to load', self.db_attrs
        try:
            self._jdict = json.loads(self.db_attrs)
        except ValueError:
            print 'Corrupt db_attrs'

    def freeze_db_attrs(self):
        if self.db_attrs != self._orig_db_attrs:
            # Someone has gone in raw and changed db_attrs.  It was probably
            # the Django admin interface.
            print 'Lost track of the source of truth.'
            try:
                self._jdict = json.loads(self.db_attrs)
                print 'db_attrs clobbers _jdict'
            except ValueError:
                print 'db_attrs invalid, _jdict clobbers db_attrs'

        if self.db_attrs == '{}':
            # Brand new in the original packaging
            dba = self._lazy_defaults.copy()
        else:
            # We may have added some items to _lazy_defaults since last save
            dba = json.loads(self.db_attrs)
            print 'non default dba', dba
            for key,val in self._lazy_defaults.items():
                if key not in dba:
                    print 'key %s was not in dba' % key
                    dba[key] = val
        if hasattr(self, '_jdict'):
            dba.update(self._jdict)
        else:
            print 'SHOULD NOT GET HERE'

        self.db_attrs = json.dumps(dba)

    def __getattr__(self, attrname):
        #if not hasattr(self, '_jdict'):
        #    print 'LasyJason needs to laze() first'
        if attrname in self._jdict:
            return self._jdict[attrname]
        return object.__getattribute__(self, attrname)

    def lazy_set(self, **kwargs):
        self._jdict.update(kwargs)

    def to_dict(self, *extra_args):
        self.freeze_db_attrs()
        d = self._jdict.copy()
        d.update(id=self.id)
        for key in extra_args:
            d[key] = getattr(self, key)
        return d

def pre_save_for_lazies(**kwargs):
    instance = kwargs.get('instance')
    print 'in pre save for ', kwargs
    instance.freeze_db_attrs()

def post_init_for_lazies(**kwargs):
    instance = kwargs.get('instance')
    instance.laze()