import tkinter as tk


# todo add gui component that makes this applet more functional
# todo load small/mid-sized images into a file system
# todo create file that saves and logs images
# todo create layer in GUI that reads file and loads image
# todo create drag and drop functionality


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
