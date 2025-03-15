import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar
import threading
import time
from datetime import datetime
from database import DatabaseManager

class EventNotifierGUI:
    """Основний клас інтерфейсу програми."""

    def __init__(self, root, db_manager):
        self.root = root
        self.db = db_manager
        self.root.title("Система інформування користувачів")
        self.root.geometry("800x900")
        self.root.configure(bg="#e6f7e6")

        self.create_gui()
        self.load_users()

        # Потік для перевірки нагадувань
        reminder_thread = threading.Thread(target=self.check_reminders)
        reminder_thread.daemon = True
        reminder_thread.start()

    def create_gui(self):
        """Створення графічного інтерфейсу."""
        tk.Label(self.root, text="Повідомлення для користувачів",
                 font=("Arial", 16), bg="#e6f7e6", fg="#333").pack(pady=10)

        self.users_listbox = tk.Listbox(self.root, height=6, width=45, font=("Arial", 12))
        self.users_listbox.pack(pady=10)

        tk.Label(self.root, text="Введіть повідомлення", bg="#e6f7e6", fg="#333").pack()
        self.message_entry = tk.Text(self.root, font=("Arial", 12), width=50, height=8)
        self.message_entry.pack(pady=10)

        tk.Button(self.root, text="Відправити повідомлення", font=("Arial", 12),
                  bg="#4CAF50", fg="#fff", command=self.send_message).pack(pady=20)

        buttons_frame = tk.Frame(self.root, bg="#e6f7e6")
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Додати користувача", font=("Arial", 12),
                  bg="#2196F3", fg="#fff", command=self.add_user).pack(side=tk.LEFT, padx=10)

        tk.Button(buttons_frame, text="Видалити користувача", font=("Arial", 12),
                  bg="#F44336", fg="#fff", command=self.delete_user).pack(side=tk.LEFT, padx=10)

        # Кнопка для створення події
        tk.Button(self.root, text="Створити подію", font=("Arial", 12),
                  bg="#FFC107", fg="#fff", command=self.create_event).pack(pady=20)

        # Календар для вибору дати події
        tk.Label(self.root, text="Виберіть дату події", bg="#e6f7e6", fg="#333").pack()
        self.calendar = Calendar(self.root, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(pady=20)

    def load_users(self):
        """Завантаження списку користувачів."""
        self.users_listbox.delete(0, tk.END)
        users = self.db.execute_query("SELECT id, name, contact_method, email, phone FROM users", fetch=True)
        self.user_data = {}  # Зберігаємо ID користувачів у словник
        for user in users:
            user_id, name, method, email, phone = user
            contact_info = email if method == "email" else phone
            display_text = f"{name} ({method}: {contact_info})"
            self.users_listbox.insert(tk.END, display_text)
            self.user_data[display_text] = user_id

    def send_message(self):
        """Відправка повідомлення вибраному користувачу."""
        selected = self.users_listbox.curselection()
        if not selected:
            self.show_custom_message("Помилка", "Виберіть користувача зі списку.", "red")
            return

        user_text = self.users_listbox.get(selected[0])
        user_id = self.user_data[user_text]

        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            self.show_custom_message("Помилка", "Введіть повідомлення.", "red")
            return

        self.db.execute_query("INSERT INTO messages (user_id, message) VALUES (?, ?)", (user_id, message))
        self.show_custom_message("Готово", "Повідомлення відправлено.", "green")
        self.message_entry.delete("1.0", tk.END)

    def add_user(self):
        """Додавання користувача."""
        def save_user():
            name, email, phone = name_entry.get(), email_entry.get(), phone_entry.get()
            contact_method = contact_var.get()

            if not name or (contact_method == "email" and not email) or (contact_method == "phone" and not phone):
                self.show_custom_message("Помилка", "Заповніть всі поля.", "red")
                return

            self.db.execute_query("INSERT INTO users (name, email, phone, contact_method) VALUES (?, ?, ?, ?)",
                                  (name, email if contact_method == "email" else None,
                                   phone if contact_method == "phone" else None, contact_method))
            self.show_custom_message("Готово", "Користувача додано.", "green")
            new_user_window.destroy()
            self.load_users()

        new_user_window = tk.Toplevel(self.root)
        new_user_window.title("Додати користувача")
        new_user_window.geometry("400x300")

        tk.Label(new_user_window, text="Ім'я").pack()
        name_entry = tk.Entry(new_user_window)
        name_entry.pack()

        tk.Label(new_user_window, text="Електронна пошта").pack()
        email_entry = tk.Entry(new_user_window)
        email_entry.pack()

        tk.Label(new_user_window, text="Номер телефону").pack()
        phone_entry = tk.Entry(new_user_window)
        phone_entry.pack()

        contact_var = tk.StringVar(value="email")
        tk.Radiobutton(new_user_window, text="Email", variable=contact_var, value="email").pack()
        tk.Radiobutton(new_user_window, text="Телефон", variable=contact_var, value="phone").pack()

        tk.Button(new_user_window, text="Зберегти", command=save_user).pack()

    def delete_user(self):
        """Видалення користувача."""
        selected = self.users_listbox.curselection()
        if not selected:
            self.show_custom_message("Помилка", "Виберіть користувача зі списку.", "red")
            return

        user_text = self.users_listbox.get(selected[0])
        user_id = self.user_data[user_text]

        self.db.execute_query("DELETE FROM users WHERE id=?", (user_id,))
        self.show_custom_message("Готово", "Користувача видалено.", "green")
        self.load_users()

    def create_event(self):
        """Створення події для користувача на вибрану дату з описом."""
        selected = self.users_listbox.curselection()
        if not selected:
            self.show_custom_message("Помилка", "Виберіть користувача зі списку.", "red")
            return

        user_text = self.users_listbox.get(selected[0])
        user_id = self.user_data[user_text]

        # Вибір дати події з календаря
        event_date_str = self.calendar.get_date()  # Отримуємо вибрану дату
        try:
            event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
        except ValueError:
            self.show_custom_message("Помилка", "Невірний формат дати.", "red")
            return

        # Введення опису події
        event_description = simpledialog.askstring("Опис події", "Введіть опис події:")
        if not event_description:
            return

        self.db.execute_query("INSERT INTO events (user_id, event_date, event_description) VALUES (?, ?, ?)",
                              (user_id, event_date, event_description))
        self.show_custom_message("Готово", "Подію додано.", "green")

    def check_reminders(self):
        """Перевірка нагадувань та виведення їх у консоль."""
        while True:
            # Отримуємо всі події
            events = self.db.execute_query("SELECT id, user_id, event_date, event_description FROM events", fetch=True)
            for event in events:
                event_id, user_id, event_date, event_description = event
                # Якщо подія сьогодні або в найближчі 15 хвилин
                if (event_date - datetime.now()).total_seconds() <= 900 and (event_date - datetime.now()).total_seconds() > 0:
                    # Відправляємо нагадування
                    self.send_reminder(user_id, event_description)
            time.sleep(60)  # Перевірка раз на хвилину

    def send_reminder(self, user_id, event_description):
        """Відправка нагадування користувачу."""
        user = self.db.execute_query("SELECT name, contact_method, email, phone FROM users WHERE id=?", (user_id,), fetch=True)[0]
        name, contact_method, email, phone = user
        message = f"Нагадування для {name}: {event_description}"

        # Виводимо нагадування в консоль
        print(f"Нагадування: {message}")

        # Для подальшої реалізації: можна додати відображення нагадування в інтерфейсі
        self.show_custom_message("Нагадування", message, "blue")

    def show_custom_message(self, title, message, color):
        """Виведення кастомного повідомлення в кольоровому вікні."""
        msg_box = tk.Toplevel(self.root)
        msg_box.title(title)
        msg_box.geometry("400x200")
        msg_box.configure(bg=color)

        label = tk.Label(msg_box, text=message, font=("Arial", 14), bg=color, fg="white", wraplength=350)
        label.pack(expand=True, fill=tk.BOTH, pady=20)

        button = tk.Button(msg_box, text="Закрити", font=("Arial", 12), bg="gray", fg="white", command=msg_box.destroy)
        button.pack(pady=10)

# Створення екземпляра GUI та підключення до бази даних
if __name__ == "__main__":
    root = tk.Tk()
    db_manager = DatabaseManager()  # Ініціалізуємо об'єкт для роботи з базою даних
    app = EventNotifierGUI(root, db_manager)
    root.mainloop()
