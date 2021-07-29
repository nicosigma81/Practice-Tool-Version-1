
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import datetime
import os
from random import randint
from time import sleep
from playsound import playsound

now = str(datetime.datetime.now())
now = now[:-10]

metronomeOn = False

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Practice Tool')
        self.setWindowIcon(QtGui.QIcon('python logo.ico'))

        # Tab Widget

        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(FirstWidget(), "Practice Log")
        tabWidget.addTab(SecondWidget(), "Scale Randomizer")

        self.form_widget = tabWidget
        _widget = QtWidgets.QWidget()
        _layout = QtWidgets.QVBoxLayout(_widget)
        _layout.addWidget(self.form_widget)
        self.setCentralWidget(_widget)

        # Menu bar

        extractAction = QtWidgets.QAction('&Exit', self)
        extractAction.setShortcut('Ctrl+Q')
        extractAction.setStatusTip('Leave The App')
        extractAction.triggered.connect(sys.exit)

        debug = QtWidgets.QAction('&Debug', self)
        debug.setShortcut('Ctrl+D')
        debug.triggered.connect(FirstWidget.debug)

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractAction)
        fileMenu.addAction(debug)

        self.show()

    def resizeEvent(self, event):
        self.setFocus()


class FirstWidget(QtWidgets.QWidget):

    def __init__(self):
        super(FirstWidget, self).__init__()

        self.init_gui()

    def init_gui(self):
        # Initialize widgets

        # Left side:

        self.logList = QtWidgets.QListWidget(self)
        self.logList.clicked.connect(self.readEntries)  # Read log entries if log is clicked
        self.logList.setDragDropMode(4)
        self.logList.doubleClicked.connect(self.edit_logs_handler)

        self.label = QtWidgets.QLabel(self)
        self.label.setText("Open log:")

        self.addLogLine = QtWidgets.QLineEdit(self)
        self.addLogLine.returnPressed.connect(self.addLog)

        self.addLogBtn = QtWidgets.QPushButton(self)
        self.addLogBtn.setText("Add")
        self.addLogBtn.clicked.connect(self.addLog)  # Add a log to the log list if button is pressed

        # Dividing line:

        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Right side:

        self.entryList = QtWidgets.QListWidget(self)
        self.entryList.setSelectionMode(3)
        self.entryList.doubleClicked.connect(self.edit_entries_handler)

        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setText("Entries:")

        self.addEntryLine = QtWidgets.QLineEdit(self)
        self.addEntryLine.returnPressed.connect(self.addEntry)

        self.addEntryBtn = QtWidgets.QPushButton(self)
        self.addEntryBtn.setText("Add")
        self.addEntryBtn.clicked.connect(self.addEntry)  # Add an entry to the entry list of a selected log if button is pressed

        self.label_4 = QtWidgets.QLabel(self)
        self.label_4.setText("Total Hours Practiced:")

        self.hoursLbl = QtWidgets.QLabel(self)
        self.hoursLbl.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.hoursLbl.setFrameShadow(QtWidgets.QFrame.Raised)
        self.hoursLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hoursLbl.setText('0')

        # Initialize edit lines

        self.editLine = QtWidgets.QLineEdit(self)
        self.editLine.editingFinished.connect(self.editLine.hide)
        self.editLine.returnPressed.connect(self.edit_entries)

        self.logLine = QtWidgets.QLineEdit(self)
        self.logLine.editingFinished.connect(self.logLine.hide)
        self.logLine.returnPressed.connect(self.edit_logs)

        # Initialize error dialog

        self.error_dialog = QtWidgets.QErrorMessage()

        # Read the log list

        self.readLogs()

        # Set Layout

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.addLogLine)
        hbox.addWidget(self.addLogBtn)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.addEntryLine)
        hbox2.addWidget(self.addEntryBtn)

        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.addWidget(self.label_4)
        hbox3.addWidget(self.hoursLbl)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.logList)
        vbox.addLayout(hbox)

        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addWidget(self.label_2)
        vbox2.addWidget(self.entryList)
        vbox2.addLayout(hbox2)
        vbox2.addLayout(hbox3)

        hboxMain = QtWidgets.QHBoxLayout()
        hboxMain.addLayout(vbox)
        hboxMain.addWidget(self.line)
        hboxMain.addLayout(vbox2)

        self.setLayout(hboxMain)

        # Show GUI

        self.show()
        self.editLine.hide()
        self.logLine.hide()

    # Delete key pressed event

    def keyPressEvent(self, event):
        print("event", event)
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_key_pressed()

    # Read logs and entries

    def readLogs(self):
        directory = os.path.dirname(os.path.abspath('app.py'))
        files = os.listdir(directory)
        self.logList.clear()
        for file in files:
            if not file == 'instrumentFile.txt':
                if not file == 'transpositionFile.txt':
                    if '.txt' in file:
                        self.logList.addItem(file[:-4])

    def readEntries(self):
        item = self.logList.currentItem()
        itemName = str(item.text()) + '.txt'
        self.entryList.clear()
        itemSelected = bool(self.logList.selectedItems())
        if itemSelected:
            with open(itemName, 'r') as file:  # Read selected log files into entry list
                lines = file.readlines()
                for line in lines:
                    if not line[:6] == 'Total:':
                        self.entryList.addItem(line[:-1])
            self.read_total(str(itemName))
        else:
            self.entryList.clear()

    def read_total(self, log):
        if not isinstance(log, str):
            return
        with open(log, 'r') as file:
            lines = file.readlines()
            total = 0.00
            linesStr = ''
            if lines:
                for line in lines[:-1]:
                    linesStr += line
                    entry = self.partition_entry(line)[2].lstrip()[:-4]
                    entryAmount = float(entry) / 60
                    total += entryAmount
        with open(log, 'w') as file:
            file.write(linesStr)
            file.write('Total: ' + str(total))
        self.hoursLbl.setText('{0:.{1}f}'.format(total, 2))

    # Add logs and entries

    def addLog(self):
        newLog = self.addLogLine.text().rstrip()
        logFile = newLog + '.txt'
        self.addLogLine.clear()
        if newLog:
            path = os.path.dirname(os.path.abspath('app.py'))
            files = os.listdir(path)
            for file in files:
                if logFile == file:
                    choice = QtWidgets.QMessageBox.question(self, 'Replace file',
                                                                 f'A log named "{newLog}" already exists. Do you want to overwrite it?',
                                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                                 QtWidgets.QMessageBox.No)
                    if choice == QtWidgets.QMessageBox.Yes:
                        open(logFile, 'w').close()
                        self.readLogs()
                        self.logList.setCurrentRow(self.logList.count())
                        self.readEntries()
                        return
                    else:
                        return
            open(logFile, 'x').close()
            self.readLogs()
            self.logList.setCurrentRow(self.logList.count())

    def addEntry(self):
        itemSelected = bool(self.logList.selectedItems())
        if not itemSelected:
            return
        newEntry = str(self.addEntryLine.text())
        if not self.addEntryLine.text().isdigit():
            self.error_dialog.showMessage('Entry must be an integer.')
            return
        self.addEntryLine.clear()
        if newEntry:
            newEntry = f'{str(self.entryList.count() + 1)}      |      {now}      |      {newEntry} min'
            item = self.logList.currentItem()
            itemName = str(item.text()) + '.txt'
            with open(itemName, 'r') as file:
                lines = file.readlines()
            writeLines = ''
            for line in lines[:-1]:
                writeLines += line
            with open(itemName, 'w') as file:
                file.write(writeLines)
                file.write(newEntry + '\n')
                file.write(lines[-1])
            self.entryList.addItem(newEntry)
            self.read_total(itemName)

    # Delete logs and entries

    def delete_key_pressed(self):
        row = self.entryList.currentRow()
        itemSelected = self.entryList.selectedItems()
        if bool(itemSelected):
            if len(itemSelected) == 1:
                choice = QtWidgets.QMessageBox.question(self, 'Delete Item',
                                                        'Do you want to delete entry ' + str(row + 1) + '?',
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                        QtWidgets.QMessageBox.No)
                if choice == QtWidgets.QMessageBox.Yes:
                    rows = [row]
                    self.delete_entries(rows)
            elif len(itemSelected) > 1:
                pass
                rowi = self.entryList.row(itemSelected[0])
                rowf = self.entryList.row(itemSelected[-1])
                choice = QtWidgets.QMessageBox.question(self, 'Delete Items',
                                                        'Do you want to delete entries ' + str(rowi + 1) + ' to ' + str(rowf + 1) + '?',
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                        QtWidgets.QMessageBox.No)
                if choice == QtWidgets.QMessageBox.Yes:
                    rows = []
                    for entry in itemSelected:
                        row = int(self.entryList.row(entry))
                        rows.append(row)
                    self.delete_entries(rows)

        else:
            itemSelected = self.logList.selectedItems()
            if bool(itemSelected):
                item = self.logList.currentItem().text()
                choice = QtWidgets.QMessageBox.question(self, 'Delete Item',
                                                        'Do you want to delete ' + str(item) + '?',
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                        QtWidgets.QMessageBox.No)
                if choice == QtWidgets.QMessageBox.Yes:
                    self.delete_logs(self.logList.currentRow())

    def delete_logs(self, row):
        item = self.logList.item(row).text()
        if not os.path.exists(item + '.txt'):
            return
        os.remove(item + '.txt')
        self.readLogs()
        if row == 0:
            self.entryList.clear()
            return
        self.logList.setCurrentRow(row - 1)
        self.readEntries()

    def delete_entries(self, rows):
        log = self.logList.currentItem().text() + '.txt'
        with open(log, 'r') as file:
            lines = file.readlines()
        for row in rows:
            item = self.entryList.item(row).text()
            lines.remove(item + '\n')
        writeLines = ''
        i = 1
        for line in lines[:-1]:
            end = '      |' + str(self.partition_entry(line)[1]) + str(self.partition_entry(line)[2])
            writeLines += str(i) + end
            i += 1
        writeLines += lines[-1]
        with open(log, 'w') as file:
            file.write(writeLines)
        self.read_total(log)
        self.readEntries()

    # Edit logs

    def edit_logs_handler(self):
        row = self.logList.currentRow()
        item = self.logList.currentItem().text()
        geometry = self.logList.geometry()
        x = geometry.x()
        y = geometry.y()
        w = geometry.width()
        self.logLine.setGeometry(QtCore.QRect(x + 2, (y + 2 + 17 * row), w - 4, 17))
        self.logLine.setText(item)
        self.logLine.setFocus()
        self.logLine.show()

    def edit_logs(self):
        edit = self.logLine.text()
        editFile = edit + '.txt'
        row = self.logList.currentRow()
        item = self.logList.currentItem().text()
        directory = os.path.dirname(os.path.abspath('app.py'))
        files = os.listdir(directory)
        for file in files:
            if editFile == file:
                self.error_dialog.showMessage(f'The log {edit} already exist')
                return
        path = os.path.realpath(item + '.txt')
        newPath = os.path.join(directory, edit + '.txt')
        os.rename(path, newPath)
        self.readLogs()
        self.logList.setCurrentRow(row)
        self.readEntries()

    # Edit entries

    def edit_entries_handler(self):
        row = self.entryList.currentRow()
        item = self.entryList.currentItem().text()
        editItem = self.partition_entry(item)[2].lstrip()
        geometry = self.entryList.geometry()
        x = geometry.x()
        y = geometry.y()
        w = geometry.width()
        self.editLine.setGeometry(QtCore.QRect((x + 169), (y + 2 + 17 * row), (w / 3), 17))
        self.editLine.setText(editItem)
        self.editLine.setFocus()
        self.editLine.show()

    def edit_entries(self):
        edit = self.editLine.text()
        log = self.logList.currentItem().text() + '.txt'
        if edit.isdigit():
            item = self.entryList.currentItem().text()
            editItemDate = self.partition_entry(item)[1].lstrip()[:-1].rstrip()
            edit = f'{str(self.entryList.currentRow() + 1)}      |      {editItemDate}      |      {edit} min\n'

            with open(log, 'r') as file:
                lines = file.readlines()
                i = 0
                for line in lines:
                    if line == (item + '\n'):
                        lines = lines[:i] + lines[(i + 1):]
                        lines.insert(i, edit)
                    i += 1
                writeLines = ''
                i = 1
                for line in lines:
                    writeLines += str(i) + line[1:]
                    i += 1
            with open(log, 'w') as file:
                file.write(writeLines)
            self.read_total(log)
            self.readEntries()
        else:
            self.error_dialog.showMessage('Entry must be an integer.')

    # Misc

    def partition_entry(self, entry):
        a = -1
        b = -1
        c = 0
        for i in range(0, len(entry)):
            if entry[i] == '|':
                if c == 0:
                    a = i + 1
                    c = 1
                else:
                    pass
            if entry[i] == '|':
                if c == 1:
                    b = i + 1
                else:
                    pass
        if a == -1 or b == -1:
            return
        pEntry = entry[a:b]
        return entry.partition(pEntry)

    def debug(self):
        pass


class SecondWidget(QtWidgets.QWidget):

    def __init__(self):
        super(SecondWidget, self).__init__()

        self.label_1 = QtWidgets.QLabel()
        self.label_2 = QtWidgets.QLabel()
        self.label_3 = QtWidgets.QLabel()
        self.label_4 = QtWidgets.QLabel()
        self.label_5 = QtWidgets.QLabel()
        self.label_6 = QtWidgets.QLabel()
        self.label_7 = QtWidgets.QLabel()
        self.label_8 = QtWidgets.QLabel()
        self.label_9 = QtWidgets.QLabel()
        self.label_10 = QtWidgets.QLabel()
        self.label_11 = QtWidgets.QLabel()
        self.label_12 = QtWidgets.QLabel()

        self.labelList = [self.label_1, self.label_2, self.label_3, self.label_4, self.label_5, self.label_6, self.label_7,
                          self.label_8, self.label_9, self.label_10, self.label_11, self.label_12]

        self.button_1 = QtWidgets.QPushButton()
        self.button_1.setText("Generate Scale List")
        self.button_1.clicked.connect(self.scale)

        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.label_inst = QtWidgets.QLabel("Instrument: ")

        self.label_tran = QtWidgets.QLabel("Concert Bb is your ")

        self.changeInstLine = QtWidgets.QLineEdit(self)
        self.changeInstLine.returnPressed.connect(self.changeInst)

        self.button_2 = QtWidgets.QPushButton()
        self.button_2.setText("Update Instrument")
        self.button_2.clicked.connect(self.changeInst)

        self.changeTranLine = QtWidgets.QLineEdit(self)
        self.changeTranLine.returnPressed.connect(self.changeTran)

        self.button_3 = QtWidgets.QPushButton()
        self.button_3.setText("Update Transposition")
        self.button_3.clicked.connect(self.changeTran)

        self.tempo = QtWidgets.QSpinBox()
        self.tempo.setRange(10, 300)
        self.tempo.setValue(100)

        self.toggle_metronome = QtWidgets.QPushButton()
        self.toggle_metronome.setText('Play Metronome')
        self.toggle_metronome.clicked.connect(self.metronome)

        self.line2 = QtWidgets.QFrame(self)
        self.line2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line2.setFrameShadow(QtWidgets.QFrame.Sunken)

        hbox_1 = QtWidgets.QHBoxLayout()
        hbox_1.addWidget(self.label_inst)
        hbox_1.addWidget(self.changeInstLine)
        hbox_1.addWidget(self.button_2)

        hbox_2 = QtWidgets.QHBoxLayout()
        hbox_2.addWidget(self.label_tran)
        hbox_2.addWidget(self.changeTranLine)
        hbox_2.addWidget(self.button_3)

        vbox_sub3 = QtWidgets.QVBoxLayout()
        vbox_sub3.addWidget(self.line2)
        vbox_sub3.addWidget(self.tempo)
        vbox_sub3.addWidget(self.toggle_metronome)

        vbox_1 = QtWidgets.QVBoxLayout()
        vbox_1.addLayout(hbox_1)
        vbox_1.addLayout(hbox_2)
        vbox_1.addLayout(vbox_sub3)

        vbox_2 = QtWidgets.QVBoxLayout()
        vbox_2.addWidget(self.button_1)
        for label in self.labelList:
            vbox_2.addWidget(label)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox_1)
        hbox.addWidget(self.line)
        hbox.addLayout(vbox_2)

        self.setLayout(hbox)

        self.readInst()
        self.readTran()

        # Show GUI

        self.show()

    def metronome(self):
        global metronomeOn
        metronomeOn = not metronomeOn

    def scale(self):

        key_dictionary = {
            0: "C",
            1: "Db",
            2: "D",
            3: "Eb",
            4: "E",
            5: "F",
            6: "Gb",
            7: "G",
            8: "Ab",
            9: "A",
            10: "Bb",
            11: "Cb / B"
        }

        tran_int = 0

        for (k, v) in key_dictionary.items():
            if v == str(self.transposition):
                tran_int = (k - 10) % 12

        key_array = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        scale_array = []

        for i in range(12):
            random_index = randint(0, 11 - i)
            scale_array.append(key_array[random_index])
            key_array.remove(key_array[random_index])

        for i in range(12):
            key = scale_array[i]
            self.labelList[i].setText(f"Concert {key_dictionary[key]}, {self.instrument} {key_dictionary[(key + tran_int) % 12]}, Pattern {randint(1, 4)}.")

    def readInst(self):
        directory = os.path.dirname(os.path.abspath('app.py'))
        files = os.listdir(directory)
        for file in files:
            if file == "instrumentFile.txt":
                with open("instrumentFile.txt", "r") as f:
                    self.instrument = f.read()
                self.label_inst.setText("Instrument: " + str(self.instrument))

    def readTran(self):
        directory = os.path.dirname(os.path.abspath('app.py'))
        files = os.listdir(directory)
        for file in files:
            if file == "transpositionFile.txt":
                with open("transpositionFile.txt", "r") as f:
                    self.transposition = f.read()
                self.label_tran.setText("Concert Bb is your " + str(self.transposition))

    def changeInst(self):
        self.instrument = self.changeInstLine.text().rstrip()
        self.changeInstLine.clear()
        if self.instrument:
            with open("instrumentFile.txt", "w") as f:
                f.write(str(self.instrument))
            self.label_inst.setText("Instrument: " + str(self.instrument))
        else:
            return

    def changeTran(self):
        self.transposition = self.changeTranLine.text().rstrip()
        self.changeTranLine.clear()
        if self.transposition:
            with open("transpositionFile.txt", "w") as f:
                f.write(str(self.transposition))
            self.label_tran.setText("Concert Bb is your " + str(self.transposition))
        else:
            return


def main():
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
