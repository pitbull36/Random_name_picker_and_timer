import sys, random, time, datetime, os, glob
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDialog
from PyQt5 import uic, QtCore, QtGui, QtWidgets, QtMultimedia as M
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool

# Handle high resolution displays:
# if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
#     QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
# if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
#     QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# Signals class that will store a signal. Basically it will send the results from my Thread thread
class Signals(QObject):
    return_topic = pyqtSignal(str) # return the chosen topic
    return_num = pyqtSignal(list, int) # return the random number
    finished = pyqtSignal()


# Thread class where the code will be executed
class Thread(QRunnable):

    def __init__(self, topics):
        super(Thread, self).__init__()    
        self.signal = Signals()    
        self.topics = topics

        self.last_sound = "" # keep track of the last chosen sound for the timer

    @pyqtSlot()
    def run(self):
        # basically, choose tot random topics and send it out
        for i in range(0,40):    
            num_topic = random.randint(0, len(self.topics)-1) # create a random number
            time.sleep(0.05)
            result = self.topics[num_topic].upper()
            self.signal.return_topic.emit(result)
        for i in range(0,20):
            num_topic = random.randint(0, len(self.topics)-1) # create a random number
            time.sleep(0.1)
            result = self.topics[num_topic].upper()
            self.signal.return_topic.emit(result)
        for i in range(0,10):    
            num_topic = random.randint(0, len(self.topics)-1) # create a random number
            time.sleep(0.2)
            result = self.topics[num_topic].upper()
            self.signal.return_topic.emit(result)
        for i in range(0,4):    
            num_topic = random.randint(0, len(self.topics)-1) # create a random number
            time.sleep(0.4)
            result = self.topics[num_topic].upper()
            self.signal.return_topic.emit(result)
        
        # wait one last second and then send 
        # 1. the winner topic
        # 2. the list of topics and the last random number chosen
        # 3. a signal when this whole thread finished being executed
        # these results will be catched by other functions later on
        time.sleep(1)
        self.signal.return_topic.emit(result)        
        self.signal.return_num.emit(self.topics, num_topic) # return the last random number
        self.signal.finished.emit() # when the thread is finished, emit another kind of signal

# my main window
class MyApp(QMainWindow):

    def __init__(self):
        super(MyApp, self).__init__()
        Ui_MainWindow, QtBaseClass = uic.loadUiType("random_picker.ui") 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.spin_button.clicked.connect(self.Spin)
        self.statusBar().showMessage(chr(169) + "2020 Dario Pittera")

        # create instance of the thread
        self.threadpool = QThreadPool()

        # for the timer
        self.ui.set_timer_button.clicked.connect(self.SetTime) # this is the button to set the time to the timer
        self.ui.start_button.clicked.connect(self.start_watch)
        self.ui.pause_button.clicked.connect(self.watch_pause)
        self.ui.reset_button.clicked.connect(self.watch_reset)
        self.ui.settings_button.clicked.connect(self.open_settings)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.run_watch) # call run_watch every 1 ms. 1 ms because I specified it in setInterval()
        self.timer.setInterval(1)
        self.mscounter = 0 # this is my initial time let's say
        self.isreset = True
        self.showLCD() # function to show numbers on my QLCD object

    # opend the settings Dialog
    def open_settings(self):
        self.SettingsWindow = Settings()
        self.SettingsWindow.exec_()
        
    def print_winner(self, signal):
        #print(signal)
        self.ui.chosen_text.setText(signal) # display the winner topic in the chosen_text Qlabel

    # display this once the thread finished
    def thread_complete(self):
        
        # display the "funny" sentence fron the "sentence.txt" file. You can modify it
        with open("sentences.txt",'r') as f:
            funny_list = f.read().splitlines()
        
        num_funny = random.randint(0, len(funny_list)-1) # create a random number for the funny sentence selection
        self.ui.funny_text.setText(funny_list[num_funny])

        if self.ui.mute_check.isChecked() == False: # if the audio is not muted
            path = ".\\cheers\\"
            sounds = [s for s in glob.glob(os.path.join(path, '*.wav'))] # look for all the wave files in the cheers folder
            num_sound = random.randint(0, len(sounds)-1) # create a random number for the cheer sounds selection
            M.QSound.play(sounds[num_sound])
        else:
            pass

    def remove_chosen(self, topics, random_num):
        #print(topics)
        #print(random_num)
        topics.remove(topics[random_num]) # remove the winner from the list
        self.ui.topic_box.clear() # clear the text box

        for topic in topics:
            self.ui.topic_box.append(topic) # put again the box each remaining topic of the list of topics

    def Spin(self):
                
        if self.ui.topic_box.toPlainText() == "": # if the box is empty
            self.ui.chosen_text.setText("NO TOPICS!")
            self.ui.funny_text.setText("")
        elif self.ui.topic_box.document().blockCount() == 1:
            self.ui.funny_text.setText("It is pretty obvious, don't you think :)?")
            self.ui.chosen_text.setText(self.ui.topic_box.toPlainText().upper())
            self.ui.topic_box.clear()
        else:
            if self.ui.mute_check.isChecked() == False: # if the audio is not muted
                M.QSound.play("spin.wav")
            else:
                pass

            # reset the "funny" sentence
            self.ui.funny_text.setText("")
            self.ui.funny_text.setText("...And the next topic will be...")
            
            # create the variable that contain all the topics to pass it to the thread
            topics = self.ui.topic_box.toPlainText().split("\n") # create the list of topics by reading the value of the box

            # call the external thread and pass the list of topics
            thread = Thread(topics) # create an instance of the thread
            thread.signal.return_topic.connect(self.print_winner) # catch the results (winner topic) from the thread and send it to print_winner function
            thread.signal.return_num.connect(self.remove_chosen) # catch the results (list of topics, last random num) from the thread and send it to remove_chosen function
            self.threadpool.start(thread) # start the thread

            # when the thread finished call the function to display the "funny" sentence and the clap
            thread.signal.finished.connect(self.thread_complete)

    # this function set timer box
    def SetTime(self):
        self.minutes_timer = self.ui.time_choice.time().toString() # take the content of the set timer box
        self.ui.minutes.display(self.minutes_timer[1:]) # display in the QLCS number object the content of set timer box
        #print(self.minutes_timer)
        self.minutes = self.minutes_timer.split(":")[1] # take only the minutes
        self.seconds = self.minutes_timer.split(":")[2] # take only the seconds
        self.starting_time = (int(self.minutes)*60000) + (int(self.seconds)*1000) # convert minutes and seconds in milliseconds

    # this has control the time displayed in the timer
    def showLCD(self):
        try:
            start = self.starting_time # check if we already set a time from the set timer box
        except:
            start = 0
        text = str(datetime.timedelta(milliseconds=self.mscounter+start))[:-7] # set the starting time of the timer, -7 because I avoid to show the ms
        self.ui.minutes.setDigitCount(5) # choose how many digits to show

        if not self.isreset:  # if "isreset" is False
            self.ui.minutes.display(text)
        else:
            # check if I already set the timer in the timer box. If yes, put this value, otherwise put a std 0:00:00
            try:
                self.ui.minutes.display(self.minutes_timer)
            except:
                self.ui.minutes.display("0:00:00")

        # check time and give color indication
        if text == "0:03:00":
            palette = self.ui.minutes.palette()
            palette.setColor(palette.WindowText, QtGui.QColor("orange"))
            self.ui.minutes.setPalette(palette)

        if text == "0:01:00":
            palette = self.ui.minutes.palette()
            palette.setColor(palette.WindowText, QtGui.QColor("red"))
            self.ui.minutes.setPalette(palette)

        # when time's up
        if text == "0:00:00":
            self.timer.stop()
            self.watch_reset()

            try:
                Settings.f_timer # if the user changed the timer sound from the settings
                if Settings.f_timer != "": # if it is different from empty, the user didn't select anything in the end, after the browse button
                    M.QSound.play(Settings.f_timer)
                    self.last_sound = Settings.f_timer # save this changed sound in the last_sound variable
                else:
                    try:
                        M.QSound.play(self.last_sound) # if the user changed at least once the timer sound, play the last one chosen
                    except:
                        M.QSound.play("tromba.wav")
            except:
                M.QSound.play("tromba.wav")
            
            self.ui.start_button.setDisabled(False)
            self.ui.pause_button.setDisabled(False)
            self.ui.reset_button.setDisabled(False)
            palette = self.ui.minutes.palette()
            palette.setColor(palette.WindowText, QtGui.QColor("black"))
            self.ui.minutes.setPalette(palette)
                
    # start the timer, and decrease of 1 sec each second
    def run_watch(self):
        self.mscounter -= 1
        self.showLCD()

    def start_watch(self):
        self.timer.start()
        self.isreset = False
        self.ui.start_button.setDisabled(True)
        self.ui.pause_button.setDisabled(False)
        self.ui.reset_button.setDisabled(False)
        self.ui.set_timer_button.setDisabled(False)

    def watch_pause(self):
        self.timer.stop()
        self.ui.pause_button.setDisabled(True)
        self.ui.start_button.setDisabled(False)
        self.ui.set_timer_button.setDisabled(True)
        
    def watch_reset(self):
        self.timer.stop()
        self.mscounter = 0
        self.isreset = True
        self.showLCD()
        self.ui.reset_button.setDisabled(True)
        self.ui.start_button.setDisabled(False)
        self.ui.set_timer_button.setDisabled(False)
        self.ui.minutes.setStyleSheet("QLCDNumber {color: black;}")

    # set a dialog window when trying to close the program
    def closeEvent(self, event):
        if self.ui.mute_check.isChecked() == False: # if the audio is not muted
            M.QSound.play("boo.wav")
        else:
            pass
        reply = QMessageBox.question(
            self, " Message",
            "Did you deep dived enough?",
            QMessageBox.Close | QMessageBox.Cancel)

        if reply == QMessageBox.Close:
            event.accept()
        else:
            event.ignore()

# this is for the second UI I have
class Settings(QDialog):
            def __init__(self):
                super(Settings, self).__init__()
                uic.loadUi('settings.ui', self)

                f_timer="" # define a variable that I will pass back to my mainUI

                self.confirm_button.clicked.connect(self.confirm_settings)
                self.timer_browse_button.clicked.connect(self.select_timer_audio)
                segnale = pyqtSignal(str)

            def select_timer_audio(self):
                Settings.f_timer, _ = QtWidgets.QFileDialog.getOpenFileName(self,'Single File', QtCore.QDir.rootPath(), '*.wav') # note the Setting. to use the class variable
                self.f_timer_label.setText(Settings.f_timer.split("/")[-1])

            def confirm_settings(self):
                self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # print(PyQt5.QtWidgets.QStyleFactory.keys()) # show available styles
    # choose a style sheet file form local
    # stream = QtCore.QFile("orange.txt")
    # stream.open(QtCore.QIODevice.ReadOnly)
    # app.setStyleSheet(QtCore.QTextStream(stream).readAll())
    app.setStyle('Fusion')
    window = MyApp()
    window.show()
    sys.exit(app.exec_())