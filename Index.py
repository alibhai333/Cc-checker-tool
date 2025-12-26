import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import random
import threading
import time
from datetime import datetime
import json
import csv
import os
import re

# ==================== RESPONSIVE UI MANAGER ====================
class ResponsiveUIManager:
    def __init__(self, root):
        self.root = root
        self.base_width = 1366
        self.base_height = 768
        self.current_width = self.root.winfo_screenwidth()
        self.current_height = self.root.winfo_screenheight()
        self.scale_factor = min(self.current_width/self.base_width, self.current_height/self.base_height)
        
    def update_scale(self, width, height):
        self.current_width = width
        self.current_height = height
        self.scale_factor = min(width/self.base_width, height/self.base_height)
        return self.scale_factor

# ==================== CARD VALIDATION ENGINE ====================
class CardValidator:
    def __init__(self):
        self.bin_db = self.load_bin_database()
        
    def load_bin_database(self):
        return {
            "4": {"issuer": "VISA", "type": "Credit/Debit", "country": "US", "bank": "Various"},
            "51": {"issuer": "MASTERCARD", "type": "Credit", "country": "US", "bank": "Various"},
            "52": {"issuer": "MASTERCARD", "type": "Credit", "country": "US", "bank": "Various"},
            "53": {"issuer": "MASTERCARD", "type": "Credit", "country": "US", "bank": "Various"},
            "54": {"issuer": "MASTERCARD", "type": "Credit", "country": "US", "bank": "Various"},
            "55": {"issuer": "MASTERCARD", "type": "Credit", "country": "US", "bank": "Various"},
            "34": {"issuer": "AMEX", "type": "Credit", "country": "US", "bank": "American Express"},
            "37": {"issuer": "AMEX", "type": "Credit", "country": "US", "bank": "American Express"},
            "6011": {"issuer": "DISCOVER", "type": "Credit", "country": "US", "bank": "Discover"},
            "65": {"issuer": "DISCOVER", "type": "Credit", "country": "US", "bank": "Discover"},
        }
    
    def validate_luhn(self, card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        
        return checksum % 10 == 0
    
    def get_bin_info(self, card_number):
        card_number = str(card_number)
        for prefix, info in self.bin_db.items():
            if card_number.startswith(prefix):
                return {
                    'issuer': info['issuer'],
                    'type': info['type'],
                    'country': info['country'],
                    'bank': info['bank'],
                    'prefix': prefix
                }
        return None

# ==================== MAIN APPLICATION ====================
class UltimateStripeChecker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 ULTIMATE STRIPE CHECKER PRO v3.0")
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Set initial window size (90% of screen)
        self.window_width = int(self.screen_width * 0.9)
        self.window_height = int(self.screen_height * 0.85)
        
        # Center window
        x = (self.screen_width - self.window_width) // 2
        y = (self.screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        self.root.minsize(800, 600)
        
        # Initialize managers
        self.ui_manager = ResponsiveUIManager(self.root)
        self.validator = CardValidator()
        
        # State variables
        self.total_checked = 0
        self.live_cards = 0
        self.dead_cards = 0
        self.is_bulk_running = False
        self.is_bulk_paused = False
        self.current_zoom = 100
        self.is_fullscreen = False
        
        # Colors
        self.colors = {
            'bg': '#0a0a0a',
            'fg': '#00ff00',
            'accent': '#ff0000',
            'secondary': '#00ffff',
            'panel': '#1a1a1a',
            'text': '#00ff00',
            'success': '#00ff00',
            'error': '#ff3300',
            'warning': '#ffff00',
            'info': '#ff00ff',
            'border': '#333333',
            'input_bg': '#111111',
            'card_bg': '#222222',
            'button_bg': '#2a2a2a',
            'hover_bg': '#3a3a3a'
        }
        
        # Load default proxies
        self.proxies = [
            "142.111.48.253:7030",
            "31.59.20.176:6754",
            "38.170.176.177:5572"
        ]
        
        # Setup GUI
        self.setup_gui()
        self.bind_events()
        
        # Start updates
        self.update_clock()
        self.update_responsive_layout()
        
        # Initial log
        self.log_activity("🚀 ULTIMATE STRIPE CHECKER PRO v3.0 INITIALIZED")
    
    def setup_gui(self):
        """Setup the main GUI"""
        self.root.configure(bg=self.colors['bg'])
        
        # Main container
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure main grid
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # ========== TOP TOOLBAR ==========
        self.create_top_toolbar()
        
        # ========== MAIN CONTENT AREA ==========
        self.create_main_content()
        
        # ========== STATUS BAR ==========
        self.create_status_bar()
    
    def create_top_toolbar(self):
        """Create top toolbar with controls"""
        self.top_toolbar = tk.Frame(self.main_container, bg=self.colors['panel'], height=60)
        self.top_toolbar.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        self.top_toolbar.grid_propagate(False)
        
        # Left side: Logo and title
        left_frame = tk.Frame(self.top_toolbar, bg=self.colors['panel'])
        left_frame.pack(side=tk.LEFT, padx=20)
        
        self.logo_label = tk.Label(left_frame, text="⚡", font=('Arial', 24),
                                 fg=self.colors['accent'], bg=self.colors['panel'])
        self.logo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.title_label = tk.Label(left_frame, 
                                  text="ULTIMATE STRIPE CHECKER PRO",
                                  font=('Courier', 14, 'bold'),
                                  fg=self.colors['accent'],
                                  bg=self.colors['panel'])
        self.title_label.pack(side=tk.LEFT)
        
        # Center: Quick buttons
        center_frame = tk.Frame(self.top_toolbar, bg=self.colors['panel'])
        center_frame.pack(side=tk.LEFT, expand=True, padx=20)
        
        quick_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("🔍 Single", self.show_single_check),
            ("🚀 Bulk", self.show_bulk_check),
            ("🌐 Proxies", self.show_proxy_manager)
        ]
        
        for text, command in quick_buttons:
            btn = tk.Button(center_frame, text=text, command=command,
                          font=('Arial', 10),
                          bg=self.colors['button_bg'],
                          fg=self.colors['fg'])
            btn.pack(side=tk.LEFT, padx=5)
        
        # Right side: Controls
        right_frame = tk.Frame(self.top_toolbar, bg=self.colors['panel'])
        right_frame.pack(side=tk.RIGHT, padx=20)
        
        # Zoom controls
        zoom_frame = tk.Frame(right_frame, bg=self.colors['panel'])
        zoom_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Button(zoom_frame, text="➖",
                 command=self.zoom_out,
                 font=('Courier', 10),
                 bg=self.colors['button_bg'],
                 fg=self.colors['fg']).pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = tk.Label(zoom_frame, text=f"{self.current_zoom}%",
                                  font=('Courier', 9),
                                  fg=self.colors['secondary'],
                                  bg=self.colors['panel'])
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        tk.Button(zoom_frame, text="➕",
                 command=self.zoom_in,
                 font=('Courier', 10),
                 bg=self.colors['button_bg'],
                 fg=self.colors['fg']).pack(side=tk.LEFT, padx=2)
        
        # Fullscreen toggle
        tk.Button(right_frame, text="⛶",
                 command=self.toggle_fullscreen,
                 font=('Arial', 12),
                 bg=self.colors['button_bg'],
                 fg=self.colors['fg']).pack(side=tk.LEFT, padx=5)
        
        # Exit button
        tk.Button(right_frame, text="✕",
                 command=self.exit_app,
                 font=('Arial', 12, 'bold'),
                 bg=self.colors['error'],
                 fg='white').pack(side=tk.LEFT, padx=(5, 0))
    
    def create_main_content(self):
        """Create main content area"""
        self.main_content = tk.Frame(self.main_container, bg=self.colors['bg'])
        self.main_content.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        
        # Configure main content grid
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(1, weight=1)
        
        # ========== LEFT SIDEBAR ==========
        self.sidebar = tk.Frame(self.main_content, bg=self.colors['panel'], width=200)
        self.sidebar.grid(row=0, column=0, sticky='ns', padx=(0, 10))
        self.sidebar.grid_propagate(False)
        
        self.build_sidebar()
        
        # ========== RIGHT CONTENT AREA ==========
        self.content_area = tk.Frame(self.main_content, bg=self.colors['bg'])
        self.content_area.grid(row=0, column=1, sticky='nsew')
        
        # Content header
        self.content_header = tk.Frame(self.content_area, bg=self.colors['panel'], height=40)
        self.content_header.grid(row=0, column=0, sticky='ew')
        
        self.current_view_title = tk.Label(self.content_header,
                                         text="📊 DASHBOARD",
                                         font=('Courier', 14, 'bold'),
                                         fg=self.colors['fg'],
                                         bg=self.colors['panel'])
        self.current_view_title.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Main content frame
        self.main_content_frame = tk.Frame(self.content_area, bg=self.colors['panel'])
        self.main_content_frame.grid(row=1, column=0, sticky='nsew')
        
        # Initially show dashboard
        self.show_dashboard()
    
    def build_sidebar(self):
        """Build sidebar navigation"""
        profile_frame = tk.Frame(self.sidebar, bg=self.colors['accent'], height=80)
        profile_frame.pack(fill=tk.X)
        
        tk.Label(profile_frame, text="👑 PRO USER", 
                font=('Courier', 12, 'bold'),
                fg='white',
                bg=self.colors['accent']).pack(pady=(15, 5))
        
        # Navigation menu
        nav_frame = tk.Frame(self.sidebar, bg=self.colors['panel'])
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        nav_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("🔍 Single Check", self.show_single_check),
            ("🚀 Bulk Check", self.show_bulk_check),
            ("🌐 Proxy Manager", self.show_proxy_manager),
            ("📈 Results", self.show_results),
            ("🛠️ Tools", self.show_tools),
            ("⚙️ Settings", self.show_settings),
            ("📋 Clipboard", self.show_clipboard),
            ("📝 Logs", self.show_logs)
        ]
        
        for text, command in nav_items:
            btn = tk.Button(nav_frame, text=text, command=command,
                          font=('Courier', 10),
                          bg=self.colors['button_bg'],
                          fg=self.colors['fg'],
                          anchor='w',
                          relief=tk.FLAT,
                          padx=15,
                          pady=8)
            btn.pack(fill=tk.X, pady=2)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Frame(self.main_container, bg=self.colors['panel'], height=30)
        self.status_bar.grid(row=2, column=0, sticky='ew', padx=10, pady=(5, 10))
        
        # Left status
        self.status_left = tk.Label(self.status_bar,
                                   text="⚡ Ready | Zoom: 100%",
                                   font=('Courier', 9),
                                   fg=self.colors['success'],
                                   bg=self.colors['panel'],
                                   anchor='w')
        self.status_left.pack(side=tk.LEFT, padx=10)
        
        # Center stats
        self.status_center = tk.Label(self.status_bar,
                                     text="Cards: 0 | Live: 0 | Dead: 0",
                                     font=('Courier', 9),
                                     fg=self.colors['secondary'],
                                     bg=self.colors['panel'])
        self.status_center.pack(side=tk.LEFT, expand=True)
        
        # Right clock
        self.status_clock = tk.Label(self.status_bar,
                                    text=datetime.now().strftime("%H:%M:%S"),
                                    font=('Courier', 9),
                                    fg=self.colors['info'],
                                    bg=self.colors['panel'],
                                    anchor='e')
        self.status_clock.pack(side=tk.RIGHT, padx=10)
    
    def show_dashboard(self):
        """Show dashboard"""
        self.clear_main_content()
        self.current_view_title.config(text="📊 DASHBOARD")
        
        # Create scrollable frame
        canvas = tk.Canvas(self.main_content_frame, bg=self.colors['panel'])
        scrollbar = ttk.Scrollbar(self.main_content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['panel'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Welcome banner
        banner = tk.Frame(scrollable_frame, bg=self.colors['accent'], height=80)
        banner.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(banner, text="🚀 ULTIMATE STRIPE CHECKER PRO v3.0",
                font=('Courier', 16, 'bold'),
                fg='white',
                bg=self.colors['accent']).pack(expand=True)
        
        # Stats cards
        stats_frame = tk.Frame(scrollable_frame, bg=self.colors['panel'])
        stats_frame.pack(fill=tk.X, padx=20, pady=20)
        
        stats = [
            ("Total Checks", "0", "📊"),
            ("Live Cards", "0", "✅"),
            ("Dead Cards", "0", "❌"),
            ("Success Rate", "0%", "📈"),
            ("Proxies", str(len(self.proxies)), "🌐"),
            ("Avg Speed", "0.0s", "⚡")
        ]
        
        for i, (title, value, icon) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=self.colors['card_bg'],
                          relief=tk.RAISED, borderwidth=1)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
            
            tk.Label(card, text=icon,
                    font=('Arial', 20),
                    fg=self.colors['info'],
                    bg=self.colors['card_bg']).pack(pady=(10, 5))
            
            tk.Label(card, text=title,
                    font=('Courier', 10),
                    fg=self.colors['fg'],
                    bg=self.colors['card_bg']).pack()
            
            tk.Label(card, text=value,
                    font=('Courier', 14, 'bold'),
                    fg=self.colors['accent'],
                    bg=self.colors['card_bg']).pack(pady=(5, 10))
        
        # Quick actions
        actions_frame = tk.LabelFrame(scrollable_frame, text=" Quick Actions ",
                                     font=('Courier', 12),
                                     fg=self.colors['secondary'],
                                     bg=self.colors['panel'])
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        actions = [
            ("🔍 Check Single Card", self.show_single_check),
            ("🚀 Start Bulk Check", self.show_bulk_check),
            ("🌐 Manage Proxies", self.show_proxy_manager),
            ("📊 View Results", self.show_results)
        ]
        
        for i, (text, command) in enumerate(actions):
            btn = tk.Button(actions_frame, text=text, command=command,
                          font=('Courier', 10),
                          bg=self.colors['button_bg'],
                          fg=self.colors['fg'])
            btn.grid(row=0, column=i, padx=10, pady=10)
        
        # Activity log
        log_frame = tk.LabelFrame(scrollable_frame, text=" Recent Activity ",
                                 font=('Courier', 12),
                                 fg=self.colors['secondary'],
                                 bg=self.colors['panel'])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.activity_log = scrolledtext.ScrolledText(log_frame,
                                                     height=10,
                                                     font=('Courier', 9),
                                                     bg=self.colors['input_bg'],
                                                     fg=self.colors['text'])
        self.activity_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def show_single_check(self):
        """Show single card check"""
        self.clear_main_content()
        self.current_view_title.config(text="🔍 SINGLE CARD CHECK")
        
        # Left panel
        left_panel = tk.Frame(self.main_content_frame, bg=self.colors['panel'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(left_panel, text="💳 CARD DETAILS",
                font=('Courier', 14),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w', pady=(0, 20))
        
        # Card number
        tk.Label(left_panel, text="Card Number:",
                font=('Courier', 11),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w')
        
        card_frame = tk.Frame(left_panel, bg=self.colors['panel'])
        card_frame.pack(fill=tk.X, pady=(5, 15))
        
        self.card_entry = tk.Entry(card_frame,
                                  font=('Courier', 12),
                                  bg=self.colors['input_bg'],
                                  fg=self.colors['fg'])
        self.card_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.card_entry.insert(0, "4242424242424242")
        
        tk.Button(card_frame, text="🎲",
                 command=self.generate_card,
                 font=('Courier', 10),
                 bg=self.colors['button_bg'],
                 fg=self.colors['fg']).pack(side=tk.LEFT, padx=2)
        
        # Expiry and CVV
        exp_cvv_frame = tk.Frame(left_panel, bg=self.colors['panel'])
        exp_cvv_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(exp_cvv_frame, text="Expiry (MM/YY):",
                font=('Courier', 11),
                fg=self.colors['fg'],
                bg=self.colors['panel']).grid(row=0, column=0, sticky='w')
        
        self.month_entry = tk.Entry(exp_cvv_frame,
                                   font=('Courier', 11),
                                   bg=self.colors['input_bg'],
                                   fg=self.colors['fg'],
                                   width=3)
        self.month_entry.grid(row=1, column=0, sticky='w', pady=(5, 15))
        self.month_entry.insert(0, "12")
        
        tk.Label(exp_cvv_frame, text="/",
                font=('Courier', 11),
                fg=self.colors['fg'],
                bg=self.colors['panel']).grid(row=1, column=1)
        
        self.year_entry = tk.Entry(exp_cvv_frame,
                                  font=('Courier', 11),
                                  bg=self.colors['input_bg'],
                                  fg=self.colors['fg'],
                                  width=3)
        self.year_entry.grid(row=1, column=2, sticky='w', pady=(5, 15), padx=(0, 20))
        self.year_entry.insert(0, "25")
        
        tk.Label(exp_cvv_frame, text="CVV:",
                font=('Courier', 11),
                fg=self.colors['fg'],
                bg=self.colors['panel']).grid(row=0, column=3, sticky='w')
        
        self.cvv_entry = tk.Entry(exp_cvv_frame,
                                 font=('Courier', 11),
                                 bg=self.colors['input_bg'],
                                 fg=self.colors['fg'],
                                 width=5)
        self.cvv_entry.grid(row=1, column=3, sticky='w', pady=(5, 15))
        self.cvv_entry.insert(0, "123")
        
        # Check mode
        mode_frame = tk.LabelFrame(left_panel,
                                  text=" Check Mode ",
                                  font=('Courier', 12),
                                  fg=self.colors['secondary'],
                                  bg=self.colors['panel'])
        mode_frame.pack(fill=tk.X, pady=20)
        
        self.check_mode = tk.StringVar(value="stripe")
        
        modes = [
            ("Stripe API Check", "stripe"),
            ("Luhn Validation", "luhn"),
            ("BIN Lookup", "bin"),
            ("Full Validation", "full")
        ]
        
        for i, (text, value) in enumerate(modes):
            rb = tk.Radiobutton(mode_frame, text=text,
                               variable=self.check_mode, value=value,
                               font=('Courier', 10),
                               fg=self.colors['fg'],
                               bg=self.colors['panel'])
            rb.grid(row=i//2, column=i%2, sticky='w', padx=20, pady=8)
        
        # Check button
        tk.Button(left_panel, text="⚡ CHECK CARD",
                 command=self.check_single_card,
                 font=('Courier', 14, 'bold'),
                 bg=self.colors['accent'],
                 fg='white',
                 padx=40,
                 pady=10).pack(pady=20)
        
        # Right panel
        right_panel = tk.Frame(self.main_content_frame, bg=self.colors['panel'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(right_panel, text="📊 RESULTS",
                font=('Courier', 14),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w', pady=(0, 10))
        
        self.single_results = scrolledtext.ScrolledText(right_panel,
                                                       height=25,
                                                       font=('Courier', 10),
                                                       bg=self.colors['input_bg'],
                                                       fg=self.colors['text'])
        self.single_results.pack(fill=tk.BOTH, expand=True)
        
        # Add sample text
        sample = "═" * 50 + "\n"
        sample += "        SINGLE CARD CHECKER\n"
        sample += "═" * 50 + "\n\n"
        sample += "Enter card details and click CHECK CARD\n\n"
        sample += "Test Cards:\n"
        sample += "• 4242424242424242 - Visa (Live)\n"
        sample += "• 4000000000000002 - Visa (Declined)\n"
        sample += "• 5555555555554444 - MasterCard\n"
        sample += "• 378282246310005 - American Express\n"
        sample += "═" * 50
        
        self.single_results.insert(tk.END, sample)
    
    def show_bulk_check(self):
        """Show bulk check interface"""
        self.clear_main_content()
        self.current_view_title.config(text="🚀 BULK CARD CHECK")
        
        frame = tk.Frame(self.main_content_frame, bg=self.colors['panel'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File selection
        tk.Label(frame, text="Cards File:",
                font=('Courier', 11),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w')
        
        file_frame = tk.Frame(frame, bg=self.colors['panel'])
        file_frame.pack(fill=tk.X, pady=(5, 15))
        
        self.bulk_file_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.bulk_file_var,
                font=('Courier', 10),
                bg=self.colors['input_bg'],
                fg=self.colors['fg']).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(file_frame, text="📂 Browse",
                 command=self.browse_bulk_file,
                 font=('Courier', 9),
                 bg=self.colors['button_bg'],
                 fg=self.colors['fg']).pack(side=tk.LEFT)
        
        # Settings
        settings_frame = tk.Frame(frame, bg=self.colors['panel'])
        settings_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(settings_frame, text="Threads:",
                font=('Courier', 10),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.thread_var = tk.StringVar(value="5")
        tk.Spinbox(settings_frame, from_=1, to=50,
                  textvariable=self.thread_var,
                  font=('Courier', 10),
                  bg=self.colors['input_bg'],
                  fg=self.colors['fg'],
                  width=10).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(settings_frame, text="Delay (ms):",
                font=('Courier', 10),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.delay_var = tk.StringVar(value="100")
        tk.Spinbox(settings_frame, from_=0, to=5000,
                  textvariable=self.delay_var,
                  font=('Courier', 10),
                  bg=self.colors['input_bg'],
                  fg=self.colors['fg'],
                  width=10).pack(side=tk.LEFT)
        
        # Control buttons
        button_frame = tk.Frame(frame, bg=self.colors['panel'])
        button_frame.pack(pady=20)
        
        self.start_bulk_btn = tk.Button(button_frame, text="🚀 START BULK CHECK",
                                       command=self.start_bulk_check,
                                       font=('Courier', 12, 'bold'),
                                       bg=self.colors['accent'],
                                       fg='white')
        self.start_bulk_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_bulk_btn = tk.Button(button_frame, text="⏸️ PAUSE",
                                       command=self.pause_bulk_check,
                                       font=('Courier', 10),
                                       bg=self.colors['warning'],
                                       fg='black',
                                       state=tk.DISABLED)
        self.pause_bulk_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_bulk_btn = tk.Button(button_frame, text="⏹️ STOP",
                                      command=self.stop_bulk_check,
                                      font=('Courier', 10),
                                      bg=self.colors['error'],
                                      fg='white',
                                      state=tk.DISABLED)
        self.stop_bulk_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_text = tk.StringVar(value="Ready")
        tk.Label(frame, textvariable=self.progress_text,
                font=('Courier', 10),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w', pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Output area
        self.bulk_output = scrolledtext.ScrolledText(frame,
                                                    font=('Courier', 9),
                                                    bg=self.colors['input_bg'],
                                                    fg=self.colors['text'])
        self.bulk_output.pack(fill=tk.BOTH, expand=True)
    
    def show_proxy_manager(self):
        """Show proxy manager"""
        self.clear_main_content()
        self.current_view_title.config(text="🌐 PROXY MANAGER")
        
        frame = tk.Frame(self.main_content_frame, bg=self.colors['panel'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="PROXY LIST",
                font=('Courier', 16, 'bold'),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w', pady=(0, 20))
        
        # Treeview for proxies
        tree_frame = tk.Frame(frame, bg=self.colors['panel'])
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.proxy_tree = ttk.Treeview(tree_frame, columns=('Proxy', 'Status'), show='headings')
        self.proxy_tree.heading('Proxy', text='Proxy')
        self.proxy_tree.heading('Status', text='Status')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.proxy_tree.yview)
        self.proxy_tree.configure(yscrollcommand=scrollbar.set)
        
        self.proxy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load proxies
        for i, proxy in enumerate(self.proxies, 1):
            self.proxy_tree.insert('', 'end', values=(proxy, '🟢 Active'))
        
        # Control buttons
        button_frame = tk.Frame(frame, bg=self.colors['panel'])
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="➕ Add",
                 command=self.add_proxy,
                 font=('Courier', 9),
                 bg=self.colors['button_bg'],
                 fg=self.colors['fg']).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="➖ Remove",
                 command=self.remove_proxy,
                 font=('Courier', 9),
                 bg=self.colors['button_bg'],
                 fg=self.colors['fg']).pack(side=tk.LEFT, padx=5)
    
    def show_results(self):
        """Show results"""
        self.clear_main_content()
        self.current_view_title.config(text="📊 RESULTS")
        
        frame = tk.Frame(self.main_content_frame, bg=self.colors['panel'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="RESULTS DATABASE",
                font=('Courier', 16, 'bold'),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w', pady=(0, 20))
        
        # Treeview for results
        tree_frame = tk.Frame(frame, bg=self.colors['panel'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_tree = ttk.Treeview(tree_frame, columns=('Card', 'Status', 'BIN', 'Time'), show='headings')
        for col in ('Card', 'Status', 'BIN', 'Time'):
            self.results_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add sample data
        sample_data = [
            ("424242******4242", "✅ LIVE", "VISA", "12:30:45"),
            ("400000******0002", "❌ DEAD", "VISA", "12:31:10"),
            ("555555******4444", "✅ LIVE", "MC", "12:32:05")
        ]
        
        for data in sample_data:
            self.results_tree.insert('', 'end', values=data)
    
    def show_tools(self):
        """Show tools"""
        self.clear_main_content()
        self.current_view_title.config(text="🛠️ TOOLS")
        
        frame = tk.Frame(self.main_content_frame, bg=self.colors['panel'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="ADVANCED TOOLS",
                font=('Courier', 16, 'bold'),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w', pady=(0, 20))
        
        # Tools grid
        tools = [
            ("🔢 Card Generator", self.open_card_generator),
            ("🔍 BIN Analyzer", self.open_bin_analyzer),
            ("✅ Luhn Checker", self.open_luhn_checker),
            ("🌐 Network Tools", self.open_network_tools),
            ("📊 Stats Analyzer", self.open_stats_analyzer),
            ("⚡ Speed Test", self.open_speed_test)
        ]
        
        for i, (name, command) in enumerate(tools):
            row = i // 3
            col = i % 3
            
            btn = tk.Button(frame, text=name, command=command,
                          font=('Courier', 10),
                          bg=self.colors['button_bg'],
                          fg=self.colors['fg'],
                          width=20,
                          height=2)
            btn.grid(row=row, column=col, padx=10, pady=10)
    
    def show_settings(self):
        """Show settings"""
        self.clear_main_content()
        self.current_view_title.config(text="⚙️ SETTINGS")
        
        frame = tk.Frame(self.main_content_frame, bg=self.colors['panel'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="SYSTEM SETTINGS",
                font=('Courier', 16, 'bold'),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w', pady=(0, 20))
        
        # Settings content
        settings_text = f"""
Current Settings:
• Theme: Dark
• Zoom Level: {self.current_zoom}%
• Screen: {self.screen_width}x{self.screen_height}
• Window: {self.window_width}x{self.window_height}
• Proxies: {len(self.proxies)}

Keyboard Shortcuts:
• Ctrl + Plus (+) : Zoom In
• Ctrl + Minus (-) : Zoom Out
• Ctrl + 0 : Reset Zoom
• F11 : Toggle Fullscreen
• F5 : Refresh
"""
        
        settings_display = scrolledtext.ScrolledText(frame,
                                                    font=('Courier', 10),
                                                    bg=self.colors['input_bg'],
                                                    fg=self.colors['text'])
        settings_display.pack(fill=tk.BOTH, expand=True)
        settings_display.insert(tk.END, settings_text)
    
    def show_clipboard(self):
        """Show clipboard"""
        self.clear_main_content()
        self.current_view_title.config(text="📋 CLIPBOARD")
        
        frame = tk.Frame(self.main_content_frame, bg=self.colors['panel'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="CLIPBOARD HISTORY",
                font=('Courier', 16, 'bold'),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w', pady=(0, 20))
        
        text = scrolledtext.ScrolledText(frame,
                                        font=('Courier', 10),
                                        bg=self.colors['input_bg'],
                                        fg=self.colors['text'])
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, "Clipboard content will appear here")
    
    def show_logs(self):
        """Show logs"""
        self.clear_main_content()
        self.current_view_title.config(text="📝 LOGS")
        
        frame = tk.Frame(self.main_content_frame, bg=self.colors['panel'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="SYSTEM LOGS",
                font=('Courier', 16, 'bold'),
                fg=self.colors['fg'],
                bg=self.colors['panel']).pack(anchor='w', pady=(0, 20))
        
        text = scrolledtext.ScrolledText(frame,
                                        font=('Courier', 9),
                                        bg=self.colors['input_bg'],
                                        fg=self.colors['text'])
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, "System logs will appear here")
    
    # ==================== CORE FUNCTIONS ====================
    
    def check_single_card(self):
        """Check single card"""
        card = self.card_entry.get().strip()
        month = self.month_entry.get().strip()
        year = self.year_entry.get().strip()
        cvv = self.cvv_entry.get().strip()
        
        if not all([card, month, year, cvv]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        # Start check in thread
        self.single_results.delete(1.0, tk.END)
        self.single_results.insert(tk.END, "🔄 Checking card...\n")
        
        thread = threading.Thread(target=self._check_single_card_thread,
                                 args=(card, month, year, cvv))
        thread.daemon = True
        thread.start()
    
    def _check_single_card_thread(self, card, month, year, cvv):
        """Thread for single card check"""
        try:
            time.sleep(1)  # Simulate processing
            
            # Validate card
            is_valid = self.validator.validate_luhn(card)
            bin_info = self.validator.get_bin_info(card)
            
            # Get mode
            mode = self.check_mode.get()
            
            if mode == "luhn":
                status = "✅ VALID" if is_valid else "❌ INVALID"
                message = "Luhn check passed" if is_valid else "Luhn check failed"
            elif mode == "bin":
                if bin_info:
                    status = "✅ VALID BIN"
                    message = f"{bin_info.get('issuer', 'Unknown')} card"
                else:
                    status = "⚠️ UNKNOWN BIN"
                    message = "BIN not found"
            else:
                # Simulate API check
                if is_valid and random.random() > 0.3:
                    status = "✅ LIVE"
                    message = "Transaction successful"
                else:
                    status = "❌ DECLINED"
                    message = random.choice(["Insufficient funds", "Card declined"])
            
            result = {
                'card': card,
                'status': status,
                'message': message,
                'bin_info': bin_info,
                'valid': is_valid and "❌" not in status
            }
            
            self.root.after(0, self._display_single_result, result)
            
        except Exception as e:
            self.root.after(0, lambda: self.single_results.insert(tk.END, f"\n❌ ERROR: {str(e)}\n"))
    
    def _display_single_result(self, result):
        """Display single check result"""
        self.single_results.delete(1.0, tk.END)
        
        output = "═" * 50 + "\n"
        output += "        CARD CHECK RESULT\n"
        output += "═" * 50 + "\n\n"
        
        output += f"CARD: {result['card'][:6]}******{result['card'][-4:]}\n"
        output += f"STATUS: {result['status']}\n"
        output += f"MESSAGE: {result['message']}\n\n"
        
        if result['bin_info']:
            output += "BIN INFORMATION:\n"
            output += f"  ISSUER: {result['bin_info'].get('issuer', 'Unknown')}\n"
            output += f"  BANK: {result['bin_info'].get('bank', 'Unknown')}\n"
            output += f"  COUNTRY: {result['bin_info'].get('country', 'Unknown')}\n"
            output += f"  TYPE: {result['bin_info'].get('type', 'Unknown')}\n\n"
        
        output += f"TIME: {datetime.now().strftime('%H:%M:%S')}\n"
        output += "═" * 50
        
        self.single_results.insert(tk.END, output)
        
        # Update stats
        self.total_checked += 1
        if result['valid']:
            self.live_cards += 1
        else:
            self.dead_cards += 1
        
        self.log_activity(f"Single check: {result['status']} - {result['card'][-4:]}")
    
    def generate_card(self):
        """Generate random card"""
        prefixes = list(self.validator.bin_db.keys())
        prefix = random.choice(prefixes)
        
        # Generate card
        length = 15 if prefix in ["34", "37"] else 16
        card = prefix
        for _ in range(length - len(prefix) - 1):
            card += str(random.randint(0, 9))
        
        # Calculate Luhn
        for check_digit in range(10):
            test_card = card + str(check_digit)
            if self.validator.validate_luhn(test_card):
                card = test_card
                break
        
        # Update UI
        self.card_entry.delete(0, tk.END)
        self.card_entry.insert(0, card)
        
        self.month_entry.delete(0, tk.END)
        self.month_entry.insert(0, f"{random.randint(1, 12):02d}")
        
        self.year_entry.delete(0, tk.END)
        self.year_entry.insert(0, f"{random.randint(24, 30):02d}")
        
        if prefix in ["34", "37"]:
            cvv = str(random.randint(1000, 9999))
        else:
            cvv = str(random.randint(100, 999))
        
        self.cvv_entry.delete(0, tk.END)
        self.cvv_entry.insert(0, cvv)
        
        self.log_activity("Generated random card")
    
    def browse_bulk_file(self):
        """Browse for bulk file"""
        filename = filedialog.askopenfilename(
            title="Select cards file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.bulk_file_var.set(filename)
            self.log_activity(f"Selected file: {filename}")
    
    def start_bulk_check(self):
        """Start bulk check"""
        if not self.bulk_file_var.get():
            messagebox.showerror("Error", "Please select a cards file")
            return
        
        if self.is_bulk_running:
            messagebox.showwarning("Warning", "Bulk check is already running")
            return
        
        self.is_bulk_running = True
        self.is_bulk_paused = False
        
        # Update UI
        self.start_bulk_btn.config(state=tk.DISABLED)
        self.pause_bulk_btn.config(state=tk.NORMAL)
        self.stop_bulk_btn.config(state=tk.NORMAL)
        
        # Start thread
        thread = threading.Thread(target=self._bulk_check_thread)
        thread.daemon = True
        thread.start()
        
        self.log_activity("🚀 Bulk check started")
    
    def _bulk_check_thread(self):
        """Thread for bulk checking"""
        try:
            # Simulate loading cards
            time.sleep(1)
            
            # Simulate checking process
            total = 100
            for i in range(total):
                if not self.is_bulk_running:
                    break
                
                while self.is_bulk_paused:
                    time.sleep(0.1)
                
                # Simulate checking a card
                time.sleep(0.1)
                
                # Update progress
                progress = (i + 1) * 100 // total
                self.root.after(0, self._update_bulk_progress, i+1, total, progress)
                
                # Simulate result
                if random.random() > 0.5:
                    status = "✅ LIVE"
                    self.live_cards += 1
                else:
                    status = "❌ DEAD"
                    self.dead_cards += 1
                
                self.total_checked += 1
                
                # Update output
                result = f"[{i+1}/{total}] 4242******4242 - {status}\n"
                self.root.after(0, self._update_bulk_output, result)
            
            self.root.after(0, self._bulk_check_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.log_activity(f"Bulk check error: {str(e)}"))
    
    def _update_bulk_progress(self, current, total, progress):
        """Update bulk progress"""
        self.progress_text.set(f"Processing: {current}/{total}")
        self.progress_bar['value'] = progress
    
    def _update_bulk_output(self, result):
        """Update bulk output"""
        self.bulk_output.insert(tk.END, result)
        self.bulk_output.see(tk.END)
    
    def _bulk_check_complete(self):
        """Complete bulk check"""
        self.is_bulk_running = False
        self.start_bulk_btn.config(state=tk.NORMAL)
        self.pause_bulk_btn.config(state=tk.DISABLED)
        self.stop_bulk_btn.config(state=tk.DISABLED)
        
        self.log_activity(f"✅ Bulk check complete: {self.live_cards} live, {self.dead_cards} dead")
    
    def pause_bulk_check(self):
        """Pause bulk check"""
        self.is_bulk_paused = not self.is_bulk_paused
        if self.is_bulk_paused:
            self.pause_bulk_btn.config(text="▶️ RESUME")
            self.log_activity("⏸️ Bulk check paused")
        else:
            self.pause_bulk_btn.config(text="⏸️ PAUSE")
            self.log_activity("▶️ Bulk check resumed")
    
    def stop_bulk_check(self):
        """Stop bulk check"""
        self.is_bulk_running = False
        self.start_bulk_btn.config(state=tk.NORMAL)
        self.pause_bulk_btn.config(state=tk.DISABLED)
        self.stop_bulk_btn.config(state=tk.DISABLED)
        self.log_activity("⏹️ Bulk check stopped")
    
    def add_proxy(self):
        """Add proxy"""
        proxy = simpledialog.askstring("Add Proxy", "Enter proxy (ip:port):")
        if proxy:
            self.proxies.append(proxy)
            self.proxy_tree.insert('', 'end', values=(proxy, '🟢 Active'))
            self.log_activity(f"Added proxy: {proxy}")
    
    def remove_proxy(self):
        """Remove selected proxy"""
        selection = self.proxy_tree.selection()
        if selection:
            for item in selection:
                values = self.proxy_tree.item(item, 'values')
                self.proxy_tree.delete(item)
                if values[0] in self.proxies:
                    self.proxies.remove(values[0])
                    self.log_activity(f"Removed proxy: {values[0]}")
    
    def open_card_generator(self):
        """Open card generator"""
        messagebox.showinfo("Card Generator", "Card Generator Tool")
    
    def open_bin_analyzer(self):
        """Open BIN analyzer"""
        messagebox.showinfo("BIN Analyzer", "BIN Analysis Tool")
    
    def open_luhn_checker(self):
        """Open Luhn checker"""
        messagebox.showinfo("Luhn Checker", "Luhn Validation Tool")
    
    def open_network_tools(self):
        """Open network tools"""
        messagebox.showinfo("Network Tools", "Network Utilities")
    
    def open_stats_analyzer(self):
        """Open stats analyzer"""
        messagebox.showinfo("Stats Analyzer", "Statistics Analysis Tool")
    
    def open_speed_test(self):
        """Open speed test"""
        messagebox.showinfo("Speed Test", "Connection Speed Test")
    
    # ==================== UI FUNCTIONS ====================
    
    def clear_main_content(self):
        """Clear main content area"""
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
    
    def log_activity(self, message):
        """Log activity message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if hasattr(self, 'activity_log'):
            self.activity_log.insert(tk.END, log_entry)
            self.activity_log.see(tk.END)
    
    def zoom_in(self):
        """Zoom in UI"""
        if self.current_zoom < 200:
            self.current_zoom += 10
            self.zoom_label.config(text=f"{self.current_zoom}%")
            self.status_left.config(text=f"⚡ Zoom: {self.current_zoom}%")
            self.log_activity(f"Zoom: {self.current_zoom}%")
    
    def zoom_out(self):
        """Zoom out UI"""
        if self.current_zoom > 50:
            self.current_zoom -= 10
            self.zoom_label.config(text=f"{self.current_zoom}%")
            self.status_left.config(text=f"⚡ Zoom: {self.current_zoom}%")
            self.log_activity(f"Zoom: {self.current_zoom}%")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        self.log_activity("Fullscreen toggled")
    
    def update_clock(self):
        """Update clock"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_clock.config(text=now)
        self.root.after(1000, self.update_clock)
    
    def update_responsive_layout(self):
        """Update responsive layout"""
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        if width > 0 and height > 0:
            # Update window dimensions
            self.window_width = width
            self.window_height = height
            
            # Update status
            rate = (self.live_cards / self.total_checked * 100) if self.total_checked > 0 else 0
            self.status_center.config(
                text=f"Cards: {self.total_checked} | Live: {self.live_cards} | Dead: {self.dead_cards} | Rate: {rate:.1f}%"
            )
        
        # Schedule next update
        self.root.after(1000, self.update_responsive_layout)
    
    def bind_events(self):
        """Bind keyboard events"""
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.exit_app() if self.is_fullscreen else None)
    
    def exit_app(self):
        """Exit application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    app = UltimateStripeChecker()
    app.run()
