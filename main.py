from collections import OrderedDict as odict
import json
from typing import List

import attr
import xlrd
import pycountry


def int_to_str(obj):
    return str(int(obj))


@attr.s
class Municipality:
    code = attr.ib(convert=int_to_str)
    province = attr.ib()
    name = attr.ib()

    COLUMNS = """CODIGO_CA
COMUNIDAD_AUTONOMA
Codigo Provincia
PROVINCIA
NUMERO_INSCRIPCION
Codigo Municipio
DENOMINACION
FECHA_INSCRIPCION
SUPERFICIE
HABITANTES
DENSIDAD
CAPITALIDAD""".split('\n')

    @classmethod
    def from_row_to_obj(cls, values: List):
        args = [values[i] for i in (4, 3, 6)]
        return Municipality(*args)


@attr.s
class Province:
    code = attr.ib(convert=int_to_str)
    name = attr.ib()
    iso_3166_name = attr.ib(default=None)
    iso_3166_code = attr.ib(default=None)

    COLUMNS = """CODIGO_CA
COMUNIDAD_AUTONOMA
NUMERO_INSCRIPCION
DENOMINACION
FECHA_INSCRIPCION
SUPERFICIE
HABITANTES
DENSIDAD
CAPITALIDAD
REGIMEN_FUNCIONAMIENTO""".split('\n')

    @classmethod
    def from_row_to_obj(cls, values: List):
        args = [values[i] for i in (2, 3,)]
        return Province(*args)

    def search(self):
        return


MINEH_ISO = dict([
    ('Castelló/Castellón', 'Castellón'),
    ('Coruña, A', 'A Coruña'),
    ('Rioja, La', 'La Rioja'),
    ('Araba/Álava', 'Álava'),
    ('València/Valencia', 'Valencia / València'),
    ('Navarra', 'Navarra / Nafarroa'),
    ('Palmas, Las', 'Las Palmas'),
    ('Alacant/Alicante', 'Alicante'),
    ('Illes Balears', 'Balears'),
    ('Ceuta', None),
    ('Melilla', None),
])


def guess_subdivision(name):
    SUBDIVISION = {s.name: s for s in pycountry.subdivisions.get(country_code='ES')}
    if name in SUBDIVISION:
        return SUBDIVISION[name]

   # Undo ,
    if ', ' in name:
        a, __, b = name.partition(', ')
        alt_name = f'{b} {a}'
        if name in SUBDIVISION:
            return SUBDIVISION[alt_name]

    # use translation table
    alt_name = MINEH_ISO.get(name)
    if alt_name and alt_name in SUBDIVISION:
        return SUBDIVISION[alt_name]

    raise LookupError(f'{name} not found in subdivisions')


    SUBSTITUTION = {
        'València/Valencia': 'Valencia / València',
    }
    for s in pycountry.subdivisions.get(country_code='ES'):
        if name in SUBSTITUTION:
            name = SUBSTITUTION[name]
        elif ', ' in name:
            print(name)
            a, __, b = name.partition(', ')
            name = f'{b} {a}'
        if s.name == name:
            return s.code
    raise LookupError(f'{name} not found in subdivisions')


def as_dict(obj):
    try:
        return attr.asdict(obj)
    except attr.exceptions.NotAnAttrsClassError:
        raise TypeError()


def municipalities():
    book = xlrd.open_workbook('municipios_export.csv.xls')
    sheet = book.sheet_by_index(0)

    rows = iter(range(8, 8133))
    cols = range(1, 13)

    first_row = next(rows)
    headers = [sheet.cell(first_row, colx).value for colx in cols]
    for c, h in zip(Municipality.COLUMNS, headers):
        assert c == h, 'ERROR: header mistmatch'

    for rowx in rows:
        values = [sheet.cell(rowx, colx).value for colx in cols]
        yield Municipality.from_row_to_obj(values)


def provinces():
    book = xlrd.open_workbook('provincias_export.csv.xls')
    sheet = book.sheet_by_index(0)

    rows = iter(range(8, 9999))
    cols = range(1, 9)

    first_row = next(rows)
    headers = [sheet.cell(first_row, colx).value for colx in cols]
    for c, h in zip(Province.COLUMNS, headers):
        assert c == h, 'ERROR: header mistmatch'

    for rowx in rows:
        try:
            values = [sheet.cell(rowx, colx).value for colx in cols]
        except IndexError:
            break

        province = Province.from_row_to_obj(values)
        subdivision = guess_subdivision(province.name)
        province.iso_3166_code = subdivision.code
        province.iso_3166_name = subdivision.name

        yield province


def main():
    d = odict()

    d['municipalities'] = []
    for municipality in municipalities():
        d['municipalities'].append(municipality)

    d['provinces'] = []
    for province in provinces():
        d['provinces'].append(province)

    print(json.dumps(d, indent=2, default=as_dict))


if __name__ == '__main__':
    main()
