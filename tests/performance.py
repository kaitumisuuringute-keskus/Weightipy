import time

import pandas as pd

from weightipy import weight_dataframe, weighting_efficiency
from weightipy.rim import Rim
from weightipy.weight_engine import WeightEngine

"""
Performance:
0.3.2 - 0.3980s
0.3.3 - 0.0336s
"""


class PerformanceTest:
    def __init__(self):
        self.path = ''
        self.scheme_name_A2 = 'scheme_name_A2'

        name_data_A = 'engine_A'
        self.path_data_A = '{}{}_data.csv'.format(self.path, name_data_A)

        name_data_B = 'engine_B'
        self.path_meta_B = '{}{}_meta.json'.format(self.path, name_data_B)
        self.path_data_B = '{}{}_data.csv'.format(self.path, name_data_B)

        name_data_exA = 'Example Data (A)'
        self.path_meta_exA = '{}{}.json'.format(self.path, name_data_exA)
        self.path_data_exA = '{}{}.csv'.format(self.path, name_data_exA)

        # Setup engine_A
        data = pd.read_csv(self.path_data_A)
        self.engine_A = WeightEngine(data=data)

        # Setup engine_A
        data = pd.read_csv(self.path_data_A)
        self.engine_A = WeightEngine(data=data)


        self.scheme_A2 = Rim(self.scheme_name_A2)
        self.scheme_A2.target_cols = ['column1', 'column2']
        self.scheme_A2.add_group(name='Senior Type 1', filter_def='column3==1',
                                 targets=[
                                     {'column1': {code: prop for code, prop
                                                  in enumerate([37.00, 32.00, 31.00], start=1)}},
                                     {'column2': {code: prop for code, prop
                                                  in enumerate([13.3, 23.13, 14.32, 4.78, 4.70,
                                                                2.65, 2.61, 3.47, 31.04], start=1)}}
                                 ])
        self.scheme_A2.add_group(name='Senior Type 2', filter_def='column3==1',
                                 targets=[
                                     {'column1': {code: prop for code, prop
                                                  in enumerate([33.2, 33.40, 33.40], start=1)}},
                                     {'column2': {code: prop for code, prop
                                                  in enumerate([11.11, 11.11, 11.11, 11.11, 11.11,
                                                                11.11, 11.11, 11.11, 11.12], start=1)}}
                                 ])
        self.scheme_A2.add_group(name='Senior Type 3', filter_def='column3==3',
                                 targets=[
                                     {'column1': {code: prop for code, prop
                                                  in enumerate([37.1, 33.2, 29.7], start=1)}},
                                     {'column2': {code: prop for code, prop
                                                  in enumerate([13.3, 23.13, 14.32, 4.78, 4.70,
                                                                2.65, 2.61, 3.47, 31.04], start=1)}}
                                 ])
        self.scheme_A2.add_group(name='Senior Type 4', filter_def='column3==4',
                                 targets=[
                                     {'column1': {code: prop for code, prop
                                                  in enumerate([37.1, 33.2, 29.7], start=1)}},
                                     {'column2': {code: prop for code, prop
                                                  in enumerate([12.00, 23.13, 14.32, 4.78, 4.70,
                                                                2.65, 2.61, 3.47, 32.34], start=1)}}
                                 ])

    def run_performance_test(self):
        df = self.engine_A._df

        # measure perf
        samples = 10
        time_start = time.time()

        for i in range(samples):
            weight_dataframe(df, self.scheme_A2, "weights_")

        time_end = time.time()
        time_sample = (time_end - time_start) / samples

        # print seconds
        print("Time per sample: {}s".format(time_sample))


if __name__ == '__main__':
    PerformanceTest().run_performance_test()

