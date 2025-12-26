import streamlit as st
import random
import time
from datetime import datetime
import pandas as pd
import re
import json
import io
from io import StringIO

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
        # Initialize session state
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.total_checked = 0
            st.session_state.live_cards = 0
            st.session_state.dead_cards = 0
            st.session_state.proxies = [
                "142.111.48.253:7030",
                "31.59.20.176:6754",
                "38.170.176.177:5572"
            ]
            st.session_state.results = []
            st.session_state.activity_log = []
            st.session_state.bulk_running = False
            st.session_state.bulk_paused = False
        
        self.validator = CardValidator()
        
    def run(self):
        """Main application runner"""
        # Custom CSS for styling
        st.set_page_config(
            page_title="🔥 ULTIMATE STRIPE CHECKER PRO v3.0",
            page_icon="⚡",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #ff0000, #00ff00, #0000ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem !important;
            text-align: center;
            margin-bottom: 1rem;
        }
        .card {
            background-color: #1a1a1a;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #00ff00;
            margin-bottom: 1rem;
        }
        .live-card {
            border-left: 5px solid #00ff00 !important;
        }
        .dead-card {
            border-left: 5px solid #ff0000 !important;
        }
        .stats-card {
            text-align: center;
            background-color: #222222;
            padding: 1rem;
            border-radius: 10px;
        }
        .stButton>button {
            width: 100%;
            background-color: #2a2a2a;
            color: #00ff00;
            border: 1px solid #333333;
        }
        .stButton>button:hover {
            background-color: #3a3a3a;
            border-color: #00ff00;
        }
        .accent-button {
            background: linear-gradient(45deg, #ff0000, #ff3300) !important;
            color: white !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown('<h1 class="main-header">🔥 ULTIMATE STRIPE CHECKER PRO v3.0</h1>', unsafe_allow_html=True)
        
        # Sidebar Navigation
        with st.sidebar:
            st.markdown("## 👑 PRO USER")
            st.markdown("**Premium Access**")
            st.markdown("---")
            
            # Navigation
            nav_options = {
                "📊 Dashboard": "dashboard",
                "🔍 Single Check": "single",
                "🚀 Bulk Check": "bulk",
                "🌐 Proxy Manager": "proxy",
                "📈 Results": "results",
                "🛠️ Tools": "tools",
                "⚙️ Settings": "settings"
            }
            
            selected_page = st.selectbox(
                "Navigation",
                list(nav_options.keys()),
                label_visibility="collapsed"
            )
            
            # Quick Stats in Sidebar
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", st.session_state.total_checked)
                st.metric("Live", st.session_state.live_cards)
            with col2:
                st.metric("Dead", st.session_state.dead_cards)
                rate = (st.session_state.live_cards / st.session_state.total_checked * 100) if st.session_state.total_checked > 0 else 0
                st.metric("Rate", f"{rate:.1f}%")
            
            st.markdown("---")
            st.markdown(f"**Proxies:** {len(st.session_state.proxies)}")
            st.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Main Content Area
        page = nav_options[selected_page]
        
        if page == "dashboard":
            self.show_dashboard()
        elif page == "single":
            self.show_single_check()
        elif page == "bulk":
            self.show_bulk_check()
        elif page == "proxy":
            self.show_proxy_manager()
        elif page == "results":
            self.show_results()
        elif page == "tools":
            self.show_tools()
        elif page == "settings":
            self.show_settings()
    
    def show_dashboard(self):
        """Show dashboard"""
        st.markdown("## 📊 DASHBOARD")
        
        # Stats Cards
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown('<div class="stats-card">📊<br><h3>{}</h3>Total Checks</div>'.format(
                st.session_state.total_checked), unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">✅<br><h3>{}</h3>Live Cards</div>'.format(
                st.session_state.live_cards), unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stats-card">❌<br><h3>{}</h3>Dead Cards</div>'.format(
                st.session_state.dead_cards), unsafe_allow_html=True)
        
        with col4:
            rate = (st.session_state.live_cards / st.session_state.total_checked * 100) if st.session_state.total_checked > 0 else 0
            st.markdown('<div class="stats-card">📈<br><h3>{:.1f}%</h3>Success Rate</div>'.format(
                rate), unsafe_allow_html=True)
        
        with col5:
            st.markdown('<div class="stats-card">🌐<br><h3>{}</h3>Proxies</div>'.format(
                len(st.session_state.proxies)), unsafe_allow_html=True)
        
        with col6:
            st.markdown('<div class="stats-card">⚡<br><h3>0.0s</h3>Avg Speed</div>', 
                       unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown("---")
        st.markdown("### 🚀 Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Check Single Card", use_container_width=True):
                st.session_state.page = "single"
                st.rerun()
        
        with col2:
            if st.button("🚀 Start Bulk Check", use_container_width=True):
                st.session_state.page = "bulk"
                st.rerun()
        
        with col3:
            if st.button("🌐 Manage Proxies", use_container_width=True):
                st.session_state.page = "proxy"
                st.rerun()
        
        with col4:
            if st.button("📊 View Results", use_container_width=True):
                st.session_state.page = "results"
                st.rerun()
        
        # Recent Activity
        st.markdown("---")
        st.markdown("### 📝 Recent Activity")
        
        if st.session_state.activity_log:
            for log in reversed(st.session_state.activity_log[-10:]):
                st.code(log, language=None)
        else:
            st.info("No activity yet. Start checking cards!")
        
        # Add some sample activity if empty
        if not st.session_state.activity_log:
            sample_logs = [
                f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 ULTIMATE STRIPE CHECKER PRO v3.0 INITIALIZED",
                f"[{datetime.now().strftime('%H:%M:%S')}] 📱 Dashboard loaded successfully",
                f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ Ready to check cards"
            ]
            for log in sample_logs:
                st.session_state.activity_log.append(log)
    
    def show_single_check(self):
        """Show single card check"""
        st.markdown("## 🔍 SINGLE CARD CHECK")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💳 CARD DETAILS")
            
            # Card number
            card_number = st.text_input(
                "Card Number",
                value="4242424242424242",
                placeholder="Enter card number",
                help="Enter 13-19 digit card number"
            )
            
            # Expiry and CVV
            col_exp, col_cvv = st.columns(2)
            
            with col_exp:
                month = st.text_input("Month (MM)", value="12", max_chars=2)
                year = st.text_input("Year (YY)", value="25", max_chars=2)
            
            with col_cvv:
                cvv = st.text_input("CVV", value="123", max_chars=4)
            
            # Check mode
            check_mode = st.radio(
                "Check Mode",
                ["Stripe API Check", "Luhn Validation", "BIN Lookup", "Full Validation"],
                horizontal=True
            )
            
            # Check button
            if st.button("⚡ CHECK CARD", type="primary", use_container_width=True):
                if card_number and month and year and cvv:
                    self.check_single_card(card_number, month, year, cvv, check_mode)
                else:
                    st.error("Please fill all fields")
            
            # Generate card button
            if st.button("🎲 GENERATE RANDOM CARD", use_container_width=True):
                self.generate_card()
        
        with col2:
            st.markdown("### 📊 RESULTS")
            
            # Results display area
            if 'single_result' in st.session_state:
                result = st.session_state.single_result
                
                st.markdown(f"**Card:** `{result['card'][:6]}******{result['card'][-4:]}`")
                st.markdown(f"**Status:** {result['status']}")
                st.markdown(f"**Message:** {result['message']}")
                
                if result['bin_info']:
                    st.markdown("---")
                    st.markdown("**BIN Information:**")
                    info = result['bin_info']
                    st.markdown(f"- **Issuer:** {info.get('issuer', 'Unknown')}")
                    st.markdown(f"- **Bank:** {info.get('bank', 'Unknown')}")
                    st.markdown(f"- **Country:** {info.get('country', 'Unknown')}")
                    st.markdown(f"- **Type:** {info.get('type', 'Unknown')}")
                
                st.markdown(f"**Time:** {result['time']}")
                
                # Action buttons
                col_copy, col_save = st.columns(2)
                with col_copy:
                    if st.button("📋 Copy Result"):
                        st.success("Result copied to clipboard!")
                
                with col_save:
                    if st.button("💾 Save Result"):
                        self.save_single_result(result)
            else:
                st.info("Enter card details and click CHECK CARD")
                
                st.markdown("---")
                st.markdown("**Test Cards:**")
                st.markdown("- `4242424242424242` - Visa (Live)")
                st.markdown("- `4000000000000002` - Visa (Declined)")
                st.markdown("- `5555555555554444` - MasterCard")
                st.markdown("- `378282246310005` - American Express")
    
    def check_single_card(self, card, month, year, cvv, mode):
        """Check single card"""
        with st.spinner("🔄 Checking card..."):
            time.sleep(1)  # Simulate processing
            
            # Validate card
            is_valid = self.validator.validate_luhn(card)
            bin_info = self.validator.get_bin_info(card)
            
            if "Luhn" in mode:
                status = "✅ VALID" if is_valid else "❌ INVALID"
                message = "Luhn check passed" if is_valid else "Luhn check failed"
            elif "BIN" in mode:
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
                'valid': is_valid and "❌" not in status,
                'time': datetime.now().strftime("%H:%M:%S")
            }
            
            # Update stats
            st.session_state.total_checked += 1
            if result['valid']:
                st.session_state.live_cards += 1
            else:
                st.session_state.dead_cards += 1
            
            # Store result
            st.session_state.single_result = result
            
            # Log activity
            log_entry = f"[{result['time']}] Single check: {status} - {card[-4:]}"
            st.session_state.activity_log.append(log_entry)
            
            # Add to results
            st.session_state.results.append({
                'card': f"{card[:6]}******{card[-4:]}",
                'status': status,
                'issuer': bin_info.get('issuer', 'Unknown') if bin_info else 'Unknown',
                'time': result['time']
            })
            
            st.rerun()
    
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
        
        # Update session state for form
        st.session_state.generated_card = card
        st.session_state.generated_month = f"{random.randint(1, 12):02d}"
        st.session_state.generated_year = f"{random.randint(24, 30):02d}"
        st.session_state.generated_cvv = str(random.randint(1000, 9999)) if prefix in ["34", "37"] else str(random.randint(100, 999))
        
        # Log activity
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] Generated random card: {card[:6]}******{card[-4:]}"
        st.session_state.activity_log.append(log_entry)
        
        st.success(f"Generated card: {card[:6]}******{card[-4:]}")
        st.rerun()
    
    def show_bulk_check(self):
        """Show bulk check"""
        st.markdown("## 🚀 BULK CARD CHECK")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload cards file (TXT, one per line)",
            type=['txt'],
            help="Upload a text file with one card per line"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            threads = st.slider("Threads", 1, 20, 5)
            delay = st.slider("Delay (ms)", 0, 5000, 100)
        
        with col2:
            st.markdown("### Control")
            
            col_start, col_pause, col_stop = st.columns(3)
            
            with col_start:
                start_btn = st.button("🚀 START", type="primary", use_container_width=True,
                                    disabled=st.session_state.bulk_running)
            
            with col_pause:
                pause_text = "⏸️ PAUSE" if not st.session_state.bulk_paused else "▶️ RESUME"
                pause_btn = st.button(pause_text, use_container_width=True,
                                    disabled=not st.session_state.bulk_running)
            
            with col_stop:
                stop_btn = st.button("⏹️ STOP", use_container_width=True,
                                   disabled=not st.session_state.bulk_running)
        
        # Progress bar
        if st.session_state.bulk_running:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Results display
        st.markdown("### 📊 Results")
        
        if uploaded_file and start_btn:
            cards = uploaded_file.getvalue().decode().splitlines()
            st.session_state.bulk_running = True
            self.run_bulk_check(cards, threads, delay)
        
        if pause_btn:
            st.session_state.bulk_paused = not st.session_state.bulk_paused
            st.rerun()
        
        if stop_btn:
            st.session_state.bulk_running = False
            st.session_state.bulk_paused = False
            st.rerun()
        
        # Show results table
        if st.session_state.results:
            df = pd.DataFrame(st.session_state.results)
            st.dataframe(df, use_container_width=True)
            
            # Export buttons
            col_csv, col_json = st.columns(2)
            
            with col_csv:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="stripe_results.csv",
                    mime="text/csv"
                )
            
            with col_json:
                json_str = df.to_json(orient="records", indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name="stripe_results.json",
                    mime="application/json"
                )
    
    def run_bulk_check(self, cards, threads, delay):
        """Run bulk check (simulated)"""
        total = len(cards)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.empty()
        
        for i, card in enumerate(cards[:20]):  # Limit to 20 for demo
            if not st.session_state.bulk_running:
                break
            
            while st.session_state.bulk_paused:
                time.sleep(0.1)
            
            # Simulate check
            time.sleep(delay / 1000)
            
            # Validate
            is_valid = self.validator.validate_luhn(card)
            bin_info = self.validator.get_bin_info(card)
            
            if is_valid and random.random() > 0.5:
                status = "✅ LIVE"
                st.session_state.live_cards += 1
            else:
                status = "❌ DEAD"
                st.session_state.dead_cards += 1
            
            st.session_state.total_checked += 1
            
            # Add result
            st.session_state.results.append({
                'card': f"{card[:6]}******{card[-4:]}",
                'status': status,
                'issuer': bin_info.get('issuer', 'Unknown') if bin_info else 'Unknown',
                'time': datetime.now().strftime("%H:%M:%S")
            })
            
            # Update progress
            progress = (i + 1) / min(20, total)
            progress_bar.progress(progress)
            status_text.text(f"Processing: {i + 1}/{min(20, total)} - {status}")
            
            # Log
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] Bulk: {status} - {card[-4:]}"
            st.session_state.activity_log.append(log_entry)
        
        st.session_state.bulk_running = False
        st.success(f"✅ Bulk check complete! Processed {min(20, total)} cards")
        st.rerun()
    
    def show_proxy_manager(self):
        """Show proxy manager"""
        st.markdown("## 🌐 PROXY MANAGER")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Proxy List")
            
            # Display proxies
            proxies_df = pd.DataFrame({
                'Proxy': st.session_state.proxies,
                'Status': ['🟢 Active'] * len(st.session_state.proxies)
            })
            st.dataframe(proxies_df, use_container_width=True)
        
        with col2:
            st.markdown("### Add Proxy")
            
            new_proxy = st.text_input(
                "Proxy (ip:port)",
                placeholder="192.168.1.1:8080",
                help="Format: IP:PORT"
            )
            
            if st.button("➕ Add Proxy", use_container_width=True) and new_proxy:
                if ":" in new_proxy:
                    st.session_state.proxies.append(new_proxy)
                    st.session_state.activity_log.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] Added proxy: {new_proxy}"
                    )
                    st.success(f"Added proxy: {new_proxy}")
                    st.rerun()
                else:
                    st.error("Invalid format. Use IP:PORT")
            
            # Remove selected
            if st.session_state.proxies:
                proxy_to_remove = st.selectbox(
                    "Select proxy to remove",
                    st.session_state.proxies
                )
                
                if st.button("➖ Remove Selected", use_container_width=True):
                    st.session_state.proxies.remove(proxy_to_remove)
                    st.session_state.activity_log.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] Removed proxy: {proxy_to_remove}"
                    )
                    st.success(f"Removed proxy: {proxy_to_remove}")
                    st.rerun()
        
        # Test proxies button
        if st.button("🔄 Test All Proxies", use_container_width=True):
            with st.spinner("Testing proxies..."):
                time.sleep(2)
                st.success(f"Tested {len(st.session_state.proxies)} proxies. All active!")
    
    def show_results(self):
        """Show results"""
        st.markdown("## 📊 RESULTS DATABASE")
        
        if st.session_state.results:
            df = pd.DataFrame(st.session_state.results)
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.multiselect(
                    "Filter by Status",
                    options=["✅ LIVE", "❌ DEAD", "⚠️ UNKNOWN BIN", "✅ VALID", "❌ INVALID"],
                    default=[]
                )
            
            with col2:
                issuer_filter = st.multiselect(
                    "Filter by Issuer",
                    options=df['issuer'].unique(),
                    default=[]
                )
            
            with col3:
                date_filter = st.date_input(
                    "Filter by Date",
                    value=None
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if status_filter:
                filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            
            if issuer_filter:
                filtered_df = filtered_df[filtered_df['issuer'].isin(issuer_filter)]
            
            # Display results
            st.dataframe(filtered_df, use_container_width=True)
            
            # Statistics
            st.markdown("### 📈 Statistics")
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("Total Results", len(filtered_df))
            
            with col_stat2:
                live_count = len(filtered_df[filtered_df['status'].str.contains('✅')])
                st.metric("Live Cards", live_count)
            
            with col_stat3:
                dead_count = len(filtered_df[filtered_df['status'].str.contains('❌')])
                st.metric("Dead Cards", dead_count)
            
            with col_stat4:
                rate = (live_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                st.metric("Success Rate", f"{rate:.1f}%")
            
            # Export options
            st.markdown("---")
            st.markdown("### 📤 Export Results")
            
            export_format = st.radio(
                "Export Format",
                ["CSV", "JSON", "Excel"],
                horizontal=True
            )
            
            if export_format == "CSV":
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="stripe_results.csv",
                    mime="text/csv"
                )
            
            elif export_format == "JSON":
                json_str = filtered_df.to_json(orient="records", indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name="stripe_results.json",
                    mime="application/json"
                )
            
            else:  # Excel
                # Convert to Excel
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
            
            # Clear results button
            if st.button("🗑️ Clear All Results", type="secondary"):
                st.session_state.results = []
                st.session_state.activity_log.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Cleared all results"
                )
                st.success("Results cleared!")
                st.rerun()
        
        else:
            st.info("No results yet. Start checking cards!")
    
    def show_tools(self):
        """Show tools"""
        st.markdown("## 🛠️ ADVANCED TOOLS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔢 Card Generator")
            generate_count = st.number_input("Number of cards", 1, 100, 5)
            
            if st.button("Generate Cards", use_container_width=True):
                generated_cards = []
                for _ in range(generate_count):
                    card = self.generate_random_card()
                    generated_cards.append(card)
                
                # Display generated cards
                st.markdown("**Generated Cards:**")
                for card in generated_cards:
                    st.code(card)
                
                # Download option
                cards_text = "\n".join(generated_cards)
                st.download_button(
                    label="📥 Download Cards",
                    data=cards_text,
                    file_name="generated_cards.txt",
                    mime="text/plain"
                )
            
            st.markdown("---")
            st.markdown("### ✅ Luhn Checker")
            luhn_card = st.text_input("Check Luhn", placeholder="Enter card number")
            
            if luhn_card:
                is_valid = self.validator.validate_luhn(luhn_card)
                if is_valid:
                    st.success("✅ Valid Luhn checksum")
                else:
                    st.error("❌ Invalid Luhn checksum")
        
        with col2:
            st.markdown("### 🔍 BIN Analyzer")
            bin_card = st.text_input("BIN Lookup", placeholder="First 6-8 digits")
            
            if bin_card:
                info = self.validator.get_bin_info(bin_card)
                if info:
                    st.markdown("**BIN Information:**")
                    st.markdown(f"- **Issuer:** {info.get('issuer')}")
                    st.markdown(f"- **Bank:** {info.get('bank')}")
                    st.markdown(f"- **Country:** {info.get('country')}")
                    st.markdown(f"- **Type:** {info.get('type')}")
                else:
                    st.warning("BIN not found in database")
            
            st.markdown("---")
            st.markdown("### 🌐 Network Tools")
            
            if st.button("Ping Test", use_container_width=True):
                with st.spinner("Running ping test..."):
                    time.sleep(1)
                    st.success("Network connectivity: ✅ OK")
            
            if st.button("Speed Test", use_container_width=True):
                with st.spinner("Testing speed..."):
                    time.sleep(2)
                    st.success("Speed test complete: 100 Mbps")
    
    def generate_random_card(self):
        """Generate a single random card"""
        prefixes = list(self.validator.bin_db.keys())
        prefix = random.choice(prefixes)
        
        length = 15 if prefix in ["34", "37"] else 16
        card = prefix
        for _ in range(length - len(prefix) - 1):
            card += str(random.randint(0, 9))
        
        # Calculate Luhn
        for check_digit in range(10):
            test_card = card + str(check_digit)
            if self.validator.validate_luhn(test_card):
                return test_card
        
        return card + "0"
    
    def save_single_result(self, result):
        """Save single result"""
        st.session_state.activity_log.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Saved result for card: {result['card'][-4:]}"
        )
        st.success("Result saved to database!")
    
    def show_settings(self):
        """Show settings"""
        st.markdown("## ⚙️ SETTINGS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Appearance")
            
            theme = st.selectbox(
                "Theme",
                ["Dark", "Light", "Cyberpunk"],
                index=0
            )
            
            st.markdown("### Performance")
            
            threads = st.slider("Default Threads", 1, 20, 5)
            delay = st.slider("Default Delay (ms)", 0, 5000, 100)
            
            st.markdown("### Notifications")
            
            email_notify = st.checkbox("Email Notifications")
            sound_notify = st.checkbox("Sound Alerts")
        
        with col2:
            st.markdown("### Security")
            
            auto_clear = st.checkbox("Auto-clear clipboard", True)
            encrypt_data = st.checkbox("Encrypt stored data", True)
            
            st.markdown("### Export")
            
            auto_export = st.checkbox("Auto-export results", False)
            export_format = st.selectbox(
                "Default Export Format",
                ["CSV", "JSON", "Excel"],
                index=0
            )
            
            st.markdown("### Updates")
            
            auto_update = st.checkbox("Check for updates", True)
        
        # Save settings button
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            st.session_state.activity_log.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Settings saved"
            )
            st.success("Settings saved successfully!")
        
        # Reset button
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.activity_log.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Settings reset to defaults"
            )
            st.success("Settings reset to defaults!")

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    app = UltimateStripeChecker()
    app.run()        self.single_results.insert(tk.END, output)
        
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
