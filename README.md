# kena-arrow
Automated issue management for GitHub

## Features

* Mass-create issues for a given list of users

## Set-up/First Time

1. Install python (and maybe virtualenv + setup)
1. Install required dependencies using `pip` (viz. `pip install -r requirements.txt`)
1. Create + configure a `config.cfg` file. Use `config.sample.cfg` as a starting point.

## Using the program

The program is CLI-based. Entry point of this application is `main.py`.

You can determine the input parameters by executing the following command:

```bash
$ python main.py -h
```

Generally speaking, two input files are required:

1. A CSV file -- each row holds a user <-> issue label pair
1. A Markdown file -- contains the body of the issue to be blasted out

You can use the example files located in the `example` folder as a reference.

## Troubleshooting

All log entries for this program is stored in `log.log` on the root directory
(i.e. where `main.py` resides)
