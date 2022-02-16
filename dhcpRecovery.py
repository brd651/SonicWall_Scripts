from tkinter import *
from tkinter import filedialog
from tkinter import ttk

UI_REFRESH = 100  # your preferred refresh rate in milleseconds
UI_DELTA = 0.000001  # nanosecond scale iterative filter step size
UI_DEPTH = 10  # depth of ui_refreshes moving average
DEBUG = False

window = Tk()
window.title("DHCP Recovery")
window.geometry('400x75')
# window.maxsize(800, 500)


dhcpconfigs = {}


def selectfile():
    filename = filedialog.askopenfile()
    showname.config(text=filename.name)
    runbtn.config(state=NORMAL)
    return filename.name


def dhcprun():
    tsr = showname.cget("text")
    with open(tsr, 'r', encoding="cp1252", errors="replace") as t:
        for line in t:
            if "--DHCP Server--" in line:
                break
            else:
                continue
        for line in t:
            if "Pool Entry" in line:
                pool = line.strip()
                dhcpconfigs[pool] = {}
            elif "option" in line:

                continue
            elif "Current leases" in line:
                break
            else:
                try:
                    dhcpconfigs[pool][line.split("=")[0].strip()] = line.split("=")[
                        1].strip()
                except:
                    continue

    commands = ["dhcp-server\n"]

    for key in dhcpconfigs.keys():

        # Set dns var to nothing for use later
        dns = ""

        for f in dhcpconfigs[key]["Flags"].split(" "):
            if "DYNAMIC" in f:
                commands.insert(len(commands) - 1,
                                "\nscope dynamic " + dhcpconfigs[key]["Range Start"] + " " + dhcpconfigs[key]["Range End"] + "\n")
            elif "STATIC" in f:
                mac = dhcpconfigs[key]["MAC"].split("  ")[0].replace(" ", "")
                commands.insert(len(commands) - 1,
                                "\nscope static " + dhcpconfigs[key]["IP"] + " " + mac + "\n")
            elif "IS_ACTIVE" in f:
                commands.append("enable\n")
            elif "PROPAGATE_DNS_SETTINGS" in f:
                dns = "inherit"
                commands.append("dns server inherit\n")
        for inkey in dhcpconfigs[key].keys():
            if inkey == "Lease Period":
                commands.append(
                    "lease-time " + dhcpconfigs[key][inkey].split(" ")[0] + "\n")
            elif inkey == "Default Gateway":
                commands.append("default-gateway " +
                                dhcpconfigs[key][inkey] + "\n")
            elif inkey == "Subnet Mask":
                commands.append("netmask " + dhcpconfigs[key][inkey] + "\n")
            elif inkey == "Comment":
                if dhcpconfigs[key][inkey] is "":
                    commands.append("no comment\n")
                else:
                    commands.append(
                        "comment" + dhcpconfigs[key][inkey] + "\n")
            elif inkey == "Domain Name":
                if dhcpconfigs[key][inkey] is "":
                    commands.append("no domain-name\n")
                else:
                    commands.append(
                        "domain-name" + dhcpconfigs[key][inkey] + "\n")
            elif inkey == "DNS Servers":
                if dns is "inherit":
                    continue
                else:
                    dnum = 0
                    for d in dhcpconfigs[key][inkey].split("  "):
                        if dnum is 0:
                            commands.append(
                                "dns server static primary " + d + "\n")
                            dnum += 1
                        elif dnum is 1:
                            commands.append(
                                "dns server static secondary " + d + "\n")
                            dnum += 1
                        elif dnum is 2:
                            commands.append(
                                "dns server static tertiary " + d + "\n")
                            dnum += 1
            elif inkey == "WINS Servers":

                wnum = 0

                if dhcpconfigs[key][inkey] == "":
                    commands.append("no wins primary\nno wins secondary\n")
                else:
                    for w in dhcpconfigs[key][inkey].split("  "):
                        if wnum is 0:
                            commands.append(
                                "wins primary " + w + "\n")
                            wnum += 1
                        elif wnum is 1:
                            commands.append(
                                "wins secondary " + w + "\n")
            elif inkey == "VoIP Call Managers":
                vnum = 0

                if dhcpconfigs[key][inkey] == "":
                    commands.append(
                        "no call-manager primary\nno call-manager secondary\nno call-manager tertiary\n")
                else:
                    for v in dhcpconfigs[key][inkey].split("  "):
                        if vnum is 0:
                            commands.append(
                                "call-manager primary " + w + "\n")
                            vnum += 1
                        elif vnum is 1:
                            commands.append(
                                "call-manager secondary " + v + "\n")
                        elif vnum is 2:
                            commands.append(
                                "call-manager tertiary " + v + "\n")
            elif inkey == "Next Server":
                if dhcpconfigs[key][inkey].strip() == "0.0.0.0":
                    commands.append("no network-boot next-server\n")
                else:
                    commands.append(
                        "network-boot next-server " + dhcpconfigs[key][inkey] + "\n")
            elif inkey == "Boot File":
                if dhcpconfigs[key][inkey] is "":
                    commands.append("no network-boot boot-file\n")
                else:
                    commands.append("network-boot next-server " +
                                    dhcpconfigs[key][inkey] + "\n")
            elif inkey == "Server Name":
                if dhcpconfigs[key][inkey] is "":
                    commands.append("no network-boot server-name\n")
                else:
                    commands.append("network-boot server-name " +
                                    dhcpconfigs[key][inkey] + "\n")
        commands.append("exit\n")
    commands.append("commit best\n")

    scrollbar1.pack(side="right", fill="y")
    scrollbar1.config(command=cmdoutput.yview)
    cmdoutput.pack(side="left", fill="both", expand=True)
    frame1.grid(column=0, row=3, columnspan=3)

    for c in commands:
        cmdoutput.insert(INSERT, c)
    window.geometry("")
    copybtn.config(state=NORMAL)
    cmdoutput.config(state=DISABLED)

    popupmsg()


def popupmsg():
    popup = Tk()
    popup.wm_title("!")
    label = ttk.Label(
        popup, text="DHCP Generic Options need to be configured manaully\n For everything else just go into Config mode \nand copy the commands in the other wind")
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()


def readit():
    print(dhcpconfigs)


def copycmds():
    window.clipboard_clear()
    window.clipboard_append(cmdoutput.get(1.0, "end-1c"))
    return


btn = Button(window, text="Select File", command=selectfile)
btn.grid(column=0, row=0)

showname = Label(window)
showname.grid(column=1, row=0, sticky=W, columnspan=2)

runbtn = Button(text="Run", state=DISABLED, command=dhcprun)
runbtn.grid(column=0, row=1)

if DEBUG is True:
    readbtn = Button(text="Read", state=NORMAL, command=readit)
    readbtn.grid(column=1, row=1, sticky=W)

copybtn = Button(text="Copy Commands", state=DISABLED, command=copycmds)
copybtn.grid(column=2, row=1, sticky=W)

frame1 = Frame(window, width=100, height=80,
               borderwidth=1, relief="sunken")
scrollbar1 = Scrollbar(frame1)
cmdoutput = Text(frame1, width=50, height=50, wrap="word",
                 yscrollcommand=scrollbar1.set, borderwidth=0, highlightthickness=0)

window.mainloop()
