import tkinter as tk
import random
from tkinter import messagebox
import math

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
        dx = [-1, 0, 1, 0, -1, -1, 1, 1]  # Movement in all eight directions
        dy = [0, 1, 0, -1, -1, 1, 1, -1]

        for i in range(8):  # Consider all EIGHT directions
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
        # Combine trash positions with end cell as the last destination
        destinations = [self.start] + self.trash_positions + [self.end]

        path = []
        for i in range(len(destinations) - 1):
            start = destinations[i]
            end = destinations[i + 1]

            current_path = self.run_path(start, end)
            if not current_path:
                return None

            path.extend(current_path[:-1])  # Exclude the last cell (end position) from the current path

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
        self.root = root
        self.root.title("Meet TrashTrek")  # Window title
        self.root.iconbitmap(r"A_Star\trashtrekLogo.ico") # Custom logo icon
        self.cell_size = 20  # 20x20 pixels
        canvas_width = cols * self.cell_size
        canvas_height = rows * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg='white')
        self.canvas.pack()
        self.sand_image = tk.PhotoImage(file=r"A_Star\sandSandSand.png")
        self.draw_sand_background()
        self.trash_image = tk.PhotoImage(file=r"A_Star\trash.png")
        self.canvas.bind('<B1-Motion>', self.draw_obstacle)
        self.canvas.bind('<Button-1>', self.draw_obstacle)
        self.canvas.bind('<Button-3>', self.place_trash)
        self.highlight_goal()

        reset_button = tk.Button(root, text="Reset Board", command=self.reset_board)
        reset_button.pack()

        self.distance_label = tk.Label(root, text="Total distance traveled: 0 meters")
        self.distance_label.pack()

        self.robot_size = 10  # Robot size = 10x10 pixels
        self.robot_speed = 3  # Robot speed = 3 pixels per step

        self.robot = None

    def draw_sand_background(self):
        for x in range(0, self.cols * self.cell_size, self.sand_image.width()):
            for y in range(0, self.rows * self.cell_size, self.sand_image.height()):
                self.canvas.create_image(x, y, anchor="nw", image=self.sand_image)

    def place_trash(self, event):
        x, y = event.x // 20, event.y // 20
        cell = self.astar.grid[y][x]

        if not cell.is_obstacle and not cell.is_trash and cell != self.astar.start and cell != self.astar.end:
            cell.is_trash = True
            self.astar.trash_positions.append(cell)
            self.canvas.create_oval(x * 20 + 5, y * 20 + 5, x * 20 + 15, y * 20 + 15, fill='grey')

            # Get the count of trash positions and display it on the circle
            trash_count = len(self.astar.trash_positions)
            center_x = x * 20 + 10  # Middle x-coordinate of the circle
            center_y = y * 20 + 10  # Middle y-coordinate of the circle
            self.canvas.create_text(center_x, center_y, text=str(trash_count), fill="white", font=("Arial", 9, "bold"))

    def draw_obstacle(self, event):
        x, y = event.x // 20, event.y // 20
        if 0 <= x < self.cols and 0 <= y < self.rows:
            if not self.astar.grid[y][x].is_obstacle and not self.astar.grid[y][x].is_trash:
                self.astar.set_obstacle(y, x)
                self.canvas.create_rectangle(x * 20, y * 20, x * 20 + 20, y * 20 + 20, fill='black')

    def reset_board(self):
        self.astar = AStarPathfinding(self.rows, self.cols)
        self.canvas.delete("all")
        self.draw_sand_background()
        self.highlight_goal()

        # Deleting the robot and resetting its ID
        if self.robot:
            self.canvas.delete(self.robot)
            self.robot = None

        self.distance_label.config(text="Total distance traveled: 0 meters")

    def highlight_goal(self):
        x, y = self.astar.end.x, self.astar.end.y
        self.canvas.create_rectangle(y * 20 - 1, x * 20 - 1, y * 20 + 21, x * 20 + 21, outline='green', width=3)

    def draw_path(self, path):
        for x, y in path:
            # Calculate the CENTER of the cell for placing the robot
            center_x = y * self.cell_size + self.cell_size // 2
            center_y = x * self.cell_size + self.cell_size // 2
            # Calculate the COORDS for the robot
            x1 = center_x - self.robot_size // 2
            y1 = center_y - self.robot_size // 2
            x2 = center_x + self.robot_size // 2
            y2 = center_y + self.robot_size // 2
            self.canvas.create_oval(x1, y1, x2, y2, fill='green')

        if path and not self.robot:  # Check if the robot ID exists
            self.robot = self.canvas.create_rectangle(path[0][1] * self.cell_size + self.cell_size // 2 - self.robot_size // 2,
                                                      path[0][0] * self.cell_size + self.cell_size // 2 - self.robot_size // 2,
                                                      path[0][1] * self.cell_size + self.cell_size // 2 + self.robot_size // 2,
                                                      path[0][0] * self.cell_size + self.cell_size // 2 + self.robot_size // 2,
                                                      fill='grey')
            self.move_robot(path)

    def move_robot(self, path):
        if not path:
            return

        # Calculate the intermediate points for SMOOTHER MOVEMENT
        x_points, y_points = [], []
        for x, y in path:
            x_points.append(y * self.cell_size + self.cell_size // 2)
            y_points.append(x * self.cell_size + self.cell_size // 2)

        for i in range(1, len(x_points)):
            x1, y1 = x_points[i - 1], y_points[i - 1]
            x2, y2 = x_points[i], y_points[i]

            # Calculate the total distance and number of steps needed for interpolation
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            num_steps = max(int(distance / self.robot_speed), 1)

            # Calculate the step size for interpolation
            step_x = (x2 - x1) / num_steps
            step_y = (y2 - y1) / num_steps

            for _ in range(num_steps):
                # Move the robot to the next intermediate point
                self.canvas.coords(self.robot,
                                x1 + _ * step_x - self.robot_size // 2,
                                y1 + _ * step_y - self.robot_size // 2,
                                x1 + _ * step_x + self.robot_size // 2,
                                y1 + _ * step_y + self.robot_size // 2)
                self.canvas.update()
                self.canvas.after(30)

        x, y = path[-1]
        center_x = y * self.cell_size + self.cell_size // 2
        center_y = x * self.cell_size + self.cell_size // 2
        self.canvas.coords(self.robot,
                        center_x - self.robot_size // 2,
                        center_y - self.robot_size // 2,
                        center_x + self.robot_size // 2,
                        center_y + self.robot_size // 2)

        self.canvas.after(500, lambda: self.move_robot(path[1:]))

    def run_algorithm(self):
        path = self.astar.run_algorithm()

        if path:
            total_distance = 0
            for i in range(1, len(path)):
                x1, y1 = path[i - 1]
                x2, y2 = path[i]
                total_distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            
            self.distance_label.config(text=f"Total distance traveled: {total_distance:.2f} meters")

            self.draw_path(path)
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
