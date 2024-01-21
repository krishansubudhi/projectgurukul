import argparse
import logging
import sys
sys.path.append(".")
import dotenv
dotenv.load_dotenv(".env")
from projectgurukul import corelib
from projectgurukul.corelib import (
    SCRIPTURE_MAPPING,
    SYSTEM_PROMPT,
    get_query_engines,
    get_fusion_query_engine_trained_model,
    get_fusion_query_engine)


def main():
    parser = argparse.ArgumentParser(
        description='Process some questions about the Gita.')
    parser.add_argument('--question', metavar='question', type=str,
                        help='the question to process')
    parser.add_argument('--offline', action='store_true',
                        help='use local models')

    parser.add_argument('--debug', action='store_true',
                        help='print debug logs')

    parser.add_argument('--scripture', type=str, default='ramayana,gita',
                        help='The scripture to fetch answers from (default: ramayana)',
                        choices=SCRIPTURE_MAPPING.keys())

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    scriptures  = args.scripture.split(",")
    query_engine = get_fusion_query_engine(scriptures=scriptures, is_offline=args.offline)
    
    if len(sys.argv) < 3:
        print(
            "Usage: python main.py --question 'Why Arjuna was confused?' [--offline] [--debug]")
        sys.exit(1)

    query = args.question
    print("Q:", query)

    response = query_engine.query(
        query)
    
    print("A:", response)
    print(response.metadata)
    print(f"\n\nSources:\n")
    for i, source in enumerate(response.source_nodes):
        scripture_info = corelib.get_scripture_from_source_metadata(source.node.metadata)
        print(f"\n[{i+1}]: {scripture_info.get_reference_string(source.node.metadata)}")
        # print(source.node.get_content()[:300], '...')


if __name__ == "__main__":
    main()
