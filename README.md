# Hex4Humans
Convert register dumps in hex format to html including bitfield values and meanings.

Relies on:
* Register map in csv format (see below details)
* Register dump in csv format (see below details)

## Installation and usage

### USAGE

to display help message
```bash
python Hex4Humans -h 
```

to produce a nice html output
```bash
python Hex4Humans.py -m map822.csv -d dump822_20201029.csv -o out.htm
```

## Register Map 
csv format 

### Example #1: 802.3 clause 22

| Register Long Name|Register Short Name|Register Page|Register Address|Bit Field Number|Bit Field Name|Bit Field Reset Value|Bit Field Description|Bit Field Enumerations|
|-------------------|-------------------|-------------|----------------|----------------|----------|---------------------|---------------------|----------------------|
| Control|CTRL|0|0x0000|15|Reset|1b0|"PHY Software Reset: Writing a 1 to this bit resets the PHY PCS registers. When the reset operation is completed, this bit is cleared to 0 automatically. PHY Vendor Specific registers will not be cleared." | 1h = "Initiate software Reset / Reset in Progress" 0h = "Normal Operation"|

### Example #2 - ADS1220
Coming

## Register Dumps

### Example #1 - 802.3 clause 22
see 802.3_claus22_reset_dump.csv for full details

| Register Address|Register Value|
|-----------------|--------------|
|0x0000           |0x3100        |
