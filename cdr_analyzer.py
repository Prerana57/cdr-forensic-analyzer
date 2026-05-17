# CDR Analyzer GUI App
# Requirements: pip install pandas matplotlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ── Color Palette ──────────────────────────────────────────
BG        = "#0f0f1a"
SIDEBAR   = "#16213e"
CARD      = "#1a1a2e"
ACCENT    = "#e94560"
ACCENT2   = "#0f3460"
TEXT      = "#eaeaea"
SUBTEXT   = "#8892a4"
BTN_HOVER = "#e94560"

class CDRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CDR Analyzer")
        self.root.geometry("1100x720")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.data = None
        self.contacts = {}  # {number: name}

        self._build_layout()

    def _build_layout(self):
        # ── Sidebar ───────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(sidebar, bg=ACCENT, height=70)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="📞 CDR", font=("Helvetica", 18, "bold"),
                 bg=ACCENT, fg="white").pack(expand=True)

        tk.Label(sidebar, text="A N A L Y Z E R", font=("Helvetica", 9, "bold"),
                 bg=SIDEBAR, fg=SUBTEXT).pack(pady=(8, 20))

        # Nav buttons
        self._nav_btn(sidebar, "📂  Upload CSV",       self.load_file)
        self._nav_btn(sidebar, "📊  Summary",          self.show_summary)
        self._nav_btn(sidebar, "📈  Call Frequency",   self.plot_calls)
        self._nav_btn(sidebar, "⏱   Duration Graph",   self.plot_duration)
        self._nav_btn(sidebar, "🥧  Call Type Pie",    self.plot_pie)
        self._nav_btn(sidebar, "🏆  Top Contact",      self.show_top_contact)
        self._nav_btn(sidebar, "👤  Manage Contacts",  self.open_contacts)
        self._nav_btn(sidebar, "🔍  Search Number",    self.search_number)
        self._nav_btn(sidebar, "📍  Location Tracker", self.location_tracker)

        # Status at bottom of sidebar
        tk.Frame(sidebar, bg=SUBTEXT, height=1).pack(fill="x", padx=15, pady=10)
        self.status_var = tk.StringVar(value="No file loaded")
        tk.Label(sidebar, textvariable=self.status_var, font=("Helvetica", 9),
                 bg=SIDEBAR, fg=SUBTEXT, wraplength=190, justify="left").pack(padx=15)

        # ── Main Area ─────────────────────────────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        # Top bar
        topbar = tk.Frame(main, bg=CARD, height=55)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="Call Detail Record Analyzer",
                 font=("Helvetica", 14, "bold"), bg=CARD, fg=TEXT).pack(side="left", padx=20, pady=15)
        self.file_label = tk.Label(topbar, text="", font=("Helvetica", 10),
                                   bg=CARD, fg=ACCENT)
        self.file_label.pack(side="right", padx=20)

        # Text card
        card = tk.Frame(main, bg=CARD, bd=0)
        card.pack(fill="x", padx=20, pady=(15, 8))
        tk.Label(card, text="OUTPUT", font=("Helvetica", 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=12, pady=(8, 0))
        self.text = tk.Text(card, height=9, font=("Courier", 11),
                            bg="#0d0d1a", fg="#00ff99", insertbackground="white",
                            relief="flat", padx=12, pady=10, bd=0,
                            selectbackground=ACCENT)
        self.text.pack(fill="x", padx=12, pady=(4, 12))

        # Graph card
        graph_card = tk.Frame(main, bg=CARD, bd=0)
        graph_card.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        tk.Label(graph_card, text="GRAPH", font=("Helvetica", 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=12, pady=(8, 0))
        self.graph_frame = tk.Frame(graph_card, bg="#0d0d1a")
        self.graph_frame.pack(fill="both", expand=True, padx=12, pady=(4, 12))

    def _nav_btn(self, parent, label, cmd):
        btn = tk.Button(parent, text=label, command=cmd,
                        font=("Helvetica", 12, "bold"), bg=SIDEBAR, fg="#000000",
                        activebackground=ACCENT, activeforeground="#000000",
                        relief="flat", anchor="w", padx=20, pady=12,
                        cursor="hand2", bd=0)
        btn.pack(fill="x", pady=2)
        btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT, fg="#000000"))
        btn.bind("<Leave>", lambda e: btn.config(bg=SIDEBAR, fg="#000000"))

    # ── File Load ─────────────────────────────────────────
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            try:
                self.data = pd.read_csv(path)
                name = path.split("/")[-1]
                self.status_var.set(f"✅ {name}\n{len(self.data)} records")
                self.file_label.config(text=f"📄 {name}")
                messagebox.showinfo("Loaded", f"{len(self.data)} records loaded from {name}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ── Summary ───────────────────────────────────────────
    def show_summary(self):
        if not self._check(): return
        s = f"{'─'*42}\n  CDR SUMMARY REPORT\n{'─'*42}\n"
        s += f"  Total Records   : {len(self.data)}\n"
        s += f"  Columns         : {', '.join(self.data.columns.tolist())}\n"
        if 'duration' in self.data.columns:
            s += f"  Total Duration  : {self.data['duration'].sum()} sec\n"
            s += f"  Avg Duration    : {self.data['duration'].mean():.2f} sec\n"
            s += f"  Max Duration    : {self.data['duration'].max()} sec\n"
        if 'type' in self.data.columns:
            s += f"\n  Call Types:\n"
            for k, v in self.data['type'].value_counts().items():
                s += f"    {k:<15}: {v}\n"
        if 'number' in self.data.columns:
            s += f"\n  Top 3 Numbers:\n"
            for num, cnt in self.data['number'].value_counts().head(3).items():
                s += f"    {self._resolve(num)} ({num}): {cnt} calls\n"
        s += f"{'─'*42}\n"
        self._show_text(s)

    # ── Call Frequency ────────────────────────────────────
    def plot_calls(self):
        if not self._check(): return
        if 'date' not in self.data.columns:
            messagebox.showwarning("Warning", "'date' column required"); return
        self.clear_graph()
        df = self.data.copy()
        df['date'] = pd.to_datetime(df['date'])
        cpd = df.groupby(df['date'].dt.date).size()
        fig, ax = self._styled_fig()
        ax.bar(range(len(cpd)), cpd.values, color=ACCENT, edgecolor=BG, width=0.6)
        ax.set_xticks(range(len(cpd)))
        ax.set_xticklabels([str(d) for d in cpd.index], rotation=30, ha='right', color=TEXT, fontsize=9)
        ax.set_title("Calls per Day", color=TEXT, fontsize=13, pad=12)
        ax.set_ylabel("Calls", color=SUBTEXT)
        plt.tight_layout()
        self._embed(fig)

    # ── Duration ──────────────────────────────────────────
    def plot_duration(self):
        if not self._check(): return
        if 'duration' not in self.data.columns:
            messagebox.showwarning("Warning", "'duration' column required"); return
        self.clear_graph()
        fig, ax = self._styled_fig()
        ax.hist(self.data['duration'], bins=10, color="#0f3460", edgecolor=ACCENT, linewidth=1.2)
        ax.set_title("Call Duration Distribution", color=TEXT, fontsize=13, pad=12)
        ax.set_xlabel("Duration (seconds)", color=SUBTEXT)
        ax.set_ylabel("Frequency", color=SUBTEXT)
        plt.tight_layout()
        self._embed(fig)

    # ── Pie ───────────────────────────────────────────────
    def plot_pie(self):
        if not self._check(): return
        if 'type' not in self.data.columns:
            messagebox.showwarning("Warning", "'type' column required"); return
        self.clear_graph()
        counts = self.data['type'].value_counts()
        colors = [ACCENT, "#0f3460", "#533483", "#e8a838", "#2ec4b6"]
        fig, ax = self._styled_fig(size=(5, 4))
        wedges, texts, autotexts = ax.pie(
            counts, labels=counts.index, autopct='%1.1f%%',
            colors=colors[:len(counts)], startangle=140,
            wedgeprops={"edgecolor": BG, "linewidth": 2})
        for t in texts: t.set_color(TEXT)
        for a in autotexts: a.set_color("white"); a.set_fontsize(10)
        ax.set_title("Call Type Distribution", color=TEXT, fontsize=13, pad=12)
        plt.tight_layout()
        self._embed(fig)

    # ── Top Contact ───────────────────────────────────────
    def show_top_contact(self):
        if not self._check(): return
        if 'number' not in self.data.columns:
            messagebox.showwarning("Warning", "'number' column required"); return
        self.clear_graph()
        counts = self.data['number'].value_counts()
        top_num = counts.index[0]
        top_cnt = counts.iloc[0]

        s = f"{'─'*42}\n  🏆 MOST FREQUENT CONTACT\n{'─'*42}\n"
        s += f"  Name            : {self._resolve(top_num)}\n"
        s += f"  Number          : {top_num}\n"
        s += f"  Total Calls     : {top_cnt}\n"
        if 'duration' in self.data.columns:
            dur = self.data[self.data['number'] == top_num]['duration'].sum()
            s += f"  Total Talk Time : {dur} seconds\n"
        if 'type' in self.data.columns:
            s += f"\n  Call Breakdown:\n"
            for k, v in self.data[self.data['number'] == top_num]['type'].value_counts().items():
                s += f"    {k:<15}: {v}\n"
        s += f"\n  Top 5 Contacts:\n"
        for num, cnt in counts.head(5).items():
            star = " ⭐" if num == top_num else ""
            s += f"    {self._resolve(num)} ({num}): {cnt} calls{star}\n"
        s += f"{'─'*42}\n"
        self._show_text(s)

        top5 = counts.head(5)
        fig, ax = self._styled_fig()
        bar_colors = [ACCENT if n == top_num else ACCENT2 for n in top5.index]
        bars = ax.bar(range(len(top5)), top5.values, color=bar_colors, edgecolor=BG, width=0.55)
        ax.set_xticks(range(len(top5)))
        ax.set_xticklabels([self._resolve(n) for n in top5.index], rotation=15, ha='right', color=TEXT, fontsize=9)
        ax.set_title("Top 5 Most Frequent Contacts  (🏆 = top)", color=TEXT, fontsize=13, pad=12)
        ax.set_ylabel("Calls", color=SUBTEXT)
        for bar, val in zip(bars, top5.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(val), ha='center', va='bottom', color=TEXT, fontsize=10)
        plt.tight_layout()
        self._embed(fig)

    # ── Location Tracker ──────────────────────────────────
    def location_tracker(self):
        if not self._check(): return

        # check for at least one relevant column
        required = {'location', 'mcc', 'mnc', 'lac', 'cell_id'}
        present = required & set(self.data.columns)
        if not present:
            messagebox.showwarning("Missing Columns",
                "None of the location columns found.\n\n"
                "Add these columns to your CSV:\n"
                "location, mcc, mnc, lac, cell_id\n\n"
                "Example row:\n"
                "2024-04-01,9876543210,Incoming,120,Mumbai,404,20,1234,56789")
            return

        win = tk.Toplevel(self.root)
        win.title("Location Tracker")
        win.geometry("860x620")
        win.configure(bg=BG)
        win.resizable(True, True)

        tk.Label(win, text="📍 Location Tracker", font=("Helvetica", 15, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(15, 2))
        tk.Label(win, text="Tower & cell information from CDR data",
                 font=("Helvetica", 10), bg=BG, fg=SUBTEXT).pack()

        # Filter row
        filter_frame = tk.Frame(win, bg=BG)
        filter_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(filter_frame, text="Filter by Number (optional):",
                 bg=BG, fg=TEXT, font=("Helvetica", 10)).grid(row=0, column=0, sticky="w")
        num_entry = tk.Entry(filter_frame, font=("Helvetica", 11), bg=CARD, fg=TEXT,
                             insertbackground="white", relief="flat", width=20)
        num_entry.grid(row=0, column=1, padx=10)
        tk.Button(filter_frame, text="Show", font=("Helvetica", 11, "bold"),
                  bg=ACCENT, fg="black", relief="flat", padx=12, pady=4,
                  cursor="hand2", command=lambda: render(num_entry.get().strip())).grid(row=0, column=2)
        tk.Button(filter_frame, text="All", font=("Helvetica", 11, "bold"),
                  bg=ACCENT2, fg="black", relief="flat", padx=12, pady=4,
                  cursor="hand2", command=lambda: render("")).grid(row=0, column=3, padx=6)

        summary_label = tk.Label(win, text="", font=("Helvetica", 10, "bold"),
                                 bg=BG, fg="#00ff99")
        summary_label.pack()

        # ── Full records table ─────────────────────────────
        rec_frame = tk.Frame(win, bg=CARD)
        rec_frame.pack(fill="x", padx=20, pady=(4, 4))
        tk.Label(rec_frame, text="CELL TOWER RECORDS", font=("Helvetica", 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=10, pady=(6, 0))

        rec_cols = ("date", "number", "type", "location", "mcc", "mnc", "lac", "cell_id")
        rec_widths = (100, 115, 80, 90, 55, 55, 65, 75)
        rec_tree = ttk.Treeview(rec_frame, columns=rec_cols, show="headings", height=6)
        for col, w in zip(rec_cols, rec_widths):
            rec_tree.heading(col, text=col.upper().replace("_", "/"))
            rec_tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(rec_frame, orient="vertical", command=rec_tree.yview)
        rec_tree.configure(yscrollcommand=vsb.set)
        rec_tree.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=6)
        vsb.pack(side="left", fill="y", pady=6)

        # ── Location summary table ─────────────────────────
        sum_frame = tk.Frame(win, bg=CARD)
        sum_frame.pack(fill="x", padx=20, pady=(0, 6))
        tk.Label(sum_frame, text="LOCATION SUMMARY", font=("Helvetica", 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=10, pady=(6, 0))

        sum_cols = ("location", "mcc", "mnc", "lac", "cell_id", "total", "incoming", "outgoing", "missed")
        sum_widths = (90, 50, 50, 60, 70, 55, 70, 70, 60)
        sum_tree = ttk.Treeview(sum_frame, columns=sum_cols, show="headings", height=4)
        for col, w in zip(sum_cols, sum_widths):
            sum_tree.heading(col, text=col.upper().replace("_", "/"))
            sum_tree.column(col, width=w, anchor="center")
        sum_tree.pack(fill="x", padx=10, pady=6)

        # apply treeview style once
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0d0d1a", foreground="#00ff99",
                        fieldbackground="#0d0d1a", font=("Courier", 10), rowheight=24)
        style.configure("Treeview.Heading", background=ACCENT2, foreground="black",
                        font=("Helvetica", 10, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])

        # Graph frame
        graph_frame = tk.Frame(win, bg="#0d0d1a")
        graph_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        def safe(df, col):
            return df[col] if col in df.columns else "-"

        def render(filter_num=""):
            df = self.data.copy()
            if filter_num:
                df = df[df['number'].astype(str).str.strip() == filter_num]
                if df.empty:
                    summary_label.config(text=f"No records found for {filter_num}")
                    return
                name = self._resolve(filter_num)
                lbl = f"{name} ({filter_num})" if name != filter_num else filter_num
                summary_label.config(text=f"{len(df)} record(s) for {lbl}")
            else:
                summary_label.config(text=f"All {len(df)} records")

            # fill records table
            for r in rec_tree.get_children(): rec_tree.delete(r)
            for _, row in df.iterrows():
                rec_tree.insert("", tk.END, values=(
                    row.get('date', '-'),
                    row.get('number', '-'),
                    row.get('type', '-'),
                    row.get('location', '-'),
                    row.get('mcc', '-'),
                    row.get('mnc', '-'),
                    row.get('lac', '-'),
                    row.get('cell_id', '-'),
                ))

            # fill summary table
            for r in sum_tree.get_children(): sum_tree.delete(r)
            group_cols = [c for c in ['location', 'mcc', 'mnc', 'lac', 'cell_id'] if c in df.columns]
            if group_cols:
                grp = df.groupby(group_cols)
                for keys, sub in grp:
                    if not isinstance(keys, tuple): keys = (keys,)
                    vals = dict(zip(group_cols, keys))
                    total = len(sub)
                    inc = len(sub[sub['type'].str.lower() == 'incoming']) if 'type' in sub.columns else '-'
                    out = len(sub[sub['type'].str.lower() == 'outgoing']) if 'type' in sub.columns else '-'
                    mis = len(sub[sub['type'].str.lower() == 'missed'])   if 'type' in sub.columns else '-'
                    sum_tree.insert("", tk.END, values=(
                        vals.get('location', '-'), vals.get('mcc', '-'),
                        vals.get('mnc', '-'),      vals.get('lac', '-'),
                        vals.get('cell_id', '-'),  total, inc, out, mis
                    ))

            # bar chart by location
            for w in graph_frame.winfo_children(): w.destroy()
            if 'location' in df.columns:
                loc_counts = df.groupby('location').size().sort_values(ascending=False)
                fig, ax = self._styled_fig(size=(8, 2.8))
                bar_colors = [ACCENT if i == 0 else ACCENT2 for i in range(len(loc_counts))]
                bars = ax.bar(range(len(loc_counts)), loc_counts.values, color=bar_colors, edgecolor=BG, width=0.55)
                ax.set_xticks(range(len(loc_counts)))
                ax.set_xticklabels(loc_counts.index, rotation=20, ha='right', color=TEXT, fontsize=9)
                ax.set_title("Calls per Location / Cell Tower", color=TEXT, fontsize=12, pad=10)
                ax.set_ylabel("Calls", color=SUBTEXT)
                for bar, val in zip(bars, loc_counts.values):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                            str(val), ha='center', va='bottom', color=TEXT, fontsize=9)
                plt.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)

        render()
        num_entry.bind("<Return>", lambda e: render(num_entry.get().strip()))

    # ── Search Number ─────────────────────────────────────
    def search_number(self):
        if not self._check(): return

        win = tk.Toplevel(self.root)
        win.title("Search Number")
        win.geometry("500x520")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="🔍 Search Call Records", font=("Helvetica", 15, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(15, 5))
        tk.Label(win, text="Enter a phone number to view its records",
                 font=("Helvetica", 10), bg=BG, fg=SUBTEXT).pack()

        # Input row
        input_frame = tk.Frame(win, bg=BG)
        input_frame.pack(pady=12, padx=20, fill="x")
        tk.Label(input_frame, text="Number:", bg=BG, fg=TEXT,
                 font=("Helvetica", 11)).grid(row=0, column=0, sticky="w")
        num_entry = tk.Entry(input_frame, font=("Helvetica", 12), bg=CARD, fg=TEXT,
                             insertbackground="white", relief="flat", width=22)
        num_entry.grid(row=0, column=1, padx=10)
        tk.Button(input_frame, text="Search", font=("Helvetica", 11, "bold"),
                  bg=ACCENT, fg="black", relief="flat", padx=12, pady=4,
                  cursor="hand2", command=lambda: do_search()).grid(row=0, column=2, padx=6)

        # Result label
        result_label = tk.Label(win, text="", font=("Helvetica", 10, "bold"),
                                bg=BG, fg=ACCENT)
        result_label.pack()

        # Records list
        list_frame = tk.Frame(win, bg=CARD)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(6, 10))
        tk.Label(list_frame, text="CALL RECORDS", font=("Helvetica", 8, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=10, pady=(6, 0))

        cols = ("date", "type", "duration")
        tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col.upper())
            tree.column(col, width=140, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=6)

        # Style the treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0d0d1a", foreground="#00ff99",
                        fieldbackground="#0d0d1a", font=("Courier", 10), rowheight=24)
        style.configure("Treeview.Heading", background=ACCENT2, foreground="white",
                        font=("Helvetica", 10, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])

        def do_search():
            number = num_entry.get().strip()
            if not number:
                messagebox.showwarning("Missing", "Please enter a phone number.", parent=win)
                return
            if 'number' not in self.data.columns:
                messagebox.showwarning("Warning", "'number' column not found in CSV.", parent=win)
                return
            # normalize both sides to string, strip spaces
            filtered = self.data[self.data['number'].astype(str).str.strip() == number.strip()]
            # clear tree
            for row in tree.get_children():
                tree.delete(row)
            if filtered.empty:
                # show what values actually exist to help debug
                sample = self.data['number'].astype(str).str.strip().head(3).tolist()
                result_label.config(text=f"No records found. Sample numbers in file: {sample}")
                return
            name = self._resolve(number)
            label = f"{name} ({number})" if name != number else number
            result_label.config(text=f"Found {len(filtered)} record(s) for {label}")
            for _, row in filtered.iterrows():
                date = row.get('date', '-')
                rtype = row.get('type', '-')
                dur = f"{row.get('duration', '-')} sec"
                tree.insert("", tk.END, values=(date, rtype, dur))

        # allow pressing Enter to search
        num_entry.bind("<Return>", lambda e: do_search())

    # ── Contacts Manager ──────────────────────────────────
    def open_contacts(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Contacts")
        win.geometry("420x500")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="👤 Contacts", font=("Helvetica", 15, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(15, 5))
        tk.Label(win, text="Assign names to phone numbers",
                 font=("Helvetica", 10), bg=BG, fg=SUBTEXT).pack()

        # Input row
        input_frame = tk.Frame(win, bg=BG)
        input_frame.pack(pady=12, padx=20, fill="x")

        tk.Label(input_frame, text="Number:", bg=BG, fg=TEXT,
                 font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=4)
        num_entry = tk.Entry(input_frame, font=("Helvetica", 11), bg=CARD, fg=TEXT,
                             insertbackground="white", relief="flat", width=22)
        num_entry.grid(row=0, column=1, padx=8, pady=4)

        tk.Label(input_frame, text="Name:", bg=BG, fg=TEXT,
                 font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=4)
        name_entry = tk.Entry(input_frame, font=("Helvetica", 11), bg=CARD, fg=TEXT,
                              insertbackground="white", relief="flat", width=22)
        name_entry.grid(row=1, column=1, padx=8, pady=4)

        # Contacts list
        list_frame = tk.Frame(win, bg=CARD)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        tk.Label(list_frame, text="Saved Contacts", font=("Helvetica", 9, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=10, pady=(6, 0))

        listbox = tk.Listbox(list_frame, font=("Courier", 11), bg="#0d0d1a", fg="#00ff99",
                             selectbackground=ACCENT, relief="flat", bd=0, height=10)
        listbox.pack(fill="both", expand=True, padx=10, pady=6)

        def refresh_list():
            listbox.delete(0, tk.END)
            for num, name in self.contacts.items():
                listbox.insert(tk.END, f"  {num}  →  {name}")

        def add_contact():
            num = num_entry.get().strip()
            name = name_entry.get().strip()
            if not num or not name:
                messagebox.showwarning("Missing", "Enter both number and name.", parent=win)
                return
            self.contacts[num] = name
            num_entry.delete(0, tk.END)
            name_entry.delete(0, tk.END)
            refresh_list()

        def delete_contact():
            sel = listbox.curselection()
            if not sel:
                return
            item = listbox.get(sel[0])
            num = item.strip().split("→")[0].strip()
            if num in self.contacts:
                del self.contacts[num]
            refresh_list()

        # Buttons
        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(pady=6)
        tk.Button(btn_row, text="➕ Add", command=add_contact,
                  bg=ACCENT, fg="black", font=("Helvetica", 11, "bold"),
                  relief="flat", padx=16, pady=6, cursor="hand2").grid(row=0, column=0, padx=8)
        tk.Button(btn_row, text="🗑 Delete Selected", command=delete_contact,
                  bg=ACCENT2, fg="black", font=("Helvetica", 11, "bold"),
                  relief="flat", padx=16, pady=6, cursor="hand2").grid(row=0, column=1, padx=8)

        refresh_list()

    def _resolve(self, number):
        """Return saved name for a number, or the number itself."""
        return self.contacts.get(str(number), str(number))

    # ── Helpers ───────────────────────────────────────────
    def _check(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please load a CSV file first.")
            return False
        return True

    def _show_text(self, content):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, content)

    def _styled_fig(self, size=(9, 3.8)):
        fig, ax = plt.subplots(figsize=size)
        fig.patch.set_facecolor("#0d0d1a")
        ax.set_facecolor("#0d0d1a")
        ax.tick_params(colors=SUBTEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3e")
        ax.yaxis.label.set_color(SUBTEXT)
        ax.xaxis.label.set_color(SUBTEXT)
        return fig, ax

    def _embed(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def clear_graph(self):
        for w in self.graph_frame.winfo_children():
            w.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CDRApp(root)
    root.mainloop()
