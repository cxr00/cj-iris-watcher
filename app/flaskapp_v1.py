from flask import Flask, render_template, send_from_directory, request
from diffy import EntryList, DiffEntryHistory, DiffEntryList

import os
from datetime import datetime
from waitress import serve

app = Flask(__name__)

print("Loading legacy data sets...")

# Legacy additions
el_adds_0 = EntryList.open("repo/legacy/added/20190202-20200625+.tsv").data
el_adds_1 = EntryList.open("repo/legacy/added/20200625-20211101+.tsv").data

# Legacy removals
el_rms_0 = EntryList.open("repo/legacy/removed/20190202-20200625-.tsv").data
el_rms_1 = EntryList.open("repo/legacy/removed/20200625-20211101-.tsv").data

print("Load complete.")
print("Loading primary DiffEntryHistory...")

diff_eh = DiffEntryHistory.open("repo/diff")

count = diff_eh.count_presence()

print("Load complete.")


def construct_template(today):
    ind = diff_eh.meta.index(today)

    # Determine value of yesterday for button functionality
    if ind != 0:
        yesterday = diff_eh.meta[ind - 1]
    else:
        yesterday = today

    # Determine value of tomorrow for button functionality
    if ind != len(diff_eh.meta) - 1:
        tomorrow = diff_eh.meta[ind + 1]
    else:
        tomorrow = today

    if ind == 0:
        added = DiffEntryList()
        removed = DiffEntryList()
    else:
        diff_list = diff_eh.data[ind - 1]

        added = diff_list.added()
        removed = diff_list.removed()

    return render_template(
        "index.html",
        today=today,
        yesterday=yesterday,
        tomorrow=tomorrow,
        added=added,
        removed=removed
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static"), "favicon.ico", mimetype='image/vnd.microsoft.icon')


@app.route("/")
def front_page():
    return render_template(
        "summary.html",
        entries=count,
        today=diff_eh.meta[-1]
    )


@app.route("/<datecode>")
def go_to_page(datecode):
    return construct_template(datecode)


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
    print("Serving CJ IRIS Watcher")
    serve(app, host="0.0.0.0", port=5000)
