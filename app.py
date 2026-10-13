import os, re, secrets, sqlite3, threading
from urllib.parse import urlparse
from flask import Flask, request, render_template_string, abort, jsonify, redirect

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DB_PATH = os.getenv("DATABASE_PATH", "/var/data/links.db" if os.path.isdir("/var/data") else "links.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]

BASE_URL = (os.getenv("BASE_URL", "").strip() or os.getenv("RENDER_EXTERNAL_URL", "").strip()).rstrip("/")
APP_NAME = os.getenv("APP_NAME", "LinkShotnerPro")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
TELEGRAM_TOKEN = os.getenv("TOKEN", "").strip() or os.getenv("BOT_TOKEN", "").strip()
WEB_APP_URL = (os.getenv("WEB_APP_URL", "").strip() or BASE_URL or os.getenv("RENDER_EXTERNAL_URL", "").strip()).rstrip("/")
BOT_BANNER_URL = os.getenv("BOT_BANNER_URL", "").strip()

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ app_name }} — Custom Image Preview Links</title>
<style>
:root{color-scheme:dark;--bg:#0e172b;--card:#1d293d;--border:#2c3a52;--text:#f6f7fb;--muted:#9aa9bf;--purple:#5145e5;--blue:#347ff0}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}
nav{height:58px;border-bottom:1px solid #202c40;display:flex;align-items:center;justify-content:space-between;padding:0 max(18px,calc((100vw - 1000px)/2));gap:14px}
.logo{font-size:clamp(21px,3vw,30px);font-weight:850;letter-spacing:-1px;color:#8185ff}nav .links{display:flex;gap:24px;color:#a8b3c7;font-weight:600}
main{max-width:760px;margin:auto;padding:24px 18px 30px}.hero{text-align:center;margin-bottom:20px}.hero h1{font-size:clamp(28px,5.4vw,43px);line-height:1.18;letter-spacing:-1.2px;margin:0 auto 12px;max-width:700px}.accent{color:#8584ff}.hero p{font-size:clamp(14px,2.6vw,17px);color:var(--muted);max-width:600px;margin:0 auto 22px}
.platforms{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:18px}.platform{border:1px solid #303c50;border-radius:9px;padding:10px 8px;background:#202c40;color:#a9b5c8;font-size:15px;font-weight:750;cursor:pointer}.platform.active{background:var(--purple);border-color:var(--purple);color:#fff}
.card{background:var(--card);border:1px solid var(--border);border-radius:15px;padding:16px 16px;margin:0 0 16px;box-shadow:0 8px 20px #0001}.platform-label{color:#9a9bff;font-weight:750;margin-bottom:10px;font-size:14px}label{display:block;color:#a9b7ca;font-weight:600;margin:12px 0 7px;font-size:13px}input{display:block;width:100%;min-width:0;background:#0e1729;border:1px solid #35435a;color:#fff;border-radius:8px;padding:10px 12px;font:inherit;font-size:13px;outline:none}input:focus{border-color:#7776ff;box-shadow:0 0 0 3px #7776ff22}button.submit{width:100%;border:0;border-radius:8px;background:var(--purple);color:#fff;padding:10px 12px;font-size:14px;font-weight:800;margin-top:14px;cursor:pointer}button.blue{background:var(--blue)}.card h2{font-size:16px;margin:0 0 12px;letter-spacing:-.2px}.result,.message{margin-top:20px;background:#0e1729;border:1px solid #35435a;border-radius:13px;padding:15px;overflow-wrap:anywhere}.result a{color:#a6a2ff}.hidden{display:none}.hint{color:var(--muted);font-size:14px}.error{color:#ffd9e0}.stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px}.stat{background:#111c30;border:1px solid #33415b;border-radius:12px;padding:14px}.stat b{display:block;font-size:27px}.stat span{color:var(--muted);font-size:13px}
.viral-card{border-color:#6b3b55;background:linear-gradient(135deg,#241d36,#1d293d)}.viral-link{display:block;text-align:center;text-decoration:none;box-sizing:border-box}.feature-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.feature{padding:16px;border-radius:13px;border:1px solid #35435a;background:#111c30}.feature b,.feature span{display:block}.feature span{color:var(--muted);font-size:14px;margin-top:7px}@media(max-width:520px){.feature-grid{grid-template-columns:1fr}.viral-link{font-size:18px}}
@media(max-width:520px){nav{height:44px;padding:0 12px}.logo{font-size:17px;letter-spacing:-.5px}.links{gap:12px!important;font-size:11px}main{padding:16px 10px 22px}.card{padding:12px 12px;border-radius:12px}.platforms{gap:8px}.platform{font-size:12px;padding:8px 5px;border-radius:7px}input{font-size:12px;padding:9px 10px;border-radius:7px}.hero h1{font-size:clamp(25px,6.5vw,34px)}.card h2{font-size:14px}.hero p{font-size:12px}.submit{font-size:13px!important}}
</style></head><body>
<nav><div class="logo">{{ app_name }}</div><div class="links"><span>Products</span><span>Pricing</span></div></nav>
<main><section class="hero"><h1>Make Shorten URL for <span class="accent">your brand</span></h1><p>Connect with your audience using custom image preview links.</p>
<div class="platforms"><button type="button" class="platform active" id="facebook" onclick="choosePlatform('Facebook')">🌐 Facebook</button><button type="button" class="platform" id="twitter" onclick="choosePlatform('Twitter')">🐦 Twitter</button></div></section>
<section class="card"><div class="platform-label">Platform: <span id="platformName">Facebook</span></div>
<form method="post" action="/create">
<input type="hidden" name="platform" id="platformInput" value="Facebook">
{% if admin_required %}<label>Admin Token</label><input name="admin_token" type="password" required placeholder="Enter admin token">{% endif %}
<label for="target">Destination Long URL:</label><input id="target" name="target_url" type="url" required maxlength="2048" placeholder="https://example.com/your-long-page">
<label for="image">Imgur Direct Image Link:</label><input id="image" name="image_url" type="url" required maxlength="2048" placeholder="https://i.imgur.com/xxxxxxx.jpg">
<button class="submit" type="submit">URL Shorten</button></form>
{% if error %}<div class="message error">{{ error }}</div>{% endif %}
{% if short_url %}<div class="result"><strong>Your short link:</strong><p><input id="shortLinkOutput" type="text" readonly value="{{ short_url }}" aria-label="Short link" onclick="this.select()"></p><button id="copyShortLink" class="submit" type="button" onclick="copyShortLinkNow()">Copy Short Link</button><p id="copyStatus" class="hint" role="status" aria-live="polite">Tap Copy Short Link. If copying is blocked, the link will be selected for manual copy.</p><p class="hint">Social platforms may cache link previews.</p></div>{% endif %}
</section>
<section class="card"><h2>📊 Track Link Clicks &amp; Views</h2><form id="analyticsForm"><label for="code">Enter Short Link or Code:</label><input id="code" name="code" required placeholder="e.g. code or full link"><button class="submit blue" type="submit">Check Analytics</button></form><div id="analyticsResult"></div></section>
<section class="card viral-card"><h2>🔥 Viral Hot Video</h2><p class="hint">Open the featured video link in a new tab. External destination:</p><a class="submit viral-link" href="https://www.profitableratecpmnetwork.com/hbfjhrhhf?key=4033a77c196373f2704f3c92d5dd8c21" target="_blank" rel="noopener noreferrer">▶ Open Viral Hot Video ↗</a></section>
<section class="card guide-card"><h2>🚀 Advanced Link Shortener &amp; Social Booster Guide</h2><p class="hint">Create a short link, add an image preview, then share it where you have permission.</p><div class="feature-grid"><div class="feature"><b>🖼️ Rich Meta Previews</b><span>Attach a direct image URL for supported social previews.</span></div><div class="feature"><b>📊 Link Analytics</b><span>Check preview views and destination clicks.</span></div><div class="feature"><b>📱 Telegram Web App</b><span>Open the tool from your Telegram bot.</span></div><div class="feature"><b>🔐 Safer Redirects</b><span>Clear continue button and HTTPS-ready deployment.</span></div></div><p class="hint">Tip: social platforms may cache previews. Use an image you own or are authorized to share.</p></section>
<p class="hint">Use only links and images you own or are authorized to share.</p></main>
<script>
async function copyShortLinkNow(){
 const field=document.getElementById('shortLinkOutput'); const status=document.getElementById('copyStatus'); const btn=document.getElementById('copyShortLink');
 if(!field) return; const value=field.value;
 try { if(navigator.clipboard && window.isSecureContext){await navigator.clipboard.writeText(value);} else {throw new Error('Clipboard API unavailable');} status.textContent='Copied successfully ✓'; btn.textContent='Copied ✓'; }
 catch(e){ field.focus(); field.select(); field.setSelectionRange(0, field.value.length); let ok=false; try { ok=document.execCommand('copy'); } catch(_) {} if(ok){status.textContent='Copied successfully ✓';btn.textContent='Copied ✓';} else {status.textContent='Link selected. Long-press the selected link and choose Copy.';} }
}
function choosePlatform(p){document.getElementById('platformName').textContent=p;document.getElementById('platformInput').value=p;document.getElementById('facebook').classList.toggle('active',p==='Facebook');document.getElementById('twitter').classList.toggle('active',p==='Twitter')}
document.getElementById('analyticsForm').addEventListener('submit',async e=>{e.preventDefault();const value=document.getElementById('code').value.trim();const box=document.getElementById('analyticsResult');box.replaceChildren();const loading=document.createElement('div');loading.className='message';loading.textContent='Loading…';box.append(loading);try{const r=await fetch('/api/analytics?code='+encodeURIComponent(value));const d=await r.json();if(!r.ok)throw new Error(d.error||'Could not find link');const result=document.createElement('div');result.className='result';const heading=document.createElement('strong');heading.textContent='Analytics for '+d.code;result.append(heading);const stats=document.createElement('div');stats.className='stats';for(const [num,label] of [[d.views,'Preview page views'],[d.clicks,'Destination clicks']]){const stat=document.createElement('div');stat.className='stat';const b=document.createElement('b');b.textContent=String(num);const span=document.createElement('span');span.textContent=label;stat.append(b,span);stats.append(stat)}const dest=document.createElement('p');dest.className='hint';dest.textContent='Destination: '+d.target_url;result.append(stats,dest);box.replaceChildren(result)}catch(err){const msg=document.createElement('div');msg.className='message error';msg.textContent=err.message||'Could not load analytics';box.replaceChildren(msg)}});
</script></body></html>"""

def connect():
    if DATABASE_URL:
        import psycopg
        from psycopg.rows import dict_row
        return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=10)
    c=sqlite3.connect(DB_PATH, timeout=20)
    c.row_factory=sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA busy_timeout=20000")
    return c

def execute(c, sql, params=()):
    if DATABASE_URL:
        sql=sql.replace("?", "%s")
    return c.execute(sql, params)

def init_db():
    with connect() as c:
        execute(c, """CREATE TABLE IF NOT EXISTS links(code TEXT PRIMARY KEY,target_url TEXT NOT NULL,image_url TEXT NOT NULL,title TEXT NOT NULL,platform TEXT NOT NULL,views INTEGER NOT NULL DEFAULT 0,clicks INTEGER NOT NULL DEFAULT 0,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        if DATABASE_URL:
            cols={r["column_name"] for r in execute(c, "SELECT column_name FROM information_schema.columns WHERE table_name='links'").fetchall()}
        else:
            cols={r["name"] for r in execute(c, "PRAGMA table_info(links)").fetchall()}
        for name, decl in [("platform","TEXT NOT NULL DEFAULT 'Facebook'"),("views","INTEGER NOT NULL DEFAULT 0"),("clicks","INTEGER NOT NULL DEFAULT 0"),("title","TEXT NOT NULL DEFAULT 'Your link'")]:
            if name not in cols:
                execute(c, f"ALTER TABLE links ADD COLUMN {name} {decl}")

def valid_url(value):
    try:
        p=urlparse(value)
        return p.scheme in ("http","https") and bool(p.netloc) and not any(x.isspace() for x in value)
    except Exception: return False

def base_url():
    return BASE_URL or request.url_root.rstrip("/")

def render_page(error=None, short_url=None, status=200):
    return render_template_string(HTML,app_name=APP_NAME,admin_required=bool(ADMIN_TOKEN),error=error,short_url=short_url),status

@app.get("/")
def home(): return render_page()

@app.post("/create")
def create():
    if ADMIN_TOKEN and not secrets.compare_digest(request.form.get("admin_token",""),ADMIN_TOKEN):
        return render_page("Admin token is incorrect.",status=403)
    target=request.form.get("target_url","").strip(); image=request.form.get("image_url","").strip()
    platform=request.form.get("platform","Facebook")
    if platform not in ("Facebook","Twitter"): platform="Facebook"
    if len(target)>2048 or len(image)>2048 or not valid_url(target) or not valid_url(image):
        return render_page("Please enter valid http:// or https:// URLs.",status=400)
    code=secrets.token_urlsafe(6).replace("-","").replace("_","")[:8]
    with connect() as c:
        while execute(c, "SELECT 1 FROM links WHERE code=?",(code,)).fetchone():
            code=secrets.token_urlsafe(6).replace("-","").replace("_","")[:8]
        execute(c, "INSERT INTO links(code,target_url,image_url,title,platform) VALUES(?,?,?,?,?)",(code,target,image,"Custom image preview link",platform))
    return render_page(short_url=f"{base_url()}/s/{code}")

@app.get("/s/<code>")
def short(code):
    if not re.fullmatch(r"[A-Za-z0-9]{4,12}",code): abort(404)
    with connect() as c:
        item=execute(c, "SELECT * FROM links WHERE code=?",(code,)).fetchone()
        if not item:
            return render_template_string("""<!doctype html><html lang='en'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Link not found — {{ app_name }}</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0e172b;color:#f6f7fb;font:16px system-ui;padding:24px;box-sizing:border-box}.box{max-width:520px;text-align:center;background:#1d293d;border:1px solid #2c3a52;border-radius:20px;padding:32px}a{color:#aaa7ff}</style><main class='box'><h1>Link not found</h1><p>This short link does not exist in the current database. It may be outdated or its stored record may have been lost.</p><p><a href='/'>Open LinkShotnerPro</a> to create a new link.</p></main></html>""", app_name=APP_NAME),404

    canonical=f"{base_url()}/s/{code}"
    target=item["target_url"]
    # Social preview crawlers need the Open Graph tags to fetch the chosen image.
    # Real visitors skip the interstitial and are redirected immediately.
    user_agent=request.headers.get("User-Agent", "")
    crawler=re.search(r"facebookexternalhit|facebot|twitterbot|telegrambot|whatsapp|slackbot|discordbot|linkedinbot|pinterest|googlebot|bingbot", user_agent, re.I)
    if crawler:
        return render_template_string("""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{ title }}</title><meta property="og:type" content="website"><meta property="og:title" content="{{ title }}"><meta property="og:description" content="Open this link to continue."><meta property="og:image" content="{{ image }}"><meta property="og:url" content="{{ canonical }}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{{ title }}"><meta name="twitter:image" content="{{ image }}"><link rel="canonical" href="{{ canonical }}"></head><body></body></html>""",title=item["title"],image=item["image_url"],canonical=canonical)

    # Count the human visit and destination click, then issue an immediate HTTP redirect.
    with connect() as c:
        execute(c, "UPDATE links SET views=views+1, clicks=clicks+1 WHERE code=?",(code,))
    return redirect(target, code=302)

@app.post("/api/click/<code>")
def click(code):
    if not re.fullmatch(r"[A-Za-z0-9]{4,12}", code): return jsonify(error="Invalid short code"),400
    with connect() as c:
        cur=execute(c, "UPDATE links SET clicks=clicks+1 WHERE code=?",(code,))
        if cur.rowcount==0: return jsonify(error="Link not found"),404
    return jsonify(ok=True)

@app.get("/api/analytics")
def analytics():
    value=request.args.get("code","").strip()
    match=re.search(r"/s/([A-Za-z0-9]{4,12})",value)
    code=match.group(1) if match else value
    if not re.fullmatch(r"[A-Za-z0-9]{4,12}",code): return jsonify(error="Enter a valid short code or link."),400
    with connect() as c: item=execute(c, "SELECT code,target_url,views,clicks FROM links WHERE code=?",(code,)).fetchone()
    if not item: return jsonify(error="Short link not found."),404
    return jsonify(dict(item))

@app.get("/health")
def health():
    try:
        with connect() as c: execute(c, "SELECT 1")
        return jsonify(status="ok", database="connected", storage="postgresql" if DATABASE_URL else "sqlite"),200
    except Exception as exc:
        app.logger.exception("Health check failed")
        return jsonify(status="error", database="unavailable"),503

init_db()

def start_telegram_bot():
    """Start Telegram long polling from Render's TOKEN environment variable."""
    if not TELEGRAM_TOKEN:
        print("Telegram bot not started: add TOKEN in Render Environment.", flush=True)
        return
    if not WEB_APP_URL.startswith("https://"):
        print("Telegram bot not started: set WEB_APP_URL or BASE_URL to the public HTTPS web URL.", flush=True)
        return
    try:
        import telebot
        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
        telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)
        # Register slash-command suggestions so Telegram can suggest /start when the user types "/".
        from telebot.types import BotCommand, MenuButtonWebApp
        telegram_bot.set_my_commands([BotCommand("start", "Open LinkShotnerPro"), BotCommand("help", "How to use the bot"), BotCommand("webapp", "Open the link shortener")])
        try:
            telegram_bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="Link Shortner", web_app=WebAppInfo(url=WEB_APP_URL)))
        except Exception as menu_exc:
            print(f"Telegram menu button could not be set: {type(menu_exc).__name__}", flush=True)

        def open_app_markup():
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔗 Open LinkShotnerPro", web_app=WebAppInfo(url=WEB_APP_URL)))
            return markup

        @telegram_bot.message_handler(commands=["start"])
        def start_message(message):
            intro = ("What can this bot do?\n\n"
                     "Welcome to LinkShotnerPro! 🚀\n"
                     "This bot helps you create custom image preview short links and manage your URL, track campaign performance, and share links efficiently.\n\n"
                     "Tap the button below to get started.")
            if BOT_BANNER_URL.startswith("https://"):
                try:
                    telegram_bot.send_photo(message.chat.id, BOT_BANNER_URL, caption=intro, reply_markup=open_app_markup())
                    return
                except Exception as photo_exc:
                    print(f"Telegram banner could not be sent: {type(photo_exc).__name__}", flush=True)
            telegram_bot.reply_to(message, intro, reply_markup=open_app_markup())

        @telegram_bot.message_handler(commands=["webapp"])
        def webapp_message(message):
            telegram_bot.reply_to(message, "Open the LinkShotnerPro Web App:", reply_markup=open_app_markup())

        @telegram_bot.message_handler(commands=["help"])
        def help_message(message):
            telegram_bot.reply_to(message, "Quick guide:\n1. Type /start and tap Open LinkShotnerPro.\n2. Enter your destination URL and a direct image URL.\n3. Create and copy your short link.\n4. Use Track Link Clicks & Views to check analytics.", reply_markup=open_app_markup())

        print("Telegram bot polling started; command menu configured.", flush=True)
        telegram_bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
    except Exception as exc:
        print(f"Telegram bot stopped: {type(exc).__name__}: {exc}", flush=True)

# Start polling on module import so it works both with `python app.py` and Gunicorn.
# Keep exactly one Gunicorn worker to avoid duplicate Telegram polling processes.
if TELEGRAM_TOKEN:
    threading.Thread(target=start_telegram_bot, name="telegram-bot", daemon=True).start()
else:
    print("TOKEN is not set; web app will run, but Telegram bot will remain inactive.", flush=True)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=False)
