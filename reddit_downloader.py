from psaw import PushshiftAPI
import json
from itertools import count
import logging
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("subreddit", help="Subreddit name", type=str)
parser.add_argument(
    "mode", help="Select which record type to download", choices=["posts", "comments"]
)
parser.add_argument(
    "-o",
    "--output-preffix",
    help="Preffix of downloaded files",
    default="records_",
    dest="preffix",
)
parser.add_argument(
    "-v", "--verbose", help="Increase output verbosity", action="store_true"
)
parser.add_argument(
    "-n",
    "--records-per-file",
    help="Number of records per file",
    default=10000,
    type=int,
    dest="nrecords",
)
args = parser.parse_args()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG if args.verbose else logging.INFO
)


# Selecting different psaw function depending on value of mode:
api = PushshiftAPI()
action_map = {"posts": api.search_submissions, "comments": api.search_comments}


def download_records(mode, subreddit):
    gen = action_map[mode](subreddit=subreddit)
    return gen

#Create generator to get all records:
gen = download_records(args.mode, args.subreddit)

cache = []
filename = (f"{args.preffix}%04i.json" % i for i in count(1))
counter = (i for i in count(1))

for c in gen:
    logging.debug(f"Record num {next(counter)}")
    cache.append(c.d_)

    if len(cache) == args.nrecords:
        name = next(filename)

        logging.info(f"Writing file: {name}")
        with open(name, "w") as f:
            json.dump(cache, f, indent=4)

        logging.info(f"Emptying record cache, size = {sys.getsizeof(cache)}")
        del cache[:]
        # break
