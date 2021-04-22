import sqlite3
import os
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from functools import partial
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import FadeTransition
from kivy.clock import Clock
import random
from kivy.core.window import Window
import math
import ftplib
import csv
import FTP



def import_data(a):
  import FTP

Clock.schedule_interval(partial(import_data), 30)



global destination
global timer
destination = 'Main'
timer = random.randint(10, 15)
global font_factor
font_factor = 1.25



def show_popup(popup, name):
    show = popup
    global popupWindow
    popupWindow = Popup(title=str(name),
                        content=show,
                        size_hint=(0.95, 0.5),
                        background_color=(0.54, 1, 0.8, 1))
    popupWindow.open()



def capitaliser(string):
    new_string = string[0].upper()
    for i, letter in enumerate(string):
        if i != 0:
            new_string += letter
    print(new_string)
    return new_string



class WelcomeScreen(Screen):
    pass



class LoadingScreen(Screen):
    dots = '.'
    occurrence = 0


    def delete(self, a, b):
        self.ids.grid_1.clear_widgets()


    def add(self, a, b):      
        label = Label(text='Loading' + self.dots,
                      color=(0, 0, 0, 0.4),
                      font_size=40,
                      italic=True)
                      
        self.ids.grid_1.add_widget(label)
        
        if len(self.dots) < 3:
            self.dots += '.'
        else:
            self.dots = '.'
            
        self.occurrence += 1
        
        if self.occurrence < timer:
            Clock.schedule_once(partial(self.delete, self), 0.35)
            Clock.schedule_once(partial(self.add, self), 0.35)
        else:
            sm.current = destination


    def on_pre_enter(self, *args):
        self.occurrence = 0
        self.dots = '.'
        self.ids.grid_1.clear_widgets()
        Clock.schedule_once(partial(self.add, self), 0)



class MainScreen(Screen):
    buttons = []
    entered = False
    position1 = 0
    global sm
    length = 0
    user_inputs_added = False


    def on_pre_enter(self):
        if self.entered == True:
            self.newbutton()
            
        if self.user_inputs_added == False:
            conn = sqlite3.connect(PlantsDatabase)
            c = conn.cursor()
            c.execute('SELECT * FROM User_Inputs')
            rows = c.fetchall()
            for row in rows:
                global plant_name
                plant_name = capitaliser(row[0])
                self.newbutton()
            self.user_inputs_added = True


    def find_name(self, text, button):
        global button_name
        button_name = text
        sm.current = 'PlantScreen'


    def show_name_popup(self):
        show_popup(NamePopup(), 'Enter Name of Plant')


    def newbutton(self):
        global new_button
        global plant_name
        layout = FloatLayout(height=Window.width * 0.5, size_hint_y=None)
        
        new_button = Button(text=capitaliser(plant_name),
                            size_hint_y=None,
                            pos_hint={"x": 0.1, "top": 0.9},
                            size_hint=(0.8, 0.9),
                            color=(0, 0, 0, 0.7),
                            background_normal='',
                            background_color=(0, 0, 0, 0.1),
                            font_size=60)

        new_button.pressed = False
        new_button.bind(on_release=partial(self.find_name, new_button.text))
        layout.add_widget(new_button)
        self.ids.grid_1.add_widget(layout)
        self.buttons.append(new_button)

        return new_button



class NamePopup(FloatLayout):
    global plant_name
    plant_name = ObjectProperty(None)


    def set_name(self):
        global plant_name
        self.plant_name = self.plant_name.text
        plant_name = self.plant_name


    def verify(self):
        conn = sqlite3.connect(PlantsDatabase)
        c = conn.cursor()
        c.execute('SELECT * FROM Plants')
        rows = c.fetchall()
        global known_plants
        known_plants = [row[0].lower() for row in rows]
        c.execute('SELECT * FROM User_Inputs')
        records = c.fetchall()
        occurrence = 0
        global plant_name
        plant_name = str(self.plant_name)
        plant_name = plant_name.lower()
        for record in records:
            if plant_name.lower()[0:len(plant_name)] == record[0][0:len(plant_name)]:
                occurrence += 1
                
        plant_type = ''
        plant_type += plant_name
        
        if occurrence > 0:
          
            dash = ' - '
            plant_name = plant_name + dash
            plant_name += str(occurrence)

        c.executemany('INSERT INTO User_Inputs VALUES (?,?)',
                      [(plant_name, plant_type)])
        conn.commit()

        if plant_type.lower() not in known_plants:
            MainScreen.entered = True
            known_plants.append(plant_name)
            sm.current = 'SecondInput'

        else:
            MainScreen.entered = True
            sm.current = 'Load'
            global destination
            global timer
            destination = 'Main'
            timer = random.randint(1, 3)

    pass



class ValidationPopup(FloatLayout):

    def move(self):
        global destination
        global timer
        destination = 'SecondInput'
        timer = random.randint(1, 3)
        sm.current = 'Load'



class SecondInputScreen(Screen):

    humidity = ObjectProperty(None)
    light = ObjectProperty(None)
    soil_moisture = ObjectProperty(None)
    soil_temp = ObjectProperty(None)
    air_temp = ObjectProperty(None)


    def cancel(self):
        MainScreen.entered = False
        sm.current = 'Main'


    def submit(self):
        invalid = False
        
        try:
            humidity = float(self.humidity.text)
            light = float(self.light.text)
            soil_moisture = float(self.soil_moisture.text)
            soil_temp = float(self.soil_temp.text)
            air_temp = float(self.air_temp.text)
            plant_name = str(known_plants[len(known_plants) - 1])

        except:
            invalid = True
            
        if invalid == False:
          
            if soil_moisture != 0 and soil_moisture != 1:
                invalid = True
                
            if humidity < 0 or humidity > 100:
                invalid = True
                
            if light < 0 or light > 24:
                invalid = True

            if soil_temp < -5 or soil_temp > 100:
                invalid = True
                
            if air_temp < -5 or air_temp > 100:
                invalid = True

        if invalid == True:
            show_popup(ValidationPopup(), 'Invalid Input')
            
        if invalid == False:
            plant_properties = [(plant_name, soil_moisture, air_temp, soil_temp, humidity, light),]
            conn = sqlite3.connect('PlantsDatabase.db')
            c = conn.cursor()
            c.executemany('INSERT INTO Plants VALUES (?,?,?,?,?,?)', plant_properties)
            conn.commit()
            conn.close()
            sm.current = 'Main'


    def on_leave(self):
        self.ids.light.text = ''
        self.ids.soilMoisture.text = ''
        self.ids.humidity.text = ''
        self.ids.soilTemp.text = ''
        self.ids.airTemp.text = ''



class DatabaseScreen(Screen):
    page = 1
    beginning = 0
    end = 10
    max = 23

    def main(self, c, b):
        sm.current = 'Main'


    def fetch(self, something):
        conn = sqlite3.connect(PlantsDatabase)
        c = conn.cursor()
        c.execute('SELECT * FROM Plants')
        rows = c.fetchall()
        separator = '   -   '
        self.max = len(rows)
        self.ids.grid_1.add_widget(
            Label(text='Type  -  Auto Water  -  Air °C  -  Soil °C  -  Humidity (%)  -  Hrs. light',
                  color=(0, 0, 0, 0.75), font_size=25, italic=True,
                  pos_hint={'x': 0, 'top': 1.275}))
        z = 1.22
        
        for i in range(self.beginning, self.end):
          
            rowsub = []
            for x in range(len(rows[i])):
              
                rowsub.append(str(rows[i][x]))
                
            a = Label(text=separator.join(rowsub),
                      color=(0, 0, 0, 0.75),
                      font_size=25,
                      italic=True,
                      pos_hint={'x': 0, 'top': z})
                      
            self.ids.grid_1.add_widget(a)
            z -= 0.055
            
        button = Button(text='Exit',
                        color=(1, 1, 1, 1),
                        size_hint=(0.4, 0.075),
                        pos_hint={'x': 0.3, 'top': 0.12},
                        background_normal='',
                        background_color=(72 / 255, 239 / 255, 128 / 255, 1),
                        font_size=50,
                        bold=False)
                        
        button.bind(on_press=partial(self.main, self))
        self.ids.grid_1.add_widget(button)
        
        title = Label(text='Database',
                      color=(28 / 255, 236 / 255, 104 / 255, 1), 
                      pos_hint={"x": -0.25, "top": 1.34}, font_size=80)
                      
        self.ids.grid_1.add_widget(title)
        
        maxpages = math.ceil(self.max / 10)

        self.ids.grid_1.add_widget(Label(text='Page ' + str(self.page) + ' of ' + str(maxpages), 
                                         font_size=20,
                                         pos_hint={'x': 0.339, 'top': 0.52}, 
                                         color=(0, 0, 0, 0.73)))
                                         
        if self.beginning == 0:
          
            button_one = Button(text='>',
                                color=(0, 0, 0, 0.75),
                                size_hint=(0.1, 0.1),
                                pos_hint={'x': 0.9, 'top': 0.5},
                                font_size=40,
                                background_normal='',
                                background_color=(1, 1, 1, 0.73))
                                
            button_one.bind(on_release=partial(self.next, self))
            self.ids.grid_1.add_widget(button_one)

        elif self.end == self.max:
          
            button_two = Button(text='<',
                                color=(0, 0, 0, 0.75),
                                size_hint=(0.1, 0.1),
                                pos_hint={'x': 0, 'top': 0.5},
                                font_size=40,
                                background_normal='',
                                background_color=(1, 1, 1, 0.73))
                                
            button_two.bind(on_release=partial(self.previous, self))
            self.ids.grid_1.add_widget(button_two)
            
        else:
            button_one = Button(text='>',
                                color=(0, 0, 0, 0.75),
                                size_hint=(0.1, 0.1),
                                pos_hint={'x': 0.9, 'top': 0.5},
                                font_size=40,
                                background_normal='',
                                background_color=(1, 1, 1, 0.73))
                                
            button_one.bind(on_release=partial(self.next, self))
            self.ids.grid_1.add_widget(button_one)
            
            button_two = Button(text='<',
                                color=(0, 0, 0, 0.75),
                                size_hint=(0.1, 0.1),
                                pos_hint={'x': 0, 'top': 0.5},
                                font_size=40,
                                background_normal='',
                                background_color=(1, 1, 1, 0.73))
                                
            button_two.bind(on_release=partial(self.previous, self))
            self.ids.grid_1.add_widget(button_two)


    def on_enter(self):
        self.fetch(self)
        MainScreen.entered = False


    def previous(self, a, b):
        self.page -= 1
        self.beginning = 10 * self.page
        self.beginning -= 10
        self.end = self.beginning + 10
        sm.current = 'Load'
        global destination
        global timer
        destination = 'Data'
        timer = random.randint(1, 3)


    def next(self, a, b):
        self.page += 1
        self.beginning = 10 * self.page
        self.beginning -= 10
        self.end = self.beginning + 10
        if self.end > self.max:

            self.end = 0
            self.end += self.max
            
        sm.current = 'Load'
        global destination
        global timer
        destination = 'Data'
        timer = random.randint(1, 3)


    def on_pre_enter(self):
        self.ids.grid_1.clear_widgets()



class PlantScreen(Screen):
    plant = ''
    pressed = 0
    pressed1 = 0
    labels = []
    button = ''
    button1 = ''
    labels1 = []
    time_stamp=''
    prev_time_stamp=''
    time_label=Label(text=time_stamp, font_size=22, pos_hint={"x": 0.05,"top": 0.975}, color = (0,0,0,0.73))
    connection_status = 'Yes'
    connection_label=Label(text='Connected: ' + connection_status,
                  color=(0, 0, 0, 1),
                  pos_hint={"x": 0.15, "top": 1.2},
                  font_size=40)

    values=[]
    connection_checking=''


    def connection_check(self):

        with open(MA.getSensorsDatabase()) as csv_file:
          
            csv_reader = csv.reader(csv_file, delimiter = ',')
            for row in csv_reader:
              
              self.values=[round(float(row[7]),1),round(float(row[2]),1),round(float(row[5]),1),round(float(row[4]),1),round(float(row[9]),1)]
            
              times=row[0]
              
        self.previous_time_stamp='' + self.time_stamp
        self.time_stamp=''
        
        for i in range(19):
          self.time_stamp+=times[i] 
        
        if self.previous_time_stamp==self.time_stamp:
          self.connection_status='No'

        else:
          self.connection_status='Yes'

        self.connection_label.text='Connected '+ self.connection_status
            

    def go_back(self, something):
        sm.current = 'Main'


    def fetch_data(self, a, b):
        conn = sqlite3.connect(PlantsDatabase)
        c = conn.cursor()
        c.execute('SELECT * FROM Plants')
        rows = c.fetchall()

        if self.pressed % 2 == 0:

            self.pressed += 1
            self.button.text = 'v Optimal Growth Conditions'
            for row in rows:

                textlist = [['Automatic Watering:', -0.3285], 
                            ['Air Temperature (°C):', -0.3179],
                            ['Soil Temperature (°C):', -0.315],
                            ['Relative Air Humidity (%):', -0.346],
                            ['No. hours of light per day:', -0.3359]]

                pos = 0 + self.button.pos_hint['top'] + 0.43

                if row[0].lower() == self.plant.lower():

                    for i in range(len(row) - 1):

                        label1 = Label(text=textlist[i][0],
                                       color=(0, 0, 0, 0.73),
                                       font_size=22,
                                       pos_hint={
                                           "x": textlist[i][1],
                                           "top": pos
                                       })

                        label = Label(text=str(row[i + 1]),
                                      color=(0, 0, 0, 0.73),
                                      font_size=22,
                                      pos_hint={"x": -0.15, "top": pos})

                        self.labels.append(label)
                        self.labels.append(label1)
                        pos -= 0.03
                        self.ids.grid_layout.add_widget(label)
                        self.ids.grid_layout.add_widget(label1)

        else:
            self.button.text = '> Optimal Growth Conditions'

            for label in self.labels:

                if label != self.button:
                    self.ids.grid_layout.remove_widget(label)

            self.labels = [self.button]
            self.pressed += 1


    def show_data(self, a, b):
        
        if self.pressed1 % 2 == 0:

            with open(MA.getSensorsDatabase()) as csv_file:

              csv_reader = csv.reader(csv_file, delimiter = ',')
              for row in csv_reader:
                
                self.values=[round(float(row[7]),1),round(float(row[2]),1),round(float(row[5]),1),round(float(row[4]),1),round(float(row[9]),1)]
            
                times=row[0]
                
            self.previous_time_stamp='' + self.time_stamp
            self.time_stamp=''

            for i in range(19):

              self.time_stamp+=times[i]
              
            self.time_label = Label(text=self.time_stamp, font_size=22, pos_hint={"x": 0.05,"top": 0.975}, color = (0,0,0,0.73))
            self.ids.grid_layout.add_widget(self.time_label)
            self.pressed1 += 1
            self.button1.text = 'v Current Growth Conditions'

            textlist = [['Automatic Watering:', -0.3285], 
                        ['Air Temperature (°C):', -0.3179],
                        ['Soil Temperature (°C):', -0.315],
                        ['Relative Air Humidity (%):', -0.346],
                        ['No. hrs of light per day::', -0.3359]]
                        
            pos = 0 + self.button1.pos_hint['top'] + 0.43

            for i in range(5):

                label1 = Label(text=textlist[i][0],
                               color=(0, 0, 0, 0.73),
                               font_size=22,
                               pos_hint={"x": textlist[i][1], "top": pos})
                label = Label(text=str(self.values[i]),
                              color=(0, 0, 0, 0.73),
                              font_size=22,
                              pos_hint={"x": -0.15, "top": pos})
                pos -= 0.03
                self.ids.grid_layout.add_widget(label)
                self.ids.grid_layout.add_widget(label1)
                self.labels1.append(label)
                self.labels1.append(label1)

            for widget in self.labels:

                widget.pos_hint['top'] -= 0.17

        else:

            self.ids.grid_layout.remove_widget(self.time_label)
            self.button1.text = '> Current Growth Conditions'
            for label in self.labels:
                label.pos_hint['top'] += 0.17
            for label in self.labels1:
                self.ids.grid_layout.remove_widget(label)
            self.pressed1 += 1
    

    def go_to_image(self, a):
        sm.current = 'Image'


    def on_pre_enter(self):
        self.connection_checking=Clock.schedule_interval(partial(self.connection_check), 30)
        
        self.pressed = 0
        self.pressed1 = 0
        MainScreen.entered = False
        conn = sqlite3.connect(PlantsDatabase)
        c = conn.cursor()
        c.execute('SELECT * FROM User_Inputs')
        rows = c.fetchall()

        for row in rows:

            if button_name.lower() == row[0]:
                self.plant = row[1]

        new_string = self.plant[0].upper()

        for i, letter in enumerate(self.plant):

            if i != 0:
                new_string += letter

        self.ids.grid_layout.clear_widgets()
        self.ids.grid_layout.add_widget(self.connection_label)
        self.ids.grid_layout.add_widget(
            Label(text=new_string,
                  color=(28 / 255, 236 / 255, 104 / 255, 1),
                  pos_hint={"x": -0.25, "top": 1.34},
                  font_size=80))
        
        imagebutton = Button(text='> See latest photo of plant',
                   color=(0, 0, 0, 1),
                   size_hint=(0.8, 0.05),
                   pos_hint={"x": -0.15, "top": 0.72},
                   background_normal='',
                   background_color=(0, 0, 0, 0),
                   font_size=30)

        imagebutton.bind(on_release=partial(self.go_to_image))
        
        self.ids.grid_layout.add_widget(imagebutton)
                   
        self.button1 = Button(text='> Current Growth Conditions',
                              color=(0, 0, 0, 1),
                              size_hint=(0.8, 0.05),
                              pos_hint={"x": -0.138, "top": 0.62},
                              background_normal='',
                              background_color=(0, 0, 0, 0),
                              font_size=30)
                              
        self.button1.bind(on_press=partial(self.show_data, self))
        
        self.button = Button(text='> Optimal Growth Conditions',
                             color=(0, 0, 0, 1),
                             size_hint=(0.8, 0.05),
                             pos_hint={"x": -0.136, "top": 0.57},
                             background_normal='',
                             background_color=(0, 0, 0, 0),
                             font_size=30)

        self.button.bind(on_press=partial(self.fetch_data, self))
        self.ids.grid_layout.add_widget(self.button)
        self.ids.grid_layout.add_widget(self.button1)
        self.labels.append(self.button)

        return_button = Button(text='Return',
                               color=(1, 1, 1, 1),
                               size_hint=(0.4, 0.05),
                               pos_hint={"x": 0.3, "top": 0.1},
                               background_normal='',
                               background_color=(195 / 255, 195 / 255, 195 / 255, 1))

        self.ids.grid_layout.add_widget(return_button)
        return_button.bind(on_release=partial(self.go_back))

        
    def on_leave(self):
      self.connection_checking.cancel()
      

class ImageScreen(Screen):

  num=9/16
  num*=6
  num/=13


  def go_back(self, a):
    sm.current = 'PlantScreen'


  def on_pre_enter(self):
      self.ids.float.clear_widgets()
      self.ids.float.add_widget(Image(source = MA.getPlantsImage(), 
                                      size = (self.width,self.height*self.num), 
                                      pos = (0,0)))
      
      button=Button(text='Return',
                               color=(1, 1, 1, 1),
                               size_hint=(0.4, 0.05),
                               pos_hint={"x": 0.3, "top": 0.1},
                               background_normal='',
                               background_color=(195 / 255, 195 / 255,
                                                 195 / 255, 1))
                                                 
      button.bind(on_press = partial(self.go_back))
      self.ids.float.add_widget(button)
  



Builder.load_string("""
#: import sm kivy.uix.screenmanager


<LoadingScreen>

  GridLayout:
    id: grid_1
    cols: 1
    size: root.width, root.height

    canvas.before:
      Color:
        rgba: (1,1,1,1)
      Rectangle:
        pos: self.pos
        size: self.size


<WelcomeScreen>

  FloatLayout:
    size: root.width, root.height

    canvas.before:
      Color:
        rgba: (1,1,1,1)
      Rectangle:
        pos: self.pos
        size: self.size

    Image:
      source: 'piplanter.png'
      size: (root.width*0.75, root.height*0.45)
      pos: (root.width*0.0, root.height*0.1)

    Button:
      font_size: 50
      size_hint: 0.4,0.075
      pos_hint: {'x': 0.3, 'top': 0.2}
      background_normal: ''
      background_color: 72/255,239/255,128/255, 1
      text: 'Next'
      on_release: root.manager.current = 'Load'

    Label:
      text: 'Westminster School (Yr 11): Aryan, Annant, Jou-Myu, Sandro & Giacomo'
      pos_hint: {"x":0.0, "top": 0.55}
      italic: True
      font_size: 20
      color: (1,1,1,1)


<DatabaseScreen>

  id: data

  FloatLayout:
    id: grid_1
    size: root.width, root.height

    canvas:
      Color:
        rgba: (28/255,236/255,104/255,0.85)
      Triangle:
        points: [root.width, root.height, root.width, root.height*0.75, root.width*0.27, root.height]
      Color:
        rgba: (173/255,246/255,68/255,0.75)
      Triangle:
        points: [0, root.height, 0, root.height*0.85, root.width*0.5, root.height]
      Color:
        rgba: (124/255,124/255,124/255, 1)

    canvas.before:
      Color:
        rgba: (1,1,1,1)
      Rectangle:
        pos: self.pos
        size: self.size


<MainScreen>

  FloatLayout: 

    size: root.width, root.height

    canvas.before:
      Color:
        rgba: (1,1,1,1)
      Rectangle:
        pos: self.pos
        size: self.size

    canvas:
      Color:
        rgba: (28/255,236/255,104/255,0.85)
      Triangle:
        points: [root.width, root.height, root.width, root.height*0.75, root.width*0.27, root.height]
      Color:
        rgba: (173/255,246/255,68/255,0.75)
      Triangle:
        points: [0, root.height, 0, root.height*0.85, root.width*0.5, root.height]
      Color: 
        rgba: (1,1,1,1)
      Ellipse:
        pos: self.width*0.86, self.height*0.91
        size: self.width*0.12, self.width*0.12

    Button: 
      font_size: 70
      text: '+'
      size_hint: 0.05,0.05
      pos_hint: {'x': 0.895, 'top': 0.9676}
      on_release: root.show_name_popup()
      color: (62/255,239/255,127/255,1)
      background_normal: ''

    Label:
      text_size: self.size
      font_size: 80*1.25
      size_hint: 0.5,0.07
      color: 28/255,236/255,104/255,1
      pos_hint: {'x': 0.08, 'top': 0.87}
      text: 'Home'

    Button:
      text_size: self.size
      text: 'See Database'
      on_press: root.manager.current = 'Data'
      pos_hint: {"x":0.08, "top": 0.8}
      size_hint: 0.7, 0.05
      color: 24/255,124/255,124/255, 1
      background_normal: ''
      source: 'https://imgur.com/a/EkK6Rbs'

    RecycleView:    
      do_scroll_x: False
      do_scroll_y: True
      size_hint: (1, 0.73)
      GridLayout:
        height: self.minimum_height
        size_hint_x: 1
        size_hint_y: None
        id: grid_1
        cols: 1


<NamePopup>:

  canvas:
    Color:
      rgba: (173/255,246/255,68/255,0.75)
    Rectangle:
      pos: self.pos
      size: self.size
  plant_name: PlantName
  cols: 2

  Label:
    text: 'We will direct you to an input screen' 
    italic: True
    color: (0,0,0,1)
    font_size: 30
    pos_hint: {'x': 0, 'top': 1.37}

  Label:
    text: 'if we do not have the values'
    italic: True
    color: (0,0,0,1)
    font_size: 30
    pos_hint: {'x': 0, 'top': 1.3}

  Label:
    text: 'for your plant in our database.'
    italic: True
    color: (0,0,0,1)
    font_size: 30
    pos_hint: {'x': 0, 'top': 1.23}

  TextInput:
    id: PlantName
    multiline: False
    size_hint: 0.6,0.1
    pos_hint: {'x': 0.2, 'top': 0.55}
    background_normal: 'white.png'
    background_active: 'white.png' 
    hint_text: 'Enter Here'
    
  Button:
    font_size: 27
    size_hint: 0.35, 0.12
    pos_hint: {'x': 0.1, 'top': 0.25}
    background_normal: ''
    background_color: 1, 1, 1, 0.73
    text: 'Exit'
    color: (0, 0, 0, 1)
    on_release: root.parent.parent.parent.dismiss()

  Button:
    font_size: 27
    size_hint: 0.35, 0.12
    background_normal: ''
    background_color: 1, 1, 1, 0.73
    pos_hint: {'x': 0.55, 'top': 0.25}
    text: 'Submit'
    color: (0, 0, 0, 1)
    on_press: root.set_name()
    on_release: root.parent.parent.parent.dismiss()
    on_release: root.verify()


<SecondInputScreen>

  light: light
  soil_moisture: soilMoisture
  humidity: humidity
  air_temp: airTemp
  soil_temp: soilTemp

  FloatLayout:

    size: root.width, root.height
    
    canvas:
      Color:
        rgba: (28/255,236/255,104/255,0.85)
      Triangle:
        points: [root.width, root.height, root.width, root.height*0.75, root.width*0.27, root.height]
      Color:
        rgba: (173/255,246/255,68/255,0.75)
      Triangle:
        points: [0, root.height, 0, root.height*0.85, root.width*0.5, root.height]
      Color:
        rgba: (124/255,124/255,124/255, 1)
      Rectangle:
        pos: root.width*0.025,root.height*(0.75-0.045-0.0525)
        size: root.width*0.8, 5
      Rectangle:
        pos: root.width*0.025,root.height*((0.75-0.12*4-0.05)-0.0525)
        size: root.width*0.8, 5
      Rectangle:
        pos: root.width*0.025,root.height*((0.75-0.12*3-0.05)-0.0525)
        size: root.width*0.8, 5
      Rectangle:
        pos: root.width*0.025,root.height*((0.75-0.12*2-0.05)-0.0525)
        size: root.width*0.8, 5
      Rectangle:
        pos: root.width*0.025,root.height*((0.75-0.12-0.05)-0.0525)
        size: root.width*0.8, 5

    canvas.before:

      Color:
        rgba: (1,1,1,1)
      Rectangle:
        pos: self.pos
        size: self.size
        
    Label:
      id: title
      text_size: self.size
      font_size: 80*1.25
      size_hint: 0.5,0.07
      color: 28/255,236/255,104/255,1
      pos_hint: {'x': 0.08, 'top': 0.87}
      text: 'Input'

    Label:
      text_size: self.size
      font_size: 40*1.25
      size_hint: 1, 0.1
      color: 124/255,124/255,124/255
      pos_hint: {'x': 0.025, 'top': 0.8}
      text: 'Relative Air Humidity (%)'

    Label:
      text_size: self.size
      font_size: 40*1.25
      size_hint: 1, 0.1
      color: 124/255,124/255,124/255
      pos_hint: {'x': 0.025, 'top': 0.68}
      text: 'Number of hours of light per day'
      
    Label:
      text_size: self.size
      font_size: 40*1.25
      size_hint: 1, 0.1
      color: 124/255,124/255,124/255
      pos_hint: {'x': 0.025, 'top': 0.56}
      text: 'Automatic Watering (0/1)'

    Label:
      text_size: self.size
      font_size: 40*1.25
      size_hint: 1, 0.1
      color: 124/255,124/255,124/255
      pos_hint: {'x': 0.025, 'top': 0.44}
      text: 'Soil Temperature (°C)'
      
    Label:
      text_size: self.size
      font_size: 40*1.25
      size_hint: 1, 0.1
      color: 124/255,124/255,124/255
      pos_hint: {'x': 0.025, 'top': 0.32}
      text: 'Air Temperature (°C)'
      
    TextInput:
      id: humidity
      multiline: False
      size_hint: 0.85,0.04
      pos_hint: {'x': 0.025, 'top': 0.75-0.05}
      background_normal: 'white.png'
      background_active: 'white.png' 
      hint_text: 'Enter Here'

    TextInput:
      id: light
      multiline: False
      size_hint: 0.85,0.04
      pos_hint: {'x': 0.025, 'top': 0.75-0.12-0.05}
      background_normal: 'white.png'
      background_active: 'white.png'
      hint_text: 'Enter Here'

    TextInput:
      id: soilMoisture
      multiline: False
      size_hint: 0.85,0.04
      pos_hint: {'x': 0.025, 'top': 0.75-0.12*2-0.05}
      background_normal: 'white.png'
      background_active: 'white.png'
      hint_text: 'Enter Here'

    TextInput:
      id: soilTemp
      multiline: False
      size_hint: 0.85,0.04
      pos_hint: {'x': 0.025, 'top': 0.75-0.12*3-0.05}
      background_normal: 'white.png'
      background_active: 'white.png'   
      hint_text: 'Enter Here'

    TextInput:
      id: airTemp
      multiline: False
      size_hint: 0.85,0.04
      pos_hint: {'x': 0.025, 'top': 0.75-0.12*4-0.05}
      background_normal: 'white.png'
      background_active: 'white.png' 
      hint_text: 'Enter Here'
      
    Button:
      font_size: 50
      size_hint: 0.4, 0.075
      pos_hint: {'x': 0.025, 'top': 0.12}
      background_normal: ''
      background_color: 195/255,195/255,195/255, 1
      text: 'Cancel'
      on_release: root.cancel()
      
    Button:
      font_size: 50
      size_hint: 0.4,0.075
      pos_hint: {'x': 0.5, 'top': 0.12}
      background_normal: ''
      background_color: 72/255,239/255,128/255, 1
      text: 'Submit'
      on_release: root.submit()
      
      
<ValidationPopup>:

  canvas:
  
    Color:
      rgba: (173/255,246/255,68/255,0.75)
    Rectangle:
      pos: self.pos
      size: self.size

  Label:
    text: 'Please try again'
    italic: True
    color: (0,0,0,1)
    font_size: 30
    pos_hint: {'x': 0, 'top': 1.35}

  Button:
    font_size: 30
    size_hint: 0.4, 0.2
    pos_hint: {'x': 0.3, 'top': 0.4}
    background_normal: ''
    background_color: 1, 1, 1, 0.73
    text: 'Next'
    color: (0, 0, 0, 1)
    on_release: root.parent.parent.parent.dismiss()

<PlantScreen>

  FloatLayout:

    size: root.width, root.height
    id: grid_layout
    
    canvas:
      Color:
        rgba: (28/255,236/255,104/255,0.85)
      Triangle:
        points: [root.width, root.height, root.width, root.height*0.75, root.width*0.27, root.height]
      Color:
        rgba: (173/255,246/255,68/255,0.75)
      Triangle:
        points: [0, root.height, 0, root.height*0.85, root.width*0.5, root.height]
      Color:
        rgba: (124/255,124/255,124/255, 1)

    canvas.before:
      Color:
        rgba: (1,1,1,1)
      Rectangle:
        pos: self.pos
        size: self.size


<ImageScreen>:

  FloatLayout:
  
    id: float
    size: root.width, root.height
    
    Button:
      size_hint: 0.3, 0.1
      pos_hint: {'x': 0.35, 'top': 0.0}
      text: 'Return'
      on_press: root.manager.current = 'PlantScreen'

""")




class MyApp(App):

    global sm
    sm = ScreenManager(transition=FadeTransition())
    sm.add_widget(WelcomeScreen(name='Welcome'))
    sm.add_widget(MainScreen(name='Main'))
    sm.add_widget(PlantScreen(name='PlantScreen'))
    sm.add_widget(SecondInputScreen(name='SecondInput'))
    sm.add_widget(DatabaseScreen(name='Data'))
    sm.add_widget(LoadingScreen(name='Load'))
    sm.add_widget(ImageScreen(name='Image'))
    sm.current = 'Welcome'


    def build(self):
        self.getPlantsDatabase()
        self.getPlantsImage()
        self.getSensorsDatabase()
        return sm


    def getPlantsDatabase(self):
        root_folder = self.user_data_dir
        plantsdb_path_getter = os.path.join(root_folder, "PlantsDatabase.db")
        return plantsdb_path_getter


    def getPlantsImage(self):
        root_folder = self.user_data_dir
        image_path_getter = os.path.join(root_folder, "imagetest.jpg")
        return image_path_getter
    
    
    def getSensorsDatabase(self):
        root_folder = self.user_data_dir
        sensorsdb_path_getter = os.path.join(root_folder, "raspberrypi.csv")
        return sensorsdb_path_getter



MA = MyApp()
PlantsDatabase = MA.getPlantsDatabase()
SensorsDatabase = MA.getSensorsDatabase()
ImageSource = MA.getPlantsImage()





if __name__ == '__main__':
    MyApp().run()
