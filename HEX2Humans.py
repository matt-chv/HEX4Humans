""" take a register dump and return a human readable bit-field wise meaning of the register dump 
Also allows to compare two register dumps to highlight in human readable way the differences
v0.0.1a (2020-09-17): generates fixed address reports in csv and htm
    expects 
    1) csv table with following columns:
        REG_ADD: str (the address of the register (prefixed by 0x))
        BF_NUMBER: int or str
            int: the bit position of the given bit-field
            str: two int separated by a '-' minus sign to indicate a range of bit positions e.g. 6-4 is bit 6 to bit 4 included
        BF_NAME: str (the name of the bit field)
        BF_MEANING: str (the different values of the bit-field and their respective meaning)
        BF_RESET_VAL: str (reset value(s))
    2) a text dump file with mutiple lines with following format
        Register 0016 is: 0100
    generates:
    1) xlsx : same as the register + bitfield description + dump values in column, removing un-dumped registers
    or
    2) html: same but in html format

Usage:
------
python HEX2Human.py --test=Y
(will generate on windows on user's desktop an html output)
"""

#STANDARD MODULES
import argparse
import logging
from os.path import abspath,join,pardir
from os import environ

#PIP INSTALLED
import pandas as pd

REG_ADD = "Register Address"
REG_NAME = "Register Long Name"
BF_NUMBER = "Bit Field Number"
BF_NAME = "Bit Field Name"
BF_MEANING = "Bit Field Enumerations"
BF_RESET_VAL = "Bit Field Reset Value"
#
REG_VALUE = "Register Value"


def load_regmap(fp):
    """ Returns a panda DataFrame with the register and bitfield definition """
    df = pd.read_csv(fp)
    df[REG_ADD] = df[REG_ADD].str.upper() 
    df[BF_MEANING]=df[BF_MEANING].fillna("")
    return df[[REG_ADD,REG_NAME,BF_NUMBER,BF_NAME,BF_MEANING,BF_RESET_VAL]]

def load_regdump(fp):
    """ load register dump from csv file formatted in 2 columns REG_ADD | REG_VAL """
    df = pd.read_csv(fp)
    df[REG_ADD] = df[REG_ADD].str.upper() 
    return df[[REG_ADD,REG_VALUE]]


def bf(x):
    """ returns the given bitfield value from within a register
    Parameters:
    x: a pandas DataFrame line - with a column named BF_NUMBER which holds the definition of given bit_field
    reg_val: integer
    Returns:
    --------
    res: str
        the bit field value from within the register
    """
    reg_val = int(x[REG_VALUE][2:],16)  

    if str(x[BF_NUMBER]).find("..")>0:
        min = int(x[BF_NUMBER].split("..")[1])
        max = int(x[BF_NUMBER].split("..")[0])
        mask = (1<<max) -(1<<min)
        res= mask & reg_val
        res = res>>min
    else:
        mask = (1<<int(x[BF_NUMBER])) 
        res = mask & reg_val
        res = res >> int(x[BF_NUMBER])

    return res

def deobfuscate_dumps(**args):
    registers = {}
    df_regdump = load_regdump(args["regdump"])
    df = load_regmap(args["regmap"])

    df=pd.merge(df,df_regdump,on=[REG_ADD],how="left")
    #remove registers for which no value was dumped
    df.dropna(subset=[REG_VALUE],inplace=True)

    df["DUMP"]=""
    df["DUMPb"]=""
    """for reg_add in registers:
        df.loc[df[REG_ADD]==reg_add,["DUMP"]]=df[df[REG_ADD]==reg_add].apply(lambda x: bf(x,registers[reg_add]) ,axis=1)
        df.loc[df[REG_ADD]==reg_add,["DUMPb"]]=df[df[REG_ADD]==reg_add].apply(lambda x: bin(bf(x,registers[reg_add])) ,axis=1)
    """
    df["DUMP"]=df.apply(lambda x: bf(x),axis=1)
    try:
        if args["reghuman"].find(".html")>=0:
                df.to_html(args["reghuman"],index=False)
        elif args["reghuman"].find(".html")>=0:
            df.to_excel(args["reghuman"])
    except:
        print("failed to save")
        raise
    else:
        print("Human friendly registers dump saved under: %s"%(args["reghuman"]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--regdump", type=str, default="regdump.txt",
                    help="filename of the register dump")
    parser.add_argument("-m", "--regmap", type=str, default="regmap.csv",
                    help="filename of the register dump")
    parser.add_argument("-o", "--output", type=str, default="output.txt",
                    help="filename of the register dump")
    parser.add_argument("-v", "--verbosity", default=0, choices=[0, 1, 2, 3],
                    help="increase output verbosity")
    parser.add_argument("-t", "--test", default="Y", choices=["Y","N"],
                    help="increase output verbosity")
    args = parser.parse_args()
    args = vars(args)
    if args["test"]=="Y":
        args["verbosity"]=4
        args["regdump"]=abspath(join(__file__,pardir,"802.3_claus22_dump.csv"))
        args["regdump"]=abspath(join(__file__,pardir,"loopback_dump.csv"))
        args["regmap"]=abspath(join(__file__,pardir,"802.3_clause_22.csv"))
        args["reghuman"]=join(join(environ['USERPROFILE']), 'Desktop',"RegisterDumps4Humans.html")
    logging.basicConfig(level=(4-args["verbosity"])*10)
    deobfuscate_dumps(**args)
