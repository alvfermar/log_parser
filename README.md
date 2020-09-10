# Log file analytics

This small script takes a text file of your choice (which is assumed to be in your current directory) and perform some analytics (as well of your choice) on it. It is assumed the structure of the log files is the [combined log format](https://httpd.apache.org/docs/2.4/logs.html). Requirements to make this work are in the log_requirements.txt file, which was created from the Conda environment used to make this technical test. Bear in mind Jupyter Lab and its dependencies were used for this purpose so they are not strictly necessary to run this project, you could get rid of those packages.

## Usage examples

Given we are in the directory where the "log_parser.py" and the text file "damavis.log" are placed, we could get the 10 most common requests like
```
python log_parser.py TOP_10_PAGES damavis.log
```
It basically admits the report_code (TOP_10_PAGES) and filename parameters. In case we want to show the PER_MIN (count of requests made every minute to the server) we could use the --time_to and --time_to parameters as well, like this:
```
python log_parser.py PER_MIN damavis.log --time_from='2020-02-07 00:00' --time_to='2020-02-07 00:30'
```

## Report list

List of available reports:

* **TOP_10_PAGES:** Top 10 pages most commonly requested
* **PERC_OK:** % of successful requests
* **PERC_BAD:** % of unsuccessful requests
* **TOP_10_BAD:** most commonly failed requests
* **TOP_10_IPS:** Top 10 IP which made more requests
* **TOP_IPS_PAGES:** 5 most common requests for each of the top 10 IPs 
* **PER_MIN:** Per minute count of requests of the period considered in the file, it is possible to determine the period you want to see
