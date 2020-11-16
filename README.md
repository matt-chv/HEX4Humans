# Hex4Humans
Convert register dumps in hex format to html including bitfield values and meanings.

Relies on:
* Register map in csv format (see below details).
* Register dump in csv format (see below details).
* python 3+

Generates html file with following features:
* register and bitfield definitions from the map file.
* bitfield values from dump file.
* ability in the html file to hide/show bitfields with values equal to reset values.
* ability in the html file to hide/show bitfields with values equal between different dumps.

## OVERVIEW

| Address | Bit Field Range | Bit Field Enumerations | Bit Field Reset Value | REGISTER from: dump.csv | Meaning |
0x000F: Reserved 	0x0000 	0x003E 	0x0003 	AINP = AIN1, AINN = AIN2
0x0000| 7..4 	| <ul><li>0x0000: AINP = AIN0, AINN = AIN1 (default)</li><li>0x0001: AINP = AIN0, AINN = AIN2</li><li>0x0002: AINP = AIN0, AINN = AIN3</li><li>0x0003: AINP = AIN1, AINN = AIN2</li><li>0x0004: AINP = AIN1, AINN = AIN3</li><li>...</li></ul> | 0x003E | 0x0003 | AINP = AIN1, AINN = AIN2 |
| ... | ... | ... | ... | ... | ... |

## Installation and usage

## USAGE

to display help message
```bash
python Hex4Humans -h 
```

to decipher a register dump and/or compare against reset values, use a single dump file:
```bash
python Hex4Humans.py -m map_ads1220.csv -d dump_ads1220_table22.csv -o ads1220_table22.htm
```

to compare different register dumps to one another and/or reset values, specify multiple dump files:

```bash
python Hex4Humans.py -m map_ads1220.csv -d dump_ads1220_table22.csv dump_ads1220_table24.csv -o ads1220_table22_24.htm
```

## Generic considerations about HEX4Humans

### Register Map 

Register Map is a unique file per device which defines the register mapping, the bitfield definitions and bitfield enumerations.

#### Key specification and considerations:

* csv format 
* UTF-8 encoded
* all relevant values are coded in hexa with 4 digits, upper case, preceeded by 0x
* Bit Field Name should be **where possible** a unique identifier for a featureset to allow comparing across multiple devices (more details to come later)
* `Bit Field Description` should contain the feature description and required explanation to be self-standing (no need to open another document)
* `Bit Field Enumerations` should be a pure list of different values that the bit field can be. For large enumeration (organisation ID, ADC values, ...) a code will be added to handle this. 

#### Example #1 - ADS1220

see `map_ads1220.csv` for full details

|Register Long Name|Register Short Name|Register Page|Register Address|Bit Field Number|Bit Field Name|Bit Field Reset Value|Bit Field Access|Bit Field Description|Bit Field Enumerations|
|------------------|-------------------|-------------|----------------|----------------|--------------|---------------------|----------------|---------------------|----------------------|
|Configuration Register 0|CONF0|0x0000|0x0000|7..4|MUX[3:0]|0x0000|R/W|Input multiplexer configuration|<ul><li>0x0000:  AINP = AIN0, AINN = AIN1 (default)</li><li>0x0001:  AINP = AIN0, AINN = AIN2</li><li>0x0002:  AINP = AIN0, AINN = AIN3</li><li>0x0003:  AINP = AIN1, AINN = AIN2</li><li>0x0004:  AINP = AIN1, AINN = AIN3</li><li>0x0005:  AINP = AIN2, AINN = AIN3</li><li>0x0006:  AINP = AIN1, AINN = AIN0</li><li>0x0007:  AINP = AIN3, AINN = AIN2</li><li>0x0008:  AINP = AIN0, AINN = AVSS</li><li>0x0009:  AINP = AIN1, AINN = AVSS</li><li>0x000A:  AINP = AIN2, AINN = AVSS</li><li>0x000B:  AINP = AIN3, AINN = AVSS</li><li>0x000C:  (V(REFPx) - V(REFNx)) / 4 monitor (PGA bypassed)</li><li>0x000D:  (AVDD - AVSS) / 4 monitor (PGA bypassed)</li><li>0x000E:  AINP and AINN shorted to (AVDD + AVSS) / 2</li><li>0x000F:  Reserved</li></ul> |
| ...              |... |...|...|...|...|...|...|    ...   |   ... |


#### Example #2: DP83822

see `map_dp83822.csv` for full details

| Register Long Name|Register Short Name|Register Page|Register Address|Bit Field Number|Bit Field Name|Bit Field Reset Value|Bit Field Description|Bit Field Enumerations|
|-------------------|-------------------|-------------|----------------|----------------|----------|---------------------|---------------------|----------------------|
| Control|CTRL|0x0000|0x0000|15|Reset|0x0001|"PHY Software Reset: Writing a 1 to this bit resets the PHY PCS registers. When the reset operation is completed, this bit is cleared to 0 automatically. PHY Vendor Specific registers will not be cleared." | <ul><li>0x0001: "Initiate software Reset / Reset in Progress"</li><li>0x0000: "Normal Operation"</li></ul>|

### Register Dumps

Register Dumps are generated during development/debug to allow closing the gap between expected IC behaviour and observed behaviour.

Following examples illustrate how a dump file should look like and how to generate the HEX4Humans html output.


#### Example #1 - ADS1220 table 22
 
 > running against [table 22 in datasheet](https://www.ti.com/document-viewer/ADS1220/datasheet/application_and_implementation#SBAS6834877), see file dump_ads1220_table22.csv in repository
 
|Register Address|Register Value|
|----------------|--------------|
|          0x0000|0x000A        |
|          0x0001|0x0004        |
|          0x0002|0x0010        |
|          0x0003|0x0000        |

to have the HEX4Humans output, type in console:

```bash
python Hex4Humans.py -d dump_ads1220_table22.csv -m map_ads1220.csv -o ads1220_table22.htm
```


#### Example #2 - ADS1220 table 24

> running against table 24 in [datasheet](https://www.ti.com/document-viewer/ADS1220/datasheet/application_and_implementation#SBAS6831374), see file see file dump_ads1220_table24.csv in repository

|Register Address|Register Value|
|----------------|--------------|
|          0x0000|0x0066        |
|          0x0001|0x0004        |
|          0x0002|0x0055        |
|          0x0003|0x0070        |

to have the HEX4Humans output, type in console:

```bash
python Hex4Humans.py -d dump_ads1220_table24.csv -m map_ads1220.csv -o ads1220_table24.htm
```


#### Example #3 - ADS1220 table 26

> running against table 26 in [datasheet](https://www.ti.com/document-viewer/ADS1220/datasheet/application_and_implementation#SBAS6839005), see file see file dump_ads1220_table24.csv in repository

|Register Address|Register Value|
|----------------|--------------|
|          0x0000|0x003E        |
|          0x0001|0x0004        |
|          0x0002|0x0098        |
|          0x0003|0x0000        |

to have the HEX4Humans output, type in console:

```bash
python Hex4Humans.py -d dump_ads1220_table26.csv -m map_ads1220.csv -o ads1220_table26.htm
```

### Example #4 - DP83822 debug 

see dump822_20201029.csv for full details

| Register Address|Register Value|
|-----------------|--------------|
|0x0000           |0x3800        |
|...              |...           |

to have the HEX4Humans output, type in console:

```bash
python Hex4Humans.py -d dump822_20201029.csv -m map_dp83822.csv -o 822_20201029.htm
```

