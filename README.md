# Residential complexes' stat data demo bot

## Demo

To try life demo http://t.me/ResComStatDataDemoBot.

## Description

### Subject area

Each arround consists of a set of residential complexes. It is a logical layer to group some residential complexes for analyzing their stat data between each other.

In this demo, the dumped demo data contains such arrounds and residential complexes respectively:

- AA Group
  - CityMix
  - Innovation
  - Peredelkino Middle
  - Prokshino
  - Rumyantsevo park
  - Salaryevo park
  - Skolkovskiy
  - Stellar City

- BB Group

  - Aquilon Park
  - Flower meadows
  - Maple alleys
  - New Vatutinki
  - New star
  - Rumyantsevo park
  - Scandinavia
  - Spanish quarters

- CC Group

  - Bolshaya Akademicheskaya 85

  - Dmitrovsky park

  - Ilmensky 17

  - Love and Pigeons

  - Seliger City

  - Signal 16

  - Talisman on Dmitrovsky

    

In its turn, the dumped data contains the next information for further analysing:

- `id_custome` - the unique identification of flat
- `rooms_count_title` - the determinator of the number of rooms
- `total_area` - the total area of a flat in м²
- `price` - the price of a flat in ₽
- `price_actual_date` - the date of actualization of the flat price
- `rb_title` - the name of the residential complex that contains this flat



The demo data contains the slice main data from 2020-09-07 to 2020-10-07 for demonstrating purposes.

In this case, 2020-10-07 is the "current" day and 2020-10-06 is the previous.



### Description of stat sections

#### The common statistics

This section provides the differences of measures of flat on the current day relative to the previous day.



#### By the new flats relative to old ones

This section provides the differences of measures of the new flats on the current day relative to the old flats on the current day.

The new flats on the current day are flats that emerge on the current day and do not exist on the previous one.

The old flats on the current day are flats that consistently exist each day in the slice from the current day minus 30 days to the current day.



#### By the old flats

This section provides the differences of measures of the old flats on the current day relative to the old flats on the previous day.

The old flats on the current day are flats that consistently exist each day in the slice from the current day minus 30 days to the current day.

The old flats on the previous day are flats that consistently exist each day in the slice from the previous day minus 30 days to the previous day.



#### By the sold flats relative to old ones

This section provides the differences of measures of the sold flats on the current day relative to the old flats on the current day.

The sold flats on the current day are flats that missing on the current day and exist on the previous one.

The old flats on the current day are flats that consistently exist each day in the slice from the current day minus 30 days to the current day.



## How to run it for tests

### Environment

Tested on:

- Python 3.7.7



### Preparations

To run the app is needed to acquire Telegram bot's token after its creation. [How to do it](https://core.telegram.org/bots#3-how-do-i-create-a-bot).

Download the source and unpack it.

Download [the arch](https://drive.google.com/file/d/11WESd6Oyd0Rm8j1ROTe-HFim7rYF5nRK/view?usp=sharing) (SHA256: E44F01BA71125E270595E2B29D0165F50EF0234CD8B5972D27CA644B9E7AE591) containing dumped data file and unpack ones in `data` folder with source files.

Create Python virtual environment and install dependencies from requirements.txt.

Copy from `configs/settings_blank.conf` to `configs/settings.conf`.

Add Telegram bot's token to `configs/settings.conf` into `token` of `CHAT` section.

### To run the app

To init python virtual environment and run:

```
python app.py
```

To send `/start` to Telegram bot.



## To-do list

- To finish translation in the source code from Russian to English
- To fix bug with empty output. Steps for producing: TR Group ->  By the old flats
- To fulfil description into 'help' for `/help` command
- To add sending technical information such as debug info and exceptions to chat for debugging