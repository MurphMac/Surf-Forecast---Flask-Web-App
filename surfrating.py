import sqlite3
import math

#Main Function
def get_rating(location_id, skill):

    #Wind Functions:
    def wind_magnitude_points(wind_magnitude):
        #Equate winds above 30kts to 30
        if wind_magnitude >= 30:
            wind_magnitude = 30

        #Get number of points wind will contribute to rating
        points = round( -0.0125*((wind_magnitude - 10) ** 2) + 5 , 1)
        return points

    def wind_points_multiplier(wind_points, difference):
        #Get multiplier from manipulated cos graph
        multiplier = 0.5 * math.cos(difference) + 0.5

        #Multiply points from wind
        points = wind_points * multiplier

        return points

    #bearings for each location
    def offshore_checker(location, wind_direction):
        location_land_direction = {
            "tauranga": 28,
            "gisborne": 151,
            "dunedin": 175,
            "christchurch": 60
        }

        #Get corresponding location direction
        land_direction = location_land_direction[location]

        #Calculate difference in angle
        difference = 180 - abs(180 - abs(wind_direction - land_direction) % 360)

        #In radians
        difference_rads = difference * (math.pi/180)

        return difference_rads

    #Swell functions
    def swell_size_points(skill, swell_size):
        global no_skill
        #Ideal wave height for different skills
        ideal_size = {
            "beginner": 0.7,
            "intermediate": 1.2,
            "expert": 1.7
        }

        #Get points for swell size
        if skill == "":
            points = 0
            no_skill = True
        else:
            points = 2.5 * (0.5 * math.cos( 5 * (swell_size - ideal_size[skill]) + 0.5 ))

        return points

    def wave_period_points(swell_period):
        global no_skill

        #Equate above 18s to 18s
        if swell_period >= 18:
            swell_period = 18

        if no_skill == True:
            no_skill_multiplier = 2
        else:
            no_skill_multiplier = 1

        #Calculate points
        points = 2.5 * (1/18 * swell_period) * no_skill_multiplier

        return points

    no_skill = False

    # Connection to the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wind.wind_direction, wind.wind_speed, waves.swell_size, waves.swell_period
        FROM wind
        JOIN waves ON waves.time_id = wind.time_id
        JOIN location l ON wind.location_id = l.location_id
        WHERE l.location_id = ?
    """, (location_id,))

    data = cursor.fetchall()
    conn.close()

    #Remove unnecessary rows
    del data[-4:]

    averaged_data = []

    #Get average of data values in 6 hour increments (28 total in 7 days)
    for i in range(0, len(data), 8):
        averaged_data.append(tuple(sum(data[i+j][col] for j in range(4)) / 4 for col in range(4)))

    #Get amount of points which wind will apply to and apply mutliplier based on direction and swell size and period contribute
    ratings = [
        int((round(wind_points_multiplier(wind_magnitude_points(value[1]), value[0]) + swell_size_points(skill, value[2]) + wave_period_points(value[3]), 0)))
        for value in averaged_data 
    ]

    return ratings
