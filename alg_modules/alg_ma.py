
from collections import namedtuple
import pandas as pd
from pandas.core.frame import DataFrame
import logging

class AlgMa():
    '''Calculate 3 moving average arrays from given dataframe'''
    @staticmethod
    def alg_main(df: DataFrame, MA_list: tuple, **kwargs) -> list[DataFrame, DataFrame, DataFrame]:
        '''Calculate moving average lines'''
        return [df.rolling(window = i).mean() for i in MA_list] 
    # @staticmethod
    # def alg_to_df(data: tuple, MA_1=7, MA_2=25, MA_3=100, **kwargs):

    # calc collisions
    # найти координаты пересечения линий
    @staticmethod
    def find_intersections(date_df: DataFrame, mov_avg1: list, mov_avg2: list,) -> list[namedtuple]:
        '''Find intersection between last 2 given lines'''
        intersections = []
        MA_point = namedtuple('MA_point', 'timestamp val type')
        for num, i in enumerate(date_df):
            # if num == 999: print(num)
            if num == 0: next(enumerate(date_df))
            else:  
                # TODO numba_intersection() calc it faster
                A1 = mov_avg1[num-1]
                A2 = mov_avg1[num] 
                B1 = mov_avg2[num-1]
                B2 = mov_avg2[num] 
                # try:
                if (A1 > B1) and (B2 > A2):
                    intersections.append(MA_point(i, mov_avg1[num], 'fall'))
                    logging.debug(f'Intersection found: {(intersections[-1])}')
                if (A1 < B1) and (B2 < A2):
                    intersections.append(MA_point(i, mov_avg1[num], 'raise'))
                    logging.debug(f'Intersection found: {(intersections[-1])}')
                # except IndexError as e:
                    # logging.debug(e)
        try:
            logging.debug(f'Last intersection: {intersections[-1]}')
        except IndexError as e:
            logging.debug(e)
        return intersections


if __name__ == '__main__':
    from datetime import datetime
    import logging
    DEBUG = __debug__ 
    LOG_FILE_NAME = 'log_file_name.log'
    format = '%(asctime)s [%(levelname)s]: %(message)s'
    logger = logging.basicConfig(
        filename=LOG_FILE_NAME if not DEBUG else None, 
        format=format,
        encoding='utf-8', 
        level=logging.INFO, 
    )
    if not DEBUG:
        logging.getLogger(logger).addHandler(logging.StreamHandler())

    # find MA lines
    from random import randint
    df = pd.DataFrame()
    df['Test'] = [randint(0, 100) for i in range(1000)]
    # print(
    MA_lines = AlgMa.alg_main(df['Test'], MA_list=(7, 25, 100))
    print(MA_lines)
    # find intersections
    df['Time'] = [datetime.fromtimestamp(i*10**6) for i in range(1000)]
    p = AlgMa.find_intersections(df['Time'], MA_lines[1], MA_lines[2])
    # print(p[0])
