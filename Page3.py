import os
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from tensorflow import keras
from PIL import Image
import trimesh
import collada
from pathlib import Path
import warnings
import matplotlib
matplotlib.use('TkAgg')

# Suppress warnings
warnings.filterwarnings('ignore')

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "furniture_layout_modelpart5.h5")

# Asset mapping for 2D PNG images
ASSET_MAPPING = {
    "Bed": "assets/images/bed.png",
    "Sofa": "assets/images/sofa.png",
    "TV Stand": "assets/images/tv_stand.png",
    "Coffee Table": "assets/images/coffeetable.png",
    "Nightstand": "assets/images/nightstand.png",
    "Dresser": "assets/images/dresser.png",
    "Wardrobe": "assets/images/wardrobe.png",
    "Armchair": "assets/images/armchair.png",
    "Toilet": "assets/images/toilet.png",
    "Sink": "assets/images/sink.png",
    "Shower": "assets/images/shower.png",
    "Bathtub": "assets/images/bathtub.png",
    "Door": "assets/images/door.png",
    "Window": "assets/images/window.png"
}

# Load the trained AI model with error handling
try:
    print(f"Looking for model at: {model_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    model = keras.models.load_model(model_path, compile=False)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

class ViewControls(ttk.Frame):
    """A class to handle 3D view controls"""
    def __init__(self, parent, canvas, ax, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = canvas
        self.ax = ax
        self.azim = 45
        self.elev = 30
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create control widgets"""
        rotation_frame = ttk.LabelFrame(self, text="Rotation Controls")
        rotation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Azimuth control
        ttk.Label(rotation_frame, text="Horizontal Rotation:").pack()
        self.azim_scale = ttk.Scale(
            rotation_frame,
            from_=0,
            to=360,
            orient=tk.HORIZONTAL,
            command=self.update_view
        )
        self.azim_scale.set(45)
        self.azim_scale.pack(fill=tk.X, padx=5)
        
        # Elevation control
        ttk.Label(rotation_frame, text="Vertical Rotation:").pack()
        self.elev_scale = ttk.Scale(
            rotation_frame,
            from_=-90,
            to=90,
            orient=tk.HORIZONTAL,
            command=self.update_view
        )
        self.elev_scale.set(30)
        self.elev_scale.pack(fill=tk.X, padx=5)
        
        # Reset button
        ttk.Button(
            rotation_frame,
            text="Reset View",
            command=self.reset_view
        ).pack(pady=5)
        
    def update_view(self, *args):
        """Update the 3D view based on current controls"""
        self.azim = self.azim_scale.get()
        self.elev = self.elev_scale.get()
        self.ax.view_init(elev=self.elev, azim=self.azim)
        self.canvas.draw()
        
    def reset_view(self):
        """Reset view to default position"""
        self.azim_scale.set(45)
        self.elev_scale.set(30)
        self.update_view()

def get_safe_model_path(furniture_type):
    """Get the path to a 3D model file, checking multiple possible formats."""
    base_path = os.path.join(script_dir, "assets", "3d_models", furniture_type.lower().replace(" ", "_"))
    supported_formats = ['.dae', '.stl', '.obj']
    
    for fmt in supported_formats:
        path = base_path + fmt
        if os.path.exists(path):
            print(f"[DEBUG] Found 3D model for {furniture_type}: {path}")
            return path
    
    print(f"[DEBUG] No 3D model found for {furniture_type}")
    return None

def load_3d_model(model_path):
    """Load a 3D model with detailed error reporting."""
    try:
        print(f"[INFO] Attempting to load 3D model: {model_path}")
        
        if model_path is None:
            print("[WARNING] No model path provided")
            return None
            
        # Specific handling for DAE files
        if str(model_path).lower().endswith('.dae'):
            try:
                # Load the Collada file
                mesh = collada.Collada(model_path)
                
                # Extract vertices and faces from all geometries
                all_vertices = []
                all_faces = []
                vertex_offset = 0
                
                for geometry in mesh.geometries:
                    for primitive in geometry.primitives:
                        # Get vertices
                        vertices = primitive.vertex
                        all_vertices.extend(vertices)
                        
                        # Get faces (triangles)
                        faces = primitive.vertex_index
                        # Adjust face indices based on vertex offset
                        adjusted_faces = faces + vertex_offset
                        all_faces.extend(adjusted_faces)
                        
                        vertex_offset += len(vertices)
                
                # Create trimesh from extracted data
                return trimesh.Trimesh(
                    vertices=np.array(all_vertices),
                    faces=np.array(all_faces)
                )
                
            except Exception as e:
                print(f"[ERROR] Failed to load DAE file: {str(e)}")
                return None
        else:
            # Handle other formats
            mesh = trimesh.load(model_path)
            
        if mesh is not None and mesh.is_empty:
            print(f"[WARNING] Loaded mesh is empty: {model_path}")
            return None
            
        print(f"[SUCCESS] Loaded 3D model: {model_path}")
        print(f"[INFO] Mesh details: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        return mesh
        
    except Exception as e:
        print(f"[ERROR] Failed to load 3D model {model_path}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def verify_3d_models():
    """Verify that 3D models exist and are accessible."""
    try:
        assets_dir = os.path.join(script_dir, "assets", "3d_models")
        os.makedirs(assets_dir, exist_ok=True)
        
        required_models = [
            "bed", "sofa", "tv_stand", "coffee_table", "nightstand",
            "dresser", "wardrobe", "armchair", "toilet", "sink",
            "shower", "bathtub", "door", "window"
        ]
        
        print(f"[INFO] Checking 3D models in: {assets_dir}")
        
        for model in required_models:
            dae_path = os.path.join(assets_dir, f"{model}.dae")
            if os.path.exists(dae_path):
                print(f"[INFO] Found DAE model: {model}.dae")
                # Test load the model
                test_mesh = load_3d_model(dae_path)
                if test_mesh is not None:
                    print(f"[SUCCESS] Successfully loaded: {model}.dae")
                else:
                    print(f"[ERROR] Failed to load: {model}.dae")
            else:
                print(f"[WARNING] Missing DAE model: {model}.dae")
                
        return True
    except Exception as e:
        print(f"[ERROR] Error verifying 3D models: {e}")
        return False

def get_furniture_dimensions(furniture_type):
    """Get standard dimensions for furniture types."""
    dimensions = {
        "Bed": {"width": 6.67, "depth": 5, "height": 2.5},
        "Sofa": {"width": 6, "depth": 3, "height": 3},
        "TV Stand": {"width": 5, "depth": 1.5, "height": 2},
        "Coffee Table": {"width": 4, "depth": 2, "height": 1.5},
        "Nightstand": {"width": 2, "depth": 2, "height": 2},
        "Dresser": {"width": 4, "depth": 2, "height": 4},
        "Wardrobe": {"width": 4, "depth": 2, "height": 7},
        "Armchair": {"width": 3, "depth": 3, "height": 3},
        "Toilet": {"width": 2.5, "depth": 2, "height": 2.5},
        "Sink": {"width": 2, "depth": 1.5, "height": 2.5},
        "Shower": {"width": 3, "depth": 3, "height": 7},
        "Bathtub": {"width": 5, "depth": 2.5, "height": 2},
        "Door": {"width": 3, "depth": 0.1, "height": 7},
        "Window": {"width": 4, "depth": 0.1, "height": 4}
    }
    return dimensions.get(furniture_type, {"width": 2, "depth": 2, "height": 2})

def check_collision(item1, item2):
    """Check if two furniture items overlap."""
    x1, y1 = item1['position']['x'], item1['position']['y']
    w1, d1 = item1['dimensions']['width'], item1['dimensions']['depth']
    x2, y2 = item2['position']['x'], item2['position']['y']
    w2, d2 = item2['dimensions']['width'], item2['dimensions']['depth']
    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + d1 <= y2 or y2 + d2 <= y1)

def generate_layouts(room_dimensions, selected_furniture):
    """Generate layouts for the room."""
    try:
        room_width = float(room_dimensions['width'])
        room_length = float(room_dimensions['length'])
        room_height = float(room_dimensions['height'])

        layouts = []
        max_attempts = 50

        X = []
        for _ in selected_furniture:
            room_features = [room_width / 20, room_length / 25, room_height / 10, 0, 0, 0, 0]
            X.append(room_features)
        X = np.array(X)
        
        predictions = model.predict(X) if model is not None else None

        for i, furniture in enumerate(selected_furniture):
            furniture_dims = get_furniture_dimensions(furniture)
            attempts = 0
            placed = False

            while attempts < max_attempts and not placed:
                if attempts == 0 and predictions is not None:
                    pos_x = max(0, min(predictions[i][0] * room_width, room_width - furniture_dims['width']))
                    pos_y = max(0, min(predictions[i][1] * room_length, room_length - furniture_dims['depth']))
                else:
                    pos_x = np.random.uniform(0, room_width - furniture_dims['width'])
                    pos_y = np.random.uniform(0, room_length - furniture_dims['depth'])

                new_item = {
                    "type": furniture,
                    "position": {"x": pos_x, "y": pos_y},
                    "rotation": 0,
                    "dimensions": furniture_dims
                }

                has_collision = False
                for existing_item in layouts:
                    if check_collision(new_item, existing_item):
                        has_collision = True
                        break

                if not has_collision:
                    layouts.append(new_item)
                    placed = True
                else:
                    attempts += 1

            if not placed:
                print(f"Warning: Could not place {furniture} without overlap after {max_attempts} attempts.")

        return layouts

    except Exception as e:
        print(f"Error generating layout: {e}")
        raise

def calculate_scale_factor(mesh, target_dims):
    """Calculate appropriate scale factor for 3D models"""
    current_dims = mesh.extents
    width_scale = target_dims['width'] / current_dims[0]
    depth_scale = target_dims['depth'] / current_dims[1]
    height_scale = target_dims['height'] / current_dims[2]
    return min(width_scale, depth_scale, height_scale)

def verify_scaling(furniture_type, mesh, dimensions):
    """Verify that 3D model scaling matches intended dimensions"""
    scaled_dims = mesh.extents
    expected_dims = [
        dimensions['width'],
        dimensions['depth'],
        dimensions['height']
    ]
    print(f"[DEBUG] {furniture_type} scaling verification:")
    print(f"Expected: {expected_dims}")
    print(f"Actual: {scaled_dims}")
    return np.allclose(scaled_dims, expected_dims, rtol=0.1)

def visualize_layouts(room_dimensions, furniture_layouts, canvas):
    """Visualize the room layout in 2D."""
    try:
        fig, ax = plt.subplots(figsize=(8, 8))

        room_width = float(room_dimensions['width'])
        room_length = float(room_dimensions['length'])
        padding = 1
        ax.set_xlim(-padding, room_width + padding)
        ax.set_ylim(-padding, room_length + padding)

        # Draw room boundaries
        room = plt.Rectangle((0, 0), room_width, room_length, 
                           fill=False, color='black', linewidth=2)
        ax.add_patch(room)

        for furniture in furniture_layouts:
            position = furniture['position']
            dimensions = furniture['dimensions']
            furniture_type = furniture['type']

            # Draw furniture in 2D
            if furniture_type in ["Door", "Window"]:
                color = 'red' if furniture_type == "Door" else 'blue'
                rect = plt.Rectangle(
                    (position['x'], position['y']),
                    dimensions['width'],
                    dimensions['depth'],
                    fill=True,
                    color=color,
                    alpha=0.7
                )
                ax.add_patch(rect)
            else:
                if furniture_type in ASSET_MAPPING:
                    img_path = os.path.join(script_dir, ASSET_MAPPING[furniture_type])
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        # Scale image to match furniture dimensions
                        scale_factor = 50  # Adjust for better visualization
                        scaled_width = int(dimensions['width'] * scale_factor)
                        scaled_depth = int(dimensions['depth'] * scale_factor)
                        img = img.resize((scaled_width, scaled_depth))
                        
                        # Place image with correct dimensions
                        ax.imshow(img, extent=(
                            position['x'],
                            position['x'] + dimensions['width'],
                            position['y'],
                            position['y'] + dimensions['depth']
                        ), aspect='auto', zorder=2)
                    else:
                        # Fallback to rectangle if image not found
                        rect = plt.Rectangle(
                            (position['x'], position['y']),
                            dimensions['width'],
                            dimensions['depth'],
                            fill=True,
                            color='gray',
                            alpha=0.5
                        )
                        ax.add_patch(rect)

            # Add furniture label
            ax.text(
                position['x'] + dimensions['width'] / 2,
                position['y'] + dimensions['depth'] / 2,
                furniture_type,
                color='black',
                ha='center',
                va='center',
                fontsize=8,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )

        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_title('2D Room Layout')
        ax.set_aspect('equal')

        canvas.figure = fig
        canvas.draw()

    except Exception as e:
        print(f"Error in 2D visualization: {e}")
        raise

def visualize_layouts_3d(room_dimensions, furniture_layouts, canvas, ax):
    """Visualize the room layout in 3D with consistent scaling."""
    try:
        ax.clear()

        room_width = float(room_dimensions['width'])
        room_length = float(room_dimensions['length'])
        room_height = float(room_dimensions['height'])

        # Draw room boundaries with enhanced visibility
        ax.plot([0, room_width, room_width, 0, 0], 
                [0, 0, room_length, room_length, 0], 
                [0, 0, 0, 0, 0], 'k-', linewidth=2)
        ax.plot([0, room_width, room_width, 0, 0],
                [0, 0, room_length, room_length, 0],
                [room_height, room_height, room_height, room_height, room_height], 
                'k-', linewidth=2)
        
        # Vertical edges
        for x, y in [(0, 0), (room_width, 0), (room_width, room_length), (0, room_length)]:
            ax.plot([x, x], [y, y], [0, room_height], 'k-', linewidth=2)

        for furniture in furniture_layouts:
            position = furniture['position']
            dimensions = furniture['dimensions']
            furniture_type = furniture['type']
            
            model_path = get_safe_model_path(furniture_type)
            mesh = load_3d_model(model_path)

            if mesh is not None:
                # Calculate and apply consistent scaling
                scale_factor = calculate_scale_factor(mesh, dimensions)
                scaled_mesh = mesh.copy()
                scaled_mesh.apply_transform(trimesh.transformations.scale_matrix(scale_factor))

                # Position the model
                scaled_mesh.apply_translation([
                    position['x'],
                    position['y'],
                    0  # Place on floor level
                ])

                # Verify scaling
                verify_scaling(furniture_type, scaled_mesh, dimensions)

                # Plot the mesh
                vertices = scaled_mesh.vertices
                faces = scaled_mesh.faces
                ax.plot_trisurf(
                    vertices[:, 0],
                    vertices[:, 1],
                    vertices[:, 2],
                    triangles=faces,
                    color='blue',
                    alpha=0.7
                )
            else:
                # Enhanced fallback visualization
                height = dimensions['height']
                ax.bar3d(
                    position['x'],
                    position['y'],
                    0,
                    dimensions['width'],
                    dimensions['depth'],
                    height,
                    color='gray',
                    alpha=0.7
                )

            # Add furniture label with improved positioning
            ax.text(
                position['x'] + dimensions['width'] / 2,
                position['y'] + dimensions['depth'] / 2,
                dimensions['height'] / 2,
                furniture_type,
                horizontalalignment='center',
                verticalalignment='center',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )

        # Set consistent view limits
        ax.set_xlim(0, room_width)
        ax.set_ylim(0, room_length)
        ax.set_zlim(0, room_height)

        # Enhance axes labels
        ax.set_xlabel('Width (ft)', labelpad=10)
        ax.set_ylabel('Length (ft)', labelpad=10)
        ax.set_zlabel('Height (ft)', labelpad=10)
        ax.set_title('3D Room Layout', pad=20)

        # Update the canvas
        canvas.draw()

    except Exception as e:
        print(f"Error in 3D visualization: {e}")
        raise

class RoomLayoutApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Room Layout Generator with 3D Toggle")
        self.geometry("1400x900")  # Adjusted window size

        if model is None:
            messagebox.showerror("Error", "Could not load the AI model. Please ensure the model file exists.")
            self.destroy()
            return

        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_room_type_section()
        self.create_dimensions_section()
        self.create_furniture_section()

        self.generate_button = ttk.Button(
            self.main_frame,
            text="Generate Layout",
            command=self.generate_layout
        )
        self.generate_button.pack(pady=10)

        self.create_visualization_section()

    def create_room_type_section(self):
        """Create the room type selection dropdown."""
        type_frame = ttk.LabelFrame(self.main_frame, text="Room Type", padding="5")
        type_frame.pack(fill=tk.X, pady=5)

        self.room_type_var = tk.StringVar()
        self.room_type_dropdown = ttk.Combobox(
            type_frame,
            textvariable=self.room_type_var,
            values=["Bedroom", "Bathroom", "Living Room"]
        )
        self.room_type_dropdown.pack(fill=tk.X)
        self.room_type_dropdown.set("Select Room Type")

        self.room_type_dropdown.bind("<<ComboboxSelected>>", self.update_furniture_list)

    def create_dimensions_section(self):
        """Create the room dimensions input section."""
        dim_frame = ttk.LabelFrame(self.main_frame, text="Room Dimensions (feet)", padding="5")
        dim_frame.pack(fill=tk.X, pady=5)

        entries_frame = ttk.Frame(dim_frame)
        entries_frame.pack(fill=tk.X)

        ttk.Label(entries_frame, text="Width:").grid(row=0, column=0, padx=5)
        self.width_entry = ttk.Entry(entries_frame, width=10)
        self.width_entry.grid(row=0, column=1, padx=5)

        ttk.Label(entries_frame, text="Length:").grid(row=0, column=2, padx=5)
        self.length_entry = ttk.Entry(entries_frame, width=10)
        self.length_entry.grid(row=0, column=3, padx=5)

        ttk.Label(entries_frame, text="Height:").grid(row=0, column=4, padx=5)
        self.height_entry = ttk.Entry(entries_frame, width=10)
        self.height_entry.grid(row=0, column=5, padx=5)

    def create_furniture_section(self):
        """Create the furniture selection section."""
        furniture_frame = ttk.LabelFrame(self.main_frame, text="Furniture Selection", padding="5")
        furniture_frame.pack(fill=tk.X, pady=5)

        list_qty_frame = ttk.Frame(furniture_frame)
        list_qty_frame.pack(fill=tk.X)

        self.furniture_listbox = tk.Listbox(
            list_qty_frame,
            selectmode=tk.SINGLE,
            height=5
        )
        self.furniture_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        qty_frame = ttk.Frame(list_qty_frame)
        qty_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Label(qty_frame, text="Quantity:").pack()
        self.qty_spinbox = ttk.Spinbox(
            qty_frame,
            from_=1,
            to=10,
            width=5
        )
        self.qty_spinbox.pack()

        self.add_furniture_btn = ttk.Button(
            furniture_frame,
            text="Add Furniture",
            command=self.add_furniture_with_quantity
        )
        self.add_furniture_btn.pack(pady=5)

        self.delete_furniture_btn = ttk.Button(
            furniture_frame,
            text="Delete Selected",
            command=self.delete_selected_furniture
        )
        self.delete_furniture_btn.pack(pady=5)

        ttk.Label(furniture_frame, text="Selected Furniture:").pack()
        self.selected_furniture_list = tk.Listbox(
            furniture_frame,
            height=5
        )
        self.selected_furniture_list.pack(fill=tk.X)

        self.furniture_options = {
            "Bedroom": ["Bed", "Nightstand", "Dresser", "Wardrobe"],
            "Living Room": ["Sofa", "Coffee Table", "TV Stand", "Armchair"],
            "Bathroom": ["Toilet", "Sink", "Shower", "Bathtub"]
        }

    def create_visualization_section(self):
        """Create the 2D and 3D visualization sections."""
        viz_frame = ttk.LabelFrame(self.main_frame, text="Layout Visualizations", padding="5")
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 2D Visualization
        fig_2d = plt.figure(figsize=(6, 4))
        self.canvas_2d = FigureCanvasTkAgg(fig_2d, master=viz_frame)
        self.canvas_2d.draw()
        canvas_2d_widget = self.canvas_2d.get_tk_widget()
        canvas_2d_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # 3D Visualization
        fig_3d = plt.figure(figsize=(6, 4))
        self.ax_3d = fig_3d.add_subplot(111, projection='3d')
        self.canvas_3d = FigureCanvasTkAgg(fig_3d, master=viz_frame)
        self.canvas_3d.draw()
        canvas_3d_widget = self.canvas_3d.get_tk_widget()
        canvas_3d_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Add view controls for 3D
        self.view_controls = ViewControls(viz_frame, self.canvas_3d, self.ax_3d)
        self.view_controls.pack(fill=tk.X, pady=5)

    def update_furniture_list(self, event=None):
        """Update the furniture list based on the selected room type."""
        self.furniture_listbox.delete(0, tk.END)
        room_type = self.room_type_var.get()
        if room_type in self.furniture_options:
            for item in self.furniture_options[room_type]:
                self.furniture_listbox.insert(tk.END, item)

    def add_furniture_with_quantity(self):
        """Add selected furniture with specified quantity."""
        selection = self.furniture_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a furniture item")
            return

        furniture_type = self.furniture_listbox.get(selection[0])
        try:
            quantity = int(self.qty_spinbox.get())
            for i in range(quantity):
                self.selected_furniture_list.insert(tk.END, f"{furniture_type} #{i + 1}")
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid quantity")

    def delete_selected_furniture(self):
        """Delete selected furniture from the list."""
        selection = self.selected_furniture_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a furniture item to delete")
            return
        
        self.selected_furniture_list.delete(selection)

    def generate_layout(self):
        """Generate room layout and visualize it."""
        try:
            if not self.validate_inputs():
                return

            room_dimensions = {
                "width": float(self.width_entry.get()),
                "length": float(self.length_entry.get()),
                "height": float(self.height_entry.get())
            }
            selected_furniture = [
                self.selected_furniture_list.get(i).split(" #")[0]
                for i in range(self.selected_furniture_list.size())
            ]

            if not selected_furniture:
                messagebox.showwarning("Warning", "Please add at least one piece of furniture.")
                return

            self.furniture_layout = generate_layouts(room_dimensions, selected_furniture)

            # Generate both 2D and 3D visualizations
            visualize_layouts(room_dimensions, self.furniture_layout, self.canvas_2d)
            visualize_layouts_3d(room_dimensions, self.furniture_layout, self.canvas_3d, self.ax_3d)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def validate_inputs(self):
        """Validate room dimensions and inputs."""
        if not self.room_type_var.get():
            messagebox.showwarning("Warning", "Please select a room type.")
            return False

        try:
            width = float(self.width_entry.get())
            length = float(self.length_entry.get())
            height = float(self.height_entry.get())

            if width <= 0 or length <= 0 or height <= 0:
                raise ValueError("Dimensions must be positive numbers.")

        except ValueError as e:
            messagebox.showwarning("Warning", "Please enter valid room dimensions.")
            return False

        return True

if __name__ == "__main__":
    verify_3d_models()
    app = RoomLayoutApp()
    app.mainloop()
