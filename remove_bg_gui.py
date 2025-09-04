import tkinter as tk
from tkinter import filedialog, messagebox
from rembg import remove
from PIL import Image, ImageTk
from io import BytesIO


def load_image():
    global selected_path, display_image
    path = filedialog.askopenfilename(
        filetypes=[("Imagens", "*.png *.jpg *.jpeg"), ("Todos os arquivos", "*.*")]
    )
    if not path:
        return
    selected_path = path
    img = Image.open(path)
    img.thumbnail((400, 400))
    display_image = ImageTk.PhotoImage(img)
    image_label.config(image=display_image)

def remove_background():
    global processed_image, display_image
    if not selected_path:
        messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
        return
    with Image.open(selected_path) as img:
        result = remove(img)
    processed_image = Image.open(BytesIO(result))
    show = processed_image.copy()
    show.thumbnail((400, 400))
    display_image = ImageTk.PhotoImage(show)
    image_label.config(image=display_image)

def save_image():
    if processed_image is None:
        messagebox.showwarning("Aviso", "Remova o fundo antes de salvar.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
    if path:
        processed_image.save(path)
        messagebox.showinfo("Sucesso", f"Imagem salva em {path}")

root = tk.Tk()
root.title("Removedor de Fundo")

selected_path = None
processed_image = None

image_label = tk.Label(root)
image_label.pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

load_btn = tk.Button(btn_frame, text="Carregar imagem", command=load_image)
load_btn.grid(row=0, column=0, padx=5)

remove_btn = tk.Button(btn_frame, text="Remover fundo", command=remove_background)
remove_btn.grid(row=0, column=1, padx=5)

save_btn = tk.Button(btn_frame, text="Salvar imagem", command=save_image)
save_btn.grid(row=0, column=2, padx=5)

root.mainloop()
