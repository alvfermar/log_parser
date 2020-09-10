import re
import pandas as pd
import argparse

REPORT_LIST = [
    'TOP_10_PAGES',
    'PERC_OK',
    'PERC_BAD',
    'TOP_10_BAD',
    'TOP_10_IPS',
    'TOP_IPS_PAGES',
    'PER_MIN'
]

class log_report():
  
    def __init__(self, filename):
        self.reg = r'\d+.\d+.\d+.\d+.|\[.*\]|\".*?\"|\d+ \d+'
        self.filename = filename

    def prepare_log_df(self):
        with open(self.filename, 'r') as file:
            lines = file.read().splitlines()
        lines_df = []
        for line in lines:
            lines_df.append(re.findall(self.reg, line))
        log_df = pd.DataFrame(lines_df, columns=['ip', 'timestamp', 'request', 'response_size', 
                                                 'referring_site', 'user_agent'])
        log_df = pd.concat([log_df, log_df.response_size.str.strip().str.split(' ', expand=True)], axis=1)
        log_df = log_df.drop(columns='response_size').\
            set_axis(['ip', 'timestamp', 'request', 'referring_site', 
                      'user_agent', 'response_code', 'response_size'], axis=1)
        log_df.timestamp = pd.to_datetime(log_df.timestamp, format='[%d/%b/%Y:%H:%M:%S %z]')
        log_df.response_code = pd.to_numeric(log_df.response_code, downcast='unsigned')
        log_df.response_size = pd.to_numeric(log_df.response_size, downcast='unsigned')
        return log_df
    
    def same_pattern(self):
        '''
        Checks if all the lines in th file follow the same 
        pattern by checking the produced list after re.findall
        has the same length in all hte cases
        '''
        with open(self.filename, 'r') as file:
            lines = file.read().splitlines()
        same_length = []
        for line in lines:
            same_length.append(re.findall(self.reg, line))
            assert all([len(l) == len(same_length[0]) for l in same_length]), 'Not all the lines have the same pattern, '
            'please revise your splitting criteria'

    def produce_report(self, log_df, report_code, time_from_arg=None, time_to_arg=None):
        if report_code == 'TOP_10_PAGES':
            # Top 10 requested pages and number of made requests for each one
            report = log_df.groupby('request', as_index=False).size().reset_index(name='count').\
                sort_values(by='count', ascending=False).head(10).reset_index(drop=True)
            assert len(report) == 10, 'The report has a length different than 10, please revise its generation'
            print(report)
        elif report_code == 'PERC_OK':
            # Percentage of successful requests (anything in the 200s and 300s range)
            report = len(log_df[(log_df.response_code >= 200) & (log_df.response_code < 400)]) / len(log_df)
            print(f'The rate of successful requests is {report * 100:.2f}%')
        elif report_code == 'PERC_BAD':
            # Percentage of unsuccessful requests (anything that is not in the 200s or 300s range)
            report = len(log_df[~((log_df.response_code >= 200) & (log_df.response_code < 400))]) / len(log_df)
            print(f'The rate of unsuccessful requests is {report * 100:.2f}%')
        elif report_code == 'TOP_10_BAD':
            # Top 10 unsuccessful page requests
            report = log_df[~((log_df.response_code >= 200) & (log_df.response_code < 400))].groupby('request', as_index=False).size().\
                reset_index(name='count').sort_values(by='count', ascending=False).head(10).reset_index(drop=True)
            assert len(report) == 10, 'The report has a length different than 10, please revise its generation'
            print(report)
        elif report_code == 'TOP_10_IPS':
            # The top 10 IPs making the largest number of requests. Please, display the IP address and the number of made requests.
            report = log_df.groupby('ip', as_index=False).size().reset_index(name='count').\
                sort_values(by='count', ascending=False).head(10).reset_index(drop=True)
            assert len(report) == 10, 'The report has a length different than 10, please revise its generation'
            print(report)
        elif report_code == 'TOP_IPS_PAGES':
            # For each of the top 10 IPs, show the top 5 pages requested and the number of requests for each one.
            top_10_ips = log_df.groupby('ip', as_index=False).size().reset_index(name='count').\
                sort_values(by='count', ascending=False).head(10).reset_index(drop=True)
            report = log_df[log_df.ip.isin(top_10_ips.ip)].groupby(['ip', 'request'], as_index=False).size().reset_index(name='count').\
                sort_values(by=['ip', 'count']).groupby('ip', as_index=False).head(5).reset_index(drop=True)
            assert all(report.groupby('ip').size() == 5), "Some IPs include more than 5 pages, please revise the report generation"
            print(report)
        elif report_code == 'PER_MIN':
            # Total number of made requests every minute in the entire time period covered by the provided file.
            report = log_df.set_index('timestamp').groupby(pd.Grouper(freq='60s')).size().reset_index(name='count').set_index('timestamp')
            time_from = report.index.min() if time_from_arg is None else time_from_arg
            time_to = report.index.max() if time_to_arg is None else time_to_arg
            print(report[time_from:time_to])
        else:
            print(f'Please ask for a valid report from {REPORT_LIST}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("report_code", 
                        help=f"The report you want to display from {REPORT_LIST}")
    parser.add_argument("filename", 
                        help="The file you want reports from, it is assumed to be in"
                        "the same directory as the .py file")
    parser.add_argument("--time_from", 
                        help="Initial time when asking for 'PER_MIN' report, otherwise "
                        "it will be the report initial value. Format is d-m-Y H:M",
                        metavar='')
    parser.add_argument("--time_to", 
                        help="Final time (inclusive) when asking for 'PER_MIN' report, otherwise "
                        "it will be report last value. Format is d-m-Y H:M",
                        metavar='')
    args = parser.parse_args()
    report = log_report(args.filename)
    report.same_pattern()
    log_df = report.prepare_log_df()
    report.produce_report(log_df, args.report_code, args.time_from, args.time_to)
