import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque, OrderedDict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class VirtualMemorySimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Memory Management Simulator")
        self.root.geometry("1400x900")
        
        # Initialize attributes
        self.history = []
        self.page_faults = 0
        self.page_hits = 0
        self.current_step = 0
        self.ref_string = []
        self.num_frames = 0
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input panel
        self.create_input_panel()
        
        # Visualization panels
        self.create_memory_visualization_panel()
        self.create_graph_visualization_panel()
        
        # Results panel
        self.create_results_panel()
    
    def create_input_panel(self):
        input_frame = ttk.LabelFrame(self.main_frame, text="Simulation Parameters")
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Reference string input
        ttk.Label(input_frame, text="Reference String (comma-separated):").grid(row=0, column=0, sticky=tk.W)
        self.ref_string_entry = ttk.Entry(input_frame, width=40)
        self.ref_string_entry.grid(row=0, column=1, padx=5)
        self.ref_string_entry.insert(0, "7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1")
        
        # Frame size input
        ttk.Label(input_frame, text="Number of Frames:").grid(row=1, column=0, sticky=tk.W)
        self.num_frames_entry = ttk.Entry(input_frame, width=10)
        self.num_frames_entry.grid(row=1, column=1, padx=5, sticky=tk.W)
        self.num_frames_entry.insert(0, "3")
        
        # Algorithm selection
        ttk.Label(input_frame, text="Algorithm:").grid(row=2, column=0, sticky=tk.W)
        self.algorithm_var = tk.StringVar()
        self.algorithm_menu = ttk.Combobox(input_frame, textvariable=self.algorithm_var, 
                                         values=["LRU", "Optimal", "FIFO", "Second Chance"])
        self.algorithm_menu.grid(row=2, column=1, padx=5, sticky=tk.W)
        self.algorithm_menu.current(0)
        
        # Control buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="Run Simulation", command=self.run_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Reset", command=self.reset_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Show Stats", command=self.show_statistics).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Show Graph", command=self.show_graph).pack(side=tk.LEFT, padx=2)
    
    def create_memory_visualization_panel(self):
        vis_frame = ttk.LabelFrame(self.main_frame, text="Memory State Visualization")
        vis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create canvas for memory state visualization
        self.canvas = tk.Canvas(vis_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create timeline navigation
        nav_frame = ttk.Frame(vis_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        ttk.Button(nav_frame, text="◀", command=self.prev_step).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="▶", command=self.next_step).pack(side=tk.LEFT)
        self.step_label = ttk.Label(nav_frame, text="Step 0/0")
        self.step_label.pack(side=tk.LEFT, expand=True)
    
    def create_graph_visualization_panel(self):
        graph_frame = ttk.LabelFrame(self.main_frame, text="Graph Visualization")
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create figure for matplotlib
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas for matplotlib figure
        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_results_panel(self):
        results_frame = ttk.LabelFrame(self.main_frame, text="Simulation Results")
        results_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        
        # Create table for results
        self.results_tree = ttk.Treeview(results_frame, columns=('Step', 'Reference', 'Memory State', 'Fault/Hit'), 
                                       show='headings', height=8)
        self.results_tree.heading('Step', text='Step')
        self.results_tree.heading('Reference', text='Reference')
        self.results_tree.heading('Memory State', text='Memory State')
        self.results_tree.heading('Fault/Hit', text='Fault/Hit')
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
    
    def validate_inputs(self):
        try:
            self.ref_string = list(map(int, self.ref_string_entry.get().split(',')))
            self.num_frames = int(self.num_frames_entry.get())
            if self.num_frames <= 0:
                raise ValueError
            return True
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input values!\nPlease enter valid numbers.")
            return False
    
    def run_simulation(self):
        if not self.validate_inputs():
            return
        
        algorithm = self.algorithm_var.get()
        
        self.history = []
        self.page_faults = 0
        self.page_hits = 0
        self.current_step = 0
        
        if algorithm == "LRU":
            self.simulate_lru()
        elif algorithm == "Optimal":
            self.simulate_optimal()
        elif algorithm == "FIFO":
            self.simulate_fifo()
        elif algorithm == "Second Chance":
            self.simulate_second_chance()
        
        self.update_visualization()
        self.update_results_table()
        self.update_step_label()
        self.update_graph()
    
    def simulate_lru(self):
        memory = OrderedDict()
        for i, page in enumerate(self.ref_string):
            if page in memory:
                self.page_hits += 1
                memory.move_to_end(page)
                self.history.append((list(memory.keys()), 'Hit'))
            else:
                self.page_faults += 1
                if len(memory) >= self.num_frames:
                    memory.popitem(last=False)
                memory[page] = True
                self.history.append((list(memory.keys()), 'Fault'))
    
    def simulate_optimal(self):
        memory = []
        for i, page in enumerate(self.ref_string):
            if page in memory:
                self.page_hits += 1
                self.history.append((memory.copy(), 'Hit'))
                continue
            
            self.page_faults += 1
            if len(memory) < self.num_frames:
                memory.append(page)
            else:
                future = self.ref_string[i+1:]
                farthest = -1
                replace_page = -1
                for p in memory:
                    if p not in future:
                        replace_page = p
                        break
                    idx = future.index(p)
                    if idx > farthest:
                        farthest = idx
                        replace_page = p
                memory[memory.index(replace_page)] = page
            self.history.append((memory.copy(), 'Fault'))
    
    def simulate_fifo(self):
        memory = set()
        queue = deque()
        for page in self.ref_string:
            if page in memory:
                self.page_hits += 1
                self.history.append((list(memory), 'Hit'))
                continue
            
            self.page_faults += 1
            if len(memory) >= self.num_frames:
                removed = queue.popleft()
                memory.remove(removed)
            memory.add(page)
            queue.append(page)
            self.history.append((list(memory), 'Fault'))
    
    def simulate_second_chance(self):
        memory = {}
        queue = deque()
        
        for page in self.ref_string:
            if page in memory:
                self.page_hits += 1
                memory[page] = True  # Give second chance
                self.history.append((list(memory.keys()), 'Hit'))
                continue
            
            self.page_faults += 1
            if len(memory) >= self.num_frames:
                while True:
                    current = queue.popleft()
                    if memory[current]:
                        memory[current] = False
                        queue.append(current)
                    else:
                        del memory[current]
                        break
            memory[page] = True
            queue.append(page)
            self.history.append((list(memory.keys()), 'Fault'))
    
    def update_visualization(self):
        self.canvas.delete("all")
        if not self.history:
            return
        
        step = self.current_step
        memory_state, status = self.history[step]
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Draw memory frames
        cell_width = canvas_width // (self.num_frames + 1)
        cell_height = 40
        for i in range(self.num_frames):
            x1 = i * cell_width + 10
            y1 = canvas_height // 2 - cell_height
            x2 = x1 + cell_width - 20
            y2 = y1 + cell_height
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='#e0e0e0')
            if i < len(memory_state):
                self.canvas.create_text((x1+x2)//2, (y1+y2)//2, 
                                      text=str(memory_state[i]), font=('Arial', 14))
        
        # Draw reference arrow
        self.canvas.create_text(canvas_width - 50, canvas_height//2, 
                               text="→", font=('Arial', 20), fill='red')
        self.canvas.create_text(canvas_width - 30, canvas_height//2 + 20, 
                               text=status, fill='red' if status == 'Fault' else 'green')
    
    def update_graph(self):
        self.ax.clear()
        
        if not self.history:
            return
        
        # Prepare data for plotting
        steps = list(range(1, len(self.history)+1))
        ref_pages = [page for page in self.ref_string]
        memory_states = [state for state, _ in self.history]
        faults = [i+1 for i, (_, status) in enumerate(self.history) if status == 'Fault']
        
        # Plot reference string
        self.ax.plot(steps, ref_pages, 'bo-', label='Reference', markersize=8)
        
        # Plot memory states
        for i in range(self.num_frames):
            frame_pages = []
            for state in memory_states:
                frame_pages.append(state[i] if i < len(state) else None)
            self.ax.plot(steps, frame_pages, 'o--', label=f'Frame {i+1}', alpha=0.7)
        
        # Mark page faults
        for fault in faults:
            self.ax.axvline(x=fault, color='r', linestyle=':', alpha=0.3)
        
        self.ax.set_title('Page Reference and Memory State Over Time')
        self.ax.set_xlabel('Time Step')
        self.ax.set_ylabel('Page Number')
        self.ax.legend()
        self.ax.grid(True)
        
        self.graph_canvas.draw()
    
    def update_results_table(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        for i, (state, status) in enumerate(self.history):
            self.results_tree.insert('', 'end', values=(
                i+1,
                self.ref_string[i],
                ', '.join(map(str, state)) if state else 'Empty',
                status
            ))
    
    def update_step_label(self):
        self.step_label.config(text=f"Step {self.current_step + 1}/{len(self.history)}")
    
    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_visualization()
            self.update_step_label()
    
    def next_step(self):
        if self.current_step < len(self.history) - 1:
            self.current_step += 1
            self.update_visualization()
            self.update_step_label()
    
    def show_statistics(self):
        if not self.history:
            return
        
        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        
        labels = ['Page Faults', 'Page Hits']
        values = [self.page_faults, self.page_hits]
        
        ax.bar(labels, values, color=['red', 'green'])
        ax.set_title('Memory Access Statistics')
        ax.set_ylabel('Count')
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Simulation Statistics")
        canvas = FigureCanvasTkAgg(fig, master=stats_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def show_graph(self):
        if not self.history:
            return
        
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Detailed Graph Visualization")
        graph_window.geometry("1000x600")
        
        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Prepare data for plotting
        steps = list(range(1, len(self.history)+1))
        ref_pages = [page for page in self.ref_string]
        memory_states = [state for state, _ in self.history]
        faults = [i+1 for i, (_, status) in enumerate(self.history) if status == 'Fault']
        
        # Plot reference string
        ax.plot(steps, ref_pages, 'bo-', label='Reference', markersize=8)
        
        # Plot memory states
        for i in range(self.num_frames):
            frame_pages = []
            for state in memory_states:
                frame_pages.append(state[i] if i < len(state) else None)
            ax.plot(steps, frame_pages, 'o--', label=f'Frame {i+1}', alpha=0.7)
        
        # Mark page faults
        for fault in faults:
            ax.axvline(x=fault, color='r', linestyle=':', alpha=0.3)
        
        ax.set_title('Page Reference and Memory State Over Time')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('Page Number')
        ax.legend()
        ax.grid(True)
        
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def reset_simulation(self):
        self.ref_string_entry.delete(0, tk.END)
        self.ref_string_entry.insert(0, "7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1")
        self.num_frames_entry.delete(0, tk.END)
        self.num_frames_entry.insert(0, "3")
        self.algorithm_menu.current(0)
        self.history = []
        self.page_faults = 0
        self.page_hits = 0
        self.current_step = 0
        self.ref_string = []
        self.num_frames = 0
        self.canvas.delete("all")
        self.ax.clear()
        self.graph_canvas.draw()
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.step_label.config(text="Step 0/0")

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMemorySimulator(root)
    root.mainloop()
