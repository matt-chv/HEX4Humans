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
        BF_MEANINGS: str (the different values of the bit-field and their respective meaning)
            format options
             0h = description
                start with hex number then h then = then description - one in many values of enumeration
             xh = description
                starts with 'x' : meaning data not bitfield meaning
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
from os.path import abspath,basename,exists,join,pardir
from os import environ

#PIP INSTALLED
import pandas as pd
from numpy import isnan, nan

REG_ADD = "Register Address"
REG_NAME = "Register Long Name"
BF_NUMBER = "Bit Field Number"
BF_NAME = "Bit Field Name"
BF_MEANINGS = "Bit Field Enumerations"
BF_RESET_VAL = "Bit Field Reset Value"
#
REG_VALUE = "Register Value"

#FIXME: move this tos separate file
html_table_css = """/* includes alternating gray and white with on-hover color */

.mystyle {
    font-size: 11pt; 
    font-family: Arial;
    border-collapse: collapse; 
    border: 1px solid silver;

}

.mystyle td, th {
    padding: 5px;
}

.mystyle tr:nth-child(even) {
    background: #E0E0E0;
}

.mystyle tr:hover {
    background: silver;
    cursor: pointer;
}"""

page_css = """ /* multiple formatting for the rest of the page */

#control {
    position:fixed;
    top:0px;
    right:0px;
    height:50px;
    width: 100%;
    background-color: rgba(255, 255, 255, 0.5);
}
#all {
    position: absolute;
    top:0px;
    lef:50px;
}
#reg {
    position: absolute;
    top:0px;
    left:200px;
}
#bf {
    position: absolute;
    top:0px;
    left:400px;
}

.button {
  transition-duration: 0.4s;
}

.button:hover {
  background-color: #4CAF50; /* Green */
  color: white;
}

"""


def load_regmap(fp):
    """ Returns a panda DataFrame with the register and bitfield definition """
    if exists(fp):
        df = pd.read_csv(fp)
    else:
        logging.error("regmap path does not exist")
    df[REG_ADD] = df[REG_ADD].str.lower() 
    df[BF_MEANINGS]=df[BF_MEANINGS].fillna("")
    return df[[REG_ADD,REG_NAME,BF_NUMBER,BF_NAME,BF_MEANINGS,BF_RESET_VAL]]

def load_regdump(fp):
    """ load register dump from csv file formatted in 2 columns REG_ADD | REG_VAL """
    print("regdump fp",fp)
    df = pd.read_csv(fp)
    df[REG_ADD] = df[REG_ADD].str.lower() 
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
    try:
        reg_val = int(x[REG_VALUE][2:],16)  
    except:
        if isnan(x[REG_VALUE]):
            return nan
        else:
            raise

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

def hex_bf_to_text(regmap_line,):
    """ return the text description associated with the BitField value"""
    bf_values = regmap_line[BF_MEANINGS].split("\n")
    bf_dict = {}
    if len(bf_values)>1 and not isnan(regmap_line["DUMP"]):
        bf_hex_value = int(regmap_line["DUMP"])

        for v in bf_values:
            try:
                key, val = v.split(" = ")
            except:
                print("error in REGMAP formatting in line : ",bf_values)
            key = key.split("h")[0]
            if key =="x":
                return val
            else:
                bf_dict[int(key.split("h")[0],16)]=val
        if bf_hex_value in bf_dict:
            return bf_dict[bf_hex_value]
        else:
            return "Value not enumerated"
    else:
        return ""

def deobfuscate_dumps(**args):
    registers = {}
    df = load_regmap(args["regmap"])
    reg_val_columns = []
    bf_val_columns = []
    bf_dump_columns =[]
    for dump_file in args["regdump"]:
        if exists(dump_file):
            fn = basename(dump_file)
            df_regdump = load_regdump(dump_file)

            df=pd.merge(df,df_regdump,on=[REG_ADD],how="left")

            df["DUMP"]=""
            df["BF_Meaning"]=""
            """for reg_add in registers:
                df.loc[df[REG_ADD]==reg_add,["DUMP"]]=df[df[REG_ADD]==reg_add].apply(lambda x: bf(x,registers[reg_add]) ,axis=1)
                df.loc[df[REG_ADD]==reg_add,["DUMPb"]]=df[df[REG_ADD]==reg_add].apply(lambda x: bin(bf(x,registers[reg_add])) ,axis=1)
            """
            df["DUMP"]=df.apply(lambda x: bf(x),axis=1)
            df["BF_Meaning"]=df.apply(lambda x: hex_bf_to_text(x),axis=1)
            df.rename(columns={REG_VALUE: f'{REG_VALUE}_{fn}', 
                            "DUMP": f"DUMP_{fn}",
                            "BF_Meaning": f"BF_Meaning{fn}"}, inplace=True)

            #add the name of the column to filter at the end
            if len(args["regdump"])>1:
                reg_val_columns.append(f'{REG_VALUE}_{fn}')
                bf_dump_columns.append(f"DUMP_{fn}")
                bf_val_columns.append(f"BF_Meaning{fn}")
            else:
                reg_val_columns.append(REG_VALUE)
                bf_dump_columns.append("DUMP")
                bf_val_columns.append("BF_Meaning")
        else:
            print(f"file does not exists: {dump_file}")

    #remove registers for which no value was dumped
    df.dropna(subset=reg_val_columns,inplace=True)
    df = df[[REG_ADD,REG_NAME,BF_NUMBER,BF_NAME, BF_MEANINGS, BF_RESET_VAL]+reg_val_columns+bf_dump_columns+bf_val_columns]

    #now save the DataFrame to HDD for human eye's pleasures :)
    try:
        if args["output"].find(".htm")>=0:
                df.to_html(args["output"],index=False)
                df = df[df[reg_val_columns[0]] != df[reg_val_columns[1]] ]
                fpn = args["output"].replace(".htm","_reg_deltas.htm")
                print("version with only register deltas: ",fpn)
                df.to_html(fpn,index=False)
                df = df[df[bf_val_columns[0]] != df[bf_val_columns[1]] ]
                fpn = args["output"].replace(".htm","_bf_deltas.htm")
                print("version with only bitfield deltas: ",fpn)
                df_to_css_js_html(df,fpn) #.to_html(fpn,index=False)
        elif args["output"].find(".html")>=0:
            df.to_excel(args["output"])
    except:
        print("failed to save")
        raise
    else:
        print("Human friendly registers dump saved under: %s"%(args["output"]))

def df_to_css_js_html(df, html_fp):
    pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>
    global html_table_css
    html_string = '''
    <html>
    <head><title>Hex 2 Humans</title></head>
    <style>{page_css}</style>
    <style>{html_table_css}</style>
    <body>
        <div id="control">
            <div class="button" id="all">view all</div><div class="button"  id="reg">only register differences</div>
            <div class="button" id="bf">only bit field differences</div>
        </div>
        <div id="blank" style="height: 100px; position:absolute;"/>

        {table}
    </body>
    </html>.
    '''
    # OUTPUT AN HTML FILE
    with open(html_fp, 'w') as f:
        f.write(html_string.format(html_table_css=html_table_css,page_css=page_css,table=df.to_html(classes='mystyle',index=False)))
    print(f"saved {html_fp}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--regdump",  default="regdump.txt",type=str, nargs='+',
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
        args["output"]=join(join(environ['USERPROFILE']), 'Desktop',"RegisterDumps4Humans.html")
    logging.basicConfig(level=(4-args["verbosity"])*10)
    deobfuscate_dumps(**args)
