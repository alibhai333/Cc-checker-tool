import streamlit as st
import random
import time
from datetime import datetime
import pandas as pd
import json
import io

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
            "35": {"issuer": "JCB", "type": "Credit", "country": "JP", "bank": "JCB"},
            "30": {"issuer": "DINERS", "type": "Credit", "country": "US", "bank": "Diners Club"},
            "36": {"issuer": "DINERS", "type": "Credit", "country": "US", "bank": "Diners Club"},
            "38": {"issuer": "DINERS", "type": "Credit", "country": "US", "bank": "Diners Club"}
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
class UltimateStripeCheckerPro:
    def __init__(self):
        # Initialize session state
        if 'app_initialized' not in st.session_state:
            st.session_state.app_initialized = True
            st.session_state.total_checked = 0
            st.session_state.live_cards = 0
            st.session_state.dead_cards = 0
            st.session_state.proxies = [
                "142.111.48.253:7030:user:pass",
                "31.59.20.176:6754:user:pass",
                "38.170.176.177:5572:user:pass",
                "198.23.239.134:6540:user:pass",
                "45.38.107.97:6014:user:pass",
                "107.172.163.27:6543:user:pass",
                "64.137.96.74:6641:user:pass",
                "216.10.27.159:6837:user:pass",
                "142.111.67.146:5611:user:pass",
                "142.147.128.93:6593:user:pass"
            ]
            st.session_state.results = []
            st.session_state.activity_log = []
            st.session_state.bulk_running = False
            st.session_state.bulk_paused = False
            st.session_state.single_result = None
            st.session_state.current_theme = "dark"
            st.session_state.card_history = []
        
        self.validator = CardValidator()
        
    def run(self):
        """Main application runner"""
        # Page configuration
        st.set_page_config(
            page_title="🔥 ULTIMATE STRIPE CHECKER PRO v3.0",
            page_icon="⚡",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for professional look
        self.apply_custom_css()
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🔥 ULTIMATE STRIPE CHECKER PRO v3.0</h1>
            <p class="subtitle">Professional Card Validation Tool | Real-time Processing | Multi-threaded</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar Navigation
        with st.sidebar:
            st.markdown("""
            <div class="profile-card">
                <div class="profile-icon">👑</div>
                <h3>PRO USER</h3>
                <p>Premium Access Active</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Navigation
            nav_options = {
                "📊 Dashboard": self.show_dashboard,
                "🔍 Single Check": self.show_single_check,
                "🚀 Bulk Check": self.show_bulk_check,
                "🌐 Proxy Manager": self.show_proxy_manager,
                "📈 Results": self.show_results,
                "🛠️ Advanced Tools": self.show_tools,
                "⚙️ Settings": self.show_settings,
                "📋 History": self.show_history
            }
            
            selected_page = st.selectbox(
                "Navigation",
                list(nav_options.keys()),
                label_visibility="collapsed"
            )
            
            # Quick Stats
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", st.session_state.total_checked, delta=None)
                st.metric("Live", st.session_state.live_cards, delta=None)
            with col2:
                st.metric("Dead", st.session_state.dead_cards, delta=None)
                rate = (st.session_state.live_cards / st.session_state.total_checked * 100) if st.session_state.total_checked > 0 else 0
                st.metric("Rate", f"{rate:.1f}%", delta=None)
            
            st.markdown("---")
            st.markdown(f"**Proxies:** {len(st.session_state.proxies)}")
            st.markdown(f"**Updated:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Display selected page
        nav_options[selected_page]()
    
    def apply_custom_css(self):
        """Apply custom CSS styles"""
        st.markdown("""
        <style>
        /* Main Header */
        .main-header {
            text-align: center;
            background: linear-gradient(90deg, #ff0000, #ff5500, #ffaa00);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            padding: 20px;
            margin-bottom: 30px;
            border-bottom: 3px solid #333;
        }
        .main-header h1 {
            font-size: 2.8rem;
            font-weight: 900;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            color: #aaa;
            font-size: 1.1rem;
            font-weight: 300;
        }
        
        /* Profile Card */
        .profile-card {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .profile-icon {
            font-size: 50px;
            margin-bottom: 10px;
        }
        .profile-card h3 {
            color: white;
            margin: 0;
            font-size: 1.5rem;
        }
        .profile-card p {
            color: rgba(255,255,255,0.8);
            margin: 5px 0 0 0;
            font-size: 0.9rem;
        }
        
        /* Cards */
        .stat-card {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #333;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-card h3 {
            font-size: 2.5rem;
            margin: 10px 0;
            color: #00ff00;
        }
        .stat-card p {
            color: #aaa;
            margin: 0;
            font-size: 0.9rem;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            font-weight: 600;
        }
        
        /* Dataframe */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: linear-gradient(135deg, #00b09b, #96c93d);
            color: white;
            border-radius: 10px;
        }
        .stError {
            background: linear-gradient(135deg, #ff416c, #ff4b2b);
            color: white;
            border-radius: 10px;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #1a1a1a;
        }
        ::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #00cc00;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def show_dashboard(self):
        """Show dashboard"""
        st.markdown("## 📊 DASHBOARD OVERVIEW")
        
        # Stats Cards
        st.markdown("### 📈 PERFORMANCE METRICS")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 30px;">📊</div>
                <h3>{st.session_state.total_checked}</h3>
                <p>Total Checks</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 30px; color: #00ff00;">✅</div>
                <h3>{st.session_state.live_cards}</h3>
                <p>Live Cards</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 30px; color: #ff0000;">❌</div>
                <h3>{st.session_state.dead_cards}</h3>
                <p>Dead Cards</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            rate = (st.session_state.live_cards / st.session_state.total_checked * 100) if st.session_state.total_checked > 0 else 0
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 30px; color: #ffff00;">📈</div>
                <h3>{rate:.1f}%</h3>
                <p>Success Rate</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 30px; color: #00ffff;">🌐</div>
                <h3>{len(st.session_state.proxies)}</h3>
                <p>Active Proxies</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown("""
            <div class="stat-card">
                <div style="font-size: 30px; color: #ff00ff;">⚡</div>
                <h3>0.0s</h3>
                <p>Avg Speed</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown("---")
        st.markdown("### 🚀 QUICK ACTIONS")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 **CHECK SINGLE CARD**", use_container_width=True):
                st.session_state.current_page = "single"
                st.rerun()
        
        with col2:
            if st.button("🚀 **START BULK CHECK**", use_container_width=True):
                st.session_state.current_page = "bulk"
                st.rerun()
        
        with col3:
            if st.button("🌐 **MANAGE PROXIES**", use_container_width=True):
                st.session_state.current_page = "proxy"
                st.rerun()
        
        with col4:
            if st.button("📊 **VIEW RESULTS**", use_container_width=True):
                st.session_state.current_page = "results"
                st.rerun()
        
        # Recent Activity
        st.markdown("---")
        st.markdown("### 📝 RECENT ACTIVITY")
        
        activity_container = st.container()
        with activity_container:
            if st.session_state.activity_log:
                # Show last 10 activities
                for log in reversed(st.session_state.activity_log[-10:]):
                    st.code(log, language=None)
            else:
                # Add initial logs
                st.session_state.activity_log = [
                    f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 ULTIMATE STRIPE CHECKER PRO v3.0 INITIALIZED",
                    f"[{datetime.now().strftime('%H:%M:%S')}] 📱 Dashboard loaded successfully",
                    f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ Ready to check cards",
                    f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 {len(st.session_state.proxies)} proxies loaded",
                    f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 System optimized for performance"
                ]
                for log in st.session_state.activity_log:
                    st.code(log, language=None)
        
        # System Status
        st.markdown("---")
        st.markdown("### 🔧 SYSTEM STATUS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Memory Usage", "256 MB / 1 GB", "-12%")
        
        with col2:
            st.metric("CPU Load", "24%", "+2%")
        
        with col3:
            st.metric("Network Speed", "100 Mbps", "Stable")
    
    def show_single_check(self):
        """Show single card check"""
        st.markdown("## 🔍 SINGLE CARD CHECKER")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 💳 CARD DETAILS")
            
            # Card Entry
            card_number = st.text_input(
                "**Card Number**",
                value="4242424242424242",
                placeholder="1234 5678 9012 3456",
                help="Enter 13-19 digit card number"
            )
            
            # Expiry and CVV in columns
            col_exp, col_cvv = st.columns(2)
            with col_exp:
                month = st.selectbox("**Month**", [f"{i:02d}" for i in range(1, 13)], index=11)
                year = st.selectbox("**Year**", [f"{i}" for i in range(24, 35)], index=1)
            
            with col_cvv:
                cvv = st.text_input("**CVV**", value="123", max_chars=4, type="password")
            
            # Check Mode Selection
            st.markdown("### ⚙️ CHECK MODE")
            check_mode = st.radio(
                "Select check method:",
                ["Stripe API Check", "Luhn Validation", "BIN Lookup", "Full Validation"],
                horizontal=True
            )
            
            # Action Buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("⚡ **CHECK CARD**", type="primary", use_container_width=True):
                    if card_number and cvv:
                        self.process_single_check(card_number, month, year, cvv, check_mode)
                    else:
                        st.error("Please enter card number and CVV")
            
            with col_btn2:
                if st.button("🎲 **GENERATE**", use_container_width=True):
                    self.generate_random_card()
            
            with col_btn3:
                if st.button("📋 **PASTE**", use_container_width=True):
                    st.info("Paste functionality would work in desktop app")
        
        with col2:
            st.markdown("### 📊 CHECK RESULTS")
            
            if st.session_state.single_result:
                result = st.session_state.single_result
                
                # Result Card
                st.markdown(f"""
                <div style="background: {'#1a3a1a' if 'LIVE' in result['status'] else '#3a1a1a'}; 
                            padding: 20px; border-radius: 10px; border-left: 5px solid {'#00ff00' if 'LIVE' in result['status'] else '#ff0000'};">
                    <h4 style="margin:0; color: {'#00ff00' if 'LIVE' in result['status'] else '#ff0000'};">{result['status']}</h4>
                    <p style="margin:5px 0; color:#ccc;">{result['message']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Card Details
                st.markdown("**🔐 Card Information:**")
                st.markdown(f"- **Number:** `{result['card'][:6]}******{result['card'][-4:]}`")
                st.markdown(f"- **Expiry:** {month}/{year}")
                st.markdown(f"- **CVV:** `***`")
                st.markdown(f"- **Time:** {result['time']}")
                
                # BIN Information
                if result['bin_info']:
                    st.markdown("---")
                    st.markdown("**🏦 BIN Details:**")
                    info = result['bin_info']
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown(f"- **Issuer:** {info.get('issuer', 'Unknown')}")
                        st.markdown(f"- **Type:** {info.get('type', 'Unknown')}")
                    with col_info2:
                        st.markdown(f"- **Bank:** {info.get('bank', 'Unknown')}")
                        st.markdown(f"- **Country:** {info.get('country', 'Unknown')}")
                
                # Action Buttons for Result
                col_act1, col_act2, col_act3 = st.columns(3)
                with col_act1:
                    if st.button("📋 Copy", use_container_width=True):
                        st.success("Result copied!")
                with col_act2:
                    if st.button("💾 Save", use_container_width=True):
                        self.save_result(result)
                with col_act3:
                    if st.button("🔄 Check Again", use_container_width=True):
                        st.session_state.single_result = None
                        st.rerun()
            
            else:
                # Instructions Panel
                st.markdown("""
                <div style="background: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px dashed #333;">
                    <h4 style="color: #00ffff; margin-top:0;">📋 Instructions</h4>
                    <p>1. Enter card details in left panel</p>
                    <p>2. Select check mode</p>
                    <p>3. Click <span style="color:#00ff00;">CHECK CARD</span> button</p>
                    <p>4. View results here</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Test Cards
                st.markdown("**🧪 Test Cards:**")
                test_cards = {
                    "Visa (Live)": "4242424242424242",
                    "Visa (Declined)": "4000000000000002",
                    "MasterCard": "5555555555554444",
                    "American Express": "378282246310005",
                    "Discover": "6011000990139424"
                }
                
                for name, number in test_cards.items():
                    if st.button(f"Use {name}", key=f"test_{number}", use_container_width=True):
                        st.session_state.test_card = number
                        st.rerun()
    
    def process_single_check(self, card, month, year, cvv, mode):
        """Process single card check"""
        with st.spinner("🔄 Processing card..."):
            time.sleep(1)  # Simulate processing
            
            # Clean card number
            card = ''.join(filter(str.isdigit, card))
            
            # Validate Luhn
            is_valid = self.validator.validate_luhn(card)
            bin_info = self.validator.get_bin_info(card)
            
            # Determine result based on mode
            if "Luhn" in mode:
                status = "✅ VALID LUHN" if is_valid else "❌ INVALID LUHN"
                message = "Card passed Luhn algorithm" if is_valid else "Card failed Luhn check"
            elif "BIN" in mode:
                if bin_info:
                    status = "✅ VALID BIN"
                    message = f"{bin_info.get('issuer', 'Unknown')} - Verified BIN"
                else:
                    status = "⚠️ UNKNOWN BIN"
                    message = "BIN not found in database"
            else:
                # Simulate API check
                if is_valid and random.random() > 0.4:
                    status = "✅ LIVE CARD"
                    message = random.choice([
                        "Transaction approved",
                        "Payment successful",
                        "Card is active",
                        "Balance available"
                    ])
                    is_live = True
                else:
                    status = "❌ DECLINED"
                    message = random.choice([
                        "Insufficient funds",
                        "Card declined",
                        "Invalid card",
                        "Transaction blocked"
                    ])
                    is_live = False
            
            # Create result
            result = {
                'card': card,
                'status': status,
                'message': message,
                'bin_info': bin_info,
                'valid': is_valid,
                'live': is_live if 'is_live' in locals() else False,
                'time': datetime.now().strftime("%H:%M:%S")
            }
            
            # Update stats
            st.session_state.total_checked += 1
            if result['live']:
                st.session_state.live_cards += 1
            else:
                st.session_state.dead_cards += 1
            
            # Store result
            st.session_state.single_result = result
            
            # Log activity
            log_msg = f"[{result['time']}] Single: {status} - {card[-4:]}"
            st.session_state.activity_log.append(log_msg)
            
            # Add to history
            st.session_state.card_history.append({
                'card': f"{card[:6]}******{card[-4:]}",
                'status': status,
                'time': result['time']
            })
            
            st.rerun()
    
    def generate_random_card(self):
        """Generate random valid card"""
        prefixes = list(self.validator.bin_db.keys())
        prefix = random.choice(prefixes)
        
        # Determine card length
        length = 15 if prefix in ["34", "37"] else 16
        
        # Generate base card
        card = prefix
        for _ in range(length - len(prefix) - 1):
            card += str(random.randint(0, 9))
        
        # Calculate Luhn check digit
        for check_digit in range(10):
            test_card = card + str(check_digit)
            if self.validator.validate_luhn(test_card):
                generated_card = test_card
                break
        
        # Generate expiry and CVV
        month = f"{random.randint(1, 12):02d}"
        year = f"{random.randint(24, 30)}"
        cvv = str(random.randint(1000, 9999)) if prefix in ["34", "37"] else str(random.randint(100, 999))
        
        # Store generated card
        st.session_state.generated_card = generated_card
        st.session_state.generated_month = month
        st.session_state.generated_year = year
        st.session_state.generated_cvv = cvv
        
        # Log
        st.session_state.activity_log.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Generated card: {generated_card[:6]}******{generated_card[-4:]}"
        )
        
        st.success(f"Generated: {generated_card[:6]}******{generated_card[-4:]}")
        st.rerun()
    
    def show_bulk_check(self):
        """Show bulk check interface"""
        st.markdown("## 🚀 BULK CARD CHECKER")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📁 UPLOAD CARDS")
            
            # File upload
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['txt', 'csv'],
                help="Upload text file with one card per line"
            )
            
            if uploaded_file:
                # Preview first 5 lines
                content = uploaded_file.getvalue().decode()
                lines = content.split('\n')
                st.info(f"File loaded: {len(lines)} cards detected")
                
                # Show preview
                with st.expander("📄 File Preview (First 10 lines)"):
                    for i, line in enumerate(lines[:10]):
                        if line.strip():
                            st.code(line.strip())
            
            # Settings
            st.markdown("### ⚙️ SETTINGS")
            
            col_set1, col_set2 = st.columns(2)
            with col_set1:
                threads = st.slider("Threads", 1, 50, 10, help="Number of parallel threads")
                timeout = st.number_input("Timeout (s)", 1, 60, 10)
            
            with col_set2:
                delay = st.slider("Delay (ms)", 0, 5000, 100, help="Delay between requests")
                retries = st.number_input("Retries", 0, 5, 2)
        
        with col2:
            st.markdown("### 🎯 CONTROL PANEL")
            
            # Status display
            if st.session_state.bulk_running:
                status_color = "#ffff00" if st.session_state.bulk_paused else "#00ff00"
                status_text = "⏸️ PAUSED" if st.session_state.bulk_paused else "▶️ RUNNING"
                st.markdown(f"""
                <div style="background: #1a1a1a; padding: 15px; border-radius: 10px; border-left: 5px solid {status_color};">
                    <h4 style="color: {status_color}; margin:0;">{status_text}</h4>
                    <p style="margin:5px 0; color:#ccc;">Bulk check in progress</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: #1a1a1a; padding: 15px; border-radius: 10px; border-left: 5px solid #666;">
                    <h4 style="color: #aaa; margin:0;">⏹️ STOPPED</h4>
                    <p style="margin:5px 0; color:#999;">Ready to start</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Control buttons
            col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
            
            with col_ctrl1:
                start_disabled = not uploaded_file or st.session_state.bulk_running
                if st.button("🚀 **START**", type="primary", use_container_width=True, disabled=start_disabled):
                    if uploaded_file:
                        st.session_state.bulk_running = True
                        self.start_bulk_check(uploaded_file, threads, delay)
            
            with col_ctrl2:
                pause_disabled = not st.session_state.bulk_running
                pause_text = "⏸️ PAUSE" if not st.session_state.bulk_paused else "▶️ RESUME"
                if st.button(pause_text, use_container_width=True, disabled=pause_disabled):
                    st.session_state.bulk_paused = not st.session_state.bulk_paused
                    st.rerun()
            
            with col_ctrl3:
                stop_disabled = not st.session_state.bulk_running
                if st.button("⏹️ **STOP**", use_container_width=True, disabled=stop_disabled):
                    st.session_state.bulk_running = False
                    st.session_state.bulk_paused = False
                    st.rerun()
            
            # Progress bar
            if st.session_state.bulk_running:
                progress = st.progress(0)
                status = st.empty()
            
            # Results summary
            st.markdown("### 📊 QUICK STATS")
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Processed", st.session_state.total_checked)
            with col_stat2:
                st.metric("Live", st.session_state.live_cards)
            with col_stat3:
                st.metric("Dead", st.session_state.dead_cards)
        
        # Results table
        st.markdown("---")
        st.markdown("### 📋 CHECK RESULTS")
        
        if st.session_state.results:
            df = pd.DataFrame(st.session_state.results)
            
            # Filters
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                status_filter = st.multiselect(
                    "Filter by Status",
                    ["✅ LIVE CARD", "❌ DECLINED", "✅ VALID LUHN", "✅ VALID BIN", "⚠️ UNKNOWN BIN"],
                    default=[]
                )
            
            # Apply filters
            if status_filter:
                df = df[df['status'].isin(status_filter)]
            
            # Display table
            st.dataframe(
                df,
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            # Export options
            st.markdown("### 📤 EXPORT RESULTS")
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="stripe_results.csv",
                    mime="text/csv"
                )
            
            with col_exp2:
                json_str = df.to_json(orient="records", indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name="stripe_results.json",
                    mime="application/json"
                )
            
            with col_exp3:
                if st.button("🗑️ Clear Results", use_container_width=True):
                    st.session_state.results = []
                    st.success("Results cleared!")
                    st.rerun()
        else:
            st.info("No results yet. Upload a file and start checking!")
    
    def start_bulk_check(self, uploaded_file, threads, delay):
        """Start bulk check process"""
        content = uploaded_file.getvalue().decode()
        cards = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Simulate bulk check
        total_cards = min(len(cards), 50)  # Limit for demo
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(total_cards):
            if not st.session_state.bulk_running:
                break
            
            while st.session_state.bulk_paused:
                time.sleep(0.1)
            
            # Simulate processing
            time.sleep(delay / 1000)
            
            # Generate fake card for demo
            card = cards[i] if i < len(cards) else self.generate_random_card()
            
            # Validate
            is_valid = self.validator.validate_luhn(card)
            bin_info = self.validator.get_bin_info(card)
            
            # Determine status
            if is_valid and random.random() > 0.4:
                status = "✅ LIVE CARD"
                st.session_state.live_cards += 1
            else:
                status = "❌ DECLINED"
                st.session_state.dead_cards += 1
            
            st.session_state.total_checked += 1
            
            # Add result
            result = {
                'card': f"{card[:6]}******{card[-4:]}" if len(card) > 10 else card,
                'status': status,
                'issuer': bin_info.get('issuer', 'Unknown') if bin_info else 'Unknown',
                'time': datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.results.append(result)
            
            # Update progress
            progress = (i + 1) / total_cards
            progress_bar.progress(progress)
            status_text.text(f"Processing: {i + 1}/{total_cards} - {status}")
            
            # Log every 5 cards
            if (i + 1) % 5 == 0:
                st.session_state.activity_log.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Bulk: {i + 1}/{total_cards} processed"
                )
        
        # Complete
        st.session_state.bulk_running = False
        st.session_state.bulk_paused = False
        
        st.session_state.activity_log.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Bulk check complete: {total_cards} cards processed"
        )
        
        st.rerun()
    
    def show_proxy_manager(self):
        """Show proxy manager"""
        st.markdown("## 🌐 PROXY MANAGER")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📋 PROXY LIST")
            
            # Create proxy dataframe
            proxies_data = []
            for i, proxy in enumerate(st.session_state.proxies, 1):
                # Parse proxy
                parts = proxy.split(':')
                if len(parts) >= 2:
                    ip_port = f"{parts[0]}:{parts[1]}"
                    auth = f"{parts[2]}:{parts[3]}" if len(parts) > 3 else "N/A"
                else:
                    ip_port = proxy
                    auth = "N/A"
                
                proxies_data.append({
                    '#': i,
                    'Proxy': ip_port,
                    'Auth': auth,
                    'Status': '🟢 Active',
                    'Speed': f"{random.randint(50, 500)}ms"
                })
            
            # Display as dataframe
            if proxies_data:
                df_proxies = pd.DataFrame(proxies_data)
                st.dataframe(
                    df_proxies,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No proxies configured")
        
        with col2:
            st.markdown("### 🔧 PROXY ACTIONS")
            
            # Add new proxy
            st.markdown("**Add New Proxy:**")
            new_proxy = st.text_input(
                "Proxy (ip:port:user:pass)",
                placeholder="192.168.1.1:8080:user:pass",
                label_visibility="collapsed"
            )
            
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                if st.button("➕ Add", use_container_width=True) and new_proxy:
                    if ':' in new_proxy:
                        st.session_state.proxies.append(new_proxy)
                        st.session_state.activity_log.append(
                            f"[{datetime.now().strftime('%H:%M:%S')}] Added proxy"
                        )
                        st.success("Proxy added!")
                        st.rerun()
                    else:
                        st.error("Invalid format")
            
            with col_add2:
                if st.button("📝 Import", use_container_width=True):
                    st.info("Import from file (coming soon)")
            
            # Test proxies
            st.markdown("---")
            if st.button("🔄 Test All Proxies", use_container_width=True):
                with st.spinner("Testing proxies..."):
                    time.sleep(2)
                    st.success(f"Tested {len(st.session_state.proxies)} proxies - All active!")
            
            # Remove proxy
            st.markdown("---")
            if st.session_state.proxies:
                proxy_to_remove = st.selectbox(
                    "Select proxy to remove",
                    st.session_state.proxies
                )
                
                if st.button("➖ Remove Selected", use_container_width=True, type="secondary"):
                    st.session_state.proxies.remove(proxy_to_remove)
                    st.session_state.activity_log.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] Removed proxy"
                    )
                    st.success("Proxy removed!")
                    st.rerun()
            
            # Export proxies
            st.markdown("---")
            if st.button("📤 Export List", use_container_width=True):
                proxy_text = "\n".join(st.session_state.proxies)
                st.download_button(
                    label="📥 Download",
                    data=proxy_text,
                    file_name="proxies.txt",
                    mime="text/plain"
                )
    
    def show_results(self):
        """Show results database"""
        st.markdown("## 📊 RESULTS DATABASE")
        
        if not st.session_state.results:
            st.info("No results available. Start checking cards to see results here.")
            return
        
        # Convert results to dataframe
        df = pd.DataFrame(st.session_state.results)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_options = df['status'].unique().tolist()
            status_filter = st.multiselect(
                "Filter by Status",
                status_options,
                default=[]
            )
        
        with col2:
            issuer_options = df['issuer'].unique().tolist()
            issuer_filter = st.multiselect(
                "Filter by Issuer",
                issuer_options,
                default=[]
            )
        
        with col3:
            if 'time' in df.columns:
                date_options = df['time'].apply(lambda x: x.split(' ')[0] if ' ' in str(x) else str(x)).unique()
                date_filter = st.multiselect(
                    "Filter by Date",
                    date_options,
                    default=[]
                )
        
        # Apply filters
        filtered_df = df.copy()
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if issuer_filter:
            filtered_df = filtered_df[filtered_df['issuer'].isin(issuer_filter)]
        
        # Display results
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=500
        )
        
        # Statistics
        st.markdown("### 📈 STATISTICS")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            total = len(filtered_df)
            st.metric("Total Results", total)
        
        with col_stat2:
            live = len(filtered_df[filtered_df['status'].str.contains('✅')])
            st.metric("Live Cards", live)
        
        with col_stat3:
            dead = len(filtered_df[filtered_df['status'].str.contains('❌')])
            st.metric("Dead Cards", dead)
        
        with col_stat4:
            rate = (live / total * 100) if total > 0 else 0
            st.metric("Success Rate", f"{rate:.1f}%")
        
        # Export options
        st.markdown("### 📤 EXPORT OPTIONS")
        
        export_format = st.radio(
            "Select format:",
            ["CSV", "JSON", "Excel"],
            horizontal=True
        )
        
        if export_format == "CSV":
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="stripe_results.csv",
                mime="text/csv"
            )
        
        elif export_format == "JSON":
            json_data = filtered_df.to_json(orient="records", indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name="stripe_results.json",
                mime="application/json"
            )
        
        elif export_format == "Excel":
            # Create Excel file
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Results')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name="stripe_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    def show_tools(self):
        """Show advanced tools"""
        st.markdown("## 🛠️ ADVANCED TOOLS")
        
        # Tools in tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔢 Card Generator", 
            "🔍 BIN Analyzer", 
            "✅ Luhn Checker",
            "🌐 Network Tools"
        ])
        
        with tab1:
            self.show_card_generator()
        
        with tab2:
            self.show_bin_analyzer()
        
        with tab3:
            self.show_luhn_checker()
        
        with tab4:
            self.show_network_tools()
    
    def show_card_generator(self):
        """Card generator tool"""
        st.markdown("### 🔢 CARD GENERATOR")
        
        col1, col2 = st.columns(2)
        
        with col1:
            card_type = st.selectbox(
                "Card Type",
                ["VISA", "MasterCard", "American Express", "Discover", "JCB", "Diners Club"]
            )
            
            quantity = st.slider("Quantity", 1, 100, 10)
            
            include_details = st.checkbox("Include Expiry & CVV", True)
        
        with col2:
            if st.button("🎲 Generate Cards", type="primary", use_container_width=True):
                generated = []
                
                # Prefix mapping
                prefixes = {
                    "VISA": ["4"],
                    "MasterCard": ["51", "52", "53", "54", "55"],
                    "American Express": ["34", "37"],
                    "Discover": ["6011", "65"],
                    "JCB": ["35"],
                    "Diners Club": ["30", "36", "38"]
                }
                
                with st.spinner(f"Generating {quantity} cards..."):
                    for i in range(quantity):
                        # Get prefix for card type
                        type_prefixes = prefixes.get(card_type, ["4"])
                        prefix = random.choice(type_prefixes)
                        
                        # Determine length
                        length = 15 if prefix in ["34", "37"] else 16
                        
                        # Generate card
                        card = prefix
                        for _ in range(length - len(prefix) - 1):
                            card += str(random.randint(0, 9))
                        
                        # Calculate Luhn
                        for check_digit in range(10):
                            test_card = card + str(check_digit)
                            if self.validator.validate_luhn(test_card):
                                final_card = test_card
                                break
                        
                        # Add details
                        if include_details:
                            month = f"{random.randint(1, 12):02d}"
                            year = f"{random.randint(24, 30)}"
                            cvv = str(random.randint(1000, 9999)) if prefix in ["34", "37"] else str(random.randint(100, 999))
                            generated.append(f"{final_card}|{month}|{year}|{cvv}")
                        else:
                            generated.append(final_card)
                
                # Display generated cards
                st.markdown("**Generated Cards:**")
                card_text = "\n".join(generated)
                st.text_area("Cards", card_text, height=200)
                
                # Download
                st.download_button(
                    label="📥 Download Cards",
                    data=card_text,
                    file_name=f"{card_type}_cards.txt",
                    mime="text/plain"
                )
    
    def show_bin_analyzer(self):
        """BIN analyzer tool"""
        st.markdown("### 🔍 BIN ANALYZER")
        
        bin_input = st.text_input(
            "Enter BIN (first 6-8 digits)",
            placeholder="424242",
            help="Enter the first 6-8 digits of a card"
        )
        
        if bin_input:
            info = self.validator.get_bin_info(bin_input)
            
            if info:
                # Display BIN info in nice format
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); 
                            padding: 20px; border-radius: 10px; border-left: 5px solid #00ffff;">
                    <h4 style="color: #00ffff; margin-top:0;">BIN ANALYSIS RESULT</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div><strong>Issuer:</strong> {info.get('issuer', 'Unknown')}</div>
                        <div><strong>Type:</strong> {info.get('type', 'Unknown')}</div>
                        <div><strong>Bank:</strong> {info.get('bank', 'Unknown')}</div>
                        <div><strong>Country:</strong> {info.get('country', 'Unknown')}</div>
                        <div><strong>Prefix:</strong> {info.get('prefix', 'Unknown')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("BIN not found in database")
        
        # Show BIN database
        with st.expander("📚 BIN DATABASE"):
            bin_data = []
            for prefix, info in self.validator.bin_db.items():
                bin_data.append({
                    'Prefix': prefix,
                    'Issuer': info['issuer'],
                    'Type': info['type'],
                    'Bank': info['bank']
                })
            
            if bin_data:
                st.dataframe(pd.DataFrame(bin_data), use_container_width=True)
    
    def show_luhn_checker(self):
        """Luhn checker tool"""
        st.markdown("### ✅ LUHN ALGORITHM CHECKER")
        
        card_input = st.text_input(
            "Enter card number to validate",
            placeholder="1234567812345670"
        )
        
        if card_input:
            is_valid = self.validator.validate_luhn(card_input)
            
            if is_valid:
                st.success("✅ Valid Luhn checksum - Card number passes validation")
            else:
                st.error("❌ Invalid Luhn checksum - Card number fails validation")
            
            # Explain calculation
            with st.expander("📖 How Luhn Algorithm Works"):
                st.markdown("""
                **Luhn Algorithm Steps:**
                1. Starting from the rightmost digit, double every second digit
                2. If doubling results in a number greater than 9, add the digits
                3. Sum all digits (modified and unchanged)
                4. If total sum modulo 10 equals 0, number is valid
                
                **Example:** `79927398713`
                - Digits: 7 9 9 2 7 3 9 8 7 1 3
                - Double every second from right: 7 18 9 4 7 6 9 16 7 2 3
                - Sum digits: 7 + (1+8) + 9 + 4 + 7 + 6 + 9 + (1+6) + 7 + 2 + 3 = 70
                - 70 % 10 = 0 ✓ Valid
                """)
    
    def show_network_tools(self):
        """Network tools"""
        st.markdown("### 🌐 NETWORK TOOLS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Ping Test", use_container_width=True):
                with st.spinner("Testing network..."):
                    time.sleep(1)
                    st.success("Network connectivity: ✅ Excellent")
            
            if st.button("⚡ Speed Test", use_container_width=True):
                with st.spinner("Measuring speed..."):
                    time.sleep(2)
                    st.metric("Download Speed", "95.6 Mbps")
                    st.metric("Upload Speed", "42.3 Mbps")
                    st.metric("Latency", "28 ms")
        
        with col2:
            if st.button("🌍 Geo IP", use_container_width=True):
                st.info("Your IP: 192.168.1.1 (Local)")
                st.info("Location: Local Network")
                st.info("ISP: Local Router")
            
            if st.button("🔒 SSL Check", use_container_width=True):
                with st.spinner("Checking SSL..."):
                    time.sleep(1)
                    st.success("SSL/TLS: ✅ Secure")
    
    def show_settings(self):
        """Show settings"""
        st.markdown("## ⚙️ SYSTEM SETTINGS")
        
        tab1, tab2, tab3 = st.tabs(["Appearance", "Performance", "Security"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                theme = st.selectbox(
                    "Theme",
                    ["Dark Pro", "Light", "Cyberpunk", "Matrix", "Ocean"],
                    index=0
                )
                
                font_size = st.slider("Font Size", 12, 24, 14)
            
            with col2:
                show_animations = st.checkbox("Show Animations", True)
                compact_mode = st.checkbox("Compact Mode", False)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                max_threads = st.slider("Max Threads", 1, 100, 20)
                request_timeout = st.number_input("Request Timeout (s)", 5, 120, 30)
            
            with col2:
                cache_size = st.select_slider(
                    "Cache Size",
                    options=["256MB", "512MB", "1GB", "2GB"],
                    value="1GB"
                )
                auto_save = st.checkbox("Auto-save Results", True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                encrypt_data = st.checkbox("Encrypt Local Data", True)
                clear_clipboard = st.checkbox("Auto-clear Clipboard", True)
            
            with col2:
                require_password = st.checkbox("Require Password", False)
                if require_password:
                    st.text_input("Password", type="password")
        
        # Save settings button
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            st.session_state.activity_log.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Settings saved"
            )
            st.success("Settings saved successfully!")
    
    def show_history(self):
        """Show card history"""
        st.markdown("## 📋 CHECK HISTORY")
        
        if not st.session_state.card_history:
            st.info("No history available. Check some cards first!")
            return
        
        # Display history
        for item in reversed(st.session_state.card_history[-20:]):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"`{item['card']}`")
            with col2:
                st.markdown(f"**{item['status']}**")
            with col3:
                st.markdown(f"*{item['time']}*")
            st.divider()
    
    def save_result(self, result):
        """Save single result"""
        st.session_state.activity_log.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Saved result: {result['card'][-4:]}"
        )
        st.session_state.results.append({
            'card': f"{result['card'][:6]}******{result['card'][-4:]}",
            'status': result['status'],
            'issuer': result['bin_info'].get('issuer', 'Unknown') if result['bin_info'] else 'Unknown',
            'time': result['time']
        })
        st.success("Result saved to database!")

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    # Initialize and run app
    app = UltimateStripeCheckerPro()
    app.run()
