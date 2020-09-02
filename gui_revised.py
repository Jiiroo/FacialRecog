import os
import cv2
import kivy
import sqlite3
import openpyxl
import webbrowser
import pandas as pd
from pathlib import Path
from datetime import date
from kivymd.app import MDApp
from data_base import DataBase
from kivymd.toast import toast
from kivy.config import Config
from kivy.clock import Clock
from kivymd.utils import asynckivy
from kivy.lang.builder import Builder
from kivymd.uix.dialog import MDDialog
from kivy.uix.modalview import ModalView
from time import time, asctime, localtime
from kivymd.uix.button import MDIconButton
from kivymd.uix.button import MDFlatButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import TwoLineAvatarListItem, OneLineListItem, ILeftBodyTouch, ImageLeftWidget
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty


kivy.require('1.11.1')


class SplashScreen(Screen):
    pass


class Navigation(Screen):
    bottomnavigation_items = ListProperty([])

    def __init__(self, **kwargs):
        super(Navigation, self).__init__(**kwargs)

    def on_enter(self, *args):
        self.bottomnavigation_items = [
            {'icon': 'google-classroom', 'text': 'Lobby', 'on_release': lambda x: self.go_to_lobby()},
            {'icon': 'camera-iris', 'text': 'camera', 'on_release': lambda x: toast('Coming Soon')},
            {'icon': 'account', 'text': 'About', 'on_release': lambda x: self.go_to_devs()},
        ]

        self.sm = self.ids.sm

        self.sm.add_widget(Lobby(name='lobby'))
        self.sm.add_widget(About(name='about'))

    def go_to_devs(self):
        self.sm.current = 'about'

    def go_to_lobby(self):
        self.sm.current = 'lobby'


class SetupWindow(Screen):
    user = ObjectProperty(None)
    password_1 = ObjectProperty(None)
    password_2 = ObjectProperty(None)

    def setup(self):
        if self.user.text != '' and self.password_1.text != '' and self.password_2 != '':
            if self.password_1.text == self.password_2.text:

                if self.validation():
                    write_data = open('user_data.txt', 'w')
                    write_data.write(self.user.text + ';' + self.password_1.text)
                    write_data.close()
                    manage.current = 'login'
                    self.reset()
                else:
                    MyApp().invalid_entry()
                    self.reset()
            else:
                MyApp().invalid_entry()
                self.reset()
        else:

            MyApp().invalid_entry()
            self.reset()

    def validation(self):
        return self.password_1.text == self.password_2.text

    def reset(self):
        self.user.text = ""
        self.password_1.text = ""
        self.password_2.text = ""

    @staticmethod
    def back_setup():
        if os.path.isfile('user_data.txt'):
            manage.current = 'login'
        else:
            MyApp().notice()


class EditWindow(Screen):
    user = ObjectProperty(None)
    password_1 = ObjectProperty(None)
    password_2 = ObjectProperty(None)

    def setup(self):

        if self.user.text != '' and self.password_1.text != '' and self.password_2 != '':
            if self.password_1.text == self.password_2.text:

                if self.validation():
                    write_data = open('user_data.txt', 'w')
                    write_data.write(self.user.text + ';' + self.password_1.text)
                    write_data.close()
                    manage.current = 'login'
                    self.reset()

                else:
                    MyApp().invalid_entry()
                    self.reset()

            else:
                MyApp().invalid_entry()
                self.reset()

        else:
            MyApp().invalid_entry()
            self.reset()

    def validation(self):
        return self.password_1.text == self.password_2.text

    def reset(self):
        self.user.text = ""
        self.password_1.text = ""
        self.password_2.text = ""

    @staticmethod
    def back_setup():
        if os.path.isfile('user_data.txt'):
            manage.current = 'login'
        else:
            MyApp().notice()

    @staticmethod
    def go_to_lobby():
        manage.current = 'navigation'


class LoginWindow(Screen):
    user = ObjectProperty(None)
    password = ObjectProperty(None)

    def login(self):
        if data().load()[0] == self.reg_user.text and data().load()[1] == self.reg_password.text:
            self.reset()
            manage.current = 'navigation'
        else:
            self.reset()
            MyApp().invalid_pass()

    def reset(self):
        self.reg_user.text = ''
        self.reg_password.text = ''

    @staticmethod
    def go_to_setup():
        manage.current = 'setup'


class Lobby(Screen):

    @staticmethod
    def attendance():
        global to_add
        information_reset = []
        os.system('py trainer.py')
        conn = sqlite3.connect('Registration.db')

        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS students(id integer unique primary key autoincrement, student_name, "
            "student_id, student_class, present_count)")

        file_trainer = "trainer/trainer.yml"
        attend = "Attendance"
        if not os.path.isfile(file_trainer):
            MyApp().file_error()
        else:
            if not os.path.exists(attend):
                os.makedirs("Attendance")
            else:
                pass

            cap = cv2.VideoCapture(0)

            temp_name = 'Temporary Image.jpg'
            confirm = True
            count = 0
            while confirm:
                ret, img = cap.read()
                cv2.imshow('Face Recognizer', img)
                k = cv2.waitKey(30)
                count += 1
                if k >= 0 or count >= 30:
                    cv2.imwrite(temp_name, img)
                    confirm = False
            cap.release()

            face_cascade = cv2.CascadeClassifier(
                'haarcascade_frontalface_alt.xml')

            read_image = cv2.imread(temp_name)
            gray = cv2.cvtColor(read_image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(file_trainer)
            for (x, y, w, h) in faces:
                cv2.rectangle(read_image, (x, y), (x + w - 10,
                                                   y + h - 10), (0, 255, 0), 3)
                ids, conf = recognizer.predict(gray[y:y + h, x:x + w])
                c.execute(
                    "select student_name from students where id = (?);", (ids,))
                result = c.fetchall()
                student_name = result[0][0]

                if conf < 50:
                    cv2.putText(read_image, student_name, (x + 5, y + h - 12), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (150, 255, 0),
                                2)
                else:
                    cv2.putText(read_image, 'No Match', (x + 5, y + h - 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                cv2.imshow('Face Recognizer', read_image)
                cv2.waitKey(0)
                c.execute('select present_count from students where id = (?);', (ids,))
                count = c.fetchall()

                for count_num in count:
                    to_add = count_num[0]

                if conf < 50:
                    add = int(to_add) + 1
                    update_attendance = "UPDATE students SET present_count =? where id = ?"
                    data_values = (add, ids)
                    c.execute(update_attendance, data_values)

                    time_log = asctime(localtime(time()))
                    c.execute('INSERT INTO student_' + str(ids) + '(Date_Time) VALUES (?)', (time_log,))

                    conn.commit()

                c.execute('select * from students where id = (?);', (ids,))
                result2 = c.fetchall()
                today = str(date.today())

                data_save = pd.DataFrame(result2, columns=['Database ID', 'Student Name', 'Student ID', 'Student Class',
                                                           'Number of Present'])
                file_name = "Attendance/Student Attendance " + today + ".xlsx"
                write_data = open('status_data.txt', 'a')

                for info in result2:
                    for info_2 in info:
                        information_reset.append(info_2)

                if conf < 50:
                    write_data.write(information_reset[1] + ':' + str(date.today()) + ';')
                    write_data.close()

                    if os.path.isfile(file_name):
                        file_path = Path("Attendance", "Student Attendance " + today + ".xlsx")
                        load_sheet = openpyxl.load_workbook(file_path)
                        work_sheet = load_sheet.active
                        work_sheet.append(result2[0])
                        load_sheet.save("Attendance/Student Attendance " + today + ".xlsx")

                    else:
                        datatoexcel = pd.ExcelWriter(file_name, engine='xlsxwriter')
                        data_save.to_excel(datatoexcel, index=False, sheet_name="Sheet")
                        worksheet = datatoexcel.sheets['Sheet']
                        worksheet.set_column('A:A', 7)
                        worksheet.set_column('B:B', 20)
                        worksheet.set_column('C:C', 20)
                        worksheet.set_column('D:D', 30)
                        datatoexcel.save()
                    break

            conn.close()
            cv2.destroyAllWindows()

    @staticmethod
    def student_list():
        manage.current = 'list'

    @staticmethod
    def add_students():
        manage.current = 'register'

    @staticmethod
    def edit_data():
        manage.current = 'setup'

    @staticmethod
    def logout():
        manage.current = 'login'


class RegisterStudent(Screen):
    student_name = ObjectProperty(None)
    student_id = ObjectProperty(None)
    student_class = ObjectProperty(None)

    @staticmethod
    def back():
        manage.current = 'navigation'

    def save(self):
        id_student = self.student_id.text
        name_student = self.student_name.text
        class_student = self.student_class.text

        conn = sqlite3.connect("Registration.db")
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS students(id integer unique primary key autoincrement, student_name, "
            "student_id, student_class, present_count)")

        uid = c.lastrowid
        conn.commit()

        if name_student == "":
            MyApp().invalid_entry()
        elif id_student == "":
            MyApp().invalid_entry()
        elif class_student == "":
            MyApp().invalid_entry()
            print(class_student)
        else:
            conn = sqlite3.connect('Registration.db')
            c = conn.cursor()
            c.execute('INSERT INTO students(student_name, student_id, student_class,present_count) VALUES (?,?,?,?)',
                      (name_student, id_student, class_student, 0))

            conn.commit()
            c.close()

            conn = sqlite3.connect("Registration.db")
            c = conn.cursor()
            c.execute("SELECT max(id) FROM students")
            max_id = c.fetchone()[0]
            c.close()

            conn = sqlite3.connect("Registration.db")
            c = conn.cursor()
            table_name = str(max_id)
            create_table = "CREATE TABLE IF NOT EXISTS student_" + table_name + "(Date_Time)"
            c.execute(create_table)
            c.close()

            cap = cv2.VideoCapture(0)
            counts = 0
            assure_path_exists("thumbnails/")
            temp_name = 'thumbnails/' + str(max_id) + '.jpg'
            confirm = True
            counts = 0
            interval = 100
            stride = 100

            while confirm:
                ret, img = cap.read()
                cv2.imshow('Capturing...', img)
                img = cv2.resize(img, (300, 300))
                k = cv2.waitKey(30)
                counts += 1
                if k >= 0 or counts >= 30:
                    cv2.imwrite(temp_name, img)
                    confirm = False
            cap.release()
            cv2.destroyAllWindows()

            vid_cam = cv2.VideoCapture(0)
            face_detector = cv2.CascadeClassifier(
                "haarcascade_frontalface_alt.xml")

            count = 0
            assure_path_exists("references/")
            while True:
                _, image_frame = vid_cam.read()
                cv2.imshow('Scanning', image_frame)
                gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
                faces = face_detector.detectMultiScale(gray, 1.1, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(image_frame, (x, y), (x + w - 10, y + h - 10), (255, 0, 0), 2)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    if count >= 1:
                        cv2.putText(image_frame, 'Processing...', (0, 120),
                                    font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    else:
                        cv2.putText(image_frame, 'Take picture', (0, 120), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.imshow('Scanning', image_frame)

                    count += 1
                    cv2.imwrite(
                        "references/" + self.student_name.text.replace('.', '') + "." + str(max_id) + "." +
                        str(count) + ".jpg", gray[y:y + h, x:x + w]
                    )

                key = cv2.waitKey(1)
                if count == 10 or key >= 0:
                    vid_cam.release()
                    cv2.destroyAllWindows()
                    break

            MyApp().save_notice()
            conn.close()
            self.reset()

    def reset(self):
        self.student_name.text = ''
        self.student_id.text = ''
        self.student_class.text = ''


class WIDGETS(TwoLineAvatarListItem):
    index = NumericProperty()
    icon = StringProperty('assets/student-icon.png')


class IconLeftSampleWidget(ImageLeftWidget, MDIconButton):

    pass


class StudentList(Screen):
    x = NumericProperty(0)
    y = NumericProperty(0)

    def __init__(self, **kwargs):
        super(StudentList, self).__init__(**kwargs)

    def on_enter(self, *args):
        # Icon for list of students
        data_items = self.get_users()

        async def on_enter():
            for info in data_items:
                await asynckivy.sleep(0)
                list_students = WIDGETS(index=info[5], text=f'{info[1]}', secondary_text=f'{info[2]}',
                                        on_release=self.on_press)
                self.ids.content.add_widget(list_students)

        asynckivy.start(on_enter())

    def refresh_callback(self, *args):
        '''A method that updates the state of your application
        while the spinner remains on the screen.'''

        def refresh_callback(interval):
            self.ids.content.clear_widgets()

            if self.x == 0:
                self.x, self.y = 0, 0
            else:
                self.x, self.y = 0, 0
            self.on_enter()
            self.ids.refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_callback, 1)

    def on_press(self, instance):
        index1 = instance.index
        index1 -= 1
        self._modalview = StudentInfo(index1)
        self._modalview.open()

    def get_users(self):
        reset_data = []
        data_items = []
        connection = sqlite3.connect("Registration.db")
        cursor = connection.cursor()
        #cursor.execute(
        #    "CREATE TABLE IF NOT EXISTS students(id integer unique primary key autoincrement, student_name, "
        #    "student_id, student_class, present_count)")
        uid = cursor.lastrowid
        connection.commit()
        cursor = connection.cursor()

        cursor.execute("SELECT id, student_name, student_class FROM students")
        cursor.execute("SELECT *, ROW_NUMBER() OVER(ORDER BY id) AS NoId FROM students")

        rows = cursor.fetchall()

        for row in rows:
            reset_data.append(row)
        data_items = reset_data
        print(data_items)

        cursor.close()
        return data_items

    def back_list(self):
        self.ids.content.clear_widgets()
        manage.current = 'navigation'

    def reload(self):
        pass


class StudentInfo(ModalView):
    vision = '''
    "The premier university on historic Cavite recognized for excellence 
    in the development of globally competitive and morally upright students." 
'''
    personal_information = ListProperty([])
    name_student = StringProperty("")
    id_student = StringProperty("")
    class_student = StringProperty("")
    image_name = StringProperty("")
    status = StringProperty("Not Present Today")

    def __init__(self, locate, **kwargs):
        super(StudentInfo, self).__init__(**kwargs)
        self.index1 = locate
        self.get_info(locate)

    def get_info(self, pos):
        self.list_data = []
        separate_info = []
        split_info = []

        connection = sqlite3.connect("Registration.db")
        connect_data = connection.cursor()
        connect_data.execute("SELECT * FROM students")

        self.data_collect = connect_data.fetchall()

        for row in self.data_collect:
            self.list_data.append(row)

        for info in self.list_data[pos]:
            self.personal_information.append(info)

        self.name_student = self.personal_information[1]
        self.id_student = self.personal_information[2]
        self.class_student = self.personal_information[3]

        self.image_name = "thumbnails/" + str(
            self.personal_information[0]) + ".jpg"


        for take in status_data().load():
            separate_info.append(take)

        for take_separated in separate_info:
            listed = take_separated.split(':')
            split_info.append(listed)

        for use in split_info:
            if self.name_student in use:
                use_info = use
                if str(date.today()) == use[1]:
                    self.status = 'Present'

        connect_data.close()

    def view_log(self):
        view = StudentLog(self.personal_information[0], self.name_student)
        view.open()

    def delete_student(self):
        connection = sqlite3.connect("Registration.db")
        connect_data = connection.cursor()

        connect_data.execute("SELECT * FROM students")
        take_data = connect_data.fetchall()
        take_data = take_data[self.index1]

        delete_data = "DELETE from students where id = ?"
        connect_data.execute(delete_data, (take_data[0],))

        connection.commit()
        connect_data.close()

        count = 0
        while True:
            try:
                count += 1
                image_name = "references/" + self.name_student.replace('.', '') + "." + \
                             str(take_data[0]) + "." + str(count) + ".jpg"
                os.remove(image_name)
            except FileNotFoundError:
                MyApp().delete_notice()
                break

    def edit_student(self):
        pop = EditStudent(self.index1, self.name_student, self.id_student, self.class_student, self.image_name)
        self._modalview = pop
        self._modalview.open()

    def refresh_list(self):
        pass


class StudentLog(ModalView):
    log = ListProperty([])
    name = StringProperty("")
    x = NumericProperty(0)
    y = NumericProperty(15)

    def __init__(self, identity, name, **kwargs):
        super(StudentLog, self).__init__(**kwargs)

        self.name = name + "\'s Log"
        self.identity = identity
        self.on_start()

    def on_start(self):

        reset_data = []

        connection = sqlite3.connect("Registration.db")
        cursor = connection.cursor()

        student = "SELECT * FROM student_" + str(self.identity)
        cursor.execute(student)
        student_log = cursor.fetchall()
        print(student_log)
        for row in student_log:
            reset_data.append(row)
        data_log = reset_data

        async def on_start():

            for x in data_log:
                print(x)
                await asynckivy.sleep(0)
                list_students = OneLineListItem(text=f'{x[0]}')
                self.ids.logs.add_widget(list_students)

        asynckivy.start(on_start())

    def refresh_callback(self, *args):
        '''A method that updates the state of your application
        while the spinner remains on the screen.'''

        def refresh_callback(interval):
            self.ids.logs.clear_widgets()

            if self.x == 0:
                self.x, self.y = 15, 30
            else:
                self.x, self.y = 0, 15
            self.on_start()
            self.ids.refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_callback, 1)


class EditStudent(ModalView):
    image_name = StringProperty("")
    student_name = ObjectProperty(None)
    student_id = ObjectProperty(None)
    student_class = ObjectProperty(None)
    name_text = StringProperty("")
    id_text = StringProperty("")
    class_text = StringProperty("")

    def __init__(self, position, name, id_number, section, image_name, **kwargs):
        super(EditStudent, self).__init__(**kwargs)
        self.name_text = name
        self.id_text = id_number
        self.class_text = section
        self.position = int(position)
        self.image_name = image_name

    def save(self):
        if self.student_name.text != '' and self.student_id.text != '' and self.student_class != '':
            connection = sqlite3.connect("Registration.db")
            connect_data = connection.cursor()

            connect_data.execute("SELECT id FROM students")
            take_data = connect_data.fetchall()
            take_data = take_data[self.position]

            count = 0
            while True:
                try:
                    count += 1
                    image_name = r"references/" + self.name_text.replace('.', '') + "." + \
                                 str(take_data[0]) + "." + str(count) + ".jpg"
                    edit_name = r"references/" + self.student_name.text.replace('.', '') + "." + \
                                str(take_data[0]) + "." + str(count) + ".jpg"
                    os.rename(image_name, edit_name)
                except FileNotFoundError:
                    break

            update_data = "UPDATE students SET student_name = ?, student_id = ?, student_class =? where id = ?"
            data_values = (self.student_name.text, self.student_id.text, self.student_class.text, take_data[0])
            connect_data.execute(update_data, data_values)
            connection.commit()
            connect_data.close()
            MyApp().save_notice()
            self.dismiss()

        else:
            MyApp().invalid_entry()


class About(Screen):
    intro = "[i]The system works on face recognition where each student in the ckass is photographed and their details" \
            " will be stored.The teachers can then record the attendance by just clicking some pictures of the " \
            "classroom. The system will recognize the face and very the presence or absence of each student.[i]"

    def giovanni(self):
        self._modalview = Giovanni()
        self._modalview.open()


    def simon(self):
        self._modalview = Simon()
        self._modalview.open()

    def dave(self):
        self._modalview = Dave()
        self._modalview.open()

    def heron(self):
        self._modalview = Heron()
        self._modalview.open()
    @staticmethod
    def go_lobby():
        manage.current = 'navigation'


class Giovanni(ModalView):
    def contact_fb(self):
        self.facebook = webbrowser.open("www.facebook.com/bonjo.devera")

    def contact_tg(self):
        self.telegram = webbrowser.open('https://t.me/tickets14')

    def contact_gmail(self):
        self.gmail = toast('bonjodevera1414@gmail.com')


class Simon(ModalView):
    def contact_fb(self):
        self.facebook = webbrowser.open("www.facebook.com/bonjo.devera")

    def contact_tg(self):
        self.telegram = webbrowser.open('https://t.me/tickets14')

    def contact_gmail(self):
        self.gmail = toast('simonsycruzada@gmial.com')


class Dave(ModalView):
    def contact_fb(self):
        self.facebook = webbrowser.open("www.facebook.com/bonjo.devera")

    def contact_tg(self):
        self.telegram = webbrowser.open('https://t.me/tickets14')

    def contact_gmail(self):
        self.gmail = toast('davepresbitero03@gmail.com')


class Heron(ModalView):
    def contact_fb(self):
        self.facebook = webbrowser.open("www.facebook.com/bonjo.devera")

    def contact_tg(self):
        self.telegram = webbrowser.open('https://t.me/tickets14')

    def contact_gmail(self):
        self.gmail = toast('jhonheron.carsocho@gmail.com')


class Manager(ScreenManager):
    pass


def assure_path_exists(path):
    direct = os.path.dirname(path)
    if not os.path.exists(direct):
        os.makedirs(direct)


# this function will load the login information
def data():
    return DataBase('user_data.txt')


def go_to_edit_data():
    manage.current = 'setup'


def go_to_lobby():
    manage.current = 'navigation'


def go_to_edit():
    manage.current = 'edit'


def go_to_register():
    manage.current = 'register'


def status_data():
    return DataBase('status_data.txt')


def go_to_login():
    manage.current = 'login'


manage = Manager()


class MyApp(MDApp):

    def __init__(self, **kwargs):
        self.title = 'Facial Recognition Attendance'
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Light'
        Builder.load_file("layouts.kv")
        return manage

    def on_start(self):
        self.windows = [
            SplashScreen(name='splash'),
            LoginWindow(name='login'),
            Navigation(name='navigation'),
            StudentList(name='list'),
            EditWindow(name='edit'),
            RegisterStudent(name='register'),
            SetupWindow(name="setup")
        ]

        for window in self.windows:
            manage.add_widget(window)

    def invalid_pass(self):
        ok_button = MDFlatButton(text='Close',text_color=self.theme_cls.primary_color,on_release=self.close_dialog)
        self.pop = MDDialog(title='ERROR ENTRY', type='alert', text='Check your username or password',
                            size_hint=(.7, .1), auto_dismiss=False, buttons=[ok_button])
        self.pop.open()

    def save_notice(self):
        close_button = MDFlatButton(text='close', on_release=self.close_dialog)
        self.pop = MDDialog(title='Saved', text='Account Saved', size_hint=(.7, 1), auto_dismiss=False, type='alert',
                            buttons=[close_button])
        self.pop.open()

    def delete_notice(self):
        close_button = MDFlatButton(text='close', on_release=self.close_dialog)
        self.pop = MDDialog(title='Deleted', text='Account Deleted', size_hint=(.7, 1), auto_dismiss=False,
                            buttons=[close_button])
        self.pop.open()

    def invalid_entry(self):
        close_button = MDFlatButton(text='close', on_release=self.close_dialog)
        self.pop = MDDialog(title='Invalid Entry!', text='Enter Valid Entry!', size_hint=(.7, 1), auto_dismiss=False,
                            buttons=[close_button])
        self.pop.open()

    def file_error(self):
        close_button = MDFlatButton(text='close', on_release=self.close_dialog)

        self.pop = MDDialog(title='Missing File!', text='Missing File!', size_hint=(.7, 1), auto_dismiss=False,
                            buttons=[close_button])
        self.pop.open()

    def notice(self):
        close_button = MDFlatButton(text='close', on_release=self.close_dialog)
        self.pop = MDDialog(title='Missing Information', text='Register First', size_hint=(.7, 1), auto_dismiss=False,
                            buttons=[close_button])
        self.pop.open()

    def close_dialog(self, obj):
        self.pop.dismiss()

    def go_to_login(self):
        manage.current = 'login'

    def go_to_setup(self):
        manage.current = 'setup'

    def go_to_splash(self):
        manage.current = 'splash'

    def go_to_studentlist(self):
        manage.current = 'list'

    def change_pass(self):
        manage.current = 'edit'

    def go_to_lobby(self):
        manage.current = 'navigation'


if __name__ == "__main__":
    Config.set("graphics", "width", "380")
    Config.set("graphics", "height", "620")
    Config.write()

    MyApp().run()
