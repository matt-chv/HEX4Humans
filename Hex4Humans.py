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
from lxml import html

REG_ADD = "Register Address"
REG_NAME = "Register Long Name"
BF_NUMBER = "Bit Field Number"
BF_NAME = "Bit Field Name"
BF_MEANINGS = "Bit Field Enumerations"
BF_RESET_VAL = "Bit Field Reset Value"
#
REG_VALUE = "Register Value"

def load_regmap(fp):
    """ Returns a panda DataFrame with the register and bitfield definition """
    if exists(fp):
        df = pd.read_csv(fp, encoding="utf-8")
    else:
        log_msg = f"regmap path {fp} does not exist"
        logging.error(log_msg)
        raise Exception(log_msg)

    df[REG_ADD] = df[REG_ADD].str.lower() 
    df[BF_MEANINGS]=df[BF_MEANINGS].fillna("")
    hmtl_br = "\n"
    df[BF_MEANINGS]=df[BF_MEANINGS].str.replace("\r\n",hmtl_br).replace("\r\n",hmtl_br).replace("\n",hmtl_br).replace("\r",hmtl_br)
    cols = [REG_ADD,REG_NAME,BF_NUMBER,BF_NAME,BF_MEANINGS,BF_RESET_VAL]
    for col in cols:
        err = False
        if col not in df.columns:
            logging.error(f"Expected column {col} which was not found")
            err = True
        if err:
            raise Exception("Register Mapping file column header names not as expected")
    return df[cols]

def load_regdump(fp):
    """ load register dump from csv file formatted in 2 columns REG_ADD | REG_VAL """
    df = pd.read_csv(fp, encoding="utf-8")
    if not REG_ADD in df.columns:
        log_msg = f"{REG_ADD} needded for processing and not found in columns"
        logging.error(log_msg)
        raise Expception(log_msg)
    if not REG_VALUE in df.columns:
        log_msg = f"{REG_VALUE} needded for processing and not found in columns"
        logging.error(log_msg)
        raise Expception(log_msg)
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
        #Example
        #BF=3..1 => min_bit =1 , max_bit = 3
        #mask = 14 = 0xE
        #(1<<4) - (1<<1)= 16 - 2 =14
        min_bit = int(x[BF_NUMBER].split("..")[1])
        max_bit = int(x[BF_NUMBER].split("..")[0])
        mask = (1<<(max_bit+1)) -(1<<(min_bit))
        res= mask & reg_val
        res = res>>min_bit
        res = "{:04x}".format(res).upper()
        res = "0x"+res
    else:
        mask = (1<<int(x[BF_NUMBER])) 
        res = mask & reg_val
        res = res >> int(x[BF_NUMBER])
        res = "{:04x}".format(res).upper()
        res = "0x"+res
    return res

def hex_bf_to_text(regmap_line):
    """ return the text description associated with the BitField value"""
    #bf_values: list of bitfield values starting with hexvalues and description
    bf_values = regmap_line[BF_MEANINGS].split("\n")
    bf_dict = {}
    
    if len(bf_values)>1: # and not isnan(regmap_line["DUMP"]):
        #if we have multiple values then look for the good one
        
        bf_hex_value = regmap_line["DUMP"]

        for v in bf_values:
            try:
                #the expected formatting of the bit field description is to be
                #0x000A: description
                #namely 4 digit hex value preceeded by 0x and followed by semicolumn and SPACE
                key = v.split(": ")[0]
            except:
                log_msg=f"error in REGMAP formatting in line : {v}"
                logging.error(log_msg)
                raise
            # key = key.split("h")[0] #old formatting where keys where Ah = 
            #if key =="x":
            #    return val
            #else:
            #we need to handle the case where there is a semicolumn in the BF description
            vals = v.split(": ")[1:]
            val = ": ".join(vals).replace("\r\n","<br/>").replace("\r\n","<br/>").replace("\n","<br/>").replace("\r","<br/>")
            bf_dict[key]=val
        if bf_hex_value in bf_dict:
            return bf_dict[bf_hex_value]
        else:
            return "Value not enumerated"
    else:
        #if we do not have multiple values return a blank
        return ""

def bf_status(row, bf_delta_status):
    """ return a string indicating how the different bit fields are different
    r if one or more different from reset value
    b if one or more different between each other (provided 2 or more dumps where processed)

    this is then used by the javascript for hiding or not rows
    """

    status = ""

    bf_values = []
    for i in range(len(bf_delta_status)):
        bf_values.append(row[bf_delta_status[i]])

    bf_values = list(set(bf_values))
    if len(bf_values)>1:
        status="b"
    for bf in bf_values:
        if not bf == row[BF_RESET_VAL]:
            status+="r"
            break

    return status


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
            reg_val_new_name =f'REGISTER from: {fn}'
            bf_new_name = f"BIT FIELD from: {fn}"
            bf_meaning = f"Meaning in: {fn}"
            
            df.rename(columns={REG_VALUE: reg_val_new_name, 
                            "DUMP": bf_new_name,
                            "BF_Meaning": bf_meaning}, inplace=True)

            #add the name of the column to filter at the end
            reg_val_columns.append(reg_val_new_name)
            bf_dump_columns.append(bf_new_name)
            bf_val_columns.append(bf_meaning)
        else:
            print(f"file does not exists: {dump_file}")

    #remove registers for which no value was dumped
    df.dropna(subset=reg_val_columns,inplace=True)
    df = df[[REG_ADD,REG_NAME,BF_NUMBER,BF_NAME, BF_MEANINGS, BF_RESET_VAL]+reg_val_columns+bf_dump_columns+bf_val_columns]
    df["S"]=""
    #set column S to 'r' where one or more dumps have values different than reset value
    df["S"]=df.apply(lambda x: bf_status(x,bf_dump_columns),axis=1)

    #now save the DataFrame to HDD for human eye's pleasures :)
    hmtl_br = "<br>"
    df[BF_MEANINGS]=df[BF_MEANINGS].str.replace("\n",hmtl_br) #.replace("\r\n",hmtl_br).replace("\n",hmtl_br).replace("\r",hmtl_br)
    try:
        if args["output"].find(".htm")>=0:
                #df.to_html(args["output"],index=False,escape=False)
                df_to_css_js_html(df, args["output"])
                if len(reg_val_columns)==1:
                    #if we have only one dump compare to reset values
                    df = df[df[bf_dump_columns[0]] != df[BF_RESET_VAL] ]
                    fpn = args["output"].replace(".htm","_bf_deltas.htm")
                    df_to_css_js_html(df,fpn) #.to_html(fpn,index=False)

                else:
                    #if we have more than one dump compare them to one another
                    df = df[df[reg_val_columns[0]] != df[reg_val_columns[1]] ]
                    fpn = args["output"].replace(".htm","_reg_deltas.htm")
                    df_to_css_js_html(df, fpn)
                    df = df[df[bf_val_columns[0]] != df[bf_val_columns[1]] ]
                    fpn = args["output"].replace(".htm","_bf_deltas.htm")
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
    with open('css/table_fixed_header.css','r') as fi:
        table_fix_header_css=fi.read()
    with open('css/page.css','r') as fi:
        page_css=fi.read()
    with open('css/html_table.css','r') as fi:
        html_table_css=fi.read()
    with open('js/table.js','r') as fi:
        table_js=fi.read()

    #settling for manual templating
    #considered using Django/Jinja2 but this would be overkill so far
    html_string = '''<html>
    <head><title>Hex 4 Humans</title></head>
    <style>{table_fix_header_css}</style>
    <style>{page_css}</style>
    <style>{html_table_css}</style>
    <script>{table_js}</script>
    <body>
        <!--div id="control">
            <div class="button" id="all">view all</div><div class="button"  id="reg">only register differences</div>
            <div class="button" id="bf">only bit field differences</div>
        </div>
        <div id="blank" style="height: 100px; position:absolute;"/-->
    <div class="header">
        <div class="button" id="all" onclick="show_all()">view all</div>
        <div class="button" id="bitfield" onclick="show_bf_delta()">delta across dumps</div>
        <div class="button" id="reset" onclick="show_reset_delta()">delta vs reset</div>
    </div>
    <div class="footer">footer</div>
    <section class="">
    <div class="container">
        {table}
    </body>
    </html>.
    '''
    # OUTPUT AN HTML FILE
    with open(html_fp, 'w',encoding="utf-8") as f:
        #get the html code for the table from pandas
        html_table = df.to_html(classes='mystyle',index=False,escape=False)
        #load it for formtting and styling in with lxml
        xhtml = html.fromstring(html_table)
        
        for th in xhtml.xpath("//th"):
            #add here a div so the css from table_fixed_header can work
            # it does a select on .th div
            es = html.fragments_fromstring(f"<div>{th.text}</div>")
            #es is a list of fragments, we only want to add the fisrt (and only one) to the th
            th.append(es[0])

        #add here class information for the rows as a function of the column S (S for show)
        for td in xhtml.xpath("//tr//td[last()]"):
            tr = td.getparent()
            if td.text:
                for character in td.text:
                    tr.attrib['class']=character
            else:
                tr.attrib['class']="all"

        #transform teh lxml object in a string back
        html_table = html.tostring(xhtml,encoding="utf-8",pretty_print=True).decode('utf-8')

        #then add the html table to the rest of the html pag and save it to file
        f.write(html_string.format(html_table_css=html_table_css,page_css=page_css,\
            table_fix_header_css=table_fix_header_css,\
            table_js = table_js,\
            table=html_table))
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
    parser.add_argument("-t", "--test", default="N", choices=["Y","N"],
                    help="manual hack for debugging - only use if you are sure of what you want")
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
