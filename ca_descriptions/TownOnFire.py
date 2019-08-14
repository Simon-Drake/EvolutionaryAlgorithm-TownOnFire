# Name: Conway's game of life
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np


def transition_func(grid, neighbourstates, neighbourcounts, fuel_parameter, water_break, fire_break):
    # dead = state == 0, burning = state == 1, chaparral = state = 2,
    # lake = state == 3, canyon = state == 4, forest = state == 5, town = state == 6

    # unpack state counts for all states
    dead, burning_neighbours, chaparral_neighbours, lake_neighbours, canyon_neighbours, forest_neighbours, town_neighbours = neighbourcounts
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    #Identify which cells have neighbours burning in the NSWE.
    north_wind_vulnerable = (N == 1) #Wind direction N -> S
    west_wind_vulnerable = (W == 1) #Wind direction W -> E
    south_wind_vulnerable = (S == 1) #Wind direction S -> N
    east_wind_vulnerable = (E == 1) #Wind direction E -> W

    #Identify water break terrain.
    water_break_grid = (water_break == 1)

    #Introduce stochastic based decisions.
    #Create a grid containing random numbers.
    #Increment the grid depending on how many burning neighbours a cell has.
    random_grid = (np.random.rand(200,200))
    bias_grid = random_grid + (0.01 * burning_neighbours)

    #Increment the grid further depending on wind direction
    #The appropriate lines need to be commented out, if all lines are commented out there is no wind.
    #bias_grid[north_wind_vulnerable] += 0.2 #Wind direction N -> S
    #bias_grid[west_wind_vulnerable] += 0.2 #Wind direction W -> E
    #bias_grid[south_wind_vulnerable] += 0.2 #Wind direction S -> N
    #bias_grid[east_wind_vulnerable] += 0.2 #Wind direction E -> W

    #Identify where the water break of fire break will be.
    water_break_grid = (water_break == 1)
    fire_break_grid = (fire_break == 1)

    #Determine which cell catches fire
    birth_fire_chaparral =  (grid == 2 ) & ( burning_neighbours >= 1) & (bias_grid > 0.83)
    birth_fire_canyon = (grid == 4 ) & (burning_neighbours >= 1) & (bias_grid > 0.5)
    birth_fire_forest =  (grid == 5)  & (burning_neighbours >= 1) & (bias_grid > 0.99)
    birth_fire_town = (grid == 6 ) & (burning_neighbours >= 1)
    birth_water_break = (((grid == 2) | (grid == 4) | (grid == 5)) & (burning_neighbours >= 1) & (water_break == 1)) | (lake_neighbours > 3)
    birth_fire_break = ((grid == 2) | (grid == 4) | (grid == 5)) & (burning_neighbours >= 1) & (fire_break == 1)

    #Reduce fuel parameter for burning cells and identify those which have no more fuel.
    cells_in_state1 = (grid == 1)
    fuel_parameter[cells_in_state1] -= 1
    decayed_to_zero = (fuel_parameter == 0)
    grid[decayed_to_zero] = 0

    #Fire break.
    #Uncomment this for fire break study.
    if(np.any(birth_fire_break)):
        grid[fire_break_grid] = 0

    #Set birth_fire cells to burning.
    grid[birth_fire_chaparral] = 1
    grid[birth_fire_canyon] = 1
    grid[birth_fire_forest] = 1
    grid[birth_fire_town] = 1
    #Drop water.
    #Uncomment this for water break study.
    #grid[birth_water_break] = 3

    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Conway's game of life"
    config.dimensions = 2
    config.states = (0, 1, 2, 3, 4, 5, 6)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    #Assigning colours to states
    config.state_colors = [(0,0,0),(0.87,0.5,0.05),(0.3,0.79,0.5),
    (0.44,0.49,0.82),(0.63,0.5,0.3),(0.2,0.44,0.14),(0.5, 0.5, 0.5)]

    #Creating the terrain
    config.initial_grid = np.full((200,200), 2)
    for i in range(20, 64):
        for j in range(40, 64):
            config.initial_grid[j][i] = 3
    for i in range(128, 144):
        for j in range(20, 144):
            config.initial_grid[j][i] = 4
    for i in range(196,200):
        for j in range(0, 8):
            config.initial_grid[i][j] = 6

    #Mapping forest.
    #Extending dense forest in 4 direcions.
    #The appropriate lines of code need to be commented out.
    #for i in range(17, 104): #Extend East ( overlaps canyon )
    #for i in range(60, 147): #Extend West
    for i in range(60, 104): #No extention W/E
        #for j in range(72, 168): #Extend north
        #for j in range(120, 200): #Extend south ( cannot double area )
        for j in range(120, 168): #No extention N/S
            config.initial_grid[j][i] = 5


    #Fire starting at the power plant
    #config.initial_grid[0][0] = 1

    #Fire starting at the proposed incinirator
    config.initial_grid[0][199] = 1

    config.grid_dims = (200,200)
    config.num_generations = 1000
    config.wrap = False

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    #Define fuel parameter matrix ( 1 = 1.5hours )
    fuel_parameter = np.full((200,200), 34) #2.1 days
    for i in range(128, 144):
        for j in range(20, 144):
            fuel_parameter[j][i] = 4#6 hours
    #Setting fuel for  forest.
    #Extending dense forest in 4 direcions.
    #The appropriate lines of code need to be commented out.
    #for i in range(17, 104): #Extend East ( overlaps canyon )
    #for i in range(60, 147): #Extend West
    for i in range(60, 104): #No extention W/E
        #for j in range(72, 168): #Extend north
        #for j in range(120, 200): #Extend south ( cannot double area )
        for j in range(120, 168): #No extention N/S
            fuel_parameter[j][i] = 400 #25 days
    for i in range(196,200):
        for j in range(0, 8):
            fuel_parameter[i][j] = 1

    #Define water break coordinate matrix
    water_break = np.zeros((200,200))
    #for i in range(0,41):
    for i in range(155,195):
        for j in range(5,46):
        #for j in range(140,181):
            water_break[j][i] = 1

    #Define fire break coordinate matrix
    fire_break = np.zeros((200,200))
    for i in range(190,195):
        for j in range(0, 20):
            fire_break[i][j] = 1
    for i in range(190,200):
        for j in range(20, 25):
            fire_break[i][j] = 1

    # Create grid object
    grid = Grid2D(config, (transition_func, fuel_parameter, water_break, fire_break))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()

    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
