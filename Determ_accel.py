import customtkinter as ctk

class AccelerationWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Определение ускорения")
        self.geometry("900x600")
        self.minsize(800, 500)
        self.master = master
        
        # Скрыть главное окно при открытии
        self.master.withdraw()
        
        # Настройка пропорций окна
        self.grid_columnconfigure(0, weight=2)  # 2/3 для установки
        self.grid_columnconfigure(1, weight=1)  # 1/3 для управления
        self.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()
    
    def on_close(self):
        # Восстановить главное окно
        self.master.deiconify()
        self.destroy()
    
    def create_widgets(self):
        # Левая часть - установка (2/3 экрана)
        self.simulation_frame = ctk.CTkFrame(self, corner_radius=10)
        self.simulation_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Правая часть - управление (1/3 экрана)
        self.control_frame = ctk.CTkFrame(self, corner_radius=10)
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Заголовок установки
        ctk.CTkLabel(self.simulation_frame, text="Экспериментальная установка", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        # Элементы управления
        ctk.CTkLabel(self.control_frame, text="Параметры эксперимента:", 
                    font=ctk.CTkFont(size=14)).pack(pady=10, padx=5)
        
        # Поле для массы
        self.mass_var = ctk.DoubleVar(value=1.0)
        ctk.CTkLabel(self.control_frame, text="Масса груза (кг):").pack(pady=(10,0))
        mass_entry = ctk.CTkEntry(self.control_frame, textvariable=self.mass_var)
        mass_entry.pack(pady=5, padx=10)
        
        # Слайдер для угла
        self.angle_var = ctk.IntVar(value=30)
        ctk.CTkLabel(self.control_frame, text="Угол наклона (°):").pack(pady=(10,0))
        angle_slider = ctk.CTkSlider(self.control_frame, variable=self.angle_var,
                                   from_=0, to=90, number_of_steps=90)
        angle_slider.pack(pady=5, padx=10)
        
        # Кнопка старта
        self.start_btn = ctk.CTkButton(self.control_frame, text="Начать эксперимент",
                                     fg_color="green", hover_color="darkgreen")
        self.start_btn.pack(pady=20, padx=10)
        
        # Виджеты установки (можно добавить графики/анимацию)
        self.canvas = ctk.CTkCanvas(self.simulation_frame, bg="#2b2b2b")
        self.canvas.pack(expand=True, fill="both", padx=20, pady=20)