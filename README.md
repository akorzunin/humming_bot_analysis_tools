# humming_bot_analysis_tools

Provides a set of data analysis tools for humming bot instances

## Insatllation

- Install dependencies
    `python -m pip install -r requirements.txt`
- Configure env files
  - Create `.env` file to use api keys in python files

        ```sh
        TOKEN=
        BINANCE_API_KEY=
        BINANCE_SECRET_KEY=
        PWD=
        LOCAL_FOLDER=
        ```

        `TOKEN` - telegram bot token (optional)
        `PWD` - Windows path to directory (looks like `C:\Users\`)
        `LOCAL_FOLDER` - wsl path to directory (looks like `/mnt/c/Users`)
  - Create `.env.sh` file to use sh scripts and access host over ssh

        ```sh
        export HUMMINGBOT_HOST_USER=
        export HUMMINGBOT_HOST_IP=
        export HUMMINGBOT_HOST_LOCATION="/home/akorz/Documents/humming_bot"
        export LOCAL_FOLDER="/mnt/c/Users/akorz/Documents/humming_bot_analysis_tools"
        ```

        `HUMMINGBOT_HOST_LOCATION` - path to directory w/ humming bot instances (example `"/home/"`)

        `LOCAL_FOLDER` - same as LOCAL_FOLDER in .env file

## Usage

### Manage humming bot files

- Copy all files fron defined `bot_instances` to /temp directory
    `python ./humming_bot_maintenance/modules/manage_bot_over_ssh.py --copy`

- Generate config files for all `bot_instances` into /generated_configs folder
    `python ./humming_bot_maintenance/modules/config_manager.py`

- Send generated configs to all `bot_instances`
    `python ./humming_bot_maintenance/modules/manage_bot_over_ssh.py --send`

### Plots

With  [log_to_plot_tool_.ipynb](https://github.com/akorzunin/humming_bot_analysis_tools/blob/main/humming_bot_maintenance/log_to_plot_tool.ipynb) you can plot trade data from bot instances

Data would be displayed in IPython widgets:

- Dataframe with values from each bot

    ![image](https://user-images.githubusercontent.com/54314123/181363421-713e7756-0ffc-482a-b325-9409894a8a95.png)

- Plot with all trades for each bot
    ![image](https://user-images.githubusercontent.com/54314123/181363758-fbdd2781-4e71-401b-8025-0c9e5859dfa1.png)

  - Yellow bar means that order was canceled
  - Green bar means that order sell order was filled
  - Red bar means that order buy order was filled

- Plot with profitability of each bot over time
    ![image](https://user-images.githubusercontent.com/54314123/181363966-e5b86b37-841a-4a42-9a32-ed672443215a.png)

  - Global: profit relative to initial state
  - Prev: profit relative to previous filled order

### Connection analysis

[connection_analysis.ipynb](https://github.com/akorzunin/humming_bot_analysis_tools/blob/main/utils/connection_analysis.ipynb)
Provides utility to measure weight of current connection to binance api

Read more about binance weight limit [here](https://dev.binance.vision/t/request-limit-on-the-api-endpoints/9275)
![newplot](https://user-images.githubusercontent.com/54314123/181340072-7151db46-7a20-4f1b-95d1-3552bb6fd6c0.png)

### Profit range

[profit_range.ipynb](https://github.com/akorzunin/humming_bot_analysis_tools/blob/main/utils/profit_range.ipynb)
Interactive widget calulator

- Widget 1: calculate fee amount and minimal profit range with geven amount of currency and price
![image](https://user-images.githubusercontent.com/54314123/181341645-503e8071-5307-4f8b-8212-65aa69616519.png)

- Widget 2: calculate sell/buy trade based on geven spread, price and amount
![image](https://user-images.githubusercontent.com/54314123/181341858-fb80e7e6-a3f6-47ea-9be5-7a6dac2693cf.png)

## License

Humming bot analysis tools is free and open-source software licensed under the [Apache 2.0 License](https://github.com/akorzunin/humming_bot_analysis_tools/blob/main/LICENSE).
