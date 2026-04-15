# 这是一个策略映射字典，供 rule_engine 调用
# 实际逻辑需根据 GB2828.1-2012 标准实现

def gb2828_CL(qty: int):    # 16-22
    a, b = get_output(qty)
    c = get_output_O(qty)
    return [a] + [b] * 4 + [c] + [f"30[0-1"]

def gb2828_SL(qty: int):    # 15-20
    a, b = get_output(qty)
    c = get_output_O(qty)
    return [a] + [b] * 3 + [c] + [f"30[0-1"]

def gb2828_TB(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_FTN(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_CHS(qty: int):    # 13-16 试装一项抽检？        
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_CHA(qty: int):    # 13-16 试装一项抽检？
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_CB(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_HST(qty: int):    # 14-18
    a, b = get_output(qty)
    return [a] + [b] * 2 + [f"50[0-1"] + [f"10[0-1"]

def gb2828_DS(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_TS(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_PSU(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_HS(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_ISP(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_PP(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_TP(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_SPD(qty: int):    # 12-14
    a, b = get_output(qty)
    return [a] + [b] * 2

def gb2828_FLT(qty: int):    # 12-14
    a, b = get_output(qty)
    return [a] + [b] * 2

def gb2828_CC(qty: int):    # 11-12
    a, b = get_output(qty)
    return [a] + [b] * 1

def gb2828_EC(qty: int):    # 12-14
    a, b = get_output(qty)
    return [a] + [b] * 2

def gb2828_INV(qty: int):    # 14-18
    a, b = get_output(qty)
    return [a] + [b] * 4

def gb2828_ACDC(qty: int):    # 14-18
    a, b = get_output(qty)
    return [a] + [b] * 4

def gb2828_SBS(qty: int):    # 12-14
    a, b = get_output(qty)
    return [a] + [b] * 2

def gb2828_PCBA(qty: int):    # 12-14
    a, b = get_output(qty)
    return [a] + [b] * 2

def gb2828_FG(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_CTR(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_LED(qty: int):    # 15-20
    a, b = get_output(qty)
    return [a] + [b] * 4 + [f"5[0-1]"]

def gb2828_DIO(qty: int):    # 14-18
    a, b = get_output(qty)
    return [a] + [b] * 3 + [f"5[0-1]"]

def gb2828_IL(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_MOS(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 2 + [f"5[0-1]"]

def gb2828_IC(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 2 + [f"5[0-1]"]

def gb2828_TRN(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 2 + [f"5[0-1]"]

def gb2828_POT(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 2 + [f"5[0-1]"]

def gb2828_RES(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 2 + [f"5[0-1]"]

def gb2828_PCB(qty: int):    # 15-20  最后一个抽样标准0.01
    a, b = get_output(qty)
    return [a] + [b] * 4 + [f"5[0-1]"]

def gb2828_BR(qty: int):    # 12-14
    a, b = get_output(qty)
    return [a] + [b] * 2

def gb2828_FAN(qty: int):    # 17-24  17-20 21 22-24 后续更新
    a, b = get_output(qty)
    c = get_output_O(qty)
    return [a] + [b] * 3 + [c] + [b] * 3

def gb2828_LBL(qty: int):    # 14-18
    a, b = get_output(qty)
    return [a] + [b] * 4

def gb2828_LCD(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_DDM(qty: int):    # 14-18
    a, b = get_output(qty)
    return [a] + [b] * 4

def gb2828_DPTS(qty: int):    # 14-18
    a, b = get_output(qty)
    return [a] + [b] * 4

def gb2828_HSS(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_CT(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_FH(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_FUSE(qty: int):    # 14-18
    a, b = get_output(qty)
    return [a] + [b] * 4

def gb2828_RLY(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_MCCB(qty: int):    # 15-20
    a, b = get_output(qty)
    return [a] + [b] * 5

def gb2828_CBKR(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_IGBT(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

# --- 特定模板的 GB2828 策略 ---
def gb2828_BAT(qty: int):   # 17-23
    a, b = get_output(qty)
    return [a] + [b] * 6

def gb2828_BT(qty: int):    # 13-16
    a, b = get_output(qty)
    return [a] + [b] * 3

def gb2828_SCR(qty: int):   # 17-24
    a, b = get_output(qty)
    return [a] + [b] * 7

def gb2828_IND(qty: int):   # 29-37
    a, b = get_output(qty)
    return [a] + [b] * 8

def gb2828_TR(qty: int):    # 46-59
    a, b = get_output(qty)
    return [a] + [b] * 13

def gb2828_CAP(qty: int):   # 17-22
    a, b = get_output(qty)
    return [a] + [b] * 5

def gb2828_CAP1(qty: int):   # 23
    # CAP.json 中的规则，当 contains({2}, '') 时调用
    return get_output_O(qty)


# 将所有策略函数汇总到一个字典中，供 engine 查找
STRATEGY_MAP = {
    "gb2828_CL": gb2828_CL, "gb2828_SL": gb2828_SL, "gb2828_TB": gb2828_TB,
    "gb2828_FTN": gb2828_FTN, "gb2828_CHS": gb2828_CHS, "gb2828_CHA": gb2828_CHA,
    "gb2828_CB": gb2828_CB, "gb2828_HST": gb2828_HST, "gb2828_DS": gb2828_DS,
    "gb2828_TS": gb2828_TS, "gb2828_PSU": gb2828_PSU, "gb2828_HS": gb2828_HS,
    "gb2828_ISP": gb2828_ISP, "gb2828_PP": gb2828_PP, "gb2828_TP": gb2828_TP,
    "gb2828_SPD": gb2828_SPD, "gb2828_FLT": gb2828_FLT, "gb2828_CC": gb2828_CC,
    "gb2828_EC": gb2828_EC, "gb2828_INV": gb2828_INV, "gb2828_ACDC": gb2828_ACDC,
    "gb2828_SBS": gb2828_SBS, "gb2828_PCBA": gb2828_PCBA, "gb2828_FG": gb2828_FG,
    "gb2828_CTR": gb2828_CTR, "gb2828_LED": gb2828_LED, "gb2828_DIO": gb2828_DIO,
    "gb2828_IL": gb2828_IL, "gb2828_MOS": gb2828_MOS, "gb2828_IC": gb2828_IC,
    "gb2828_TRN": gb2828_TRN, "gb2828_POT": gb2828_POT, "gb2828_RES": gb2828_RES,
    "gb2828_PCB": gb2828_PCB, "gb2828_BR": gb2828_BR, "gb2828_FAN": gb2828_FAN,
    "gb2828_LBL": gb2828_LBL, "gb2828_LCD": gb2828_LCD, "gb2828_DDM": gb2828_DDM,
    "gb2828_DPTS": gb2828_DPTS, "gb2828_HSS": gb2828_HSS, "gb2828_CT": gb2828_CT,
    "gb2828_FH": gb2828_FH, "gb2828_FUSE": gb2828_FUSE, "gb2828_RLY": gb2828_RLY,
    "gb2828_MCCB": gb2828_MCCB, "gb2828_CBKR": gb2828_CBKR,
    # 特定模板
    "gb2828_BAT": gb2828_BAT, "gb2828_BT": gb2828_BT, "gb2828_SCR": gb2828_SCR,
    "gb2828_IND": gb2828_IND, "gb2828_TR": gb2828_TR, "gb2828_CAP": gb2828_CAP,
    "gb2828_CAP1": gb2828_CAP1, "gb2828_IGBT": gb2828_IGBT,
}

def get_output(number: int) -> tuple[str, str]:
    if number <= 1:
        return "1[0-1]", "1[0-1]"
    elif number <= 2:
        return "2[0-1]", "2[0-1]"
    elif number <= 3:
        return "3[0-1]", "3[0-1]"
    elif number <= 4:
        return "4[0-1]", "4[0-1]"
    elif number <= 5:
        return "5[0-1]", "5[0-1]"
    elif number <= 6:
        return "5[0-1]", "6[0-1]"
    elif number <= 7:
        return "5[0-1]", "7[0-1]"
    elif number <= 8:
        return "5[0-1]", "8[0-1]"
    elif number <= 9:
        return "5[0-1]", "9[0-1]"
    elif number <= 10:
        return "5[0-1]", "10[0-1]"
    elif number <= 11:
        return "5[0-1]", "11[0-1]"
    elif number <= 12:
        return "5[0-1]", "12[0-1]"
    elif number <= 13:
        return "5[0-1]", "13[0-1]"
    elif number <= 14:
        return "5[0-1]", "13[0-1]"
    elif number <= 15:
        return "5[0-1]", "13[0-1]"
    elif number <= 25:
        return "5[0-1]", "13[0-1]"
    elif number <= 50:
        return "5[0-1]", "13[0-1]"
    elif number <= 90:
        return "20[1-2]", "13[0-1]"
    elif number <= 150:
        return "20[1-2]", "13[0-1]"
    elif number <= 280:
        return "32[2-3]", "50[1-2]"
    elif number <= 500:
        return "50[3-4]", "50[1-2]"
    elif number <= 1200:
        return "80[5-6]", "80[2-3]"
    elif number <= 3200:
        return "125[7-8]", "125[3-4]"
    elif number <= 10000:
        return "200[10-11]", "200[5-6]"
    elif number <= 35000:
        return "315[14-15]", "315[7-8]"
    elif number <= 150000:
        return "500[21-22]", "500[10-11]"
    elif number <= 500000:
        return "500[21-22]", "800[14-15]"
    else:  # > 500000
        return "500[21-22]", "1250[21-22]"

# 抽样标准0.01
def get_output_O(number: int) -> str:
    if number <= 1250:
        c = f"{number}[0-1]"
        return c
    else:
        c = f"1250[0-1]"
        return c