import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
restoreimage =None
cover_image = None
hidden_text = ""
modified_image = None

def choose_cover_image():
    global cover_image
    file_path = filedialog.askopenfilename(title="Select Cover Image", filetypes=[("BMP files", "*.bmp")])
    if file_path:
        try:
            cover_image = Image.open(file_path)
            resized_image = cover_image.resize((800, 500))
            image_window = tk.Toplevel(root)
            image_window.title("Cover Image")
            image_window.geometry("800x500")
            cover_image_display = ImageTk.PhotoImage(resized_image)
            img_label = tk.Label(image_window, image=cover_image_display)
            img_label.image = cover_image_display
            img_label.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load the image: {str(e)}")


def embed_hidden_text(bits_count):
    global modified_image
    if cover_image is None or not hidden_text:
        messagebox.showerror("Error", "Please choose a cover image and provide a hidden text first!")
        return

    text_with_delimiter = hidden_text + '#'
    binary_text = ''.join(format(ord(char), '08b') for char in text_with_delimiter)

    output_image = cover_image.copy()
    pixel_data = list(output_image.getdata())

    new_pixel_data = []
    text_index = 0
    for pixel in pixel_data:
        if text_index < len(binary_text):
            new_pixel = list(pixel)
            for i in range(3):  # RGB channels
                if text_index < len(binary_text):
                    new_pixel[i] = (new_pixel[i] & ~(1 << (bits_count - 1))) | (int(binary_text[text_index]) << (bits_count - 1))
                    text_index += 1
            new_pixel_data.append(tuple(new_pixel))
        else:
            new_pixel_data.append(pixel)

    output_image.putdata(new_pixel_data)
    modified_image = output_image
    display_modified_image()

def display_modified_image():
    global modified_image
    if modified_image is None:
        messagebox.showerror("Error", "There is no modified image to display!")
        return

    image_window = tk.Toplevel(root)
    image_window.title("Modified Image")
    image_window.geometry("800x500")
    modified_image_display = ImageTk.PhotoImage(modified_image.resize((800, 500)))
    img_label = tk.Label(image_window, image=modified_image_display)
    img_label.image = modified_image_display
    img_label.pack()

    coverage_label = tk.Label(image_window, text="Coverage: Text Hidden in Image", font=('Arial', 12), bg='white', fg='black')
    coverage_label.pack()

def retrieve_hidden_text(bits_count):
    if restoreimage is None:
        messagebox.showerror("Error", "Please load an image with hidden text before attempting to retrieve it!")
        return

    retrieved_bits = []
    pixel_data = list(restoreimage.getdata())

    for pixel in pixel_data:
        for channel in pixel[:3]:
            retrieved_bits.append((channel >> (bits_count - 1)) & 1)

    binary_string = ''.join(str(bit) for bit in retrieved_bits)
    byte_segments = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    extracted_chars = []
    for byte in byte_segments:
        if len(byte) < 8:
            continue
        char = chr(int(byte, 2))
        if char == '#':
            break
        extracted_chars.append(char)

    recovered_text = ''.join(extracted_chars)
    messagebox.showinfo("Recovered Text", f"Recovered Hidden Text: {recovered_text}")


def loadrestoreimage():
    global restoreimage
    file_path = filedialog.askopenfilename(title="Select Cover Image", filetypes=[("BMP files", "*.bmp")])
    if file_path:
        try:
            restoreimage = Image.open(file_path)
            resized_image = restoreimage.resize((800, 500))
            image_window = tk.Toplevel(root)
            image_window.title("Cover Image")
            image_window.geometry("800x500")
            cover_image_display = ImageTk.PhotoImage(resized_image)
            img_label = tk.Label(image_window, image=cover_image_display)
            img_label.image = cover_image_display
            img_label.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load the image: {str(e)}")
def embed_text_wrapper():
    bits_count = get_selected_bits()
    if bits_count is not None:
        embed_hidden_text(bits_count)

def retrieve_text_wrapper():
    bits_count = get_selected_bits_restore()
    if bits_count is not None:
        retrieve_hidden_text(bits_count)

def get_selected_bits():
    if bits_selection.get() == 1:
        return 1
    elif bits_selection.get() == 2:
        return 2
    elif bits_selection.get() == 3:
        return 3
    else:
        messagebox.showerror("Error", "You need to select the number of bits.")
        return None

def get_selected_bits_restore():
    if bits_selection_restore.get() == 1:
        return 1
    elif bits_selection_restore.get() == 2:
        return 2
    elif bits_selection_restore.get() == 3:
        return 3
    else:
        messagebox.showerror("Error", "You need to select the number of bits.")
        return None

def reset_all():
    global cover_image, hidden_text, modified_image
    cover_image = None
    hidden_text = ""
    modified_image = None
    cover_label.config(text="Cover")
    hidden_label.config(text="Hidden")
    bits_selection.set(0)
    bits_selection_restore.set(0)

    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()

def save_modified_image():
    if modified_image is None:
        messagebox.showerror("Error", "No modified image to save!")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".bmp", filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")])
    if file_path:
        try:
            modified_image.save(file_path)
            messagebox.showinfo("Success", "Image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save the image: {str(e)}")

def selecttext():
    global hidden_text
    hidden_text_file = filedialog.askopenfilename(title="Select Secret Text", filetypes=[("Text files", "*.txt")])
    if hidden_text_file:
        try:
            with open(hidden_text_file, 'r') as file:
                hidden_text = file.read()
            hidden_label.config(text=f"The Secret Text:\n{hidden_text}")
        except Exception as e:
            messagebox.showerror("Error", f"Theres an error to read file: {str(e)}")

root = tk.Tk()
root.title("Embed Hidden Text")
root.geometry("800x500")

bg_color = "#D3D3D3"  # Light black color
label_bg_color = "#E6E6FA"  # Light purple for labels
button_bg_color = "#6A5ACD"  # SlateBlue for buttons
button_fg_color = "white"

root.configure(bg=bg_color)

cover_label = tk.Label(root, text="Cover", bg=label_bg_color, width=35, height=5, font=('Arial', 14, 'bold'))
hidden_label = tk.Label(root, text="Hidden", bg=label_bg_color, width=35, height=5, font=('Arial', 14, 'bold'))
result_label = tk.Label(root, text="Result", bg=label_bg_color, width=35, height=5, font=('Arial', 14, 'bold'))

# Swap rows and columns
cover_label.grid(row=0, column=0, padx=30, pady=15)
hidden_label.grid(row=0, column=1, padx=30, pady=15)
result_label.grid(row=0, column=2, padx=30, pady=15)

select_secret_button = tk.Button(root, text="Set Secret Text", command=selecttext, width=20, height=2, bg=button_bg_color, fg=button_fg_color, font=('Arial', 12))
select_image_button = tk.Button(root, text="Select Cover Image", command=choose_cover_image, width=15, height=1, bg=button_bg_color, fg=button_fg_color, font=('Arial', 12))


bits_label = tk.Label(root, text="Select Number of Bits:", bg=label_bg_color, font=('Arial', 12))
bits_selection = tk.IntVar()
bit_option1 = tk.Radiobutton(root, text="1 Bit", variable=bits_selection, value=1, bg=bg_color, font=('Arial', 12))
bit_option2 = tk.Radiobutton(root, text="2 Bits", variable=bits_selection, value=2, bg=bg_color, font=('Arial', 12))
bit_option3 = tk.Radiobutton(root, text="3 Bits", variable=bits_selection, value=3, bg=bg_color, font=('Arial', 12))


bits_label_restore = tk.Label(root, text="Select Number of Bits:", bg=label_bg_color, font=('Arial', 12))
bits_selection_restore = tk.IntVar()
bit_option1_restore  = tk.Radiobutton(root, text="1 Bit", variable=bits_selection_restore, value=1, bg=bg_color, font=('Arial', 12))
bit_option2_restore  = tk.Radiobutton(root, text="2 Bits", variable=bits_selection_restore, value=2, bg=bg_color, font=('Arial', 12))
bit_option3_restore  = tk.Radiobutton(root, text="3 Bits", variable=bits_selection_restore, value=3, bg=bg_color, font=('Arial', 12))

# Arrange buttons in a single column
button_frame = tk.Frame(root, bg=bg_color)
button_frame.grid(row=5, column=1, pady=15)

embed_text_button = tk.Button(button_frame, text="Hide Text", command=embed_text_wrapper, width=15, height=1, bg=button_bg_color, fg=button_fg_color, font=('Arial', 12))
save_button = tk.Button(button_frame, text="Save Modified Image", command=save_modified_image, width=15, height=1, bg=button_bg_color, fg=button_fg_color, font=('Arial', 12))
reset_button = tk.Button(button_frame, text="Clear All", command=reset_all, width=15, height=1, bg=button_bg_color, fg=button_fg_color, font=('Arial', 12))
retrieve_button = tk.Button(root, text="Restore Text", command=retrieve_text_wrapper, width=15, height=1, bg=button_bg_color, fg=button_fg_color, font=('Arial', 12))
loadrestoreimg = tk.Button(root, text="Load Image to restore ", command=loadrestoreimage, width=18, height=1, bg=button_bg_color, fg=button_fg_color, font=('Arial', 12))

# Add buttons to the frame
embed_text_button.pack(pady=5)
reset_button.pack(pady=5)
save_button.pack(pady=5)  

# Arrange other widgets
select_image_button.grid(row=1, column=0, padx=10, pady=15)
select_secret_button.grid(row=1, column=1, padx=10, pady=15)

bits_label.grid(row=3, column=0, padx=30, pady=5)
bit_option1.grid(row=4, column=0, padx=30, pady=5)
bit_option2.grid(row=4, column=1, padx=30, pady=5)
bit_option3.grid(row=4, column=2, padx=30, pady=5)
retrieve_button.grid(row=6, column=0, padx=10, pady=15)
loadrestoreimg.grid(row=6, column=1, padx=10, pady=15)
bits_label_restore.grid(row=7, column=2, padx=30, pady=5)
bit_option1_restore.grid(row=8, column=0, padx=30, pady=5)
bit_option2_restore.grid(row=8, column=1, padx=30, pady=5)
bit_option3_restore.grid(row=8, column=2, padx=30, pady=5)
root.mainloop()
