import ruamel.yaml
from datetime import datetime, timedelta
import pytz
import os
import math
tzdata_bot = pytz.timezone('UTC') 
tzdata_local = pytz.timezone('Europe/Moscow') 
yaml = ruamel.yaml.YAML()

def create_config_file(template_path: str, config_path: str, new_data: dict=None):
    # read template
    with open(template_path, 'r') as f:
        data = yaml.load(f)
    # write new data to tamplate based object
    if new_data is not None:
        for k, v in new_data.items(): 
            data[k] = v
    # save file
    with open(config_path, 'w+') as f:
        yaml.dump(data, f)
    return data

def get_dates_daily(start_hour: int, ) -> dict:
    start_date = datetime.now()\
        .replace(
            hour=start_hour,
            minute=0,
            second=0, 
            microsecond=0,
        )
    assert start_date > datetime.now()
    # change time zone to humming bot default and make dateime naive
    start_date_bot_naive = tzdata_local\
        .localize(start_date)\
        .astimezone(tzdata_bot)\
        .replace(tzinfo=None)

    return dict(
        start_time=str(start_date_bot_naive),
        end_time=str(start_date_bot_naive + timedelta(days=1)),
    )

def get_log_range(min_val: int, max_val: int, number_of_steps: int):
    def remap(x: float, max_val: float, min_val: float, out_min: float, out_max: float ):
        return (x - min_val) * (out_max - out_min) / (max_val - min_val) + out_min
    log_list = [math.log(i, 10) for i in range(10, 100, int((100-10)/number_of_steps))]
    return [int(remap(i, max(log_list), min(log_list), min_val, max_val)) for i in log_list]

def create_config_structure(strat_name: str, instances: list, dates: dict, swap_param: dict):
    swap_param_names = list(swap_param)
    new_data = {}
    for num, i in enumerate(instances):
        # add key val pairs to config
        for name in swap_param_names:
            new_data |= {name: swap_param[name][num]}

        # add start and end date to strat config files
        new_data |= dates
        # create directory for new config if its not existed
        os.makedirs(f'./humming_bot_maintenance/generated_configs/{i}/', exist_ok=1)
        # create strategy config for each bot from tamplate but replace new_data
        conf_strat = create_config_file(
            template_path='./humming_bot_maintenance/templates/conf_avellaneda_market_making_1.yml',
            config_path=f'./humming_bot_maintenance/generated_configs/{i}/conf_{strat_name}_{swap_param_names[0]}_{new_data[swap_param_names[0]]}.yml',
            new_data=new_data,
        )
        # create global config for each bot from tamplate but replace new_data
        conf_global = create_config_file(
            template_path='./humming_bot_maintenance/templates/conf_global.yml',
            config_path=f'./humming_bot_maintenance/generated_configs/{i}/conf_global.yml',
            new_data=None,
        )


if __name__ == '__main__':
    from manage_bot_over_ssh import send_files_to_bot
    # from humming_bot_maintenance.bot_instances import instances
    instances = [
        'humming_bot_1',
        'humming_bot_2',
        'humming_bot_3',
        'humming_bot_4',
        'humming_bot_5',
    ]

    STRAT_NAME = 'pure_mm_1'
    START_HOUR = 13
    
    
    create_config_structure(
        strat_name=STRAT_NAME, 
        instances=instances, 
        dates=get_dates_daily(START_HOUR),
        swap_param=dict(
            # filled_order_delay=get_log_range(60 ,1800, 5)
            # risk_factor= [1, 10, 100, 1000, 10000]
        ),
    )
    print('Configs created')

    # send configs to bots
    send_files_to_bot(instances, 'all')
    


