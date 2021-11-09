from flask import Flask, render_template, send_from_directory
from diffy import EntryList, DiffEntryList
from pipeline import scrape_and_diff_today_from_yesterday
from waitress import serve

import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Legacy additions - cache for /legacy
el_adds_0 = EntryList.open("repo/added/20190202-20200625+.tsv").data
el_adds_1 = EntryList.open("repo/added/20200625-20211101+.tsv").data

# Legacy removals - cache for /legacy
el_rms_0 = EntryList.open("repo/removed/20190202-20200625-.tsv").data
el_rms_1 = EntryList.open("repo/removed/20200625-20211101-.tsv").data

# Cache for difference files
cache = {}


def construct_filename(today, yesterday):
    return f"repo/diff/{yesterday}-{today}.tsv"


def today_yesterday_tomorrow(today):
    yesterday = (datetime.strptime(today, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    tomorrow = (datetime.strptime(today, "%Y%m%d") + timedelta(days=1)).strftime("%Y%m%d")

    return [today, yesterday, tomorrow]


def construct_template(today):
    tyt = today_yesterday_tomorrow(today)
    filename = construct_filename(tyt[0], tyt[1])
    if filename in cache:
        print(f"Accessing {filename} from cache")
        diff_list = cache[filename]
    else:
        print(f"Accessing {filename} for the first time")
        diff_list = DiffEntryList.open(filename)
        cache[filename] = diff_list

    added = diff_list.added()
    removed = diff_list.removed()

    return render_template(
        "index.html",
        today=tyt[0],
        yesterday=tyt[1],
        tomorrow=tyt[2],
        added=added,
        removed=removed
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static"), "favicon.ico", mimetype='image/vnd.microsoft.icon')


@app.route("/")
def front_page():
    today = datetime.today().strftime("%Y%m%d")
    tyt = today_yesterday_tomorrow(today)
    filename = construct_filename(tyt[0], tyt[1])
    if os.path.exists(filename):
        print(f"{filename} exists")
        return construct_template(today)
    else:
        print(f"{filename} does not exist")
        scrape_and_diff_today_from_yesterday()
        return construct_template(today)


@app.route("/<datecode>")
def go_to_page(datecode):
    tyt = today_yesterday_tomorrow(datecode)

    filename = construct_filename(tyt[0], tyt[1])
    if os.path.exists(filename):
        print(f"{filename} exists")
        return construct_template(datecode)
    else:
        print(f"{filename} does not exist")

        return render_template(
            "no-diff.html",
            today=tyt[0],
            yesterday=tyt[1],
            tomorrow=tyt[2]
        )


@app.route("/legacy")
def legacy_portal():
    return render_template(
        "legacy.html",
        adds0=el_adds_0,
        adds1=el_adds_1,
        rms0=el_rms_0,
        rms1=el_rms_1
    )


if __name__ == "__main__":
    print("Serving PPB Watcher")
    serve(app, listen="*:5000")
