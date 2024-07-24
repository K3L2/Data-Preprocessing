import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import os


class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        self.upload_button = tk.Button(root, text="Select Image Folder", command=self.select_image_folder)
        self.upload_button.pack()

        self.save_location_button = tk.Button(root, text="Set Save Location", command=self.set_save_location)
        self.save_location_button.pack()

        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)

        self.image = None
        self.photo = None
        self.display_image = None
        self.resize_ratio = 1
        self.save_directory = None
        self.image_counter = 1
        self.image_files = []
        self.current_image_index = -1

    def select_image_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            self.image_files.sort()  # Sort files for consistent order
            if self.image_files:
                self.current_image_index = 0
                self.load_image(self.image_files[self.current_image_index])
            else:
                messagebox.showerror("Error", "No images found in the selected folder.")

    def set_save_location(self):
        self.save_directory = filedialog.askdirectory()
        if self.save_directory:
            print(f"Save directory set to: {self.save_directory}")

    def load_image(self, file_path):
        self.image = cv2.imread(file_path)
        self.display_image = self.resize_image_to_fit(self.image)
        self.photo = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(self.display_image, cv2.COLOR_BGR2RGB)))
        self.canvas.config(width=self.photo.width(), height=self.photo.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def resize_image_to_fit(self, image):
        # screen_width = self.root.winfo_screenwidth()
        # screen_height = self.root.winfo_screenheight()

        screen_width = 600
        screen_height = 600

        img_height, img_width = image.shape[:2]
        ratio = min(screen_width / img_width, screen_height / img_height)

        self.resize_ratio = ratio
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return resized_image

    def on_click(self, event):
        if self.image is not None and self.save_directory is not None:
            orig_x = int(event.x / self.resize_ratio)
            orig_y = int(event.y / self.resize_ratio)
            print(f"Clicked at: ({orig_x}, {orig_y}) in original image coordinates")

            left = max(0, orig_x - 128)
            top = max(0, orig_y - 128)
            right = min(self.image.shape[1], orig_x + 128)
            bottom = min(self.image.shape[0], orig_y + 128)

            cropped_image = self.image[top:bottom, left:right]
            cropped_image_resized = cv2.resize(cropped_image, (256, 256), interpolation=cv2.INTER_AREA)

            save_path = os.path.join(self.save_directory, f"crop_img_{self.image_counter:03d}.png")
            cv2.imwrite(save_path, cropped_image_resized)
            print(f"Cropped image saved as {save_path}")
            self.image_counter += 1

    def prev_image(self, event):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image(self.image_files[self.current_image_index])
        else:
            messagebox.showinfo("Info", "This is the first image.")

    def next_image(self, event):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image(self.image_files[self.current_image_index])
        else:
            messagebox.showinfo("Info", "This is the last image.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
