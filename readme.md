# CJ IRIS Watcher

This project consists of a few parts:

* A web scraper to gather data from the [CJ IRIS database](https://www.bpl-orsnapshot.net/PublicInquiry_CJ/EmployeeSearch.aspx)
* A differencing library which compares changes gathered
* A streamlined pipeline for gathering and differencing data
* A web application for displaying and navigating data

My routine is fairly straightforward: I run `pipeline.py` to get the most current data, then I run `flaskapp_v1.py`to view the updated data via localhost.

## To do this yourself

If you decide to try to run this, make sure to change the name of `sample_repo` to just `repo` (trust me, it's easier this way). You should also download the most recent chromedriver [here](https://chromedriver.chromium.org/downloads) instead of using the one included in this repo. It is a mysterious `.exe` file on the internet after all.

`run_scraper.cmd` accesses CJ IRIS. Don't be alarmed, but it may open a window and navigate its links. You can do other stuff while this runs, the program doesn't need browser focus to work.

`run_flaskapp.cmd` compiles the data into a simple web application which can be accessed at `127.0.0.1:5000`. The home page includes an explanation of what you're looking at.

I don't have a requirements.txt or anything like that, so you'll have to configure your environment with Flask, Waitress, and Selenium.

### Web scraper

`bpl_scraper.py` is by far the most heavily-documented module. It should not need to be changed at all. If you want to manually access the scraper module instead of using `pipeline.py`, the method you want is `scrape_all_data`.

### Differencing library

`diffy.py` contains the ORMs used to manage and compare the data gathered by the scraper. The end product is `DiffEntryHistory`, which tracks all changes over the lifespan of the archive. You can access an alternate repository with `DiffEntryHistory.open(directory)`. The directory I use is `repo/diff`.

### The pipeline

`pipeline.py` consists primarily of the `scrape_and_diff_today_from_yesterday` method. If you specify the `directory` parameter you can scrape into an alternate repository.

### The web app

`flaskapp_v1.py` contains the implementation of a simple web application for navigating the data. This **only** works for a repo named `repo`, so if you want to change that you will have to edit this file. But it's just easier to give the repo the proper name in the first place, I promise.
