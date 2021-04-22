import sqlite3


def create_connection(db_file):
    """ create a database connection to a SQLite database """

    conn = None

    try:

        conn = sqlite3.connect(db_file)

        print(sqlite3.version)

    except Error as e:

        print(e)

    finally:

        if conn:
            conn.close()

var = r"C:\Users\heeri\PycharmProjects\pythonProject2\Database.db"
if __name__ == '__main__':
    create_connection
    (var)


conn = sqlite3.connect('PlantsDatabase.db')
c = conn.cursor()
c.execute('''CREATE TABLE Plants
             (Plant text, Soil_Moisture real, Air_Temperature real, Soil_Temperature real, Humidity real, Light_Intensity real)''')

plants = [('Basil', True, 25, 25, 40, 7),
          ('Rosemary', True, 17, 17, 50, 6 ),
          ('Parsley', True, 23, 25, 50, 7),
          ('Oregano', True, 15, 15, 50, 10),
          ('Broad beans', True, 15, 15, 50, 8),
          ('Tomato', True, 20, 20, 50, 9),
          ('Carrots', True, 16, 16, 50, 6),
          ('Beetroot', True, 18, 18, 50, 6),
          ('Radish', True, 16, 16, 50, 7),
          ('Sweet peppers', True, 23, 24, 50, 5),
          ('Spinach', True, 24, 24, 50, 5),
          ('Garlic', True, 12, 12, 50, 7),
          ('Ginger', True, 22, 23, 50, 5),
          ('Watercress', True, 20, 20, 60, 4),
          ('Mint', True, 17, 17, 70, 7),
          ('Coriander', True, 21, 21, 50, 5),
          ('Chives', True, 20, 20, 50, 6),
          ('Sage', True, 17, 17, 40, 8),
          ('Dill', True, 20, 20, 50, 8),
          ('Peas', True, 15, 15, 50, 8),
          ('Chili', True, 20, 20, 50, 7),
          ('Lettuce', True, 15, 15, 50, 7),
          ('Potato', True, 15, 15, 50, 7)
            ]
c.executemany('INSERT INTO Plants VALUES (?,?,?,?,?,?)', plants)

c.execute('''CREATE TABLE User_Inputs
             (Plant_Name text, Plant_Type text)''')

conn.commit()

conn.close()
