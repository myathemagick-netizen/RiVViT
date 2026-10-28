"""Export a filtered JSON view without deleting source collection records."""
import argparse
import json
from pathlib import Path


def export_view(dataset, labels, use_suggestions=False):
    events = []
    for event in dataset['events']:
        reading = event['classification']
        # An explicit review always overrides a lexical suggestion, including neither.
        reviewed = reading['label'] != 'unreviewed'
        label = reading['label'] if reviewed or not use_suggestions else reading['suggestion']
        if label in labels:
            events.append(event)
    return {'schemaVersion':1,'year':dataset['year'],'license':dataset['license'],
            'selection':{'labels':sorted(labels),'allowUnreviewedSuggestions':use_suggestions,
                         'description':'Filtered view; the source collection is retained. Suggestions are not approved MMS readings.'},
            'records':len(events),'pages':dataset['pages'],'events':events}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--labels',nargs='+',choices=['novelty','tradition','mixed','neither','unreviewed'],default=['novelty','tradition','mixed'])
    parser.add_argument('--allow-suggestions',action='store_true')
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.input.resolve()==args.output.resolve():
        parser.error('Output must differ from the source collection')
    result=export_view(json.loads(args.input.read_text(encoding='utf-8')),set(args.labels),args.allow_suggestions)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Exported {result['records']} records; source retained.")


if __name__=='__main__':
    main()
