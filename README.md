# Workout Scraper

A collection of Webcrawler that scrape data from [ErgDB](https://ergdb.org/) and
[What On Zwift](https://whatsonzwift.com/)

## Prerequisite

```
    pip install scrapy
```

## Scrape Data

```
    scrapy runspider ergdbspider.py -o ergdb.json -L INFO
```

## Parse Spider Output

The following command will create a directory with the name given with the parameter ``-O``
and parse the data from the JSON file into MRC files.
With the optional command ``--WipeFile`` an empty MRC and PLAN file is created to delete
unwanted workouts from a Wahoo Unit or from the Wahoo App.

```
    python MRCFile.py -I ergdb.json -O ergdb
```
