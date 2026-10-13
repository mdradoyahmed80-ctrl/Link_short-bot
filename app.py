import os, re, secrets, sqlite3, threading
from urllib.parse import urlparse
from flask import Flask, request, render_template_string, abort, jsonify

app = Flask(__name__)
DB_PATH = os.getenv("DATABASE_PATH", "links.db")
BASE_URL = (os.getenv("BASE_URL", "").strip() or os.getenv("RENDER_EXTERNAL_URL", "").strip()).rstrip("/")
APP_NAME = os.getenv("APP_NAME", "LinkShotnerPro")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
TELEGRAM_TOKEN = os.getenv("TOKEN", "").strip() or os.getenv("BOT_TOKEN", "").strip()
WEB_APP_URL = (os.getenv("WEB_APP_URL", "").strip() or BASE_URL or os.getenv("RENDER_EXTERNAL_URL", "").strip()).rstrip("/")

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ app_name }} — Custom Image Preview Links</title>
<style>
:root{color-scheme:dark;--bg:#0e172b;--card:#1d293d;--border:#2c3a52;--text:#f6f7fb;--muted:#9aa9bf;--purple:#5145e5;--blue:#347ff0}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}
nav{height:95px;border-bottom:1px solid #202c40;display:flex;align-items:center;justify-content:space-between;padding:0 max(26px,calc((100vw - 1000px)/2));gap:20px}
.logo{font-size:clamp(21px,3vw,30px);font-weight:850;letter-spacing:-1px;color:#8185ff}nav .links{display:flex;gap:24px;color:#a8b3c7;font-weight:600}
main{max-width:760px;margin:auto;padding:48px 26px 42px}.hero{text-align:center;margin-bottom:30px}.hero h1{font-size:clamp(31px,6vw,49px);line-height:1.18;letter-spacing:-1.6px;margin:0 auto 18px;max-width:700px}.accent{color:#8584ff}.hero p{font-size:clamp(17px,3vw,22px);color:var(--muted);max-width:600px;margin:0 auto 32px}
.platforms{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:34px}.platform{border:1px solid #303c50;border-radius:14px;padding:15px 12px;background:#202c40;color:#a9b5c8;font-size:18px;font-weight:750;cursor:pointer}.platform.active{background:var(--purple);border-color:var(--purple);color:#fff}
.card{background:var(--card);border:1px solid var(--border);border-radius:27px;padding:32px 34px;margin:0 0 34px;box-shadow:0 18px 40px #0001}.platform-label{color:#9a9bff;font-weight:750;margin-bottom:14px;font-size:18px}label{display:block;color:#a9b7ca;font-weight:600;margin:16px 0 10px}input{display:block;width:100%;min-width:0;background:#0e1729;border:1px solid #35435a;color:#fff;border-radius:14px;padding:18px 20px;font:inherit;font-size:18px;outline:none}input:focus{border-color:#7776ff;box-shadow:0 0 0 3px #7776ff22}button.submit{width:100%;border:0;border-radius:14px;background:var(--purple);color:#fff;padding:18px;font-size:21px;font-weight:800;margin-top:26px;cursor:pointer}button.blue{background:var(--blue)}.card h2{font-size:25px;margin:0 0 22px;letter-spacing:-.5px}.result,.message{margin-top:20px;background:#0e1729;border:1px solid #35435a;border-radius:13px;padding:15px;overflow-wrap:anywhere}.result a{color:#a6a2ff}.hidden{display:none}.hint{color:var(--muted);font-size:14px}.error{color:#ffd9e0}.stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px}.stat{background:#111c30;border:1px solid #33415b;border-radius:12px;padding:14px}.stat b{display:block;font-size:27px}.stat span{color:var(--muted);font-size:13px}
@media(max-width:520px){nav{height:95px;padding:0 26px}.links{gap:16px!important;font-size:15px}main{padding:48px 26px 30px}.card{padding:30px 34px;border-radius:27px}.platforms{gap:16px}.platform{font-size:16px;padding:15px 8px}input{font-size:17px;padding:18px 20px}.hero h1{font-size:clamp(30px,7vw,40px)}.card h2{font-size:23px}}
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
{% if short_url %}<div class="result"><strong>Your short link:</strong><p><a href="{{ short_url }}">{{ short_url }}</a></p><button class="submit" type="button" onclick="navigator.clipboard.writeText({{ short_url|tojson }}).then(()=>this.textContent='Copied ✓')">Copy Short Link</button><p class="hint">Social platforms may cache link previews.</p></div>{% endif %}
</section>
<section class="card"><h2>📊 Track Link Clicks &amp; Views</h2><form id="analyticsForm"><label for="code">Enter Short Link or Code:</label><input id="code" name="code" required placeholder="e.g. code or full link"><button class="submit blue" type="submit">Check Analytics</button></form><div id="analyticsResult"></div></section>
<p class="hint">Use only links and images you own or are authorized to share.</p></main>
<script>
function choosePlatform(p){document.getElementById('platformName').textContent=p;document.getElementById('platformInput').value=p;document.getElementById('facebook').classList.toggle('active',p==='Facebook');document.getElementById('twitter').classList.toggle('active',p==='Twitter')}
document.getElementById('analyticsForm').addEventListener('submit',async e=>{e.preventDefault();const value=document.getElementById('code').value.trim();const box=document.getElementById('analyticsResult');box.innerHTML='<div class="message">Loading…</div>';try{const r=await fetch('/api/analytics?code='+encodeURIComponent(value));const d=await r.json();if(!r.ok)throw new Error(d.error||'Could not find link');box.innerHTML=`<div class="result"><strong>Analytics for ${d.code}</strong><div class="stats"><div class="stat"><b>${d.views}</b><span>Preview page views</span></div><div class="stat"><b>${d.clicks}</b><span>Destination clicks</span></div></div><p class="hint">Destination: ${d.target_url}</p></div>`}catch(err){box.innerHTML='<div class="message error">'+err.message+'</div>'}});
</script></body></html>"""

def connect():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS links(code TEXT PRIMARY KEY,target_url TEXT NOT NULL,image_url TEXT NOT NULL,title TEXT NOT NULL,platform TEXT NOT NULL,views INTEGER NOT NULL DEFAULT 0,clicks INTEGER NOT NULL DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        # Upgrade older database schemas safely.
        cols={r["name"] for r in c.execute("PRAGMA table_info(links)")}
        for name, decl in [("platform","TEXT NOT NULL DEFAULT 'Facebook'"),("views","INTEGER NOT NULL DEFAULT 0"),("clicks","INTEGER NOT NULL DEFAULT 0"),("title","TEXT NOT NULL DEFAULT 'Your link'")]:
            if name not in cols: c.execute(f"ALTER TABLE links ADD COLUMN {name} {decl}")

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
        while c.execute("SELECT 1 FROM links WHERE code=?",(code,)).fetchone():
            code=secrets.token_urlsafe(6).replace("-","").replace("_","")[:8]
        c.execute("INSERT INTO links(code,target_url,image_url,title,platform) VALUES(?,?,?,?,?)",(code,target,image,"Custom image preview link",platform))
    return render_page(short_url=f"{base_url()}/s/{code}")

@app.get("/s/<code>")
def short(code):
    if not re.fullmatch(r"[A-Za-z0-9]{4,12}",code): abort(404)
    with connect() as c:
        item=c.execute("SELECT * FROM links WHERE code=?",(code,)).fetchone()
        if not item: abort(404)
        c.execute("UPDATE links SET views=views+1 WHERE code=?",(code,))
    canonical=f"{base_url()}/s/{code}"
    return render_template_string("""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title><meta property="og:type" content="website"><meta property="og:title" content="{{ title }}"><meta property="og:description" content="Open this link to continue."><meta property="og:image" content="{{ image }}"><meta property="og:url" content="{{ canonical }}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{{ title }}"><meta name="twitter:image" content="{{ image }}"><link rel="canonical" href="{{ canonical }}"><meta http-equiv="refresh" content="2;url={{ target }}">
<style>body{background:#0e172b;color:#fff;font:17px system-ui;display:grid;place-items:center;min-height:90vh;text-align:center;padding:20px}a{color:#9a9bff}</style></head><body><main><h2>Opening your link…</h2><p><a href="{{ target }}" onclick="fetch('/api/click/{{ code }}',{method:'POST',keepalive:true})">Continue now</a></p></main><script>setTimeout(()=>{fetch('/api/click/{{ code }}',{method:'POST',keepalive:true}).finally(()=>location.replace({{ target|tojson }}));},1800)</script></body></html>""",title=item["title"],image=item["image_url"],canonical=canonical,target=item["target_url"],code=code)

@app.post("/api/click/<code>")
def click(code):
    with connect() as c:
        cur=c.execute("UPDATE links SET clicks=clicks+1 WHERE code=?",(code,))
        if cur.rowcount==0: return jsonify(error="Link not found"),404
    return jsonify(ok=True)

@app.get("/api/analytics")
def analytics():
    value=request.args.get("code","").strip()
    match=re.search(r"/s/([A-Za-z0-9]{4,12})",value)
    code=match.group(1) if match else value
    if not re.fullmatch(r"[A-Za-z0-9]{4,12}",code): return jsonify(error="Enter a valid short code or link."),400
    with connect() as c: item=c.execute("SELECT code,target_url,views,clicks FROM links WHERE code=?",(code,)).fetchone()
    if not item: return jsonify(error="Short link not found."),404
    return jsonify(dict(item))

@app.get("/health")
def health(): return jsonify(status="ok")

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

        @telegram_bot.message_handler(commands=["start"])
        def start_message(message):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔗 Open LinkShotnerPro", web_app=WebAppInfo(url=WEB_APP_URL)))
            telegram_bot.reply_to(message, "Welcome to LinkShotnerPro! Tap below to create short links and view analytics.", reply_markup=markup)

        @telegram_bot.message_handler(commands=["help"])
        def help_message(message):
            telegram_bot.reply_to(message, "Send /start and tap Open LinkShotnerPro to open the web app.")

        print("Telegram bot polling started.", flush=True)
        telegram_bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
    except Exception as exc:
        print(f"Telegram bot stopped: {type(exc).__name__}: {exc}", flush=True)

if __name__=="__main__":
    if TELEGRAM_TOKEN:
        threading.Thread(target=start_telegram_bot, name="telegram-bot", daemon=True).start()
    else:
        print("TOKEN is not set; web app will run, but Telegram bot will remain inactive.", flush=True)
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=False)
