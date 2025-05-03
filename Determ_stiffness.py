import customtkinter as ctk
import math
import time

class SimpleSpring:
    """Простая реализация физики пружины без pymunk"""
    def __init__(self, k, rest_length, mass, damping=0.2):
        # Параметры
        self.k = k / 1000.0  # Жесткость (Н/мм)
        self.rest_length = rest_length  # Длина покоя (мм)
        self.mass = mass  # Масса груза (кг)
        self.damping = damping  # Коэффициент затухания
        
        # Состояние
        self.anchor_pos = (0, 200)  # Верхняя точка крепления
        self.weight_pos = (0, 200 + rest_length)  # Положение груза
        self.velocity = 0  # Скорость по вертикали (мм/с)
        self.force = 0  # Текущая сила (Н)
        self.gravity = 9.81  # Ускорение свободного падения (м/с^2)
    
    def set_anchor_x(self, x):
        """Устанавливает горизонтальную позицию точки крепления"""
        self.anchor_pos = (x, self.anchor_pos[1])
        self.weight_pos = (x, self.weight_pos[1])
    
    def step(self, dt):
        """Обновление физики за шаг времени dt (в секундах)"""
        # Вычисляем текущую длину пружины
        extension = self.weight_pos[1] - self.anchor_pos[1]
        
        # Вычисляем силу упругости: F = -k * (x - L0)
        # Отрицательная при растяжении (пружина тянет вверх)
        spring_force = -self.k * (extension - self.rest_length)
        
        # Сила тяжести: F = m * g (положительная вниз)
        gravity_force = self.mass * self.gravity
        
        # Сила трения (демпфирования): F = -c * v (противоположна скорости)
        damping_force = -self.damping * self.velocity
        
        # Суммарная сила
        total_force = spring_force + gravity_force + damping_force
        self.force = total_force
        
        # Ускорение: F = m * a -> a = F / m
        acceleration = total_force / self.mass
        
        # Обновление скорости: v = v0 + a * dt
        self.velocity += acceleration * dt
        
        # Обновление позиции: y = y0 + v * dt
        new_y = self.weight_pos[1] + self.velocity * dt
        self.weight_pos = (self.weight_pos[0], new_y)
        
        return extension - self.rest_length  # Возвращаем величину растяжения

class StiffnessWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Определение жесткости пружины")
        self.geometry("900x600")
        self.minsize(800, 500)
        self.master = master
        
        # Инициализация фреймов
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.simulation_frame = ctk.CTkFrame(self, corner_radius=10)
        self.simulation_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.control_frame = ctk.CTkFrame(self, corner_radius=10)
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()

        # Параметры симуляции
        self.sim_running = False
        self.spring = None  # Объект пружины
        
        self.spring_params = {
            'k': 500,           # Жесткость (Н/м)
            'rest_length': 100, # Длина в покое (мм)
            'mass': 0.1,        # Масса груза (кг)
            'damping': 0.2      # Демпфирование
        }
        
        # Цвета для темной темы
        self.colors = {
            'background': "#1e1e1e",
            'spring': "#ff5d5d",
            'weight': "#3a86ff",
            'platform': "#8d99ae",
            'text': "#ffffff",
            'stand': "#8d99ae",
            'ruler': "#f9c74f",
            'anchor': "#ffb703"
        }
        
        # Параметры измерений
        self.extension = 0      # Текущее растяжение
        self.last_extensions = []  # История растяжений для определения стабилизации
        self.measurements_ready = False
        
        # Размеры canvas
        self.canvas_width = 800
        self.canvas_height = 500
        self.canvas_ready = False

        # Создаем интерфейс и инициализируем симуляцию
        self.create_widgets()
        self.after(100, self.check_canvas_size)

    def create_widgets(self):
        # Левая панель - визуализация
        ctk.CTkLabel(self.simulation_frame, 
                   text="Установка для измерения жесткости", 
                   font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        self.canvas = ctk.CTkCanvas(self.simulation_frame, bg=self.colors['background'])
        self.canvas.pack(expand=True, fill="both", padx=20, pady=20)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Информационная панель
        self.info_frame = ctk.CTkFrame(self.simulation_frame)
        self.info_frame.pack(fill="x", padx=20, pady=10)
        
        self.extension_label = ctk.CTkLabel(self.info_frame, 
                                          text="Растяжение: 0.0 мм", 
                                          font=ctk.CTkFont(size=14))
        self.extension_label.pack(side="left", padx=10)
        
        self.force_label = ctk.CTkLabel(self.info_frame, 
                                       text="Сила: 0.0 Н", 
                                       font=ctk.CTkFont(size=14))
        self.force_label.pack(side="right", padx=10)

        # Правая панель - управление
        self.create_control_widgets()
        self.add_physics_controls()

    def create_control_widgets(self):
        # Параметры эксперимента
        ctk.CTkLabel(self.control_frame, 
                   text="Параметры эксперимента:", 
                   font=ctk.CTkFont(size=14)).pack(pady=10, padx=5)

        # Выбор пружины
        self.spring_var = ctk.StringVar(value="Стальная")
        ctk.CTkLabel(self.control_frame, text="Тип пружины:").pack(pady=(10,0))
        spring_combo = ctk.CTkComboBox(self.control_frame, 
                                    values=["Стальная", "Медная", "Титановая"],
                                    variable=self.spring_var,
                                    command=self.change_spring_type)
        spring_combo.pack(pady=5, padx=10)

        # Слайдер нагрузки
        self.load_var = ctk.IntVar(value=100)
        ctk.CTkLabel(self.control_frame, text="Нагрузка (г):").pack(pady=(10,0))
        load_slider = ctk.CTkSlider(self.control_frame, 
                                  variable=self.load_var,
                                  from_=50, 
                                  to=1000,
                                  command=self.update_load_label)
        load_slider.pack(pady=5, padx=10)
        self.load_label = ctk.CTkLabel(self.control_frame, text="100 г")
        self.load_label.pack()

    def add_physics_controls(self):
        # Кнопки управления
        btn_frame = ctk.CTkFrame(self.control_frame)
        btn_frame.pack(pady=20)

        self.start_btn = ctk.CTkButton(btn_frame, 
                                     text="Старт", 
                                     command=self.toggle_simulation)
        self.start_btn.pack(side="left", padx=5)

        reset_btn = ctk.CTkButton(btn_frame, 
                                text="Сброс", 
                                command=self.reset_simulation)
        reset_btn.pack(side="left", padx=5)

        # Слайдер жесткости
        self.k_var = ctk.DoubleVar(value=self.spring_params['k'])
        ctk.CTkLabel(self.control_frame, text="Жесткость (Н/м):").pack(pady=(10,0))
        self.k_slider = ctk.CTkSlider(self.control_frame, 
                                    variable=self.k_var,
                                    from_=50,
                                    to=5000,
                                    command=self.update_k_label)
        self.k_slider.pack(pady=5, padx=10)
        self.k_label = ctk.CTkLabel(self.control_frame, text=f"{self.k_var.get():.0f} Н/м")
        self.k_label.pack()

        # Слайдер демпфирования
        self.damp_var = ctk.DoubleVar(value=self.spring_params['damping'])
        ctk.CTkLabel(self.control_frame, text="Демпфирование:").pack(pady=(10,0))
        self.damp_slider = ctk.CTkSlider(self.control_frame, 
                                       variable=self.damp_var,
                                       from_=0, 
                                       to=1,
                                       command=self.update_damp_label)
        self.damp_slider.pack(pady=5, padx=10)
        self.damp_label = ctk.CTkLabel(self.control_frame, text=f"{self.damp_var.get():.1f}")
        self.damp_label.pack()
        
        # Поле для результатов
        result_frame = ctk.CTkFrame(self.control_frame)
        result_frame.pack(pady=(20,10), fill="x", padx=10)
        
        ctk.CTkLabel(result_frame, 
                    text="Результаты измерений:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        self.result_text = ctk.CTkTextbox(result_frame, height=100)
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        measure_btn = ctk.CTkButton(result_frame, 
                                   text="Измерить жесткость", 
                                   command=self.measure_stiffness)
        measure_btn.pack(pady=10)

    def check_canvas_size(self):
        """Проверяет готовность canvas и инициализирует симуляцию"""
        if self.canvas.winfo_width() > 1:
            self.canvas_width = self.canvas.winfo_width()
            self.canvas_height = self.canvas.winfo_height()
            self.canvas_ready = True
            self.setup_simulation()
        else:
            self.after(100, self.check_canvas_size)

    def on_canvas_resize(self, event):
        """Обработчик изменения размера canvas"""
        if event.width != self.canvas_width or event.height != self.canvas_height:
            self.canvas_width = event.width
            self.canvas_height = event.height
            if self.canvas_ready:
                self.update_spring_position()
                self.draw_simulation()

    def update_spring_position(self):
        """Обновляет позицию пружины при изменении размеров окна"""
        if self.spring:
            self.spring.set_anchor_x(self.canvas_width/2)

    def setup_simulation(self):
        """Инициализирует физическую симуляцию"""
        if not self.canvas_ready:
            return
        
        # Сбрасываем флаги и параметры
        self.measurements_ready = False
        self.last_extensions = []
        
        # Создаем пружину с грузом
        mass = self.load_var.get() / 1000  # г -> кг
        self.spring = SimpleSpring(
            k=self.spring_params['k'],
            rest_length=self.spring_params['rest_length'],
            mass=mass,
            damping=self.spring_params['damping']
        )
        
        # Центрируем пружину по ширине canvas
        self.spring.set_anchor_x(self.canvas_width/2)
        
        # Обновляем вывод параметров
        self.extension = 0
        self.extension_label.configure(text=f"Растяжение: {self.extension:.1f} мм")
        force = self.load_var.get() / 1000 * 9.81
        self.force_label.configure(text=f"Сила: {force:.2f} Н")
        
        # Отрисовываем начальное состояние
        self.draw_simulation()

    def toggle_simulation(self):
        """Запускает/останавливает симуляцию"""
        self.sim_running = not self.sim_running
        self.start_btn.configure(text="Пауза" if self.sim_running else "Старт")
        if self.sim_running:
            self.update_simulation()

    def update_simulation(self):
        """Обновляет состояние физической симуляции"""
        if not self.sim_running or not self.spring:
            return
            
        try:
            # Обновляем физику с малым шагом времени
            dt = 0.02  # 20 мс
            self.extension = self.spring.step(dt)
            
            # Обновляем отображение
            self.extension_label.configure(text=f"Растяжение: {self.extension:.1f} мм")
            force = self.load_var.get() / 1000 * 9.81
            self.force_label.configure(text=f"Сила: {force:.2f} Н")
            
            # Проверяем стабилизацию системы
            self.last_extensions.append(self.extension)
            if len(self.last_extensions) > 20:  # Храним последние 20 значений
                self.last_extensions.pop(0)
                
                # Если отклонение меньше 0.1 мм, считаем систему стабилизированной
                if len(self.last_extensions) == 20:
                    max_ext = max(self.last_extensions)
                    min_ext = min(self.last_extensions)
                    if max_ext - min_ext < 0.1 and not self.measurements_ready:
                        self.measurements_ready = True
            
            # Обновляем отрисовку
            self.draw_simulation()
            
            # Планируем следующее обновление
            self.after(20, self.update_simulation)
        except Exception as e:
            print(f"Ошибка в симуляции: {e}")
            import traceback
            traceback.print_exc()
            self.sim_running = False
            self.start_btn.configure(text="Старт")

    def draw_simulation(self):
        """Отрисовывает текущее состояние симуляции"""
        if not self.spring:
            return
            
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Рисуем лабораторный стенд
        self.draw_laboratory_stand(width, height)
        
        # Рисуем пружину
        anchor_pos = self.spring.anchor_pos
        weight_pos = self.spring.weight_pos
        self.draw_zigzag_spring(anchor_pos, weight_pos)
        
        # Рисуем груз
        self.draw_weight(weight_pos)
        
        # Рисуем линейку
        self.draw_ruler(weight_pos[0] + 50, anchor_pos[1], weight_pos[1])

    def draw_zigzag_spring(self, p1, p2):
        """Рисует пружину в виде зигзага между двумя точками"""
        # Параметры зигзага
        zigzag_width = 15
        segments = 12
        
        # Вычисляем направление
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        # Создаем точки зигзага
        points = []
        points.append((p1[0], p1[1]))
        
        for i in range(1, segments):
            t = i / segments
            # Основная линия
            x = p1[0] + dx * t
            y = p1[1] + dy * t
            
            # Добавляем зигзаг влево/вправо
            zigzag_factor = zigzag_width if i % 2 else -zigzag_width
            points.append((x + zigzag_factor, y))
        
        points.append((p2[0], p2[1]))
        
        # Рисуем зигзаг
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i][0], points[i][1], 
                                 points[i+1][0], points[i+1][1], 
                                 fill=self.colors['spring'], width=3)

    def draw_weight(self, pos):
        """Рисует груз по указанной позиции"""
        x, y = pos
        self.canvas.create_oval(x-20, y-20, x+20, y+20, 
                             fill=self.colors['weight'], outline="")
        # Надпись с массой
        self.canvas.create_text(x, y, text=f"{self.load_var.get()}г", 
                             fill=self.colors['text'], font=("Arial", 10, "bold"))

    def draw_laboratory_stand(self, width, height):
        """Рисует лабораторный стенд"""
        stand_width = 40
        stand_height = height - 100
        stand_x = width/2 - stand_width/2
        
        # Основание стойки
        self.canvas.create_rectangle(stand_x - 20, 100, 
                                  stand_x + stand_width + 20, 130, 
                                  fill=self.colors['stand'], outline="")
        
        # Вертикальная стойка
        self.canvas.create_rectangle(stand_x, 100, 
                                  stand_x + stand_width, stand_height, 
                                  fill=self.colors['stand'], outline="")
        
        # Кронштейн для крепления
        bracket_width = 80
        self.canvas.create_rectangle(stand_x + stand_width, 180, 
                                  stand_x + stand_width + bracket_width, 200, 
                                  fill=self.colors['stand'], outline="")
        
        # Точка крепления
        if self.spring:
            x, y = self.spring.anchor_pos
            self.canvas.create_oval(x-5, y-5, x+5, y+5, 
                                fill=self.colors['anchor'], outline="")

    def draw_ruler(self, x, y_start, y_end):
        """Рисует линейку для измерения растяжения"""
        # Проверяем корректность аргументов
        if not all(isinstance(val, (int, float)) for val in (x, y_start, y_end)):
            return
        
        # Убеждаемся, что конечная точка не меньше начальной
        if y_end < y_start:
            y_start, y_end = y_end, y_start
        
        # Основная линия линейки
        ruler_width = 5
        self.canvas.create_rectangle(x, y_start, x + ruler_width, y_end, 
                                 fill=self.colors['ruler'], outline="")
        
        # Деления
        tick_length = 10
        range_length = max(0, int(y_end - y_start))
        
        for i in range(0, range_length + 10, 10):
            y = y_start + i
            if y > y_end:
                break
                
            tick_len = tick_length if i % 50 == 0 else tick_length / 2
            self.canvas.create_line(x, y, x + tick_len, y, fill="black", width=1)
            
            # Подписи
            if i % 50 == 0:
                self.canvas.create_text(x + tick_len + 10, y, text=str(i), 
                                    anchor="w", fill=self.colors['text'])

    def change_spring_type(self, spring_type):
        """Меняет параметры в зависимости от типа пружины"""
        if spring_type == "Стальная":
            self.k_var.set(500)
            self.colors['spring'] = "#ff5d5d"
        elif spring_type == "Медная":
            self.k_var.set(300)
            self.colors['spring'] = "#f9c74f"
        elif spring_type == "Титановая":
            self.k_var.set(1200)
            self.colors['spring'] = "#4cc9f0"
            
        self.update_k_label(self.k_var.get())
        self.reset_simulation()

    def reset_simulation(self):
        """Сбрасывает симуляцию"""
        # Останавливаем симуляцию
        self.sim_running = False
        self.start_btn.configure(text="Старт")
        
        # Сбрасываем параметры
        self.extension = 0
        self.last_extensions = []
        self.measurements_ready = False
        
        # Обновляем отображение
        self.extension_label.configure(text="Растяжение: 0.0 мм")
        self.force_label.configure(text="Сила: 0.0 Н")
        
        # Пересоздаем симуляцию
        self.setup_simulation()

    def measure_stiffness(self):
        """Измеряет жесткость пружины"""
        # Проверяем готовность к измерениям
        if self.extension < 1.0:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", "Запустите симуляцию и дождитесь растяжения пружины!")
            return
            
        if not self.measurements_ready and self.sim_running:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", "Дождитесь стабилизации системы для точных измерений!")
            return
        
        # Рассчитываем параметры
        force = self.load_var.get() / 1000 * 9.81  # Сила в Н
        measured_k = force / (self.extension / 1000)  # Жесткость в Н/м
        
        # Формируем отчет
        self.result_text.delete("1.0", "end")
        result = f"Нагрузка: {self.load_var.get()} г\n"
        result += f"Сила тяжести: {force:.2f} Н\n"
        result += f"Растяжение: {self.extension:.1f} мм\n"
        result += f"Измеренная жесткость: {measured_k:.1f} Н/м\n"
        
        # Погрешность
        error = abs(measured_k - self.k_var.get()) / self.k_var.get() * 100
        result += f"Заданная жесткость: {self.k_var.get():.1f} Н/м\n"
        result += f"Погрешность: {error:.1f}%"
        
        self.result_text.insert("1.0", result)

    def update_load_label(self, value):
        """Обновляет отображение нагрузки"""
        self.load_label.configure(text=f"{int(value)} г")
        self.reset_simulation()

    def update_k_label(self, value):
        """Обновляет отображение жесткости"""
        self.k_label.configure(text=f"{float(value):.0f} Н/м")
        self.spring_params['k'] = float(value)
        self.reset_simulation()

    def update_damp_label(self, value):
        """Обновляет отображение демпфирования"""
        self.damp_label.configure(text=f"{float(value):.1f}")
        self.spring_params['damping'] = float(value)
        self.reset_simulation()

    def on_close(self):
        """Обработчик закрытия окна"""
        self.master.deiconify()
        self.destroy()
