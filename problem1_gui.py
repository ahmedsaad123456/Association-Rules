import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logic

class Problem1GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Problem 1 GUI")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Main Frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File name input
        file_frame = ttk.LabelFrame(main_frame, text="Dataset", padding="10")
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(file_frame, text="Enter CSV File Name:").pack(anchor="w")
        self.file_entry = ttk.Entry(file_frame, width=50)
        self.file_entry.pack(pady=3)

        # Parameters Frame
        param_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="10")
        param_frame.pack(fill=tk.X, padx=5, pady=5)

        self.create_param_input(param_frame, "Confidence Threshold (0.0 - 1.0):", "conf_entry")
        self.create_param_input(param_frame, "Minimum Support Count:", "sup_entry")
        self.create_param_input(param_frame, "Percentage of Dataset (0 - 100):", "perc_entry")

        # Run Button
        self.run_button = ttk.Button(main_frame, text="Run Algorithm", command=self.run_apriori)
        self.run_button.pack(pady=10)

        # Loading Indicator
        self.loading_label = ttk.Label(main_frame, text="", foreground="blue")
        self.loading_label.pack()

        self.progress_bar = ttk.Progressbar(main_frame, mode="indeterminate", length=200)

        # Output Frame
        output_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.output_text = tk.Text(output_frame, height=10, width=80, wrap=tk.WORD)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)

    def create_param_input(self, parent, label_text, attr_name):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=3)

        ttk.Label(frame, text=label_text, width=30, anchor="w").pack(side=tk.LEFT)
        entry = ttk.Entry(frame)
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        setattr(self, attr_name, entry)

    def run_apriori(self):
        try:
            file_name = self.file_entry.get().strip()
            confidence_threshold = float(self.conf_entry.get())
            sup_count = int(self.sup_entry.get())
            percentage = float(self.perc_entry.get())

            # Validation
            if not file_name:
                raise ValueError("Please enter a valid file name.")
            if not (0.0 <= confidence_threshold <= 1.0):
                raise ValueError("Confidence must be between 0.0 and 1.0.")
            if sup_count <= 0:
                raise ValueError("Minimum support count must be a positive integer.")
            if not (0 <= percentage <= 100):
                raise ValueError("Percentage must be between 0 and 100.")

            # Start processing in a separate thread
            self.loading_label.config(text="Processing... Please wait.")
            self.run_button.config(state=tk.DISABLED)
            self.progress_bar.pack(pady=5)
            self.progress_bar.start()

            thread = threading.Thread(target=self.execute_apriori, args=(file_name, confidence_threshold, sup_count, percentage))
            thread.start()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def execute_apriori(self, file_name, confidence_threshold, sup_count, percentage):
        try:
            # Load and process dataset
            df = logic.load_dataset_problem1(file_name, percentage)
            vertical_data, filtered_vertical_data = logic.generate_vertical_data_problem1(df, sup_count)
            frequent_itemsets = logic.generate_frequent_itemsets(filtered_vertical_data, sup_count)
            strong_rules = logic.generate_association_rules(frequent_itemsets, vertical_data, confidence_threshold)

            # Update UI with results
            self.output_text.delete("1.0", tk.END)

            self.output_text.insert(tk.END, " Frequent Itemsets:\n")
            for itemset in frequent_itemsets.keys():
                self.output_text.insert(tk.END, f"{itemset}\n")

            self.output_text.insert(tk.END, "\n Strong Association Rules:\n")
            for rule in strong_rules:
                self.output_text.insert(tk.END, f"{rule['Rule']} (Confidence: {rule['Confidence']:.2f})\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))

        # Reset UI after processing
        self.loading_label.config(text="")
        self.run_button.config(state=tk.NORMAL)
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = Problem1GUI(root)
    root.mainloop()
