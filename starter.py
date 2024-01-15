import argparse
import logging
import sys
sys.path.append(".")
import dotenv
dotenv.load_dotenv(".env")
from projectgurukul.corelib import (
    SCRIPTURE_MAPPING,
    SYSTEM_PROMPT,
    get_query_engines)


def main():
    parser = argparse.ArgumentParser(
        description='Process some questions about the Gita.')
    parser.add_argument('--question', metavar='question', type=str,
                        help='the question to process')
    parser.add_argument('--offline', action='store_true',
                        help='use local models')

    parser.add_argument('--debug', action='store_true',
                        help='print debug logs')

    parser.add_argument('--scripture', type=str, default='ramayana',
                        help='The scripture to fetch answers from (default: ramayana)',
                        choices=SCRIPTURE_MAPPING.keys())

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    scripture_info = SCRIPTURE_MAPPING[args.scripture]
    query_engine = get_query_engines(args.scripture, is_offline=args.offline)
    
    if len(sys.argv) < 3:
        print(
            "Usage: python main.py [--offline] 'Why Arjuna was confused?'")
        sys.exit(1)

    query = args.question
    print("Q:", query)

    response = query_engine.query(
        query)
    print("A:", response)
    print(f"\n\nSources: {scripture_info.name}")
    for i, source in enumerate(response.source_nodes):
        print(f"\n\n[{i+1}]:" ,{k:v for k,v in source.node.metadata.items() if k in scripture_info.metadatas_to_display})
        print(source.node.get_content()[:1000], '...')


if __name__ == "__main__":
    main()
