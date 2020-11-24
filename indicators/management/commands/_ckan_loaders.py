import os
import json

from django.db.utils import IntegrityError
from indicators.models.ckan import CKANGeomSource

DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../../data/ckan/',
)


def load_sources():
    with open(DATA_DIR + 'sources.json') as f:
        sources = json.load(f)

    for source in sources:
        s = CKANGeomSource(**source)
        try:
            s.save()
        except IntegrityError as e:
            print('\x1b[1;31m', source['name'], 'already exists!', '\x1b[0m')