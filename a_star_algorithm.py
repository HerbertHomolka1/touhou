import pygame
import csv

def load_walls():
    walls = []
    csv_file = "grid.csv"
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        grid = list(reader)
        # new_grid = []
        # for row in grid:
        #     new_row = [ True if cell == 'x' else False for cell in row]
        #     new_grid.append(new_row)
        return grid #new_grid
# Define the grid size and square size
GRID_SIZE_X = 80
GRID_SIZE_Y = 45
SQUARE_SIZE = 20
BUTTON_HEIGHT = 50

# Initialize Pygame
pygame.init()

# Calculate the window size based on the grid and square size
window_width = GRID_SIZE_X * SQUARE_SIZE
window_height = GRID_SIZE_Y * SQUARE_SIZE + 2*BUTTON_HEIGHT
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Grid Demo")

# Create a 2D list to store the state of each square (True for black, False for white)
grid = [['o' for _ in range(GRID_SIZE_X)] for _ in range(GRID_SIZE_Y)]

# Create a button rectangle
button_rect = pygame.Rect(0, window_height - 2*BUTTON_HEIGHT, window_width, BUTTON_HEIGHT)
button_rect2 = pygame.Rect(0, window_height - BUTTON_HEIGHT, window_width, BUTTON_HEIGHT)

# Variables for mouse dragging
mouse_dragging = False

# Main game loop

current = 'x'
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Check if the button is clicked
            if button_rect.collidepoint(mouse_pos):
                # Create and save the CSV file
                with open('grid.csv', 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    for row in grid:
                        writer.writerow([cell for cell in row])
            elif button_rect2.collidepoint(mouse_pos):
                grid = load_walls()
                
            else:
                # Start mouse dragging
                mouse_dragging = True
                square_x = mouse_pos[0] // SQUARE_SIZE
                square_y = mouse_pos[1] // SQUARE_SIZE
                # Toggle the state of the clicked square
                if grid[square_y][square_x] in ['x','g','m','d','p','s']:
                    grid[square_y][square_x] = 'o'
                else:
                    grid[square_y][square_x] = current
        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop mouse dragging
            mouse_dragging = False
        elif event.type == pygame.MOUSEMOTION and mouse_dragging:
            # Update the state of squares when dragging the mouse
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] > 0 and mouse_pos[0] <1600 and mouse_pos[1] >0 and mouse_pos[1] <900:
                square_x = mouse_pos[0] // SQUARE_SIZE
                square_y = mouse_pos[1] // SQUARE_SIZE
            # Toggle the state of the square under the mouse cursor
            grid[square_y][square_x] = 'x'

    keys = pygame.key.get_pressed()
    # enemies: monster, drone, guard
    if keys[pygame.K_m]:
        current = 'm'
    elif keys[pygame.K_d]:
        current = 'd'
    elif keys[pygame.K_g]:
        current = 'g'
    #????
    elif keys[pygame.K_p]:
        current = 'p'
    # switch
    elif keys[pygame.K_s]:
        current = 's'
    #chest: opens when all switches are open
    elif keys[pygame.K_c]:
        current = 'c'

    # Draw the grid
    for y in range(GRID_SIZE_Y):
        for x in range(GRID_SIZE_X):
            square_pos = (x * SQUARE_SIZE, y * SQUARE_SIZE)
            if grid[y][x] == 'x':
                color = pygame.Color("black")  
            elif grid[y][x] in ['g','d','m']:
                color = pygame.Color("red")

            elif grid[y][x] in ['s']:
                color = (140,110,23)
            elif grid[y][x] in ['c']:
                color = pygame.Color('pink')
            
            else:
                color = pygame.Color('white')
          

            pygame.draw.rect(screen, color, (*square_pos, SQUARE_SIZE, SQUARE_SIZE))

    # Draw the save button
    pygame.draw.rect(screen, pygame.Color("green"), button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render("Save to CSV", True, pygame.Color("white"))
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)
    # # Draw the load button
    pygame.draw.rect(screen, pygame.Color("blue"), button_rect2)
    text = font.render("Load from CSV", True, pygame.Color("white"))
    text_rect = text.get_rect(center=button_rect2.center)
    screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()
