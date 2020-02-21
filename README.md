# GSoC Scraper

## Quick setup
```shell script
virtualenv env
source env/bin/activate
pip install -r requirements.txt
cd stat_scraper/stat_scraper
scrapy crawl orgs
# Wait for scraping to complete
```

This generates a sqlite database file. Run your queries against this file to fetch required stats.

## DB Schema
`org` table:

    name: char

`projectcount` table:
    
    org_id: foreignkey(org)
    year: int
    count: int