# Facebook Status Scraper
Scrapes/crawls/culls a Facebook handle's **statuses** as well as each status' **comments** and each comment's **replies**.

### Usage:

##### For example, to crawl Facebook posts from ``leehsienloong`` starting from ``2015-09-01`` to ``2015-09-12``:
```bash
$ python FacebookStatusScraper.py -p leehsienloong -s 2015-09-01 -e 2015-09-12
```

##### In general:
```bash
$ python FacebookStatusScraper.py -p <facebook_id> -a <your fb app_id> -t <your fb app_secret> -s <start-date> -e <end-date> -S <use-simple-mode>
```

##### Or launch the *HELP*:
```bash
$ python FacebookStatusScraper.py -h
```

##### BTW, you should get your own ``app_id`` and ``app_secret`` from [https://developers.facebook.com/apps/](https://developers.facebook.com/apps/ "Facebook for Developers").

### Output:

##### The script outputs a CSV of the Facebook Handle (in the *output* folder).
- Check out [this sample output](https://github.com/jovianlin/facebook-status-scraper/blob/master/output/mokyingren_2016-01-18_210427_fb_page_feed.csv "mokyingren sample output") from the Facebook page of Mok Ying Ren \(``mokyingren``\). It's the "normal mode" scrape that contains (i) the comments to his posts and (ii) the replies to the comments.
- "Simple Mode" basically excludes the the comments and replies, retaining only the status post and its related metadata. See this "simple mode" [sample](https://github.com/jovianlin/facebook-status-scraper/blob/master/output/leehsienloong_2016-01-18_210825_fb_page_feed_SIMPLE_MODE.csv) of Lee Hsien Loong's Facebook posts.
 
### More Examples can be found from the ``.ipynb`` files:
- [Example 1](https://github.com/jovianlin/facebook-status-scraper/blob/master/example-1-crawl-statuses-only.ipynb)
- [Example 2](https://github.com/jovianlin/facebook-status-scraper/blob/master/example-2-crawl-statuses-comments-and-replies.ipynb)
- [Example 3](https://github.com/jovianlin/facebook-status-scraper/blob/master/example-3-crawl-from-a-list-of-status-ids.ipynb)
