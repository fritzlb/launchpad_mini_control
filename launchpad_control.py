import sys
import time
import rtmidi
import datetime
import tkinter as tk
import tkinter.messagebox
from functools import partial


class launchpad_button(tk.Button):
    mididevice = None
    def __init__(self, *args, buttonID=0, midicommandLed=144, **kwargs):
        self.midicommand_led = midicommandLed
        self.button_id = buttonID
        self.set_color(0, 0)
        super().__init__(*args, **kwargs)

    def set_color(self, red, green, blink=False):
        self.red = red
        self.green = green
        self.blink = blink
        if not self.mididevice:
            raise Exception("No mididevice specified.")
        if blink:
            self.color = 16*green+red+8
        else:
            self.color = 16*green+red+12
        self.mididevice.send_message([self.midicommand_led, self.button_id, self.color])
        #print([self.midicommand_led, self.button_id, self.color])


def update_color(button, red, green, blink):
    button.set_color(red, green, blink)

def button_handler(button_str):
    button = globals()[button_str]
    print(button_str)
    colorwindow = tk.Tk()
    colorwindow.title("Set Color "+button_str)
    red = 0
    redslider = tk.Scale(colorwindow, from_=3, to=0)
    redslider.pack()
    green = 0
    greenslider = tk.Scale(colorwindow, from_=3, to=0)
    greenslider.pack()

    blinkvar = tk.IntVar(master=colorwindow)
    blinkvar.set(0)
    
    blink_checkbox = tk.Checkbutton(colorwindow, text="blink", variable=blinkvar, onvalue=1, offvalue=0)
    blink_checkbox.pack()

    okbutton = tk.Button(colorwindow, text="Update", command=lambda: update_color(button, redslider.get(), greenslider.get(), blinkvar.get()))
    okbutton.pack()
    colorwindow.mainloop()







if __name__ == "__main__":
    print(datetime.datetime.now().strftime("%H:%M:%S"))


    midiout = rtmidi.MidiOut()
    midi_opened = False
    available_ports = midiout.get_ports()
    for port_nr in range(len(available_ports)):
        if available_ports[port_nr].find("Launchpad Mini 16") > -1:
            midiout.open_port(port_nr)
            midi_opened = True
    if not midi_opened:
        tk.messagebox.showerror("Connection error.", "Launchpad Mini couldn't be detected. Make sure to connect it.")
        sys.exit()

    try:
        midiout.send_message([176, 0, 0])
    except:
        pass
    midiout.send_message([176, 0, 127])
    midiout.send_message([176, 0, 40]) #enable blinking

    time.sleep(2)
    launchpad_button.mididevice = midiout

    mainwindow = tk.Tk()
    mainwindow.title("Launchpad Control")
    mainwindow.geometry("700x700")



    #Buttons
    button_size = 40
    button_space = 20
    pixel = tk.PhotoImage(width=1, height=1)
    margin_top_left = 20
    labels_grid = ["A", "B", "C", "D", "E", "F", "G", "H"]
    buttons = []

    #Buttons top
    for i in range(8):
        globals()["Btn"+str(i)] = launchpad_button(mainwindow, buttonID=104+i, midicommandLed=176, text=str(i+1), height=button_size, width=button_size, compound="c", image=pixel, command=partial(button_handler, "Btn"+str(i)))
        globals()["Btn"+str(i)].place(x=(button_size+button_space)*i+margin_top_left, y=margin_top_left)
        buttons.append(globals()["Btn"+str(i)])

    #Button grid:
    for i in range(8): # 8 Zeilen
        for j in range(8): # 8 Spalten
            globals()["Btn"+labels_grid[i]+str(j)] = launchpad_button(mainwindow, buttonID=16*i+j, text=labels_grid[i]+str(j+1), height=button_size, width=button_size, compound="c", image=pixel, command=partial(button_handler, "Btn"+labels_grid[i]+str(j)))
            globals()["Btn"+labels_grid[i]+str(j)].place(x=(button_size+button_space)*j+margin_top_left, y=(button_size+button_space)*(i+1.2)+margin_top_left)
            buttons.append(globals()["Btn"+labels_grid[i]+str(j)])
            
    #Buttons right:
    for i in range(8):
        globals()["Btn"+labels_grid[i]] = launchpad_button(mainwindow, buttonID=16*i+8, text=labels_grid[i], height=button_size, width=button_size, compound="c", image=pixel, command=partial(button_handler, "Btn"+labels_grid[i]))
        globals()["Btn"+labels_grid[i]].place(y=(button_size+button_space)*i+margin_top_left+(button_size+button_space)*1.2, x=margin_top_left+8.2*(button_size+button_space))
        buttons.append(globals()["Btn"+labels_grid[i]])
    
    mainwindow.mainloop()

    del midiout
