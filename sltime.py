import time
from Tkinter import *
import Queue
from bussinfo import NextBusChecker
from pynrk import YR


class NextBusVisualization:
    def __init__(self, busInfoQueue):
        self.root = None
        self.canvas = None
        self.busInfo = None
        self.busInfoQueue = busInfoQueue
        self.nextBusLabel = None
        self.isBlinking = False

    def start(self):



        # Start Tkinter
        self.root = Tk()
        self.root.title("almy")

        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.root.overrideredirect(True)
        self.root.geometry("{0}x{1}+0+0".format(w, h))

        quit = Button(self.canvas,  text="QUIT", command=self.root.destroy)
        quit.place(relx=1, x=-2, y=2, anchor=NE)
        quit.pack()

        # Draw GUI
        self.canvas = Canvas(self.root, width=w, height=h, background="white", cursor='none')
        self.canvas.pack(expand=YES, fill=BOTH)

        self.nextBusLabel = Label(self.canvas, text="Startar...", font=("Helvetica", -int(h / 1.5)), background="white")
        self.nextBusLabel.pack()
        self.canvas.create_window(w / 2, h / 2, window=self.nextBusLabel)

        self.root.after(0, self.updateLoop())
        self.root.mainloop()

    def updateLoop(self):
        while True:
            # Only redraw if new item in busInfoQueue
            if not self.busInfoQueue.empty():
                self.busInfo = self.busInfoQueue.get()
            self.redraw()
            time.sleep(0.5)

    def redraw(self):
        # Draw busInfo
        if self.busInfo:
            if self.isBlinking:
                if self.busInfo.error_with_data:
                    symbol = "?"
                else:
                    symbol = "."
            else:
                symbol = " "
            self.isBlinking = not self.isBlinking

            if self.busInfo.bus_is_coming:
                text = "%s" % self.busInfo.minutes_to_next_bus
            else:
                text = "Zzz"
            text = "%s%s" % (text, symbol)
            self.nextBusLabel.config(text=text)
            self.canvas.update()


if __name__ == "__main__":
    busInfoQueue = Queue.Queue()
    weatherInfoQueue = Queue.Queue()
    weather = YR("Sweden/Stockholm/Stockholm/", "2015-12-21", weatherInfoQueue)
    next_bus_checker = NextBusChecker(busInfoQueue)
    next_bus_checker.daemon = True
    next_bus_checker.start()
    nextBusVisualization = NextBusVisualization(busInfoQueue)
    nextBusVisualization.start()
