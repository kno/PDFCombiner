import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PyPDF2 import PdfWriter, PdfReader
from pdf_utils import AdvancedPDFCombiner, TextProcessor

class PDFCombinerGUI(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("PDF Combiner Pro - GUI Edition")
        self.geometry("900x500")
        self.resizable(False, False)
        self.selected_files = []
        # Variables para el drag & drop
        self.drag_start_index = None
        self.drag_data = None
        self._setup_ui()

    def _setup_ui(self):
        # Layout: 3 columns (left: file browser, center: add button, right: selected files)
        self.columnconfigure(0, weight=1, minsize=250)
        self.columnconfigure(1, weight=0, minsize=100)
        self.columnconfigure(2, weight=1, minsize=250)
        self.rowconfigure(0, weight=1)

        # File browser (left)
        frame_left = tb.Frame(self)
        frame_left.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        lbl_files = tb.Label(frame_left, text="Navegador de archivos", bootstyle=PRIMARY)
        lbl_files.pack(anchor="w")
        self.file_listbox = tk.Listbox(frame_left, selectmode=tk.MULTIPLE, height=22)
        self.file_listbox.pack(fill="both", expand=True, pady=5)
        self._populate_file_list()
        self.file_listbox.bind('<Up>', self._on_file_listbox_up)
        self.file_listbox.bind('<Down>', self._on_file_listbox_down)
        self.file_listbox.bind('<Return>', self._on_file_listbox_enter)
        self.file_listbox.bind('<Tab>', self._on_file_listbox_tab)
        self.file_listbox.bind('<Double-Button-1>', self._on_file_listbox_double_click)
        self.file_listbox.focus_set()

        # Center controls
        frame_center = tb.Frame(self)
        frame_center.grid(row=0, column=1, sticky="ns", pady=10)
        btn_add = tb.Button(frame_center, text="Añadir →", bootstyle=SUCCESS, command=self.add_selected_files)
        btn_add.pack(pady=(100,10))

        # Checkbox para índice
        self.create_index_var = tk.BooleanVar(value=True)
        chk_index = tb.Checkbutton(frame_center, text="Crear índice interactivo",
                                  variable=self.create_index_var, bootstyle=INFO)
        chk_index.pack(pady=5)

        btn_combine = tb.Button(frame_center, text="Combinar PDFs", bootstyle=INFO, command=self.combine_pdfs)
        btn_combine.pack(pady=10)

        # Selected files (right)
        frame_right = tb.Frame(self)
        frame_right.grid(row=0, column=2, sticky="nsew", padx=(5,10), pady=10)
        lbl_selected = tb.Label(frame_right, text="Ficheros seleccionados", bootstyle=PRIMARY)
        lbl_selected.pack(anchor="w")
        self.selected_listbox = tk.Listbox(frame_right, selectmode=tk.SINGLE, height=22)
        self.selected_listbox.pack(fill="both", expand=True, pady=5)
        self.selected_listbox.bind('<Up>', self._on_selected_listbox_up)
        self.selected_listbox.bind('<Down>', self._on_selected_listbox_down)
        self.selected_listbox.bind('<Shift-Up>', self._on_selected_listbox_shift_up)
        self.selected_listbox.bind('<Shift-Down>', self._on_selected_listbox_shift_down)
        self.selected_listbox.bind('<Shift-Tab>', self._on_selected_listbox_shift_tab)
        self.selected_listbox.bind('<Button-1>', self._on_selected_listbox_click)
        self.selected_listbox.bind('<B1-Motion>', self._on_selected_listbox_drag)
        self.selected_listbox.bind('<ButtonRelease-1>', self._on_selected_listbox_drop)
        # Reorder buttons
        btn_up = tb.Button(frame_right, text="↑ Subir", bootstyle=SECONDARY, command=self.move_up)
        btn_up.pack(side="left", padx=5, pady=5)
        btn_down = tb.Button(frame_right, text="↓ Bajar", bootstyle=SECONDARY, command=self.move_down)
        btn_down.pack(side="left", padx=5, pady=5)
        btn_remove = tb.Button(frame_right, text="Eliminar", bootstyle=DANGER, command=self.remove_selected)
        btn_remove.pack(side="right", padx=5, pady=5)

    def _on_file_listbox_enter(self, event):
        cur = self.file_listbox.curselection()
        if cur:
            idx = cur[0]
            if idx < len(self.file_tooltips):
                f = self.file_tooltips[idx]
                if f not in self.selected_files:
                    self.selected_files.append(f)
                    self._refresh_selected_listbox()
        return "break"

    def _on_file_listbox_up(self, event):
        cur = self.file_listbox.curselection()
        if cur:
            idx = cur[0]
            new_idx = max(0, idx - 1)
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(new_idx)
            self.file_listbox.see(new_idx)
        return "break"

    def _on_file_listbox_down(self, event):
        cur = self.file_listbox.curselection()
        if cur:
            idx = cur[0]
            new_idx = min(self.file_listbox.size()-1, idx + 1)
            if new_idx < self.file_listbox.size():
                self.file_listbox.selection_clear(0, tk.END)
                self.file_listbox.selection_set(new_idx)
                self.file_listbox.see(new_idx)
        return "break"

    def _on_file_listbox_tab(self, event):
        # Mover el foco a la lista de la derecha
        self.selected_listbox.focus_set()
        if self.selected_listbox.size() > 0:
            self.selected_listbox.selection_set(0)  # Seleccionar el primer archivo
        return "break"

    def _on_file_listbox_double_click(self, event):
        # Añadir archivo con doble click
        cur = self.file_listbox.curselection()
        if cur:
            idx = cur[0]
            if idx < len(self.file_tooltips):
                f = self.file_tooltips[idx]
                if f not in self.selected_files:
                    self.selected_files.append(f)
                    self._refresh_selected_listbox()
        return "break"

    def _on_selected_listbox_up(self, event):
        cur = self.selected_listbox.curselection()
        if cur:
            idx = cur[0]
            new_idx = max(0, idx - 1)
            self.selected_listbox.selection_clear(0, tk.END)
            self.selected_listbox.selection_set(new_idx)
            self.selected_listbox.see(new_idx)
        return "break"

    def _on_selected_listbox_down(self, event):
        cur = self.selected_listbox.curselection()
        if cur:
            idx = cur[0]
            new_idx = min(self.selected_listbox.size()-1, idx + 1)
            if new_idx < self.selected_listbox.size():
                self.selected_listbox.selection_clear(0, tk.END)
                self.selected_listbox.selection_set(new_idx)
                self.selected_listbox.see(new_idx)
        return "break"

    def _on_selected_listbox_shift_up(self, event):
        cur = self.selected_listbox.curselection()
        if cur:
            idx = cur[0]
            if idx > 0:
                # Reordenar en la lista interna
                self.selected_files[idx-1], self.selected_files[idx] = self.selected_files[idx], self.selected_files[idx-1]
                self._refresh_selected_listbox()
                # Mantener selección en el nuevo índice
                self.selected_listbox.selection_set(idx - 1)
                self.selected_listbox.see(idx - 1)
        return "break"

    def _on_selected_listbox_shift_down(self, event):
        cur = self.selected_listbox.curselection()
        if cur:
            idx = cur[0]
            if idx < len(self.selected_files) - 1:
                # Reordenar en la lista interna
                self.selected_files[idx+1], self.selected_files[idx] = self.selected_files[idx], self.selected_files[idx+1]
                self._refresh_selected_listbox()
                # Mantener selección en el nuevo índice
                self.selected_listbox.selection_set(idx + 1)
                self.selected_listbox.see(idx + 1)
        return "break"

    def _on_selected_listbox_shift_tab(self, event):
        # Mover el foco a la lista de la izquierda
        self.file_listbox.focus_set()
        if self.file_listbox.size() > 0:
            self.file_listbox.selection_set(0)  # Seleccionar el primer archivo
        return "break"

    def _on_selected_listbox_click(self, event):
        # Iniciar drag & drop en la lista de seleccionados
        index = self.selected_listbox.nearest(event.y)
        if index >= 0 and index < self.selected_listbox.size():
            self.drag_start_index = index
            self.drag_data = self.selected_files[index]
            self.selected_listbox.selection_clear(0, tk.END)
            self.selected_listbox.selection_set(index)

    def _on_selected_listbox_drag(self, event):
        # Durante el arrastre, mostrar la posición donde se soltaría
        if self.drag_start_index is not None:
            index = self.selected_listbox.nearest(event.y)
            if index >= 0 and index < self.selected_listbox.size():
                self.selected_listbox.selection_clear(0, tk.END)
                self.selected_listbox.selection_set(index)

    def _on_selected_listbox_drop(self, event):
        # Soltar y reordenar en la lista de seleccionados
        if self.drag_start_index is not None:
            drop_index = self.selected_listbox.nearest(event.y)
            if drop_index >= 0 and drop_index < len(self.selected_files) and drop_index != self.drag_start_index:
                # Reordenar los elementos en la lista interna
                item = self.selected_files.pop(self.drag_start_index)
                self.selected_files.insert(drop_index, item)

                # Actualizar la interfaz
                self._refresh_selected_listbox()
                self.selected_listbox.selection_set(drop_index)

        # Limpiar variables de drag & drop
        self.drag_start_index = None
        self.drag_data = None

    def _populate_file_list(self):
        self.file_listbox.delete(0, tk.END)
        pdfs = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
        self.file_tooltips = {}  # Diccionario para mapear índices a nombres de archivos

        for i, f in enumerate(sorted(pdfs)):
            # Insertar solo el título extraído
            title = TextProcessor.extract_title(f)
            self.file_listbox.insert(tk.END, title)
            # Guardar el mapeo de índice a nombre de archivo para el tooltip
            self.file_tooltips[i] = f

        # Crear tooltip para la lista de archivos
        self._create_file_tooltip()

    def _create_file_tooltip(self):
        def show_tooltip(event):
            # Obtener el índice del elemento bajo el cursor
            index = self.file_listbox.nearest(event.y)
            if 0 <= index < len(self.file_tooltips):
                filename = self.file_tooltips[index]
                # Crear tooltip temporal
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                label = tk.Label(tooltip, text=f"📄 {filename}",
                               background="lightyellow", relief="solid", borderwidth=1,
                               font=("Arial", 9))
                label.pack()

                # Guardar referencia al tooltip
                self.current_tooltip = tooltip

                # Programar destrucción del tooltip después de 3 segundos
                self.after(3000, lambda: tooltip.destroy() if tooltip.winfo_exists() else None)

        def hide_tooltip(event):
            if hasattr(self, 'current_tooltip') and self.current_tooltip.winfo_exists():
                self.current_tooltip.destroy()

        # Vincular eventos de mouse
        self.file_listbox.bind('<Motion>', show_tooltip)
        self.file_listbox.bind('<Leave>', hide_tooltip)

    def add_selected_files(self):
        selected_indices = self.file_listbox.curselection()
        for idx in selected_indices:
            if idx < len(self.file_tooltips):
                filename = self.file_tooltips[idx]
                if filename not in self.selected_files:
                    self.selected_files.append(filename)
                    self._refresh_selected_listbox()

    def remove_selected(self):
        idx = self.selected_listbox.curselection()
        if idx:
            selected_idx = idx[0]
            if selected_idx < len(self.selected_files):
                self.selected_files.pop(selected_idx)
                self._refresh_selected_listbox()

    def move_up(self):
        idx = self.selected_listbox.curselection()
        if idx:
            selected_idx = idx[0]
            if selected_idx > 0:
                self.selected_files[selected_idx-1], self.selected_files[selected_idx] = self.selected_files[selected_idx], self.selected_files[selected_idx-1]
                self._refresh_selected_listbox()
                self.selected_listbox.selection_set(selected_idx - 1)

    def move_down(self):
        idx = self.selected_listbox.curselection()
        if idx:
            selected_idx = idx[0]
            if selected_idx < len(self.selected_files) - 1:
                self.selected_files[selected_idx+1], self.selected_files[selected_idx] = self.selected_files[selected_idx], self.selected_files[selected_idx+1]
                self._refresh_selected_listbox()
                self.selected_listbox.selection_set(selected_idx + 1)

    def _refresh_selected_listbox(self):
        self.selected_listbox.delete(0, tk.END)
        self.selected_tooltips = {}  # Diccionario para mapear índices a nombres de archivos

        for i, f in enumerate(self.selected_files):
            # Insertar solo el título extraído
            title = TextProcessor.extract_title(f)
            self.selected_listbox.insert(tk.END, title)
            # Guardar el mapeo de índice a nombre de archivo para el tooltip
            self.selected_tooltips[i] = f

        # Crear tooltip para la lista de seleccionados si no existe
        if not hasattr(self, 'selected_tooltip_created'):
            self._create_selected_tooltip()
            self.selected_tooltip_created = True

    def _create_selected_tooltip(self):
        def show_selected_tooltip(event):
            # Obtener el índice del elemento bajo el cursor
            index = self.selected_listbox.nearest(event.y)
            if 0 <= index < len(self.selected_tooltips):
                filename = self.selected_tooltips[index]
                # Crear tooltip temporal
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                label = tk.Label(tooltip, text=f"📄 {filename}",
                               background="lightyellow", relief="solid", borderwidth=1,
                               font=("Arial", 9))
                label.pack()

                # Guardar referencia al tooltip
                self.current_selected_tooltip = tooltip

                # Programar destrucción del tooltip después de 3 segundos
                self.after(3000, lambda: tooltip.destroy() if tooltip.winfo_exists() else None)

        def hide_selected_tooltip(event):
            if hasattr(self, 'current_selected_tooltip') and self.current_selected_tooltip.winfo_exists():
                self.current_selected_tooltip.destroy()

        # Vincular eventos de mouse
        self.selected_listbox.bind('<Motion>', show_selected_tooltip)
        self.selected_listbox.bind('<Leave>', hide_selected_tooltip)

    def combine_pdfs(self):
        if not self.selected_files:
            messagebox.showwarning("Advertencia", "No hay ficheros seleccionados.")
            return
        output = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Guardar PDF combinado")
        if not output:
            return

        try:
            # Generar títulos automáticamente basados en los nombres de archivo
            titles = [TextProcessor.extract_title(f) for f in self.selected_files]

            # Crear combinador avanzado
            combiner = AdvancedPDFCombiner(self.selected_files, titles)

            # Combinar con o sin índice según la opción seleccionada
            if self.create_index_var.get():
                final_file = combiner.combine_with_index(output)
                messagebox.showinfo("Éxito", f"PDF combinado con índice interactivo guardado como:\n{final_file}")
            else:
                final_file = combiner.combine_simple(output)
                messagebox.showinfo("Éxito", f"PDF combinado guardado como:\n{final_file}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo combinar los PDFs:\n{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    app = PDFCombinerGUI()
    app.mainloop()
