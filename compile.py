#!/usr/bin/python3.9

import sys
import re

if len(sys.argv) < 2:
    print("Not enough arguments provided")
    sys.exit()

debug = True

state_codes = {
    "start": "start",
    "runtime_error": "runtime_error"
}

src_file = sys.argv[1]
out_file = (".".join(src_file.split(".")[:-1]) if "." in src_file else src_file)+".tur"

def write(state, read, replace, direction, new_state, cmd="%NOCMD%"):
    if state != "start" and not re.match(r"^ready[0-9]+$", state):
        state = f"{cmd}_{state}"
    if new_state != "start" and not re.match(r"^ready[0-9]+$", new_state) and new_state != "runtime_error" and new_state != "done":
        new_state = f"{cmd}_{new_state}"
    if not debug:
        if state not in state_codes:
            state_codes[state] = str(len(state_codes))
        state = state_codes[state]

        if new_state not in state_codes:
            state_codes[new_state] = str(len(state_codes))
        new_state = state_codes[new_state]
    with open(out_file, "a", encoding="utf-8") as out:
        arrow = "\u2190" if direction == "<" else "→"
        out.write("\u0394(%s,%s) = (%s,%s,%s)\n" % (state, read, replace, arrow, new_state))

with open(src_file, "r") as read:
    src = [x.split("//")[0].strip().split(" ") for x in read.read().split("\n") if x.split("//")[0].strip() != ""]

digits = list("-0123456789")
non_minus_digits = [d for d in digits if d != "-"]

for i in digits + [";"]:
    write("start", i, i, "<", "start")
write("start", "", "#", ">", "gotoend")

for i in digits + [";"]:
    write("gotoend", i, i, ">", "goingtoend")
    write("goingtoend", i, i, ">", "goingtoend")
write("gotoend", "", "", ">", "getready")
write("getready", "", "", "<", "ready0")
write("goingtoend", "", "", "<", "ready0")

variable_names = []
labels = {}

preprocessing = {
    "SET": lambda line: variable_names.append(line[1]),
    "LOAD": lambda line: variable_names.append(line[1]),
    "UNSET": lambda line: variable_names.append(line[1])
}

for line in src:
    if line[0] in preprocessing:
        try:
            preprocessing[line[0]](line)
        except IndexError:
            pass # Circumstances which might cause this error are handled later

for a, line in enumerate(src):
    cmd = line[0]
    if cmd.startswith(":"):
        label_name = cmd[1:]
        if len(label_name) > 0:
            if len(line) > 1:
                print(f"Line {a+1}. Label names cannot contain a space")
                sys.exit()
            elif label_name in labels:
                print(f"Line {a+1}. Label {label_name} already defined on line {labels[label_name]+1}")
                sys.exit()
            else:
                labels[label_name] = a
        else:
            print(f"Line {a+1}. Label names cannot be empty")
            sys.exit()



variable_names = list(set(variable_names))

def push_cmd(a, line):
    cmd = "PUSH"
    arg = line[1].lstrip("-").lstrip("0")
    minus = line[1][0] == "-"
    if arg == "":
        arg = "0"
    elif minus:
        arg = "-" + arg
    for d in digits:
        write(f"ready{a}", d, d, ">", f"sready{a}", cmd)
    write(f"ready{a}", "", arg[0], ">", f"put1_{a}", cmd)
    write(f"sready{a}", "", ";", ">", f"put0_{a}", cmd)
    for i, d in enumerate(arg):
        write(f"put{i}_{a}", "", d, ">", f"put{i+1}_{a}", cmd)
    write(f"put{len(arg)}_{a}", "", "", "<", f"ready{a+1}", cmd)

def pop_cmd(a, line):
    cmd = "POP"
    write(f"ready{a}", "", "", ">", "runtime_error", cmd)
    for d in digits:
        write(f"ready{a}", d, "", "<", f"popping{a}", cmd)
        write(f"popping{a}", d, "", "<", f"popping{a}", cmd)
    write(f"popping{a}", ";", "", "<", f"ready{a+1}", cmd)
    write(f"popping{a}", "#", "#", ">", f"ready{a+1}", cmd)

def set_cmd(a, line):
    cmd = "SET"
    var = line[1]
    for d in digits+[";"]:
        write(f"ready{a}", d, d, "<", f"sready{a}", cmd)
    for d in digits + variable_names + [";", "#"]:
        write(f"sready{a}", d, d, "<", f"sready{a}", cmd)
    write(f"ready{a}", "", "", "<", f"runtime_error", cmd)
    write(f"sready{a}", "", var, ">", f"fetchvaluefromstack{a}", cmd)
    for d in digits + variable_names + [";", "#"]:
        write(f"fetchvaluefromstack{a}", d, d, ">", f"fetchvaluefromstack{a}", cmd)
    write(f"fetchvaluefromstack{a}", "", "", "<", f"foundvalueinstack{a}", cmd)
    for d in digits:
        write(f"foundvalueinstack{a}", d, "", "<", f"putdigit{a}_{d}", cmd)
    for d in digits:        
        for e in digits + variable_names + [";", "#"]:
            write(f"putdigit{a}_{d}", e, e, "<", f"putdigit{a}_{d}", cmd)

        write(f"putdigit{a}_{d}", "", d, ">", f"fetchvaluefromstack{a}", cmd)
    
    write(f"foundvalueinstack{a}", ";", "", "<", f"ready{a+1}", cmd)
    write(f"foundvalueinstack{a}", "#", "#", ">", f"ready{a+1}", cmd)

def load_cmd(a, line):
    cmd = "LOAD"
    var = line[1]
    other_variable_names = [i for i in variable_names if i != var]
    for d in digits:
        write(f"ready{a}", d, d, ">", f"sready{a}", cmd)
        write(f"sready{a}", d, d, ">", f"sready{a}", cmd)
    write(f"ready{a}", "", "", "<", f"readyinenv{a}", cmd)
    write(f"sready{a}", "", ";", "<", f"readyinenv{a}", cmd)
    for d in digits + variable_names + [";", "#"]:
        write(f"readyinenv{a}", d, d, "<", f"readyinenv{a}", cmd)
    write(f"readyinenv{a}", "", "", ">", f"locatevariable{a}", cmd)
    write(f"locatevariable{a}", "#", "#", ">", "runtime_error", cmd)
    for d in digits + other_variable_names:
        write(f"locatevariable{a}", d, d, ">", f"locatevariable{a}", cmd)
    write(f"locatevariable{a}", var, var, "<", f"locatedvariable{a}", cmd)
    for d in digits:
        write(f"locatedvariable{a}", d, d, "<", f"locatedvariable{a}", cmd)
    for d in other_variable_names + [""]:
        write(f"locatedvariable{a}", d, d, ">", f"copyvariable{a}", cmd)
    for d in digits:
        write(f"copyvariable{a}", d, f"!{d}", ">", f"copyingvariable{a}_{d}", cmd)
    for d in digits:
        for e in digits + variable_names + [";", "#"]:
            write(f"copyingvariable{a}_{d}", e, e, ">", f"copyingvariable{a}_{d}", cmd)
        write(f"copyingvariable{a}_{d}", "", d, "<", f"fetchnext{a}", cmd)
    for d in digits + variable_names + [";", "#"]:
        write(f"fetchnext{a}", d, d, "<", f"fetchnext{a}", cmd)
    for d in digits:
        write(f"fetchnext{a}", f"!{d}", d, ">", f"copyvariable{a}", cmd)
    write(f"copyvariable{a}", var, var, ">", f"getready{a}", cmd)
    for d in digits + variable_names + [";", "#"]:
        write(f"getready{a}", d, d, ">", f"getready{a}", cmd)
    write(f"getready{a}", "", "", "<", f"ready{a+1}", cmd)

def unset_cmd(a, line):
    cmd = "UNSET"
    var = line[1]
    other_variable_names = [i for i in variable_names if i != var]
    for d in digits + [""]:
        write(f"ready{a}", d, d, "<", f"sready{a}", cmd)
    for d in digits + variable_names + [";", "#"]:
        write(f"sready{a}", d, d, "<", f"sready{a}", cmd)
    write(f"sready{a}", "", "", ">", f"locatevariable{a}", cmd)
    write(f"locatevariable{a}", "#", "#", ">", "runtime_error", cmd)
    for d in digits + other_variable_names:
        write(f"locatevariable{a}", d, d, ">", f"locatevariable{a}", cmd)
    write(f"locatevariable{a}", var, "@", "<", f"locatedvariable{a}", cmd)
    for d in digits:
        write(f"locatedvariable{a}", d, "!", "<", f"locatedvariable{a}", cmd)
    for d in other_variable_names:
        write(f"locatedvariable{a}", d, "!", ">", f"copyingvariable{a}_{d}", cmd)
    write(f"locatedvariable{a}", "", "", ">", f"donecopying{a}", cmd)
    for d in digits + other_variable_names:
        write(f"copyingvariable{a}_{d}", "!", "!", ">", f"copyingvariable{a}_{d}", cmd)
        write(f"copyingvariable{a}_{d}", "@", d, "<", f"keepcopyingvariable{a}", cmd)
    write(f"keepcopyingvariable{a}", "!", "@", "<", f"stillcopyingvariable{a}", cmd)
    write(f"stillcopyingvariable{a}", "!", "!", "<", f"stillcopyingvariable{a}", cmd)
    for d in digits + variable_names:
        write(f"stillcopyingvariable{a}", d, "!", ">", f"copyingvariable{a}_{d}", cmd)
    write(f"stillcopyingvariable{a}", "", "", ">", f"donecopying{a}", cmd)
    for d in ["!", "@"]:
        write(f"donecopying{a}", d, "", ">", f"donecopying{a}", cmd)
    for d in digits + variable_names + [";", "#"]:
        write(f"donecopying{a}", d, d, ">", f"donecopying{a}", cmd)
    write(f"donecopying{a}", "", "", "<", f"getready{a}", cmd)
    write(f"getready{a}", "#", "#", ">", f"ready{a+1}", cmd)
    for d in digits:
        write(f"getready{a}", d, d, ">", f"gettingready{a}", cmd)
    write(f"gettingready{a}", "", "", "<", f"ready{a+1}", cmd)

def jump_cmd(a, line):
    cmd = "JUMP"
    offset = int(line[1])
    for d in digits + [""]:
        write(f"ready{a}", d, d, ">", f"getready{a}", cmd)
    write(f"getready{a}", "", "", "<", f"ready{min(a+offset+1, len(src))}", cmd)

def jlz_cmd(a, line):
    cmd = "JLZ"
    offset = int(line[1])
    write(f"ready{a}", "", "", ">", "runtime_error", cmd)
    for d in non_minus_digits:
        write(f"ready{a}", d, "", "<", f"checking{a}", cmd)
        write(f"checking{a}", d, "", "<", f"checking{a}", cmd)
    write(f"checking{a}", ";", "", "<", f"ready{a+1}", cmd)
    write(f"checking{a}", "#", "#", ">", f"ready{a+1}", cmd)
    write(f"checking{a}", "-", "", "<", f"passed{a}", cmd)
    write(f"passed{a}", "#", "#", ">", f"ready{a+offset+1}", cmd)
    write(f"passed{a}", ";", "", "<", f"ready{a+offset+1}", cmd)

def goto_cmd(a, line):
    label_name = line[1]
    if label_name in labels:
        jump_cmd(a, ["JUMP", str(labels[label_name]-a)])
    else:
        print(f"Line {a+1}. Label {label_name} is not defined")

def return_cmd(a, line):
    cmd = "RETURN"
    write(f"ready{a}", "", "", ">", "runtime_error", cmd)
    max_depth = len(str(len(src)))
    
    def recurse(current, depth):
        if depth >= max_depth:
            return
        for d in digits:
            write(current, d, "", "<", f"{current}_{d}", cmd)
            recurse(f"{current}{d}", depth+1)

    for d in digits:
        write(f"ready{a}", d, "", "<", f"popping{a}_{d}", cmd)
        write(f"popping{a}", d, "", "<", f"popping{a}_{d}", cmd)
        recurse(f"popping{a}_{d}", 1)

    for i in range(pow(10, max_depth)):
        write(f"popping{a}_{'_'.join(list(str(i)))}", ";", "", "<", f"ready{str(i)[::-1]}", cmd)
        write(f"popping{a}_{'_'.join(list(str(i)))}", "#", "#", ">", f"ready{str(i)[::-1]}", cmd)

def bigger_cmd(a, line):
    cmd = "BIGGER"
    
def add_together(a_negative, b_negative, a, b, carry, a_bigger):
    a = int(0 if a == "-" else a)
    b = int(0 if b == "-" else b)
    
    if (a_negative and b_negative) or (not a_negative and not b_negative):
        s = a + b
        if carry:
            s += 1
        return [s % 10, s >= 10]
    else:
        s = (a - b) if a_bigger else (b - a)
        if carry:
            s -= 1
        return [s % 10, s < 0]

def subtract_together(a_negative, b_negative, a, b, carry, a_bigger):
    return add_together(a_negative, not b_negative, a, b, carry, a_bigger)

def add_cmd(a, line, mux=add_together, bflip=False):
    cmd = "ADD"

    write(f"ready{a}", "", "", ">", f"runtime_error", cmd)
    for d in non_minus_digits:
        write(f"ready{a}", d, f"!{d}", ">", f"inc{a}", cmd)
    for d in non_minus_digits:
        write(f"inc{a}", d, d, ">", f"inc{a}", cmd)
    write(f"inc{a}", "", "", ">", f"incing{a}", cmd)
    for d in non_minus_digits:
        ans, c = add_together(False, False, d, 1, False, True)
        write(f"incing{a}", d, ans, ">" if c else "<", f"incing{a}" if c else f"inced{a}", cmd)
    write(f"incing{a}", "", "1", "<", f"inced{a}", cmd)
    for d in non_minus_digits:
        write(f"inced{a}", d, d, "<", f"inced{a}", cmd)
    write(f"inced{a}", "", "", "<", f"incnext{a}", cmd)
    for d in non_minus_digits:
        write(f"incnext{a}", d, d, "<", f"incnext{a}", cmd)
        write(f"incnext{a}", f"!{d}", d, "<", f"ready{a}", cmd)
    
    write(f"ready{a}", ";", ";", "<", f"decnext{a}", cmd)
    write(f"ready{a}", "#", "#", ">", f"runtime_error", cmd)
    write(f"ready{a}", "-", "-", "<", f"ready{a}", cmd)

    for d in non_minus_digits:
        write(f"decnext{a}", d, f"!{d}", ">", f"dec{a}", cmd)
    for d in ";#-":
        write(f"decnext{a}", d, d, ">", f"comparecounts{a}", cmd)
    for d in digits + [";"]:
        write(f"dec{a}", d, d, ">", f"dec{a}", cmd)
    write(f"dec{a}", "", "", ">", f"decing{a}", cmd)
    for d in non_minus_digits:
        ans, c = add_together(False, True, d, 1, False, True)
        write(f"decing{a}", d, ans, ">" if c else "<", f"decing{a}" if c else f"deced{a}", cmd)
    write(f"decing{a}", "", "", "<", f"correctorder{a}", cmd)
    for d in digits + ["", ";"]:
        write(f"deced{a}", d, d, "<", f"deced{a}", cmd)
    for d in non_minus_digits:
        write(f"deced{a}", f"!{d}", d, "<", f"decnext{a}", cmd)
    for d in digits + [";"]:
        write(f"comparecounts{a}", d, d, ">", f"comparecounts{a}", cmd)
    write(f"comparecounts{a}", "", "", ">", f"iszero{a}", cmd)
    for d in digits:
        if d == "0":
            continue
        write(f"iszero{a}", d, d, ">", f"incorrectorder{a}", cmd)
    write(f"iszero{a}", "0", "0", ">", f"iszero{a}", cmd)
    write(f"iszero{a}", "", "", "<", f"samesize{a}", cmd)

    for d in non_minus_digits:
        write(f"correctorder{a}", d, "", "<", f"correctorder{a}", cmd)
    write(f"correctorder{a}", "", "", "<", f"sready{a}_True", cmd)

    for d in non_minus_digits:
        write(f"incorrectorder{a}", d, d, ">", f"incorrectorder{a}", cmd)
    write(f"incorrectorder{a}", "", "", "<", f"removecounter{a}", cmd)
    for d in non_minus_digits:
        write(f"removecounter{a}", d, "", "<", f"removecounter{a}", cmd)
    write(f"removecounter{a}", "", "", "<", f"sready{a}_False", cmd)
    
    write(f"samesize{a}", "0", "", "<", f"samesize{a}", cmd)
    write(f"samesize{a}", "", "", "<", f"gotostart{a}", cmd)
    for d in digits:
        write(f"gotostart{a}", d, d, "<", f"gotostart{a}", cmd)
        write(f"keepgoingtostart{a}", d, d, "<", f"keepgoingtostart{a}", cmd)
    write(f"gotostart{a}", ";", ";", "<", f"keepgoingtostart{a}", cmd)
    for d in ";#":
        write(f"keepgoingtostart{a}", d, d, ">", f"checkdigit{a}", cmd)
    write(f"checkdigit{a}", "-", "-", ">", f"checkdigit{a}", cmd)
    for d in non_minus_digits:
        write(f"checkdigit{a}", d, f"!{d}", ">", f"checkdigit{a}_{d}", cmd)
        for e in digits + ["~"]:
            write(f"checkdigit{a}_{d}", e, e, ">", f"checkdigit{a}_{d}", cmd)
        write(f"checkdigit{a}_{d}", ";", "~", ">", f"checkdigithere{a}_{d}", cmd)
        for e in non_minus_digits:
            write(f"checkdigit{a}_{d}", f"!{e}", e, ">", f"checkdigithere{a}_{d}", cmd)
        write(f"checkdigithere{a}_{d}", "-", "-", ">", f"checkdigithere{a}_{d}", cmd)
        for e in non_minus_digits:
            ans, c = add_together(False, True, d, e, False, True)
            if c:
                write(f"checkdigithere{a}_{d}", e, e, "<", f"failed{a}", cmd)
            elif ans != 0:
                write(f"checkdigithere{a}_{d}", e, e, "<", f"passed{a}", cmd)
            else:
                write(f"checkdigithere{a}_{d}", e, f"!{e}", "<", f"continuechecking{a}", cmd)

        for d in digits + ["~"]:
            write(f"continuechecking{a}", d, d, "<", f"continuechecking{a}", cmd)
        for d in non_minus_digits:
            write(f"continuechecking{a}", f"!{d}", d, ">", f"checkdigit{a}", cmd)

    write(f"checkdigit{a}", "~", ";", ">", f"alsopassed{a}", cmd)

    for d in digits:
        write(f"passed{a}", d, d, "<", f"passed{a}", cmd)
    write(f"passed{a}", "~", ";", ">", f"alsopassed{a}", cmd)
    
    for d in digits:
        write(f"alsopassed{a}", d, d, ">", f"alsopassed{a}", cmd)
        write(f"alsopassed{a}", f"!{d}", d, ">", f"alsopassed{a}", cmd)
    write(f"alsopassed{a}", "", "", "<", f"sready{a}_True", cmd)

    for d in digits:
        write(f"failed{a}", d, d, "<", f"failed{a}", cmd)
    write(f"failed{a}", "~", ";", ">", f"alsofailed{a}", cmd)
    
    for d in digits:
        write(f"alsofailed{a}", d, d, ">", f"alsofailed{a}", cmd)
    write(f"alsofailed{a}", "", "", "<", f"sready{a}_False", cmd)

    for b in [True, False]:
        write(f"sready{a}_{b}", "#", "#", ">", f"rutime_error", cmd)
        for d in non_minus_digits:
            write(f"sready{a}_{b}", d, d, "<", f"sready{a}_{b}", cmd)
        write(f"sready{a}_{b}", ";", "~", "<", f"check1sign{a}_{b}_1", cmd)
        write(f"sready{a}_{b}", "-", "-", "<", f"gotocheck1sign{a}_{b}_0", cmd)
        write(f"gotocheck1sign{a}_{b}_0", ";", "~", "<", f"check1sign{a}_{b}_0", cmd)
        write(f"gotocheck1sign{a}_{b}_0", "#", "#", ">", f"runtime_error", cmd)
        for s2 in "01":
            for d in non_minus_digits:
                write(f"check1sign{a}_{b}_{s2}", d, d, "<", f"check1sign{a}_{b}_{s2}", cmd)
                write(f"check1sign{a}_{b}_{s2}", f"!{d}", d, "<", f"check1sign{a}_{b}_{s2}", cmd)
            for d in [";", "#"]:
                write(f"check1sign{a}_{b}_{s2}", d, d, ">", f"gotsigns{a}_{b}_1_{s2}", cmd)
            write(f"check1sign{a}_{b}_{s2}", "-", "-", ">", f"gotsigns{a}_{b}_0_{s2}", cmd)
        for s1 in "01":
            for s2 in "01":
                result_negative = (b  and s1 == "0") or (not b and s2 == ("1" if bflip else "0"))
                for d in digits + ["!", "~"]:
                    write(f"gotsigns{a}_{b}_{s1}_{s2}", d, d, ">", f"gotsigns{a}_{b}_{s1}_{s2}", cmd)
                write(f"gotsigns{a}_{b}_{s1}_{s2}", "", "!", "<", f"getnextdigits{a}_{b}_{s1}_{s2}", cmd)
                for d in digits:
                    write(f"getnextdigits{a}_{b}_{s1}_{s2}", d, "!", "<", f"getnextdigits{a}_{b}_{s1}_{s2}_{d}", cmd)
                for d in "!~":
                    write(f"getnextdigits{a}_{b}_{s1}_{s2}", d, "!", "<", f"gettingnextdigits{a}_{b}_{s1}_{s2}_-", cmd)
                for d in digits:
                    for e in digits:
                        write(f"getnextdigits{a}_{b}_{s1}_{s2}_{d}", e, e, "<", f"getnextdigits{a}_{b}_{s1}_{s2}_{d}", cmd)
                    write(f"getnextdigits{a}_{b}_{s1}_{s2}_{d}", "~", "~", "<", f"gettingnextdigits{a}_{b}_{s1}_{s2}_{d}", cmd)
                    write(f"gettingnextdigits{a}_{b}_{s1}_{s2}_{d}", "!", "!", "<", f"gettingnextdigits{a}_{b}_{s1}_{s2}_{d}", cmd)
                    write(f"gettingnextdigits{a}_{b}_{s1}_{s2}_{d}", "-", "!", ">", f"gotnextdigits{a}_{b}_{s1}_{s2}_-_{d}", cmd)
                    for e in ";#":
                        write(f"gettingnextdigits{a}_{b}_{s1}_{s2}_{d}", e, e, ">", f"gotnextdigits{a}_{b}_{s1}_{s2}_-_{d}", cmd)
                    for e in digits:
                        write(f"gettingnextdigits{a}_{b}_{s1}_{s2}_{d}", e, "!", ">", f"gotnextdigits{a}_{b}_{s1}_{s2}_{e}_{d}", cmd)
                        for f in digits + ["!", "~"]:
                            write(f"gotnextdigits{a}_{b}_{s1}_{s2}_{e}_{d}", f, f, ">", f"gotnextdigits{a}_{b}_{s1}_{s2}_{e}_{d}", cmd)
                        if d != "-" or e != "-":
                            sum_no_carry = mux(s1=="0", s2=="0", e, d, False, b)
                            sum_carry = mux(s1=="0", s2=="0", e, d, True, b)
                            write(f"gotnextdigits{a}_{b}_{s1}_{s2}_{e}_{d}", "", sum_no_carry[0], ">" if sum_no_carry[1] else "<", f"dropcarry{a}_{b}_{s1}_{s2}" if sum_no_carry[1] else f"gotogetnextdigits{a}_{b}_{s1}_{s2}", cmd)
                            write(f"gotnextdigits{a}_{b}_{s1}_{s2}_{e}_{d}", "@", sum_carry[0], ">" if sum_carry[1] else "<", f"dropcarry{a}_{b}_{s1}_{s2}" if sum_carry[1] else f"gotogetnextdigits{a}_{b}_{s1}_{s2}", cmd)
                write(f"gotnextdigits{a}_{b}_{s1}_{s2}_-_-", "", "", "<", f"removezeros{a}_{result_negative}", cmd)
                write(f"gotnextdigits{a}_{b}_{s1}_{s2}_-_-", "@", 1 if s1 == s2 else "", ">", f"putcarry{a}_{result_negative}", cmd)
                write(f"putcarry{a}_{result_negative}", "", "", "<", f"removezeros{a}_{result_negative}", cmd)
                write(f"dropcarry{a}_{b}_{s1}_{s2}", "", "@", "<", f"gotogetnextdigits{a}_{b}_{s1}_{s2}", cmd)
                for d in non_minus_digits:
                    write(f"gotogetnextdigits{a}_{b}_{s1}_{s2}", d, d, "<", f"gotogetnextdigits{a}_{b}_{s1}_{s2}", cmd)
                write(f"gotogetnextdigits{a}_{b}_{s1}_{s2}", "!", "!", "<", f"goingtonextdigits{a}_{b}_{s1}_{s2}", cmd)
                write(f"goingtonextdigits{a}_{b}_{s1}_{s2}", "!", "!", "<", f"goingtonextdigits{a}_{b}_{s1}_{s2}", cmd)
                write(f"goingtonextdigits{a}_{b}_{s1}_{s2}", "~", "~", "<", f"gettingnextdigits{a}_{b}_{s1}_{s2}_-", cmd)
                for d in digits:
                    write(f"goingtonextdigits{a}_{b}_{s1}_{s2}", d, d, ">", f"stillgoingtonextdigits{a}_{b}_{s1}_{s2}", cmd)
                write(f"stillgoingtonextdigits{a}_{b}_{s1}_{s2}", "!", "!", "<", f"getnextdigits{a}_{b}_{s1}_{s2}", cmd)

    for n in [True, False]:
        write(f"removezeros{a}_{n}", "0", "", "<", f"removezeros{a}_{n}", cmd)
        for d in non_minus_digits:
            if d == "0":
                continue
            write(f"removezeros{a}_{n}", d, d, ">", f"addnegativesign{a}" if n else f"copyback{a}", cmd)
        write(f"removezeros{a}_{n}", "!", "0", ">", f"copyback{a}", cmd)
    write(f"addnegativesign{a}", "", "-", ">", f"copyback{a}", cmd)
    
    for s in ["addnegativesign", "copyback"]:
        for d in digits:
            write(f"{s}{a}", d, d, ">", f"{s}{a}", cmd)
    write(f"copyback{a}", "", "", "<", f"copybackhere{a}", cmd)
    for d in digits:
        write(f"copybackhere{a}", d, "", "<", f"copyback{a}_{d}", cmd)
        for e in digits + ["!", "~"]:
            write(f"copyback{a}_{d}", e, e, "<", f"copyback{a}_{d}", cmd)
        for e in ";#":
            write(f"copyback{a}_{d}", e, e, ">", f"drophere{a}_{d}", cmd)
        for e in digits:
            write(f"copyback{a}_{d}", f"!{e}", e, ">", f"drophere{a}_{d}", cmd)
        for e in "!~":
            write(f"drophere{a}_{d}", e, f"!{d}", ">", f"keepcopying{a}", cmd)

    for d in digits + ["!", "~"]:
        write(f"keepcopying{a}", d, d, ">", f"keepcopying{a}", cmd)
    write(f"keepcopying{a}", "", "", "<", f"copybackhere{a}", cmd)

    for d in "!~":
        write(f"copybackhere{a}", d, "", "<", f"copybackhere{a}", cmd)
    
    for d in non_minus_digits:
        write(f"copybackhere{a}", f"!{d}", d, ">", f"getready{a}", cmd)
    
    write(f"getready{a}", "", "", "<", f"ready{a+1}", cmd)

def lshift_cmd(a, line):
    cmd = "LSHIFT"
    amount = int(line[1])

    write(f"ready{a}", "", "", ">", "runtime_error", cmd)
    for d in digits:
        write(f"ready{a}", d, d, "<", f"ready{a}", cmd)
    for d in ";#":
        write(f"ready{a}", d, d, ">", f"checkfirst{a}", cmd)
    for d in digits:
        if d == "0":
            continue
        write(f"checkfirst{a}", d, d, ">", f"fine{a}", cmd)
    for d in non_minus_digits:
        write(f"fine{a}", d, d, ">", f"fine{a}", cmd)
    write(f"fine{a}", "", "", "<", f"sready{a}", cmd)

    write(f"checkfirst{a}", "0", "0", ">", f"getready{a}", cmd)
    write(f"getready{a}", "", "", "<", f"ready{a+1}", cmd)

    write(f"sready{a}", "", "", ">", "runtime_error", cmd)
    for d in digits:
        write(f"sready{a}", d, d, ">", f"add{a}_0", cmd)
    for i in range(amount+1):
        write(f"add{a}_{i}", "", "0" if i < amount else "", ">" if i < amount else "<", f"add{a}_{i+1}" if i < amount else f"ready{a+1}", cmd)

def rshift_cmd(a, line):
    cmd = "RSHIFT"
    amount = int(line[1])

    write(f"ready{a}", "", "", ">", "runtime_error", cmd)
    for d in digits:
        write(f"ready{a}", d, d, ">", f"startremoving{a}", cmd)
    write(f"startremoving{a}", "", "", "<", f"remove{a}_0", cmd)
    for i in range(amount):
        for d in non_minus_digits:
            write(f"remove{a}_{i}", d, "", "<", f"remove{a}_{i+1}", cmd)
    for i in range(amount+1):
        write(f"remove{a}_{i}", "-", "0", ">", f"getready{a}", cmd)
        for d in ";#":
            write(f"remove{a}_{i}", d, d, ">", f"putzeroback{a}", cmd)
    write(f"putzeroback{a}", "", "0", ">", f"getready{a}", cmd)
    write(f"getready{a}", "", "", "<", f"ready{a+1}", cmd)
    for d in non_minus_digits:
        write(f"remove{a}_{amount}", d, d, ">", f"getready{a}", cmd)

def reverse_cmd(a, line):
    # TODO remove leading zeros
    cmd = "REVERSE"

    write(f"ready{a}", "", "", ">", f"runtime_error", cmd)
    for d in non_minus_digits:
        write(f"ready{a}", d, d, ">", f"dropmarker{a}", cmd)
    write(f"dropmarker{a}", "", "!", "<", f"get{a}", cmd)
    for d in non_minus_digits:
        write(f"get{a}", d, d, "<", f"get{a}", cmd)
    for d in ";#-!":
        write(f"get{a}", d, d, ">", f"gethere{a}", cmd)
    for d in non_minus_digits:
        write(f"gethere{a}", d, "!", ">", f"carrying{a}_{d}", cmd)
        for e in non_minus_digits + ["!"]:
            write(f"carrying{a}_{d}", e, e, ">", f"carrying{a}_{d}", cmd)
        write(f"carrying{a}_{d}", "", d, "<", f"gotoget{a}", cmd)
    write(f"gotoget{a}", "!", "!", "<", f"goingtoget{a}", cmd)
    write(f"goingtoget{a}", "!", "!", "<", f"goingtoget{a}", cmd)
    for d in non_minus_digits:
        write(f"gotoget{a}", d, d, "<", f"gotoget{a}", cmd)
        write(f"goingtoget{a}", d, d, "<", f"get{a}", cmd)
    for d in ";#-":
        write(f"goingtoget{a}", d, d, ">", f"copy{a}", cmd)
    for d in non_minus_digits + ["!"]:
        write(f"copy{a}", d, d, ">", f"copy{a}", cmd)
    write(f"copy{a}", "", "", "<", f"copyhere{a}", cmd)
    for d in non_minus_digits:
        write(f"copyhere{a}", d, "", "<", f"copying{a}_{d}", cmd)
        for e in non_minus_digits:
            write(f"copying{a}_{d}", e, e, "<", f"copying{a}_{d}", cmd)
        write(f"copying{a}_{d}", "!", "!", "<", f"copyinghere{a}_{d}", cmd)
        write(f"copyinghere{a}_{d}", "!", "!", "<", f"copyinghere{a}_{d}", cmd)
        for e in non_minus_digits + [";", "#", "-"]:
            write(f"copyinghere{a}_{d}", e, e, ">", f"drophere{a}_{d}", cmd)
        write(f"drophere{a}_{d}", "!", d, ">", f"copy{a}", cmd)
    write(f"copyhere{a}", "!", "", "<", f"ready{a+1}", cmd)

        
def last_cmd(a, line):
    # TODO remove leading zeros
    cmd = "LAST"
    amount = int(line[1])

    write(f"ready{a}", "", "", ">", f"runtime_error", cmd)

    for d in non_minus_digits:
        write(f"ready{a}", d, f"!{d}", "<", f"protect{a}_0", cmd)
    
    for i in range(amount-1):
        for d in non_minus_digits:
            write(f"protect{a}_{i}", d, f"!{d}", "<", f"protect{a}_{i+1}", cmd)
        for d in ";#":
            write(f"protect{a}_{i}", d, d, ">", f"copyback{a}", cmd)
        write(f"protect{a}_{i}", "-", "!", ">", f"copyback{a}", cmd)
    
    for d in non_minus_digits:
        write(f"protect{a}_{amount-1}", d, "!", "<", f"protect{a}_{amount-1}", cmd)
    for d in ";#":
        write(f"protect{a}_{amount-1}", d, d, ">", f"copyback{a}", cmd)
    write(f"protect{a}_{amount-1}", "-", "!", ">", f"copyback{a}", cmd)
    write(f"copyback{a}", "!", "!", ">", f"copyback{a}", cmd)
    for d in non_minus_digits:
        write(f"copyback{a}", f"!{d}", "!", "<", f"copying{a}_{d}", cmd)
        write(f"copying{a}_{d}", "!", "!", "<", f"copying{a}_{d}", cmd)
        for e in digits + [";", "#"]:
            write(f"copying{a}_{d}", e, e, ">", f"drophere{a}_{d}", cmd)
        write(f"drophere{a}_{d}", "!", d, ">", f"copyback{a}", cmd)
    write(f"copyback{a}", "", "", "<", f"cleanup{a}", cmd)
    write(f"cleanup{a}", "!", "", "<", f"cleanup{a}", cmd)
    for d in non_minus_digits:
        write(f"cleanup{a}", d, d, ">", f"getready{a}", cmd)
    write(f"getready{a}", "", "", "<", f"ready{a+1}", cmd)

def digits_cmd(a, line):
    cmd = "DIGITS"

    write(f"ready{a}", "", "", ">", f"runtime_error", cmd)

    for d in non_minus_digits:
        write(f"ready{a}", d, "!", ">", f"extend{a}", cmd)
        write(f"sready{a}", d, "!", ">", f"inc{a}", cmd)
    write(f"extend{a}", "", "!", ">", f"inc{a}", cmd)
    write(f"sready{a}", "!", "!", "<", f"sready{a}", cmd)
    for d in ";#":
        write(f"sready{a}", d, d, ">", f"copy{a}", cmd)
    write(f"sready{a}", "-", "!", ">", f"copy{a}", cmd)
    write(f"inc{a}", "!", "!", ">", f"inc{a}", cmd)
    write(f"inc{a}", "", "1", "<", f"goback{a}", cmd)
    write(f"dropcarry{a}", "", "1", "<", f"goback{a}", cmd)
    for d in non_minus_digits:
        write(f"goback{a}", d, d, "<", f"goback{a}", cmd)
    write(f"goback{a}", "!", "!", "<", f"sready{a}", cmd)
    for d in non_minus_digits:
        ans, c = add_together(False, False, d, "1", False, True)
        write(f"inc{a}", d, ans, ">" if c else "<", f"dropcarry{a}" if c else f"goback{a}", cmd)
    
    for d in non_minus_digits + ["!"]:
        write(f"copy{a}", d, d, ">", f"copy{a}", cmd)
    write(f"copy{a}", "", "", "<", f"copyhere{a}", cmd)
    for d in non_minus_digits:
        write(f"copyhere{a}", d, "", "<", f"copying{a}_{d}", cmd)
        for e in non_minus_digits:
            write(f"copying{a}_{d}", e, e, "<", f"copying{a}_{d}", cmd)
        write(f"copying{a}_{d}", "!", "!", "<", f"copyinghere{a}_{d}", cmd)
        write(f"copyinghere{a}_{d}", "!", "!", "<", f"copyinghere{a}_{d}", cmd)
        for e in non_minus_digits + [";", "#"]:
            write(f"copyinghere{a}_{d}", e, e, ">", f"drophere{a}_{d}", cmd)
        write(f"drophere{a}_{d}", "!", d, ">", f"copy{a}", cmd)
    write(f"copyhere{a}", "!", "", "<", f"cleanup{a}", cmd)
    write(f"cleanup{a}", "!", "", "<", f"cleanup{a}", cmd)
    for d in non_minus_digits:
        write(f"cleanup{a}", d, d, ">", f"getready{a}", cmd)
    write(f"getready{a}", "", "", "<", f"ready{a+1}", cmd)

def label(l):
    def dec(func):
        func.label = l
        return func
    return dec

@label("integer")
def number(x):
    for i, d in enumerate(x):
        if d not in digits and (i == 0 or d != "-"):
            return False
    return len(x) > 0 and (x[0] != "-" or len(x) > 1)

@label("natural number")
def natural_number(x):
    for i, d in enumerate(x):
        if d not in non_minus_digits:
            return False
    return True

@label("positive integer")
def positive_number(x):
    for i, d in enumerate(x):
        if d not in non_minus_digits:
            return False
    return int(x) > 0

@label("variable name")
def var_name(x):
    return re.match(r"^[A-Za-z_][A-Za-z0-9-_]*$", x)

@label("valid_label")
def valid_label(x):
    return True

commands = {
    "PUSH": [[number], push_cmd],
    "PUSHADDR": [[number], lambda a, line: push_cmd(a, ['PUSH', str(a+int(line[1]))])],
    "POP": [[], pop_cmd],
    "SET": [[var_name], set_cmd],
    "LOAD": [[var_name], load_cmd],
    "UNSET": [[var_name], unset_cmd],
    "JUMP": [[number], jump_cmd],
    "JLZ": [[number], jlz_cmd],
    "GOTO": [[valid_label], goto_cmd],
    "RETURN": [[], return_cmd],
    "ADD": [[], add_cmd],
    "SUB": [[], lambda a, line: add_cmd(a, line, subtract_together, True)],
    "LSHIFT": [[natural_number], lshift_cmd],
    "RSHIFT": [[natural_number], rshift_cmd],
    "REVERSE": [[], reverse_cmd],
    "LAST": [[positive_number], last_cmd],
    "DIGITS": [[], digits_cmd]
}

for a, line in enumerate(src):
    cmd = line[0].upper()
    if cmd.startswith(":"):
        jump_cmd(a, ["JUMP", "0"])
    elif cmd in commands:
        validators, function = commands[cmd]
        if len(line) != len(validators)+1:
            print(f"Line {a+1}. Command {cmd} takes {len(validators)} argument{'s' if len(validators) != 1 else ''}, but got {len(line)-1}")
            sys.exit()
        for i, arg in enumerate(line[1:]):
            if not validators[i](arg):
                print(f"Line {a+1}. Command {cmd} requires argument {i} to be a {validators[i].label}")
                sys.exit()
        function(a, line)
    else:
        print(f"Line {a+1}. Unknown command: {cmd}")
        sys.exit()

for d in digits + [";", ""]:
    write(f"ready{len(src)}", d, d, ">", "done")