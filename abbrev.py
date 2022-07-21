from importlib.resources import contents
import sys
import json
import re
import argparse
from unicodedata import digit

def abbreviate(line, journal_to_abbr, booktitile_to_abbr):
    if re.search('".*"', line) is not None:
        name_template = '"{}"'
        name_full = re.search('".*"', line).group(0)
    elif re.search('{.*}', line) is not None:
        name_template = '{{{}}}'
        name_full = re.search('{.*}', line).group(0)
    else:
        raise ValueError('the format "{}" is not valid'.format(line))
    name_full_strip = name_full[1:-1]
    name_abbr = name_full_strip.replace('{','').replace('}','')
    if line.strip().startswith('journal'):
        name_abbr = journal_to_abbr.get(name_abbr, name_full_strip)
    elif line.strip().startswith('booktitle'):
        name_abbr = re.sub(r'\d{4}', '', name_abbr) # remove year
        name_abbr = name_abbr.strip(' ,')
        if re.search('\d', name_abbr) is not None:
            ordinal = re.search('\d+(st|nd|rd|th)', name_abbr).group(0)
            name_abbr = name_abbr.replace(ordinal, '')
            name_abbr = ' '.join(name_abbr.split()) # spaces to space
            name_abbr = booktitile_to_abbr.get(name_abbr, name_full_strip)
            if name_abbr.split()[0] == 'Proc.':
                name_abbr =  name_abbr.replace('Proc. ', 'Proc. '+ordinal+' ')
            else:
                name_abbr = ordinal + ' ' + name_abbr
        else:
            name_abbr = ' '.join(name_abbr.split()) # spaces to space
            name_abbr = booktitile_to_abbr.get(name_abbr, name_full_strip)
    name_abbr = name_template.format(name_abbr)

    return line.replace(name_full, name_abbr)

def main(journal_to_abbr, booktitile_to_abbr):
    for line in sys.stdin:
        line_strip = line.strip()
        if line_strip.startswith('journal') or line_strip.startswith('booktitle'):
            new_line = abbreviate(line, journal_to_abbr, booktitile_to_abbr)
            print(new_line.rstrip())
        else:
            print(line.rstrip())
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Abbreviation")
    parser.add_argument('--user-json', type=str, default=None, help="customized json file")
    args = parser.parse_args()

    with open('journal.json') as fin:
        journal_to_abbr = json.load(fin)
    
    with open('booktitile.json') as fin:
        booktitile_to_abbr = json.load(fin)

    if args.user_json is not None:
        with open(args.user_json) as fin:
            customize_json = json.load(fin)
        journal_to_abbr.update(customize_json)
        booktitile_to_abbr.update(customize_json)

    main(journal_to_abbr, booktitile_to_abbr)
