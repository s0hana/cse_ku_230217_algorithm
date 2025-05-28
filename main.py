import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import webbrowser
import scheduler  

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scheduler Input Interface")
        self.root.geometry("700x500")
        self.root.configure(bg="#e6f2ff")

        self.teacher_data = []
        self.teacher_availability = {}
        self.course_data = {}
        self.coordinators = {}
        self.batch_count = 0
        self.batch_names = []
        self.current_teacher = None
        self.current_batch_index = 0
        self.current_courses = []

        self.init_start_prompt()

    def init_start_prompt(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        label = tk.Label(self.root, text="Do you want to input from file?", font=("Arial", 14), bg="#e6f2ff")
        label.pack(pady=20)

        yes_btn = tk.Button(self.root, text="Yes", bg="#99ccff", command=self.load_from_file, width=20)
        yes_btn.pack(pady=10)
        no_btn = tk.Button(self.root, text="No", bg="#ff9999", command=self.start_manual_input, width=20)
        no_btn.pack(pady=10)

    def load_from_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            self.process_and_generate(filepath)

    def start_manual_input(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.teacher_label = tk.Label(self.root, text="Enter Teacher Name and Rank (e.g. Prof. X 1):", bg="#e6f2ff")
        self.teacher_label.pack()
        self.teacher_entry = tk.Entry(self.root, width=40)
        self.teacher_entry.pack(pady=5)
        add_placeholder(self.teacher_entry, "Teacher Name Rank")
        self.ok_button = tk.Button(self.root, text="OK", bg="#b3ffb3", command=self.save_teacher)
        self.ok_button.pack(pady=5)
        self.stop_button = tk.Button(self.root, text="Stop Taking Input", bg="#ff6666", command=self.start_batch_input)
        self.stop_button.pack(pady=5)
        self.teacher_listbox = tk.Listbox(self.root, width=50)
        self.teacher_listbox.pack(pady=10)

    def save_teacher(self):
        text = self.teacher_entry.get().strip()
        if text:
            self.teacher_data.append(text)
            self.teacher_listbox.insert(tk.END, text)
            self.teacher_entry.delete(0, tk.END)
            parts = text.rsplit(" ", 1)
            name = parts[0].strip()
            count = int(parts[1].strip())

            self.input_teacher_slots(name)

    def input_teacher_slots(self, teacher_name):
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        hours = ["9", "10", "11", "12", "14", "15", "16"]

        slot_window = tk.Toplevel(self.root)
        slot_window.title(f"Select slots for {teacher_name}")
        slot_window.configure(bg="#ffffe6")

        tk.Label(slot_window, text=f"{teacher_name} Availability", bg="#ffffe6").grid(row=0, column=0, columnspan=8, pady=5)
        slot_vars = {}

        for i, day in enumerate(days):
            tk.Label(slot_window, text=day, bg="#ffffe6").grid(row=i+1, column=0)
            for j, hour in enumerate(hours):
                slot = f"{day} {hour}"
                var = tk.BooleanVar()
                chk = tk.Checkbutton(slot_window, text=hour, variable=var, bg="#ffffe6")
                chk.grid(row=i+1, column=j+1)
                slot_vars[slot] = var

        def save_slots():
            selected = [slot for slot, var in slot_vars.items() if var.get()]
            self.teacher_availability[teacher_name] = selected
            slot_window.destroy()

        tk.Button(slot_window, text="Save Slots", bg="#cce6ff", command=save_slots).grid(row=len(days)+2, column=0, columnspan=8, pady=10)

    def start_batch_input(self):
        self.batch_count = simpledialog.askinteger("Batch Count", "Enter number of batches:")
        self.batch_names = []
        for i in range(self.batch_count):
            name = simpledialog.askstring("Batch Name", f"Enter name for batch {i+1}:")
            self.batch_names.append(name)
        self.course_data = {}
        self.current_batch_index = 0
        self.load_course_input()

    def load_course_input(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.course_frame = tk.Frame(self.root, bg="#f9f9f9")
        self.course_frame.pack(pady=20)

        self.course_entries = []
        tk.Label(self.course_frame, text=f"Enter Courses for {self.batch_names[self.current_batch_index]}", bg="#f9f9f9").pack()

        def add_course_input():
            entry_frame = tk.Frame(self.course_frame, bg="#f9f9f9")
            entry_frame.pack(pady=2)
            code_entry = tk.Entry(entry_frame, width=10)
            code_entry.grid(row=0, column=0, padx=2)
            add_placeholder(code_entry, "Course Code")
            credit_entry = tk.Entry(entry_frame, width=5)
            credit_entry.grid(row=0, column=1, padx=2)
            add_placeholder(credit_entry, "Credit")
            teacher_entry = tk.Entry(entry_frame, width=30)
            teacher_entry.grid(row=0, column=2, padx=2)
            add_placeholder(teacher_entry, "Teacher(s)")
            self.course_entries.append((code_entry, credit_entry, teacher_entry))

        add_btn = tk.Button(self.course_frame, text="Add Course", command=add_course_input, bg="#ccffcc")
        add_btn.pack(pady=5)

        next_btn = tk.Button(self.course_frame, text="Next Batch", bg="#ffcc99", command=self.save_batch_courses)
        next_btn.pack(pady=5)
        add_course_input()

    def save_batch_courses(self):
        courses = []
        for code_entry, credit_entry, teacher_entry in self.course_entries:
            code = code_entry.get().strip()
            credit = credit_entry.get().strip()
            teacher = teacher_entry.get().strip()
            if code and credit and teacher:
                courses.append(f"{code} {credit} {teacher}")
        self.course_data[self.batch_names[self.current_batch_index]] = courses
        self.current_batch_index += 1

        if self.current_batch_index < self.batch_count:
            self.load_course_input()
        else:
            self.input_coordinators()

    def input_coordinators(self):
        self.coordinators = {}
        for name in self.batch_names:
            coord = simpledialog.askstring("Coordinator", f"Enter coordinator for {name}:")
            self.coordinators[name] = coord
        self.ask_filename_to_process()

    def ask_filename_to_process(self):
        filename = simpledialog.askstring("Filename", "Enter filename to process with main_code (e.g., input.txt):")
        if filename:
            self.generate_file(filename)
            self.process_and_generate(filename)

    def generate_file(self, filename):
        lines = ["teacher_rank"]
        lines.extend(self.teacher_data)
        lines.append("\nteacher_availability")
        for t, slots in self.teacher_availability.items():
            lines.append(f"{t}: {', '.join(slots)}")
        lines.append("\ncourses")
        for batch, courses in self.course_data.items():
            lines.append(f"{batch}: {', '.join(courses)}")
        lines.append("\ncoordinator info")
        for batch, coord in self.coordinators.items():
            lines.append(f"{batch}: {coord}")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def process_and_generate(self, filename):
        result = scheduler.process_file(filename)
        if len(result) == 2:
            pdf_path, html_path = result
            self.show_open_buttons(pdf_path, html_path)
        elif len(result) == 3:
            pdf_path, html_path, data_list = result
            self.show_open_buttons(pdf_path, html_path)
            self.show_data_page(data_list)

    def show_open_buttons(self, pdf_path, html_path):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Files created successfully!", font=("Arial", 14), bg="#e6f2ff").pack(pady=20)
        tk.Button(self.root, text="Open PDF", command=lambda: webbrowser.open(pdf_path), bg="#ffccff").pack(pady=10)
        tk.Button(self.root, text="Open HTML", command=lambda: webbrowser.open(html_path), bg="#ccffff").pack(pady=10)

    def show_data_page(self, data_list):
        if data_list: 
            data_win = tk.Toplevel(self.root)
            data_win.title("Processed Data")
            data_win.geometry("600x400")
            data_win.configure(bg="#fffff0")
            tk.Label(data_win, text="⚠ Could Not Assign All Slots", bg="#fffff0", font=("Arial", 12, "bold")).pack()
            textbox = tk.Text(data_win, wrap="word", bg="#f2f2f2")
            textbox.pack(expand=True, fill="both")
            for item in data_list:
                textbox.insert(tk.END, f"{item}\n")

def add_placeholder(entry, placeholder_text):
    entry.insert(0, placeholder_text)
    entry.config(fg='gray')

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(fg='gray')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
