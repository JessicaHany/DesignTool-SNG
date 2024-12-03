import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import ifcopenshell
import os
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Conversion factor from meters to inches
METERS_TO_INCHES = 39.3701


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Singularity's Design Tool")
        self.geometry("1400x800")

        # Define project types dictionary as a class attribute
        self.project_types_dict = {
            "Residential": ["Bedroom", "Living Room", "Kitchen", "Bathroom"],
            "Commercial": ["Store", "Office", "Coworking Space", "Restaurant"],
            "Healthcare": ["Clinic", "Hospital", "Operation Room"]
        }

        # Initialize room dimensions
        self.room_dimensions = {"length": 0, "width": 0, "height": 0}

        # Create toolbar frame with light grey background
        self.toolbar = ttk.Frame(self)
        self.toolbar.grid(row=0, column=0, sticky="nsew")

        # Create main content frame
        self.main_content = ttk.Frame(self)
        self.main_content.grid(row=0, column=1, sticky="nsew")

        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize pages dictionary
        self.pages = {}

        # Create styles
        self.create_styles()

        # Setup toolbar and pages
        self.setup_toolbar()
        self.setup_pages()

        # Show default page
        self.show_page("Room Type and Boundaries")

        # Store the current IFC file
        self.current_ifc_file = None

    def create_styles(self):
        style = ttk.Style()
        style.configure('Toolbar.TFrame', background='#E0E0E0')
        style.configure('Toolbar.TButton', font=('Arial', 10), padding=5, foreground='#1ab3ff')
        style.configure('Active.TButton', font=('Arial', 11, 'bold'), foreground='#1ab3ff')
        style.configure('ComingSoon.TLabel', font=('Arial', 14, 'bold'), anchor='center')

    def setup_toolbar(self):
        self.toolbar_buttons = {}

        # Main functionality buttons
        self.toolbar_buttons["Room Type and Boundaries"] = ttk.Button(
            self.toolbar,
            text="Room Type and Boundaries",
            command=lambda: self.show_page("Room Type and Boundaries"),
            style='Toolbar.TButton'
        )
        self.toolbar_buttons["Room Type and Boundaries"].pack(pady=5, padx=5, fill="x")

        self.toolbar_buttons["Place Families"] = ttk.Button(
            self.toolbar,
            text="Place Families",
            command=lambda: self.show_page("Place Families"),
            style='Toolbar.TButton'
        )
        self.toolbar_buttons["Place Families"].pack(pady=5, padx=5, fill="x")

        # Coming soon buttons
        ttk.Separator(self.toolbar, orient='horizontal').pack(pady=10, fill='x')

        self.toolbar_buttons["Generate Layouts"] = ttk.Button(
            self.toolbar,
            text="Generate Layouts",
            command=lambda: self.show_page("Generate Layouts"),
            style='Toolbar.TButton'
        )
        self.toolbar_buttons["Generate Layouts"].pack(pady=5, padx=5, fill="x")

        # Add the new pages
        self.toolbar_buttons["Validation & Regulations"] = ttk.Button(
            self.toolbar,
            text="Validation & Regulations",
            command=lambda: self.show_page("Validation & Regulations"),
            style='Toolbar.TButton'
        )
        self.toolbar_buttons["Validation & Regulations"].pack(pady=5, padx=5, fill="x")

        self.toolbar_buttons["Materials & Visualization"] = ttk.Button(
            self.toolbar,
            text="Materials & Visualization",
            command=lambda: self.show_page("Materials & Visualization"),
            style='Toolbar.TButton'
        )
        self.toolbar_buttons["Materials & Visualization"].pack(pady=5, padx=5, fill="x")

        self.toolbar_buttons["Your Feedback"] = ttk.Button(
            self.toolbar,
            text="Your Feedback",
            command=lambda: self.show_page("Your Feedback"),
            style='Toolbar.TButton'
        )
        self.toolbar_buttons["Your Feedback"].pack(pady=5, padx=5, fill="x")
    def setup_pages(self):
        # Create main functionality pages
        self.pages["Room Type and Boundaries"] = RoomTypePage(self.main_content, self)
        self.pages["Place Families"] = FamiliesPage(self.main_content, self)
        self.pages["Generate Layouts"] = ComingSoonPage(self.main_content, "Generate Layouts")

        # Create the new pages
        self.pages["Validation & Regulations"] = ComingSoonPage(self.main_content, "Validation & Regulations")
        self.pages["Materials & Visualization"] = ComingSoonPage(self.main_content, "Materials & Visualization")
        self.pages["Your Feedback"] = ComingSoonPage(self.main_content, "Your Feedback")

        # Grid all pages
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name):
        # Update button styles
        for name, button in self.toolbar_buttons.items():
            if name == page_name:
                button.configure(style='Active.TButton')
            else:
                button.configure(style='Toolbar.TButton')

        # Hide all pages
        for page in self.pages.values():
            page.grid_remove()

        # Show selected page
        self.pages[page_name].grid()

        # Update room preview if showing families page
        if page_name == "Place Families":
            self.pages[page_name].update_preview()

    def get_room_types(self, project_type):
        return self.project_types_dict.get(project_type, [])

    def update_room_dimensions(self, length, width, height):
        self.room_dimensions = {
            "length": float(length),
            "width": float(width),
            "height": float(height)
        }


class ComingSoonPage(ttk.Frame):
    def __init__(self, parent, page_name):
        super().__init__(parent)
        self.setup_ui(page_name)

    def setup_ui(self, page_name):
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create frame for message
        message_frame = ttk.Frame(self)
        message_frame.grid(row=0, column=0, sticky="nsew")

        # Add message
        message = f"{page_name}\nSOON TO BE PUBLISHED :)"
        label = ttk.Label(message_frame, text=message, style='ComingSoon.TLabel')
        label.pack(expand=True)
class RoomTypePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create frames
        self.left_frame = ttk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.right_frame = ttk.Frame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize variables
        self.init_variables()

        # Setup GUI components
        self.setup_preview()
        self.setup_controls()

    def init_variables(self):
        self.ifc_file = None
        self.categories = {}
        self.selected_wall = None

        # Initialize StringVar variables
        self.file_path_var = tk.StringVar()
        self.project_type_var = tk.StringVar()
        self.room_type_var = tk.StringVar()
        self.length_var = tk.StringVar(value="0")
        self.width_var = tk.StringVar(value="0")
        self.height_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar()

        # Add trace to variables
        self.project_type_var.trace('w', self.on_project_type_change)
        self.length_var.trace('w', self.on_dimension_change)
        self.width_var.trace('w', self.on_dimension_change)

    def setup_controls(self):
        # File Selection
        file_frame = ttk.LabelFrame(self.right_frame, text="IFC File Selection", padding="5")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1, padx=5, pady=5)

        # Project Type Selection
        type_frame = ttk.LabelFrame(self.right_frame, text="Project Configuration", padding="5")
        type_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(type_frame, text="Project Type:").grid(row=0, column=0, padx=5, pady=2)
        self.project_type_combo = ttk.Combobox(type_frame, textvariable=self.project_type_var,
                                               values=list(self.controller.project_types_dict.keys()))
        self.project_type_combo.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(type_frame, text="Room Type:").grid(row=1, column=0, padx=5, pady=2)
        self.room_type_combo = ttk.Combobox(type_frame, textvariable=self.room_type_var)
        self.room_type_combo.grid(row=1, column=1, padx=5, pady=2)

        # Components Display
        comp_frame = ttk.LabelFrame(self.right_frame, text="Available Walls", padding="5")
        comp_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)

        self.components_text = ScrolledText(comp_frame, height=10, width=60)
        self.components_text.grid(row=0, column=0, padx=5, pady=5)

        # Wall Selection
        wall_frame = ttk.LabelFrame(self.right_frame, text="Wall Selection", padding="5")
        wall_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)

        self.wall_combobox = ttk.Combobox(wall_frame, width=50, state='disabled')
        self.wall_combobox.grid(row=0, column=0, padx=5, pady=5)

        # Room Dimensions
        dim_frame = ttk.LabelFrame(self.right_frame, text="Room Dimensions (inches)", padding="5")
        dim_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(dim_frame, text="Length:").grid(row=0, column=0, padx=5, pady=2)
        ttk.Entry(dim_frame, textvariable=self.length_var, width=20).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(dim_frame, text="Width:").grid(row=1, column=0, padx=5, pady=2)
        ttk.Entry(dim_frame, textvariable=self.width_var, width=20).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(dim_frame, text="Height:").grid(row=2, column=0, padx=5, pady=2)
        ttk.Entry(dim_frame, textvariable=self.height_var, width=20).grid(row=2, column=1, padx=5, pady=2)

        # Proceed Button
        ttk.Button(self.right_frame, text="Proceed to Place Families",
                   command=self.proceed_to_families).grid(row=5, column=0, pady=20)

        # Status Label
        ttk.Label(self.right_frame, textvariable=self.status_var, wraplength=500).grid(row=6, column=0, pady=5)
    def setup_preview(self):
        preview_frame = ttk.LabelFrame(self.left_frame, text="Room Preview", padding="5")
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=preview_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.update_preview()

    def on_project_type_change(self, *args):
        project_type = self.project_type_var.get()
        room_types = self.controller.get_room_types(project_type)
        self.room_type_combo['values'] = room_types
        if room_types:
            self.room_type_combo.set(room_types[0])

    def on_dimension_change(self, *args):
        self.update_preview()

    def update_preview(self):
        try:
            self.ax.clear()

            try:
                length = float(self.length_var.get() or 0)
                width = float(self.width_var.get() or 0)
            except ValueError:
                length = width = 0

            if length > 0 and width > 0:
                rect = plt.Rectangle((0, 0), length, width, fill=False, color='blue')
                self.ax.add_patch(rect)

                padding = max(length, width) * 0.1
                self.ax.set_xlim(-padding, length + padding)
                self.ax.set_ylim(-padding, width + padding)
            else:
                self.ax.grid(True, linestyle=':')
                self.ax.set_xlim(-1, 1)
                self.ax.set_ylim(-1, 1)

            self.ax.set_aspect('equal')
            self.ax.set_xlabel('Length (inches)')
            self.ax.set_ylabel('Width (inches)')
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating preview: {str(e)}")

    def validate_dimensions(self):
        try:
            length = float(self.length_var.get()) / METERS_TO_INCHES  # Convert to meters for internal storage
            width = float(self.width_var.get()) / METERS_TO_INCHES
            height = float(self.height_var.get()) / METERS_TO_INCHES

            if length <= 0 or width <= 0 or height <= 0:
                raise ValueError("Dimensions must be positive numbers")

            return True
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive numbers for dimensions")
            return False

    def proceed_to_families(self):
        if not self.validate_dimensions():
            return

        # Convert inches to meters when saving to controller
        self.controller.update_room_dimensions(
            float(self.length_var.get()) / METERS_TO_INCHES,
            float(self.width_var.get()) / METERS_TO_INCHES,
            float(self.height_var.get()) / METERS_TO_INCHES
        )

        # Switch to families page
        self.controller.show_page("Place Families")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select IFC File",
            filetypes=[("IFC files", "*.ifc"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.load_ifc_file(file_path)

    def load_ifc_file(self, file_path):
        try:
            self.ifc_file = ifcopenshell.open(file_path)
            self.controller.current_ifc_file = self.ifc_file
            self.status_var.set("IFC file loaded successfully!")
            self.analyze_file_contents()
        except Exception as e:
            self.status_var.set(f"Error loading IFC file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load IFC file: {str(e)}")

    def analyze_file_contents(self):
        try:
            self.components_text.delete(1.0, tk.END)
            self.categories.clear()

            walls = self.ifc_file.by_type('IfcWall')
            if walls:
                self.categories['Walls'] = walls
                self.components_text.insert(tk.END, f"Walls found: {len(walls)}\n")
                for i, wall in enumerate(walls, 1):
                    self.components_text.insert(tk.END, f"Wall {i}: ID: {wall.GlobalId}\n")

                self.wall_combobox['values'] = [f"Wall {i+1}: {wall.GlobalId}" for i, wall in enumerate(walls)]
                self.wall_combobox['state'] = 'readonly'
                if len(walls) > 0:
                    self.wall_combobox.current(0)
        except Exception as e:
            self.status_var.set(f"Error analyzing file: {str(e)}")
            messagebox.showerror("Error", f"Failed to analyze file: {str(e)}")
class FamiliesPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Create frames
        self.left_frame = ttk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.right_frame = ttk.Frame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialize variables
        self.init_variables()

        # Setup GUI components
        self.setup_controls()
        self.setup_preview()

    def init_variables(self):
        self.families_folder = ""
        self.selected_family = None
        self.family_positions = {}  # Store family positions as {family_name: (x, y)}

    def setup_controls(self):
        # Folder Selection
        folder_frame = ttk.LabelFrame(self.right_frame, text="Select Families Folder", padding="5")
        folder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).grid(row=0, column=0, padx=5, pady=5)
        self.folder_label = ttk.Label(folder_frame, text="No folder selected", wraplength=300)
        self.folder_label.grid(row=0, column=1, padx=5, pady=5)

        # Families List
        families_frame = ttk.LabelFrame(self.right_frame, text="Available Families", padding="5")
        families_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        self.families_listbox = tk.Listbox(families_frame, height=15, width=40)
        self.families_listbox.grid(row=0, column=0, padx=5, pady=5)
        self.families_listbox.bind("<<ListboxSelect>>", self.on_family_select)

        # Family Position Controls
        position_frame = ttk.LabelFrame(self.right_frame, text="Adjust Family Position", padding="5")
        position_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(position_frame, text="X Position:").grid(row=0, column=0, padx=5, pady=2)
        self.x_slider = tk.Scale(position_frame, from_=-10, to=10, orient=tk.HORIZONTAL, resolution=0.1,
                                 command=self.update_family_position)
        self.x_slider.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(position_frame, text="Y Position:").grid(row=1, column=0, padx=5, pady=2)
        self.y_slider = tk.Scale(position_frame, from_=-10, to=10, orient=tk.HORIZONTAL, resolution=0.1,
                                 command=self.update_family_position)
        self.y_slider.grid(row=1, column=1, padx=5, pady=2)

        # Proceed to Generating Layouts Button
        ttk.Button(self.right_frame,
                   text="Proceed to Generating Layouts",
                   command=lambda: self.controller.show_page("Generate Layouts")).grid(row=3, column=0, pady=20)
    def setup_preview(self):
        preview_frame = ttk.LabelFrame(self.left_frame, text="Room and Families Preview", padding="5")
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=preview_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.update_preview()

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Revit Families (OBJ Files)")
        if folder:
            self.families_folder = folder
            self.folder_label.config(text=folder)
            self.load_families()

    def load_families(self):
        # Clear the listbox
        self.families_listbox.delete(0, tk.END)

        # Load OBJ files from the selected folder
        if self.families_folder:
            obj_files = [f for f in os.listdir(self.families_folder) if f.endswith(".obj")]
            for obj_file in obj_files:
                self.families_listbox.insert(tk.END, obj_file)

    def on_family_select(self, event):
        selected_index = self.families_listbox.curselection()
        if selected_index:
            self.selected_family = self.families_listbox.get(selected_index)

            # Update sliders to reflect the current position of the selected family
            if self.selected_family in self.family_positions:
                x, y = self.family_positions[self.selected_family]
                self.x_slider.set(x)
                self.y_slider.set(y)
            else:
                self.x_slider.set(0)
                self.y_slider.set(0)

            self.update_preview()

    def update_family_position(self, *args):
        if self.selected_family:
            x = self.x_slider.get()
            y = self.y_slider.get()
            self.family_positions[self.selected_family] = (x, y)
            self.update_preview()

    def get_family_dimensions(self, family_name):
        """
        Extract dimensions from OBJ file.
        Returns width and height in inches.
        """
        try:
            obj_path = os.path.join(self.families_folder, family_name)
            if not os.path.exists(obj_path):
                return 20, 20  # Default size in inches if file not found

            # Read OBJ file and find min/max coordinates
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')

            with open(obj_path, 'r') as f:
                for line in f:
                    if line.startswith('v '):
                        _, x, y, _ = map(float, line.split())
                        min_x = min(min_x, x)
                        max_x = max(max_x, x)
                        min_y = min(min_y, y)
                        max_y = max(max_y, y)

            width = (max_x - min_x) * METERS_TO_INCHES
            height = (max_y - min_y) * METERS_TO_INCHES

            return width, height
        except Exception as e:
            print(f"Error getting family dimensions: {str(e)}")
            return 20, 20  # Default size in inches
    def update_preview(self):
        try:
            self.ax.clear()

            # Draw room boundaries
            room_length = self.controller.room_dimensions["length"] * METERS_TO_INCHES
            room_width = self.controller.room_dimensions["width"] * METERS_TO_INCHES

            if room_length > 0 and room_width > 0:
                rect = plt.Rectangle((0, 0), room_length, room_width, fill=False, color='blue')
                self.ax.add_patch(rect)

            # Draw families as boxes instead of points
            for family, (x, y) in self.family_positions.items():
                # Get family dimensions from OBJ file
                width, height = self.get_family_dimensions(family)

                # Create a rectangle for the family
                family_rect = plt.Rectangle(
                    (x - width / 2, y - height / 2),  # Center the box at the position
                    width,
                    height,
                    fill=True,
                    alpha=0.5,
                    label=family
                )
                self.ax.add_patch(family_rect)

            # Add legend
            if self.family_positions:
                self.ax.legend(loc="upper right")

            # Set limits with padding
            padding = max(room_length, room_width) * 0.1 if room_length > 0 and room_width > 0 else 1
            self.ax.set_xlim(-padding, room_length + padding if room_length > 0 else padding)
            self.ax.set_ylim(-padding, room_width + padding if room_width > 0 else padding)

            self.ax.set_aspect('equal')
            self.ax.set_xlabel('X Position (inches)')
            self.ax.set_ylabel('Y Position (inches)')
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating preview: {str(e)}")


def main():
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
