import customtkinter as ctk
import tkinter
from Determ_accel import AccelerationWindow
from Determ_stiffness import StiffnessWindow

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Физические лабораторные работы")
        self.geometry("600x400")
        
        self.create_widgets()
    
    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(self.main_frame, text="Выберите лабораторную работу:", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        btn1 = ctk.CTkButton(self.main_frame, text="Определение ускорения тела при равноускоренном движении", 
                           command=lambda: AccelerationWindow(self))
        btn1.pack(pady=15, ipadx=20, ipady=10)
        
        btn2 = ctk.CTkButton(self.main_frame, text="Определение коэффициента жёсткости пружины", 
                           command=lambda: StiffnessWindow(self))
        btn2.pack(pady=15, ipadx=20, ipady=10)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()