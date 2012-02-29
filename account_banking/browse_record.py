# -*- coding: utf-8 -*-
from osv.orm import browse_record

def refresh(self):
    """
    This method taken from OpenERP 6.1. We use it to monkeypatch the
    browse_record class with. Note that this affects the behaviour of the
    OpenERP instance on all databases that it runs.

    Force refreshing this browse_record's data and all the data of the
    records that belong to the same cache, by emptying the cache completely,
    preserving only the record identifiers (for prefetching optimizations).
    """
    for model, model_cache in self._cache.iteritems():
        # only preserve the ids of the records that were in the cache
        cached_ids = dict([(i, {'id': i}) for i in model_cache.keys()])
        self._cache[model].clear()
        self._cache[model].update(cached_ids)
        
browse_record.refresh = refresh
