"""
SQL Table Alteration Automation GUI
------------------------------------
Built with customtkinter.

Install dependency first:
    pip install customtkinter

Features:
- Table name input
- Issue number input
- ADD / DROP radio button choice
- Dynamic list of columns to add/drop
    -> when "ADD" is selected, each column also gets a data type field
    -> when "DROP" is selected, only the column name is needed
- Options popup: output path + "Include Spool" Yes/No
- RUN button collects everything into ready-to-use Python variables
  (table_name, issue_number, action, columns, output_path, include_spool)
"""

import os
from tkinter import filedialog

import customtkinter as ctk
from service import calculate_n_write

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Data types offered in the dropdown, as required by the receiving service.
# Fixed-length types map straight to their required length (not editable).
# Variable-length types (None) let the user type in the length themselves.
DATA_TYPES = {
    "TEXT": None,
    "DATE": 8,
    "TIMESTAMP": 20,
    "NUMBER": None,
}


class ColumnRow(ctk.CTkFrame):
    """A single row representing one column to ADD or DROP."""

    def __init__(self, master, action_getter, on_remove, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.action_getter = action_getter  # callable returning current "ADD"/"DROP"
        self.on_remove = on_remove

        self.col_name_entry = ctk.CTkEntry(self, placeholder_text="Column name", width=150)
        self.col_name_entry.grid(row=0, column=0, padx=(0, 8), pady=4)

        self.dtype_combo = ctk.CTkComboBox(
            self, values=list(DATA_TYPES.keys()), width=130, command=self._on_dtype_change
        )
        self.dtype_combo.set(list(DATA_TYPES.keys())[0])
        self.dtype_combo.grid(row=0, column=1, padx=(0, 8), pady=4)

        # Length field: editable for variable-length types (TEXT, NUMBER),
        # read-only / auto-filled for fixed-length types (DATE, TIMESTAMP).
        self.length_entry = ctk.CTkEntry(self, placeholder_text="Length", width=70)
        self.length_entry.grid(row=0, column=2, padx=(0, 8), pady=4)

        self.remove_btn = ctk.CTkButton(
            self, text="✕", width=28, fg_color="#8B2020", hover_color="#A82A2A",
            command=self._remove
        )
        self.remove_btn.grid(row=0, column=3, padx=(0, 4), pady=4)

        self._on_dtype_change(self.dtype_combo.get())
        self.refresh_visibility()

    def _remove(self):
        self.on_remove(self)

    def _on_dtype_change(self, selected_type):
        """Update the length field based on the chosen data type."""
        fixed_length = DATA_TYPES.get(selected_type)
        if fixed_length is not None:
            # Fixed-length type (DATE, TIMESTAMP): auto-fill and lock it.
            self.length_entry.configure(state="normal")
            self.length_entry.delete(0, "end")
            self.length_entry.insert(0, str(fixed_length))
            self.length_entry.configure(state="disabled")
        else:
            # Variable-length type (TEXT, NUMBER): let the user type it in.
            self.length_entry.configure(state="normal")
            self.length_entry.delete(0, "end")

    def refresh_visibility(self):
        """Show/hide the data type + length fields depending on current action (ADD/DROP)."""
        if self.action_getter() == "ADD":
            self.dtype_combo.grid()
            self.length_entry.grid()
        else:
            self.dtype_combo.grid_remove()
            self.length_entry.grid_remove()

    def get_data(self):
        col_name = self.col_name_entry.get().strip()
        if not col_name:
            return None

        if self.action_getter() != "ADD":
            return {"column_name": col_name}

        data_type = self.dtype_combo.get().strip()
        length_str = self.length_entry.get().strip()

        if not length_str:
            raise ValueError(f"Column '{col_name}': length is required.")
        if "," in length_str:
            raise ValueError(f"Column '{col_name}': Please dont use ',' for decimal precision. Use '.' instead.")
        if not length_str.isdigit():
            if data_type != "NUMBER":
                raise ValueError(f"Column '{col_name}': length must be a whole number.")

            _int, _dec = length_str.split(".")
            if int(_dec) >= int(_int):
                raise ValueError(f"Column '{col_name}': invalid SQL decimal syntax! Decimal number ({_dec}) should be smaller than the integer ({_int}) .")

            length_str = float(length_str)
        else:
            length_str = int(length_str)

        return {
            "column_name": col_name,
            "data_type": data_type,
            "length": length_str,
        }


class OptionsPopup(ctk.CTkToplevel):
    """
    Popup for run-level options:
      - output path (folder the generated .sql files get written to)
      - "Include Spool" Yes/No

    on_done is called with (output_path: str, include_spool: bool) once
    the user clicks "Done", after which the popup closes itself.
    """

    def __init__(self, master, current_output_path, current_include_spool, on_done):
        super().__init__(master)
        self.on_done = on_done

        self.title("Options")
        self.geometry("460x220")
        self.resizable(False, False)

        # Keep it modal-ish: stays on top of the main window, grabs input focus
        self.transient(master)
        self.grab_set()

        self.output_path_var = ctk.StringVar(value=current_output_path)
        self.include_spool_var = ctk.StringVar(
            value="Yes" if current_include_spool else "No"
        )

        # ---------- Output path ----------
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkButton(
            path_frame, text="Select output path", command=self._select_output_path
        ).pack(side="left")

        self.path_label = ctk.CTkLabel(
            path_frame, textvariable=self.output_path_var,
            wraplength=280, justify="left", anchor="w"
        )
        self.path_label.pack(side="left", padx=(10, 0), fill="x", expand=True)

        # ---------- Include Spool ----------
        spool_frame = ctk.CTkFrame(self, fg_color="transparent")
        spool_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(spool_frame, text="Include Spool:").pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(
            spool_frame, text="Yes", variable=self.include_spool_var, value="Yes"
        ).pack(side="left", padx=10)
        ctk.CTkRadioButton(
            spool_frame, text="No", variable=self.include_spool_var, value="No"
        ).pack(side="left", padx=10)

        # ---------- Done ----------
        ctk.CTkButton(
            self, text="Done", height=38, font=ctk.CTkFont(weight="bold"),
            command=self._done
        ).pack(fill="x", padx=20, pady=(20, 20))

    def _select_output_path(self):
        selected = filedialog.askdirectory(
            title="Select output path", initialdir=self.output_path_var.get() or os.getcwd()
        )
        if selected:  # user might cancel, leaving it empty - keep the previous value in that case
            self.output_path_var.set(selected)

    def _done(self):
        output_path = self.output_path_var.get().strip()
        include_spool = self.include_spool_var.get() == "Yes"
        self.on_done(output_path, include_spool)
        self.destroy()


class SQLAlterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SQL Table Alteration Automation")
        self.geometry("560x800")
        self.minsize(520, 500)

        self.column_rows = []

        # Options, defaulted until the user opens the popup and hits Done
        self.output_path = os.getcwd()
        self.include_spool = True

        # ---------- Header: title + Options button ----------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))

        ctk.CTkLabel(
            header_frame, text="SQL Table Alteration Automation",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header_frame, text="Options", width=90, command=self.open_options
        ).pack(side="right")

        # ---------- Header info fields ----------
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=20, pady=(10, 10))

        ctk.CTkLabel(info_frame, text="Table Name:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.table_name_entry = ctk.CTkEntry(info_frame, placeholder_text="e.g. dbo.CUSTOMERS", width=280)
        self.table_name_entry.grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkLabel(info_frame, text="Issue Number:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.issue_number_entry = ctk.CTkEntry(info_frame, placeholder_text="e.g. JIRA-1234", width=280)
        self.issue_number_entry.grid(row=1, column=1, padx=10, pady=8)

        # ---------- Action radio buttons ----------
        action_frame = ctk.CTkFrame(self)
        action_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(action_frame, text="Action:").pack(side="left", padx=(10, 15), pady=10)

        self.action_var = ctk.StringVar(value="ADD")
        ctk.CTkRadioButton(
            action_frame, text="ADD", variable=self.action_var, value="ADD",
            command=self._on_action_change
        ).pack(side="left", padx=10)
        ctk.CTkRadioButton(
            action_frame, text="DROP", variable=self.action_var, value="DROP",
            command=self._on_action_change
        ).pack(side="left", padx=10)

        # ---------- Columns section ----------
        columns_header = ctk.CTkFrame(self, fg_color="transparent")
        columns_header.pack(fill="x", padx=20, pady=(10, 0))
        ctk.CTkLabel(columns_header, text="Columns:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(
            columns_header, text="+ Add Column", width=120, command=self.add_column_row
        ).pack(side="right")

        # Scrollable frame to hold dynamic column rows
        self.columns_container = ctk.CTkScrollableFrame(self, height=250)
        self.columns_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Start with one column row by default
        self.add_column_row()

        # ---------- RUN button ----------
        self.run_btn = ctk.CTkButton(
            self, text="RUN", height=42, font=ctk.CTkFont(size=16, weight="bold"),
            command=self.run
        )
        self.run_btn.pack(fill="x", padx=20, pady=(5, 15))

        # ---------- Output / log box ----------
        self.output_box = ctk.CTkTextbox(self, height=140)
        self.output_box.pack(fill="both", padx=20, pady=(0, 20))

    # ------------------------------------------------------------------
    def _current_action(self):
        return self.action_var.get()

    def _on_action_change(self):
        for row in self.column_rows:
            row.refresh_visibility()

    def add_column_row(self):
        row = ColumnRow(
            self.columns_container,
            action_getter=self._current_action,
            on_remove=self.remove_column_row,
        )
        row.pack(fill="x", pady=2)
        self.column_rows.append(row)

    def remove_column_row(self, row):
        # Always keep at least one row
        if len(self.column_rows) <= 1:
            return
        row.destroy()
        self.column_rows.remove(row)

    # ------------------------------------------------------------------
    def open_options(self):
        OptionsPopup(
            self,
            current_output_path=self.output_path,
            current_include_spool=self.include_spool,
            on_done=self.set_options,
        )

    def set_options(self, output_path, include_spool):
        self.output_path = output_path
        self.include_spool = include_spool
        self._log(f"Options updated -> output_path: {self.output_path}, include_spool: {self.include_spool}")

    # ------------------------------------------------------------------
    def run(self):
        """
        Collect everything into ready-to-use variables.
        This is the point where you'd plug in your SQL generation /
        automation logic.
        """
        table_name = self.table_name_entry.get().strip()
        issue_number = self.issue_number_entry.get().strip()
        action = self.action_var.get()  # "ADD" or "DROP"

        columns = []
        try:
            for row in self.column_rows:
                data = row.get_data()
                if data:
                    columns.append(data)
        except ValueError as exc:
            self._log(f"ERROR: {exc}")
            return

        # ---- Basic validation ----
        if not table_name:
            self._log("ERROR: Table name is required.")
            return
        if not issue_number:
            self._log("ERROR: Issue number is required.")
            return
        if not columns:
            self._log("ERROR: At least one column must be specified.")
            return

        # ==========================================================
        # These are the variables ready for you to use in your
        # automation / delivery to your service:
        #
        #   table_name      -> str
        #   issue_number    -> str
        #   action          -> "ADD" or "DROP"
        #   columns         -> list of dicts:
        #                      ADD:  {"column_name": ..., "data_type": ..., "length": ...}
        #                      DROP: {"column_name": ...}
        #   self.output_path    -> str  (folder to write the .sql files into)
        #   self.include_spool  -> bool (whether to include SPOOL lines)
        # ==========================================================

        try:
            calculate_n_write(
                table_name=table_name.upper(),
                issue=issue_number.upper(),
                columns=columns,
                action=action,
                path=self.output_path,          # wire these into service.py
                include_spool=self.include_spool # once it accepts them
            )
            self._log('DONE!!!')
        except Exception as e:
            self._log(f'Faced exception:\n{str(e)}')

    def _log(self, text):
        self.output_box.insert("end", text + "\n")
        self.output_box.see("end")


if __name__ == "__main__":
    app = SQLAlterApp()
    app.mainloop()