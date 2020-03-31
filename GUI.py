import PySimpleGUIQt as sg
from manager import manage
import os.path

sg.ChangeLookAndFeel('GreenTan')
# sg.SetOptions(text_color='white')
# ------ Column Definition ------ #
column1 = [[sg.Text('Column 1', background_color='lightblue',text_color='black', justification='center', size=(100,22))],
           [sg.Spin((1,10), size=(100,22))],
           [sg.Spin((1,10), size=(100,22))],
           [sg.Spin((1,10), size=(100,22))],]

if os.path.isfile('full collection.xlsx'):
    filename = 'full collection.xlsx'
else:
    filename = 'Default File'

layout = [
    [sg.Text('Choose A Folder')],
    [sg.Text('Your Folder'),
     sg.InputText(filename, size=(300,50)), sg.FileBrowse(), sg.Stretch()],
    [sg.Submit(tooltip='Click to submit this form',), sg.Cancel()]]

window = sg.Window('Everything bagel',
                   grab_anywhere=False,
                   font=('Helvetica', 12),
                   no_titlebar=False,
                   alpha_channel=1,
                   keep_on_top=False,
                   element_padding=(2,3),
                   default_element_size=(100, 23),
                   default_button_element_size=(120,30),
                   # background_image='C:\Python\PycharmProjects\GooeyGUI\logo500black.png',
                   ).Layout(layout)
event, values = window.Read()
print(event, values)
print(values[0].replace('file:///', '')) # this gets rid of file:///
filename = values[0].replace('file:///', '')
window.Close()

if os.path.isfile(filename):
    manage(filename)
    sg.Popup('Title',
             'The results of the window.',
             'The button clicked was "{}"'.format(event),
             'The values are', values, )
else:
    sg.Popup('Title',
             'your filename was inaccurate')




# todo load small/mid-sized images into a file system
# todo create file that saves and logs images
# todo create layer in GUI that reads file and loads image
# todo progress bar
# todo settings bar
# todo add visual polish
