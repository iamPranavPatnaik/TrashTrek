import tkinter as tk
from tkinter import messagebox
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_obstacle = False
        self.is_trash = False
        self.g_cost = float("inf")
        self.h_cost = 0
        self.parent = None

    def __lt__(self, other):
        return self.g_cost + self.h_cost < other.g_cost + other.h_cost

class AStarPathfinding:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[Cell(x, y) for y in range(cols)] for x in range(rows)]
        self.start = self.grid[0][0]
        self.end = self.grid[rows - 1][cols - 1]
        self.open_set = []
        self.closed_set = []
        self.trash_positions = []

    def set_obstacle(self, x, y):
        self.grid[x][y].is_obstacle = True

    def calculate_h_cost(self, cell, target):
        return abs(cell.x - target.x) + abs(cell.y - target.y)

    def get_neighbors(self, cell):
        neighbors = []
        dx = [-1, 0, 1, 0, -1, -1, 1, 1]
        dy = [0, 1, 0, -1, -1, 1, 1, -1]

        for i in range(8):
            nx, ny = cell.x + dx[i], cell.y + dy[i]

            if 0 <= nx < self.rows and 0 <= ny < self.cols and not self.grid[nx][ny].is_obstacle:
                neighbors.append(self.grid[nx][ny])

        return neighbors

    def reconstruct_path(self, current):
        path = []
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        return path[::-1]

    def run_algorithm(self):
        destinations = [self.start] + self.trash_positions + [self.end]

        path = []
        for i in range(len(destinations) - 1):
            start = destinations[i]
            end = destinations[i + 1]

            current_path = self.run_path(start, end)
            if not current_path:
                return None

            path.extend(current_path[:-1])

        return path

    def run_path(self, start, end):
        self.open_set = []
        self.closed_set = []
        for row in self.grid:
            for cell in row:
                cell.g_cost = float("inf")
                cell.parent = None

        self.open_set.append(start)

        while self.open_set:
            current = min(self.open_set, key=lambda cell: cell.g_cost + cell.h_cost)

            if current == end:
                return self.reconstruct_path(current)

            self.open_set.remove(current)
            self.closed_set.append(current)

            for neighbor in self.get_neighbors(current):
                if neighbor in self.closed_set:
                    continue

                tentative_g_cost = current.g_cost + self.calculate_h_cost(neighbor, end)

                if neighbor not in self.open_set:
                    self.open_set.append(neighbor)
                elif tentative_g_cost >= neighbor.g_cost:
                    continue

                neighbor.parent = current
                neighbor.g_cost = tentative_g_cost
                neighbor.h_cost = self.calculate_h_cost(neighbor, end)

        return None

class GUI:
    def __init__(self, root, rows, cols):
        self.rows = rows
        self.cols = cols
        self.astar = AStarPathfinding(rows, cols)
        self.cell_size = 25  # Adjust cell size for better visibility
        self.robot_size = 5  # Adjust robot size
        self.robot_speed = 1  # Adjust robot speed
        canvas_width = cols * self.cell_size
        canvas_height = rows * self.cell_size
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg='white')
        self.canvas.pack()
        self.canvas.bind('<B1-Motion>', self.draw_obstacle)
        self.canvas.bind('<Button-1>', self.draw_obstacle)
        self.canvas.bind('<Button-3>', self.place_trash)
        self.highlight_goal()
        reset_button = tk.Button(root, text="Reset Board", command=self.reset_board)
        reset_button.pack()

        self.distance_label = tk.Label(root, text="Total distance traveled: 0 meters")
        self.distance_label.pack()

        self.robot_image = tk.PhotoImage(file=r"A_Star\robotImage.png")

        self.robot_size = 5
        self.robot_speed = 3
        self.prev_x = self.prev_y = 0  # Initialize prev_x and prev_y for draw_path_animation

        self.sand_image = tk.PhotoImage(file=r"A_Star\sandSandSand.png")
        self.trash_image = tk.PhotoImage(file=r"A_Star\trash.png")
        self.obstacle_image = tk.PhotoImage(file=r"A_Star\obstacle.png")

        self.draw_sand_background()  # Draw sand background immediately
        
        self.trash_image = self.trash_image.subsample(self.trash_image.width() // self.cell_size,
                                                      self.trash_image.height() // self.cell_size)
        self.obstacle_image = self.obstacle_image.subsample(self.obstacle_image.width() // self.cell_size,
                                                            self.obstacle_image.height() // self.cell_size)

        self.robot = None

    def draw_sand_background(self):
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size

        # Create a background rectangle with the sand image
        bg_rect = self.canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="", outline="")
        self.canvas.itemconfig(bg_rect, fill="", outline="")
        self.canvas.tag_lower(bg_rect)

        # Overlay the sand texture on the background
        for x in range(0, canvas_width, self.sand_image.width()):
            for y in range(0, canvas_height, self.sand_image.height()):
                self.canvas.create_image(x, y, anchor="nw", image=self.sand_image)

        # Update the canvas to display the changes
        self.canvas.update()
    
    def draw_obstacle(self, event):
        x, y = event.x // self.cell_size, event.y // self.cell_size
        if 0 <= x < self.cols and 0 <= y < self.rows:
            if not self.astar.grid[y][x].is_obstacle and not self.astar.grid[y][x].is_trash:
                self.astar.set_obstacle(y, x)
                self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor="nw", image=self.obstacle_image)

    def place_trash(self, event):
        x, y = event.x // self.cell_size, event.y // self.cell_size
        cell = self.astar.grid[y][x]

        if not cell.is_obstacle and not cell.is_trash and cell != self.astar.start and cell != self.astar.end:
            cell.is_trash = True
            self.astar.trash_positions.append(cell)
            self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor="nw", image=self.trash_image)

    def reset_board(self):
        self.astar = AStarPathfinding(self.rows, self.cols)
        self.canvas.delete("all")
        self.draw_sand_background()
        self.highlight_goal()

        self.distance_label.config(text="Total distance traveled: 0 meters")

    def highlight_goal(self):
        x, y = self.astar.end.x, self.astar.end.y
        self.canvas.create_rectangle(y * self.cell_size - 1, x * self.cell_size - 1,
                                     y * self.cell_size + self.cell_size + 1, x * self.cell_size + self.cell_size + 1,
                                     outline='green', width=3)
    
    def draw_path_animation(self, path):
        if not path:
            return

        for i in range(1, len(path)):
            x, y = path[i]
            x_center = y * self.cell_size + self.cell_size // 2
            y_center = x * self.cell_size + self.cell_size // 2

            self.canvas.create_line(
                self.prev_x, self.prev_y, x_center, y_center,
                fill="blue", dash=(4, 4)
            )

            self.prev_x, self.prev_y = x_center, y_center

        self.animate_robot_on_path(path)

    def animate_robot_on_path(self, path):
        if not path:
            return

        x, y = path[0]
        x_center = y * self.cell_size + self.cell_size // 2
        y_center = x * self.cell_size + self.cell_size // 2

        if not self.robot:
            self.robot = self.canvas.create_image(
                x_center - self.robot_size // 2,
                y_center - self.robot_size // 2,
                anchor="nw",
                image=self.robot_image
            )

        self.move_robot(path, x_center, y_center)

    def move_robot(self, path, prev_x, prev_y):
        if not path:
            return

        x, y = path[0]
        x_center = y * self.cell_size + self.cell_size // 2
        y_center = x * self.cell_size + self.cell_size // 2

        # Check if the next cell is an obstacle
        if self.astar.grid[x][y].is_obstacle:
            return

        delta_x = x_center - prev_x
        delta_y = y_center - prev_y

        self.canvas.move(self.robot, delta_x, delta_y)
        self.canvas.update()
        self.canvas.after(100)  # Adjust the delay between steps (in milliseconds)

        self.move_robot(path[1:], x_center, y_center)

    def run_algorithm(self):
        path = self.astar.run_algorithm()

        if path:
            self.draw_path_animation(path)

            total_distance = 0
            for i in range(1, len(path)):
                x1, y1 = path[i - 1]
                x2, y2 = path[i]
                total_distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            self.distance_label.config(text=f"Total distance traveled: {total_distance:.2f} meters")
        else:
            messagebox.showinfo("No Path Found", "A* algorithm could not find a path to the destination.")


if __name__ == "__main__":
    rows, cols = 15, 15
    root = tk.Tk()
    root.title("A* Pathfinding Algorithm")

    gui = GUI(root, rows, cols)

    run_button = tk.Button(root, text="Run A* Algorithm", command=gui.run_algorithm)
    run_button.pack()

    root.mainloop()
