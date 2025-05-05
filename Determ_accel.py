import customtkinter as ctk
import math
import time

class MovingBody:
    """Модель движения тела по наклонной плоскости"""
    def __init__(self, mass, angle, friction=0.1):
        self.mass = mass          # Масса тела (кг)
        self.angle = math.radians(angle)  # Угол в радианах
        self.friction = friction  # Коэффициент трения
        
        # Физические константы
        self.gravity = 9.81       # Ускорение свободного падения (м/с²)
        
        # Состояние системы
        self.position = 0.0       # Позиция тела (м)
        self.velocity = 0.0       # Скорость (м/с)
        self.acceleration = 0.0   # Ускорение (м/с²)
        self.time = 0.0           # Время движения (с)
        
    def update(self, dt):
        """Обновляет состояние за время dt"""
        # Вычисляем ускорение
        F_gravity = self.mass * self.gravity * math.sin(self.angle)
        F_friction = self.friction * self.mass * self.gravity * math.cos(self.angle)
        self.acceleration = (F_gravity - F_friction) / self.mass
        
        # Обновляем скорость и позицию
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.time += dt
        
        return self.position

class AccelerationWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Определение ускорения")
        self.geometry("900x600")
        self.minsize(800, 500)
        self.master = master
        self.gravity = 9.81  
        self.plane_length = 0  # Длина плоскости
        
        # Настройка интерфейса
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sim_running = False
        self.body = None
        self.colors = {
            'background': "#2b2b2b",
            'plane': "#8d99ae",
            'body': "#3a86ff",
            'text': "#ffffff",
            'stopper': "#ff5d5d"
        }
        
        self.create_widgets()
        self.draw_plane()  # Рисуем установку сразу
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()
        self.master.withdraw()
    
    def create_widgets(self):
        # Левая панель - визуализация
        self.simulation_frame = ctk.CTkFrame(self, corner_radius=10)
        self.simulation_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Правая панель - управление
        self.control_frame = ctk.CTkFrame(self, corner_radius=10)
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Заголовок
        ctk.CTkLabel(self.simulation_frame, text="Экспериментальная установка", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        # Canvas для анимации
        self.canvas = ctk.CTkCanvas(self.simulation_frame, bg=self.colors['background'])
        self.canvas.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Элементы управления
        ctk.CTkLabel(self.control_frame, text="Параметры эксперимента:", 
                    font=ctk.CTkFont(size=14)).pack(pady=10, padx=5)
        
        # Масса
        self.mass_var = ctk.DoubleVar(value=1.0)
        ctk.CTkLabel(self.control_frame, text="Масса (кг):").pack(pady=(10,0))
        self.mass_entry = ctk.CTkEntry(self.control_frame, textvariable=self.mass_var)
        self.mass_entry.pack(pady=5, padx=10)
        
        # Угол
        self.angle_var = ctk.IntVar(value=30)
        ctk.CTkLabel(self.control_frame, text="Угол наклона (°):").pack(pady=(10,0))
        self.angle_slider = ctk.CTkSlider(self.control_frame, variable=self.angle_var,
                                        from_=0, to=90, command=self.update_angle_label)
        self.angle_slider.pack(pady=5, padx=10)
        self.angle_label = ctk.CTkLabel(self.control_frame, text="30°")
        self.angle_label.pack()
        
        # Трение
        self.friction_var = ctk.DoubleVar(value=0.1)
        ctk.CTkLabel(self.control_frame, text="Коэффициент трения:").pack(pady=(10,0))
        self.friction_slider = ctk.CTkSlider(self.control_frame, variable=self.friction_var,
                                           from_=0, to=0.5, command=self.update_friction_label)
        self.friction_slider.pack(pady=5, padx=10)
        self.friction_label = ctk.CTkLabel(self.control_frame, text="0.1")
        self.friction_label.pack()
        
        # Кнопки управления
        self.start_btn = ctk.CTkButton(self.control_frame, text="Старт", 
                                     command=self.toggle_simulation, fg_color="green")
        self.start_btn.pack(pady=10, padx=10)
        
        reset_btn = ctk.CTkButton(self.control_frame, text="Сброс", 
                                command=self.reset_simulation)
        reset_btn.pack(pady=5, padx=10)
        
        # Результаты
        self.result_text = ctk.CTkTextbox(self.control_frame, height=150)
        self.result_text.pack(pady=10, padx=10, fill="both")
    
    def update_angle_label(self, value):
        self.angle_label.configure(text=f"{int(value)}°")
    
    def update_friction_label(self, value):
        self.friction_label.configure(text=f"{float(value):.2f}")
    
    def toggle_simulation(self):
        self.sim_running = not self.sim_running
        self.start_btn.configure(text="Пауза" if self.sim_running else "Старт")
        if self.sim_running:
            self.init_simulation()
            self.update_simulation()
    
    def init_simulation(self):
        # Создаем объект тела
        self.body = MovingBody(
            mass=self.mass_var.get(),
            angle=self.angle_var.get(),
            friction=self.friction_var.get()
        )
        self.draw_plane()
    
    def draw_plane(self):
        """Отрисовывает наклонную плоскость с центрированием"""
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Центр canvas
        center_x, center_y = w//2, h//2
        
        # Длина и угол плоскости
        self.plane_length = min(w, h) * 0.6  # Уменьшаем длину для центрирования
        angle_rad = math.radians(self.angle_var.get())
        
        # Рассчитываем конечные точки (наклон ВНИЗ)
        end_x = center_x + self.plane_length * math.cos(angle_rad)
        end_y = center_y + self.plane_length * math.sin(angle_rad)  # "+" для наклона вниз
        
        # Рисуем плоскость
        self.canvas.create_line(center_x, center_y, end_x, end_y, 
                              fill=self.colors['plane'], width=5)
        
        # Рисуем ограничитель
        self.canvas.create_rectangle(end_x-10, end_y-10, end_x+10, end_y+10,
                                   fill=self.colors['stopper'], outline="")
        
        # Рисуем тело если есть
        if self.body:
            self.draw_body()


                                  
    def draw_body(self):
        """Отрисовывает тело с корректным позиционированием"""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        center_x, center_y = w//2, h//2
        angle_rad = math.radians(self.angle_var.get())
        
        # Максимальная позиция (в метрах)
        max_pos = self.plane_length / 100  # 100 пикселей = 1 метр
        
        # Ограничиваем позицию
        if self.body.position > max_pos:
            self.body.position = max_pos
            self.body.velocity = 0
        
        # Координаты тела (относительно центра)
        pos_x = center_x + (self.body.position * 100) * math.cos(angle_rad)
        pos_y = center_y + (self.body.position * 100) * math.sin(angle_rad)
        
        self.canvas.create_oval(pos_x-15, pos_y-15, pos_x+15, pos_y+15,
                              fill=self.colors['body'], outline="")

    def update_simulation(self):
        if not self.sim_running or not self.body:
            return
        
        dt = 0.02
        self.body.update(dt)
        self.draw_plane()  # Всегда перерисовываем
        
        # Обновляем результаты
        self.result_text.delete("1.0", "end")
        results = [
            f"Время: {self.body.time:.1f} с",
            f"Пройдено: {self.body.position:.2f} м",
            f"Скорость: {self.body.velocity:.2f} м/с",
            f"Ускорение (эксп.): {self.body.acceleration:.2f} м/с²",
            f"Ускорение (теор.): {self.calculate_theoretical_accel():.2f} м/с²"
        ]
        self.result_text.insert("1.0", "\n".join(results))
        
        self.after(20, self.update_simulation)
    
    def update_simulation(self):
        if not self.sim_running or not self.body:
            return
        
        dt = 0.02  # Шаг времени 20 мс
        self.body.update(dt)
        self.draw_plane()
        
        # Обновляем результаты
        self.result_text.delete("1.0", "end")
        results = [
            f"Время: {self.body.time:.1f} с",
            f"Пройдено: {self.body.position:.2f} м",
            f"Скорость: {self.body.velocity:.2f} м/с",
            f"Ускорение (эксп.): {self.body.acceleration:.2f} м/с²",
            f"Ускорение (теор.): {self.calculate_theoretical_accel():.2f} м/с²"
        ]
        self.result_text.insert("1.0", "\n".join(results))
        
        self.after(20, self.update_simulation)
    
    def calculate_theoretical_accel(self):
        angle = math.radians(self.angle_var.get())
        return self.gravity * (math.sin(angle) -  # Используем self.gravity
                              self.friction_var.get() * math.cos(angle))
    
    def reset_simulation(self):
        self.sim_running = False
        self.start_btn.configure(text="Старт")
        self.body = None
        self.canvas.delete("all")
        self.result_text.delete("1.0", "end")
        self.draw_plane()
    
    def on_close(self):
        """Восстанавливаем главное окно при закрытии"""
        self.master.deiconify()  # Исправлено: восстанавливаем окно
        self.destroy()