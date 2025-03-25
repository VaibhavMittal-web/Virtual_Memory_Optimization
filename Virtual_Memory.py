import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from collections import deque

class VirtualMemorySimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Memory Management Simulator")
        
        # UI Elements
        tk.Label(root, text="Enter Reference String (comma-separated):").pack()
        self.ref_string_entry = tk.Entry(root)
        self.ref_string_entry.pack()
        
        tk.Label(root, text="Number of Frames:").pack()
        self.num_frames_entry = tk.Entry(root)
        self.num_frames_entry.pack()
        
        tk.Button(root, text="Simulate LRU", command=self.simulate_lru).pack()
        tk.Button(root, text="Simulate Optimal", command=self.simulate_optimal).pack()
    
    def get_inputs(self):
        try:
            ref_string = list(map(int, self.ref_string_entry.get().split(',')))
            num_frames = int(self.num_frames_entry.get())
            return ref_string, num_frames
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers!")
            return None, None
    
    def simulate_lru(self):
        ref_string, num_frames = self.get_inputs()
        if ref_string is None:
            return
        
        memory = deque()
        page_faults = 0
        history = []
        
        for page in ref_string:
            if page not in memory:
                if len(memory) >= num_frames:
                    memory.popleft()
                memory.append(page)
                page_faults += 1
            history.append(list(memory))
        
        self.plot_results(ref_string, history, "LRU Algorithm")
    
    def simulate_optimal(self):
        ref_string, num_frames = self.get_inputs()
        if ref_string is None:
            return
        
        memory = []
        page_faults = 0
        history = []
        
        for i, page in enumerate(ref_string):
            if page not in memory:
                if len(memory) < num_frames:
                    memory.append(page)
                else:
                    future_use = {frame: ref_string[i+1:].index(frame) if frame in ref_string[i+1:] else float('inf') for frame in memory}
                    to_replace = max(future_use, key=future_use.get)
                    memory[memory.index(to_replace)] = page
                page_faults += 1
            history.append(list(memory))
        
        self.plot_results(ref_string, history, "Optimal Algorithm")
    
    def plot_results(self, ref_string, history, title):
        plt.figure(figsize=(10, 5))
        for i, frame_state in enumerate(history):
            plt.scatter([i] * len(frame_state), frame_state, label=f"Step {i+1}" if i < 5 else "")
        plt.xlabel("Time")
        plt.ylabel("Page in Memory")
        plt.title(title)
        plt.legend()
        plt.show()
        
# Run the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMemorySimulator(root)
    root.mainloop()
