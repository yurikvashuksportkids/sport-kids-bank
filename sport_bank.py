import streamlit as st
import pandas as pd
import datetime
import time
import gspread
import random
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components
import base64

# --- НАЛАШТУВАННЯ СТОРІНКИ ---
st.set_page_config(page_title="Sport Kids Bank", page_icon="⚽", layout="centered")

AVAILABLE_ROLES = ["admin", "Coach", "Team A", "Team B", "Parent"]

# --- СТИЛІ ДИЗАЙНУ ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&display=swap');
    
    .stApp { background-color: #0A0A0A; font-family: 'Montserrat', sans-serif; }
    
    h1 { font-family: 'Montserrat', sans-serif; color: #FFED00; text-align: center; text-shadow: 2px 2px 0px #0A0A0A, 4px 4px 0px #3BFC00; letter-spacing: 2px; font-size: 3.2rem !important; padding-bottom: 5px; text-transform: uppercase; margin-top: 10px; }
    h2, h3, p, label { color: #FFFFFF; font-weight: 700; }
    
    div[data-testid="stForm"] { background-color: #1A1A1A; border: 4px solid #3BFC00; border-radius: 20px; padding: 25px; box-shadow: 8px 8px 0px #3BFC00; margin-bottom: 20px; margin-top: 15px; }
    
    .balance-card { background-color: #3BFC00; color: #0A0A0A; padding: 30px; border-radius: 20px; border: 4px solid #FFED00; text-align: center; margin-bottom: 25px; box-shadow: 8px 8px 0px #FFED00; }
    .balance-amount { font-size: 95px; font-weight: 900; color: #0A0A0A; text-shadow: 5px 5px 0px #FFFFFF; line-height: 1.1; margin-top: 10px; }
    
    .role-badge { display: inline-block; background-color: #FFED00; color: #0A0A0A; padding: 5px 15px; border-radius: 10px; font-size: 14px; margin-right: 5px; margin-bottom: 5px; border: 2px solid #0A0A0A; font-weight: 900;}
    
    .stButton>button { background-color: #FFED00; color: #0A0A0A; border: 4px solid #3BFC00; border-radius: 16px; font-family: 'Montserrat', sans-serif; font-weight: 900; font-size: 16px; padding: 10px 5px; width: 100%; transition: all 0.15s ease; box-shadow: 4px 4px 0px #3BFC00; }
    .stButton>button:hover { transform: translate(3px, 3px); box-shadow: 2px 2px 0px #3BFC00; background-color: #FFFFFF; color: #0A0A0A; }
    
    .stTextInput input, .stNumberInput input { background-color: #FFFFFF; color: #0A0A0A; border: 3px solid #3BFC00 !important; border-radius: 12px !important; font-size: 24px !important; text-align: center; font-weight: 700;}
    .stTextInput input::placeholder { color: #666; }
    input[type="number"]::-webkit-inner-spin-button, input[type="number"]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
    
    .stats { font-size: 16px; margin: 5px; background: #FFED00; color: #0A0A0A; padding: 5px; border-radius: 5px; border: 2px solid #3BFC00; display: inline-block;}
    #score { color: #3BFC00; font-weight: 900; }
    #startBtn { background-color: #FFED00; color: #0A0A0A; border: 4px solid #3BFC00; padding: 10px 20px; font-size: 20px; border-radius: 10px; font-weight: 900; cursor: pointer; box-shadow: 4px 4px 0px #3BFC00; margin-bottom: 10px;}
    #startBtn:active { transform: translate(3px, 3px); box-shadow: 1px 1px 0px #3BFC00; }
    </style>
""", unsafe_allow_html=True)

# --- ЕМБЛЕМА ---
logo_svg = """<svg width="200" height="230" viewBox="0 0 200 230" xmlns="http://www.w3.org/2000/svg">
  <path d="M 60 115 A 80 80 0 1 1 140 115 H 180 A 80 80 0 0 0 20 115 Z" fill="#3BFC00"/>
  <circle cx="100" cy="115" r="40" fill="#FFED00"/>
  <text x="100" y="125" font-family="Montserrat, sans-serif" font-weight="900" font-size="40" text-anchor="middle" fill="#0A0A0A">FC</text>
  <text x="100" y="215" font-family="Montserrat, sans-serif" font-weight="900" font-size="28" text-anchor="middle" fill="#FFED00" letter-spacing="1">SPORT</text>
  <text x="100" y="245" font-family="Montserrat, sans-serif" font-weight="900" font-size="28" text-anchor="middle" fill="#FFED00" letter-spacing="1">KIDS</text>
</svg>"""
logo_base64 = base64.b64encode(logo_svg.encode('utf-8')).decode('utf-8')
st.markdown(f'''
    <div style="text-align: center; margin-top: 20px;">
        <img src="data:image/svg+xml;base64,{logo_base64}" alt="FC Sport Kids Logo" style="max-height: 150px;">
    </div>
''', unsafe_allow_html=True)

st.markdown("<h1>SPORT KIDS BANK</h1>", unsafe_allow_html=True)

# --- ГРА "ДИНОЗАВР" ---
DINO_GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { margin:0; background-color: #0A0A0A; font-family: 'Montserrat', sans-serif; text-align: center; touch-action: manipulation; transition: background-color 0.2s; color: white; }
  canvas { background-color: #FFED00; border: 4px solid #3BFC00; border-radius: 10px; margin-top: 10px; max-width: 100%; box-shadow: 6px 6px 0px #3BFC00; }
  #ui { margin-top: 10px; color: #FFFFFF; font-weight: 900;}
  .stats { font-size: 16px; margin: 5px; background: #FFED00; color: #0A0A0A; padding: 5px; border-radius: 5px; border: 2px solid #3BFC00; display: inline-block;}
  h2 { margin: 5px; font-size: 24px; color: #FFED00; text-transform: uppercase; }
  button { background-color: #FFED00; color: #0A0A0A; border: 3px solid #3BFC00; padding: 10px 20px; font-size: 20px; border-radius: 10px; font-weight: 900; cursor: pointer; box-shadow: 4px 4px 0px #3BFC00; margin-bottom: 10px;}
  button:active { transform: translate(3px, 3px); box-shadow: 1px 1px 0px #3BFC00; }
</style>
</head>
<body>
<div id="ui">
  <div class="stats">⚽ Рекорд: <b id="pRecordDisplay">0</b></div>
  <h2>ОЧКИ: <span id="score">0</span> / 100 000</h2>
  <button id="startBtn" onclick="startGame()">▶ СТАРТ</button>
</div>
<canvas id="gameCanvas" width="320" height="180"></canvas>

<script>
  const currentUsername = "__USERNAME__";
  let personalRecord = localStorage.getItem("dino_rec_" + currentUsername) || 0;
  document.getElementById("pRecordDisplay").innerText = personalRecord;

  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");
  let isPlaying = false; let score = 0; let speed = 5;
  let dino = { x: 30, y: 130, w: 25, h: 25, dy: 0, gravity: 0.9, jumpForce: -11, isGrounded: true };
  let obstacles = []; let frame = 0;

  function jump() { if (dino.isGrounded && isPlaying) { dino.dy = dino.jumpForce; dino.isGrounded = false; } }
  window.addEventListener('touchstart', jump); window.addEventListener('mousedown', jump);
  window.addEventListener('keydown', (e) => { if(e.code === 'Space') jump(); });

  function startGame() {
    document.getElementById("startBtn").style.display = "none";
    dino.y = 130; dino.dy = 0; obstacles = []; score = 0; speed = 6; frame = 0; isPlaying = true;
    requestAnimationFrame(update);
  }

  function gameOver() {
    isPlaying = false; 
    
    if (score > personalRecord) {
        personalRecord = score;
        localStorage.setItem("dino_rec_" + currentUsername, score);
        document.getElementById("pRecordDisplay").innerText = personalRecord;
    }

    ctx.fillStyle = "rgba(0, 0, 0, 0.8)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    if (score >= 100000) { 
        ctx.fillStyle = "#FFED00"; ctx.font = "bold 24px Montserrat"; ctx.fillText("🎉 ПЕРЕМОГА!", 70, 70); 
        
        // Генеруємо випадковий код
        let currentWinCode = Math.floor(Math.random() * 90000) + 10000;
        
        ctx.fillStyle = "white"; ctx.font = "bold 18px Montserrat"; 
        ctx.fillText("ТВІЙ КОД: " + currentWinCode, 100, 110); 
        ctx.font = "bold 14px Montserrat"; 
        ctx.fillText("Введи його під грою!", 90, 140);
    } else { 
        ctx.fillStyle = "white"; ctx.font = "bold 24px Montserrat";
        ctx.fillText("ГРА ЗАКІНЧЕНА!", 60, 100); 
    }

    document.getElementById("startBtn").style.display = "inline-block"; 
    document.getElementById("startBtn").innerText = "🔄 Спробувати ще";
  }

  function update() {
    if (!isPlaying) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = "#FFED00"; ctx.fillRect(0, 155, canvas.width, 25);
    ctx.fillStyle = "#3BFC00"; ctx.fillRect(0, 155, canvas.width, 5);
    
    dino.dy += dino.gravity; dino.y += dino.dy;
    if (dino.y >= 130) { dino.y = 130; dino.isGrounded = true; dino.dy = 0; }
    
    ctx.fillStyle = "#3BFC00"; ctx.fillRect(dino.x, dino.y, dino.w, dino.h);
    ctx.fillStyle = "black"; ctx.fillRect(dino.x + 12, dino.y + 4, 6, 6);
    ctx.fillStyle = "yellow"; ctx.fillRect(dino.x + 14, dino.y + 6, 2, 2);

    if (frame % Math.max(30, Math.floor(Math.random() * 60 + 40)) === 0) obstacles.push({ x: canvas.width, y: 135, w: 20, h: 20 });
    
    for (let i = 0; i < obstacles.length; i++) {
      let obs = obstacles[i]; obs.x -= speed;
      ctx.fillStyle = "#0A0A0A"; ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
      if (dino.x < obs.x + obs.w - 2 && dino.x + dino.w > obs.x + 2 && dino.y < obs.y + obs.h - 2 && dino.y + dino.h > obs.y + 2) { gameOver(); return; }
    }
    
    obstacles = obstacles.filter(obs => obs.x > -30);
    score += 45; document.getElementById("score").innerText = score;
    if (score >= 100000) { gameOver(); return; }
    if (frame % 200 === 0 && speed < 12) speed += 0.5;
    frame++; requestAnimationFrame(update);
  }
</script>
</body>
</html>
"""

def generate_secure_pin(existing_pins):
    while True:
        pin = random.randint(1000, 9999)
        pin_str = str(pin)
        if len(set(pin_str)) > 1 and pin_str not in "0123456789" and pin_str not in "9876543210" and pin not in existing_pins:
            return pin

# --- БАЗА ДАНИХ (ПІДКЛЮЧЕННЯ ХМАРНЕ) ---
@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("SportKidsBank_DB")

with st.spinner("⏳ Підключення до спортивного банку..."):
    try:
        db = init_connection()
        users_sheet = db.worksheet("Users")
        trans_sheet = db.worksheet("Transactions")
    except Exception as e:
        st.error(f"🛑 Помилка підключення: {e}.")
        st.stop()

@st.cache_data(ttl=15)
def get_users_df_cached():
    return pd.DataFrame(users_sheet.get_all_records())

@st.cache_data(ttl=15)
def get_trans_df_cached():
    return pd.DataFrame(trans_sheet.get_all_records())

def update_user_balance_by_row(df_index, new_balance):
    users_sheet.update_cell(int(df_index) + 2, 4, int(new_balance)) 
    get_users_df_cached.clear() 

def update_user_roles_by_row(df_index, new_roles_str):
    users_sheet.update_cell(int(df_index) + 2, 3, new_roles_str)
    get_users_df_cached.clear()

def log_transaction(sender, receiver, amount, desc):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trans_sheet.append_row([now, sender, receiver, int(amount), desc])
    get_trans_df_cached.clear() 

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.show_transfer = False
    st.session_state.show_history = False 
    st.session_state.show_game = False 
    st.session_state.new_user_added = None
    st.session_state.last_game_code = "" 

if not st.session_state.logged_in:
    if "user" in st.query_params and "role" in st.query_params:
        st.session_state.logged_in = True
        st.session_state.username = st.query_params["user"]
        st.session_state.role = st.query_params["role"]

if st.session_state.logged_in:
    st.query_params["user"] = st.session_state.username
    st.query_params["role"] = st.session_state.role

def login(username, pin):
    users = get_users_df_cached()
    user_row = users[(users['Username'].astype(str).str.strip() == username) & (users['PIN'] == pin)]
    
    if not user_row.empty:
        role = str(user_row.iloc[0]['Role'])
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = role
        st.session_state.show_transfer = False
        st.session_state.show_history = False
        st.session_state.show_game = False
        st.session_state.last_game_code = ""
        
        st.query_params["user"] = username
        st.query_params["role"] = role
        time.sleep(0.5)
        st.rerun()
    else:
        st.error("Неправильне ім'я або секретний код! 🛑")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.last_game_code = ""
    st.query_params.clear()
    st.rerun()

def camper_dashboard():
    users = get_users_df_cached()
    users['CleanName'] = users['Username'].astype(str).str.strip()
    matched = users[users['CleanName'] == st.session_state.username]

    if matched.empty:
        st.error("Акаунт оновлюється або його видалено. Перезайдіть.")
        if st.button("🔄 Вийти"): logout()
        return

    my_idx = matched.index[0]
    my_data = matched.iloc[0]
    my_balance = my_data['Balance']
    my_roles = [r.strip() for r in str(my_data['Role']).split(",") if r.strip()]

    st.markdown(f"<h2>Привіт, чемпіоне! ⚽</h2>", unsafe_allow_html=True)
    st.info("🔖 Збережи цю сторінку в **Закладки** браузера, щоб більше ніколи не вводити пароль!")
    
    roles_html = "".join([f'<span class="role-badge">{r}</span>' for r in my_roles if r in AVAILABLE_ROLES])
    st.markdown(f"<div style='text-align: center;'>{roles_html}</div>", unsafe_allow_html=True)

    st.markdown(f'''
        <div class="balance-card">
            <p style="font-size: 24px; margin:0; font-weight: 700; color: #0A0A0A;">Твій баланс:</p>
            <p class="balance-amount">{my_balance} ⚡</p>
        </div>
    ''', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💸 ПЕРЕКАЗ"):
            st.session_state.show_transfer = not st.session_state.show_transfer
            st.session_state.show_history = False; st.session_state.show_game = False
            st.rerun()
    with col2:
        if st.button("📜 ІСТОРІЯ"):
            st.session_state.show_history = not st.session_state.show_history
            st.session_state.show_transfer = False; st.session_state.show_game = False
            st.rerun()
    with col3:
        if st.button("🎮 ГРА"):
            st.session_state.show_game = not st.session_state.show_game
            st.session_state.show_transfer = False; st.session_state.show_history = False
            st.rerun()

    if st.session_state.show_game:
        custom_game_html = DINO_GAME_HTML.replace("__USERNAME__", st.session_state.username)
        st.markdown("<h3 style='text-align: center; color: #FFED00;'>Зароби 1⚡ за 100 000 очок!</h3>", unsafe_allow_html=True)
        components.html(custom_game_html, height=400)

        st.markdown("""<style>div[data-testid="stForm"] { border-color: #3BFC00; background-color: #1A1A1A; }</style>""", unsafe_allow_html=True)
        with st.form("reward_form"):
            st.markdown("### 🎁 Отримати винагороду")
            entered_code = st.text_input("Введи код з екрану гри:", key="game_reward_input")
            if st.form_submit_button("Нарахувати 1 ⚡ собі"):
                try:
                    code_int = int(entered_code.strip())
                    if 10000 <= code_int <= 99999:
                        if entered_code != st.session_state.last_game_code:
                            update_user_balance_by_row(my_idx, my_balance + 1)
                            log_transaction("SYSTEM_GAME", st.session_state.username, 1, "Перемога в грі (100k)")
                            st.session_state.last_game_code = entered_code 
                            st.success("🎉 ВАУ! 1 ⚡ автоматично додано на твій рахунок!")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Цей код вже використано! Набери 100 000 очок, щоб отримати новий.")
                    else:
                        st.error("❌ Невірний код! Набери 100 000 очок, щоб побачити код з 5 цифр.")
                except ValueError:
                    st.error("❌ Код повинен бути числом з 5 цифр.")

    if st.session_state.show_transfer:
        other_users = users[users['CleanName'] != st.session_state.username]['Username'].tolist()
        with st.form("transfer_form"):
            receiver = st.selectbox("Кому надсилаємо?", other_users)
            amount = st.number_input("Сума", min_value=1, step=1)
            desc = st.text_input("За що?")
            if st.form_submit_button("Відправити 🚀"):
                if amount <= my_balance:
                    receiver_matched = users[users['Username'] == receiver]
                    receiver_idx = receiver_matched.index[0]
                    receiver_bal = receiver_matched.iloc[0]['Balance']

                    update_user_balance_by_row(my_idx, my_balance - amount)
                    update_user_balance_by_row(receiver_idx, receiver_bal + amount)
                    log_transaction(st.session_state.username, receiver, amount, desc)
                    
                    st.success("Надіслано!"); st.balloons(); time.sleep(1); st.rerun()
                else:
                    st.error("Недостатньо коштів!")

    if st.session_state.show_history:
        st.markdown("<h3 style='text-align: center; color: #FFED00;'>Останні дії 📜</h3>", unsafe_allow_html=True)
        try:
            df = get_trans_df_cached()
            my_trans = df[(df['Sender'] == st.session_state.username) | (df['Receiver'] == st.session_state.username)].iloc[::-1]
            
            if my_trans.empty: st.info("Транзакцій немає.")
            else:
                for _, row in my_trans.iterrows():
                    try:
                        desc_text = str(row.iloc[4]) if len(row) >= 5 else "Без коментаря"
                        if desc_text.strip() == "" or desc_text == "nan": desc_text = "Без коментаря"
                    except:
                        desc_text = "Без коментаря"

                    color = "#0A0A0A" if row['Sender'] == st.session_state.username else "#3BFC00"
                    sign = "-" if row['Sender'] == st.session_state.username else "+"
                    other_person = row['Receiver'] if row['Sender'] == st.session_state.username else row['Sender']
                    
                    html_content = f"""
                    <div style='background-color: #1A1A1A; border: 3px solid #3BFC00; border-radius: 10px; padding: 10px; margin-bottom: 10px; box-shadow: 4px 4px 0px #3BFC00;'>
                        <h4 style='margin:0; color:{color};'>{sign}{row['Amount']} ⚡</h4>
                        <p style='margin:0; font-weight: 700; color: white;'>{other_person}</p>
                        <p style='margin:0; font-size: 14px; color: #AAA;'>💬 {desc_text}</p>
                    </div>
                    """
                    st.markdown(html_content, unsafe_allow_html=True)
        except Exception:
            st.info("Транзакцій немає.")

def admin_dashboard():
    st.markdown("<h2 style='text-align: center; color: #FFED00;'>⚙️ Спортивна Панель Адміністратора</h2>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Користувачі", "Нарахувати", "Статистика"])
    users = get_users_df_cached()

    with tab1:
        st.dataframe(users[['Username', 'Role', 'Balance']], use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 👁️ Профіль та Редагування")
        user_to_edit = st.selectbox("Оберіть учасника для перегляду:", users['Username'].tolist(), key="edit_user_sel")
        if user_to_edit:
            matched_edit = users[users['Username'] == user_to_edit].iloc[0]
            edit_idx = users[users['Username'] == user_to_edit].index[0]
            current_roles = [r.strip() for r in str(matched_edit['Role']).split(",") if r.strip()]
            
            st.info(f"💳 **Баланс:** {matched_edit['Balance']} ⚡ | 🔑 **PIN-код:** {matched_edit['PIN']}")
            
            with st.form("edit_user_form"):
                valid_defaults = [r for r in current_roles if r in AVAILABLE_ROLES]
                updated_roles = st.multiselect("Категорії (Ролі)", AVAILABLE_ROLES, default=valid_defaults)
                if st.form_submit_button("💾 Зберегти зміни"):
                    roles_str = ", ".join(updated_roles)
                    update_user_roles_by_row(edit_idx, roles_str)
                    st.success(f"Категорії для {user_to_edit} успішно оновлено!")
                    time.sleep(1.5)
                    st.rerun()

        st.markdown("---")
        if st.session_state.new_user_added:
            st.success(f"Додано: **{st.session_state.new_user_added['name']}**")
            st.warning(f"🔑 PIN: **{st.session_state.new_user_added['pin']}**")
            if st.button("✅ Записав"):
                st.session_state.new_user_added = None; st.rerun()
        else:
            with st.form("add_user", clear_on_submit=True):
                st.markdown("### ➕ Додати учасника")
                new_name = st.text_input("Ім'я")
                new_roles = st.multiselect("Ролі (можна декілька)", AVAILABLE_ROLES, default=["Team A"])
                new_balance = st.number_input("Початковий баланс", min_value=0)
                if st.form_submit_button("Додати"):
                    if new_name and new_name not in users['Username'].values:
                        pin = generate_secure_pin(users['PIN'].values.tolist())
                        roles_str = ", ".join(new_roles)
                        users_sheet.append_row([new_name, int(pin), roles_str, int(new_balance)])
                        get_users_df_cached.clear()
                        st.session_state.new_user_added = {'name': new_name, 'pin': pin}; st.rerun()
                    elif new_name: st.error("Такий користувач вже є!")
                    else: st.error("Ім'я не може бути порожнім!")
        
        st.markdown("---")
        st.markdown("### ❌ Видалити учасника")
        safe_users_to_delete = users[users['Username'] != st.session_state.username]['Username'].tolist()
        
        with st.form("delete_user"):
            user_to_delete = st.selectbox("Оберіть учасника", safe_users_to_delete)
            if st.form_submit_button("🗑️ Видалити назавжди"):
                if user_to_delete:
                    matched_del = users[users['Username'] == user_to_delete]
                    if not matched_del.empty:
                        del_idx = matched_del.index[0]
                        users_sheet.delete_rows(int(del_idx) + 2) 
                        log_transaction(st.session_state.username, user_to_delete, 0, "ВИДАЛЕНО АКАУНТ")
                        get_users_df_cached.clear() 
                        st.success(f"Акаунт '{user_to_delete}' видалено!"); time.sleep(1.5); st.rerun()

    with tab2:
        target = st.selectbox("Оберіть учасника", users['Username'].tolist())
        action = st.radio("Дія", ["Нарахувати", "Зняти штраф"])
        amount = st.number_input("Сума", min_value=1)
        reason = st.text_input("Причина")
        
        if st.button("Виконати"):
            matched_target = users[users['Username'] == target]
            target_idx = matched_target.index[0]
            cur_bal = matched_target.iloc[0]['Balance']
            
            if action == "Нарахувати":
                update_user_balance_by_row(target_idx, cur_bal + amount)
                log_transaction(st.session_state.username, target, amount, reason)
                st.success("✅ Кошти нараховано."); time.sleep(1); st.rerun()
            else:
                if amount > cur_bal: st.error("❌ Не можна зняти більше, ніж є на балансі!")
                else:
                    update_user_balance_by_row(target_idx, cur_bal - amount)
                    log_transaction(st.session_state.username, target, -amount, reason)
                    st.success("✅ Штраф знято."); time.sleep(1); st.rerun()

    with tab3:
        try: st.dataframe(get_trans_df_cached(), use_container_width=True)
        except Exception: st.info("Немає даних.")

st.markdown("""<style>div[data-testid="stForm"] { border-color: #3BFC00; background-color: #1A1A1A; }</style>""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    with st.form("login_form"):
        st.markdown("<h3 style='text-align: center; color: #3BFC00;'>УВІЙТИ</h3>", unsafe_allow_html=True)
        u = st.text_input("Твоє ім'я").strip()
        p = st.number_input("Твій PIN", min_value=1000, max_value=9999, step=1, format="%d")
        if st.form_submit_button("УВІЙТИ 🚀"):
            if u: login(u, p)
            else: st.warning("Введіть ім'я!")
else:
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Вийти 🚪"): logout()
    roles_list = [r.strip().lower() for r in str(st.session_state.role).split(",")]
    if 'admin' in roles_list: admin_dashboard()
    else: camper_dashboard()