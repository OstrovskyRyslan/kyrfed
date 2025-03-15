from database import DatabaseManager
from gui import EventNotifierGUI
import tkinter as tk

def main():
    db_manager = DatabaseManager()
    root = tk.Tk()
    app = EventNotifierGUI(root, db_manager)
    root.mainloop()

if __name__ == "__main__":
    main()
