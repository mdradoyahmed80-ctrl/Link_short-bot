# LinkShotnerPro — ভিডিও রেফারেন্স ও QA রিপোর্ট

## পরীক্ষার পরিধি ও সীমাবদ্ধতা
- রেফারেন্স ভিডিও: 720×1600 portrait, প্রায় 35.69 সেকেন্ড। ভিডিওতে Telegram chat এবং Telegram Web App দেখা যায়।
- অ্যাক্সেসযোগ্য সোর্স: এই প্যাকেজের `app.py`, `.env.example`, `render.yaml`, `Dockerfile`, `Procfile`, `requirements.txt`, `.gitignore`, `README_BN.md`।
- তুলনা ভিডিওর দৃশ্যমান ফ্রেম/কন্ট্যাক্ট-শিট এবং সোর্স কোড দেখে করা হয়েছে। এই পরিবেশে Python-এর Flask/Telegram dependencies আগে থেকে ইনস্টল ছিল না এবং নেটওয়ার্ক বন্ধ থাকায় ইনস্টল করা যায়নি। ফলে live server, real Telegram API, database, browser interaction এবং screenshot-to-screenshot runtime comparison সম্পন্ন করা যায়নি। নিচের পরীক্ষায় source/static validation-কে runtime test হিসেবে দেখানো হয়নি।

## ভিডিওর স্ক্রিন ও ট্রানজিশন

| দৃশ্য | ভিডিওতে দেখা আচরণ | সোর্সে মিল / পরিবর্তন |
|---|---|---|
| 1. Telegram bot chat | সবুজ Telegram chat background; bot header; banner image; “What can this bot do?”; welcome text; `/start` ও Open app interaction | `/start` handler ছিল, কিন্তু banner ছিল না। `BOT_BANNER_URL` optional করে `send_photo` + caption + Web App button যোগ করা হয়েছে। URL না থাকলে text fallback থাকে। |
| 2. Web App ওপেন | Telegram-এর embedded browser/header; dark navy app page | `/` route-এ Web App page আছে। Telegram header Telegram নিজেই রেন্ডার করে; ওয়েবসাইটের HTML দিয়ে সেটি হুবহু নিয়ন্ত্রণ করা যায় না। |
| 3. Header | `LinkShotnerPro`, `Products`, `Pricing` | একই লেবেল রাখা হয়েছে; মোবাইলে header height/padding কমানো হয়েছে। Products/Pricing ভিডিওতে দৃশ্যমান ন্যাভিগেশন লেবেল, তবে ভিডিওতে তাদের click outcome দেখা যায়নি; তাই এগুলোকে fake navigation বানানো হয়নি। |
| 4. Hero | “Make Shorten URL for your brand”; ছোট description; Facebook/Twitter selector | একই content ও platform selector রাখা হয়েছে; selected platform label ও hidden form field update করে। |
| 5. URL creation card | Platform label; Destination Long URL; Imgur Direct Image Link; `URL Shorten` | `/create` POST route, URL validation, short code generation, database insert আছে। মোবাইল card/input/button spacing ও corner radius ভিডিওর ঘন layout-এর কাছাকাছি করা হয়েছে। |
| 6. Create result | তৈরি short URL এবং copy action | result panel ও copy button আছে; Clipboard API ব্যর্থ হলে manual select fallback আছে। |
| 7. Analytics card | “Track Link Clicks & Views”; short code/link input; `Check Analytics` | `/api/analytics` ব্যবহার করে real database record খোঁজে; fake analytics data ব্যবহার করে না। Error/success state দেখায়। Analytics DOM rendering-এ untrusted response text সরাসরি HTML-এ বসানো বন্ধ করা হয়েছে। |
| 8. Guide card | “Advanced Link Shortener & Social Booster Guide”; “How To Use This Tool”; feature bullet/card content | Guide/feature cards আছে। রেফারেন্সের দীর্ঘ লেখা ও মোবাইল scroll অবস্থার কিছু ক্ষুদ্র wording/line-wrap পুরোপুরি pixel-identical নয়। |
| 9. Viral CTA | “🔥 Viral Hot Video” এবং সবুজ pill-ধাঁচের external CTA | সোর্সে নির্দিষ্ট external destination রাখা হয়েছে। URL-এর বাইরের সাইট ও সেটির নিরাপত্তা/উপলভ্যতা এই অ্যাপের নিয়ন্ত্রণে নয়। |
| 10. Scroll/keyboard states | বিভিন্ন scroll position, Telegram keyboard, chat composer এবং Web App minimize/close chrome | Telegram keyboard ও native chrome Telegram-এর নিয়ন্ত্রণে। ওয়েব পেজের স্বাভাবিক responsive scroll বজায় আছে; keyboard/Telegram app automation করা হয়নি। |
| 11. Short-link landing page | ভিডিওতে পূর্ণাঙ্গ short-link landing-এর বিস্তারিত interaction স্পষ্টভাবে দেখানো হয়নি | `/s/<code>`-এ OG/Twitter preview metadata, continue page, view counter, click tracking ও redirect আছে। |

## দৃশ্যমান পার্থক্য যেগুলো ঠিক করা হয়েছে
- ছোট portrait viewport-এ অতিরিক্ত বড় header, hero margin, card padding, input ও button height কমিয়ে compact layout করা হয়েছে।
- মোবাইল breakpoint-এ logo/nav, form input, platform buttons, card radius ও heading sizes আলাদাভাবে নির্ধারণ করা হয়েছে।
- `/start` welcome text-এর আগে banner image দেখানোর optional support যোগ হয়েছে।
- Analytics result-এ server/database text HTML string হিসেবে interpolate না করে DOM `textContent` দিয়ে render করা হয়।
- `.env.example`, Render environment configuration এবং বাংলা run/deploy documentation-এ banner variable যোগ হয়েছে।

## Button/API QA checklist

| পরীক্ষা | অবস্থা | প্রমাণ/কারণ |
|---|---|---|
| `GET /` route source | PASS — static review | route ও template আছে; live HTTP request চালানো যায়নি। |
| Facebook/Twitter selector | PASS — source review only | click handler label, hidden form value ও active class বদলায়; browser interaction চালানো হয়নি। |
| Empty/invalid URL validation | PASS — source review only | required fields ও server-side http/https URL validation আছে। |
| Short link create + database insert | NOT RUN | Flask ও database driver dependencies এই পরিবেশে ইনস্টল করা যায়নি; live DB configured নয়। |
| Copy Short Link | NOT RUN | Clipboard API browser security context ও manual fallback source-এ আছে; real browser click test হয়নি। |
| Analytics success/error | NOT RUN | API/DOM code পর্যালোচনা হয়েছে; live DB-তে record দিয়ে পরীক্ষা হয়নি। |
| Short URL not-found state | PASS — source review only | missing record-এর জন্য 404 page আছে। |
| Preview view count | NOT RUN | database update logic আছে; runtime counter যাচাই হয়নি। |
| Destination click tracking / redirect | NOT RUN | click endpoint ও redirect script আছে; real browser/network test হয়নি। |
| `/health` | NOT RUN | route source আছে; server চালানো যায়নি। |
| Telegram `/start` banner | NOT RUN | Telegram token ও public banner URL নেই; Bot API call হয়নি। |
| Telegram `/help`, `/webapp`, menu button | NOT RUN | code-এ handlers/config আছে; live Telegram API পরীক্ষা হয়নি। |
| PostgreSQL persistence/restart | NOT RUN | valid `DATABASE_URL`/PostgreSQL instance নেই। |
| Render deploy/build | NOT RUN | Render account/service-এ deploy করা হয়নি। |
| Responsive screenshot comparison | PARTIAL | ভিডিওর 720×1600 viewport দেখে CSS compact করা হয়েছে; live app screenshot নিয়ে pixel diff করা যায়নি। |

## অবশিষ্ট mismatch / blocker
1. Runtime test ও screenshot comparison সম্পন্ন করতে dependency install করা যায় এমন environment, configured database এবং browser-served app প্রয়োজন।
2. Telegram banner দেখাতে `BOT_BANNER_URL`-এ publicly accessible HTTPS image URL দিতে হবে। Telegram bot-এর profile photo, short description এবং About text BotFather থেকে সেট করতে হয়; application code এগুলো বদলাতে পারে না।
3. স্থায়ী short-link data-এর জন্য Render PostgreSQL-এর `DATABASE_URL` দিন। SQLite ব্যবহার করলে ephemeral hosting-এ record হারাতে পারে।
4. ভিডিওতে Products/Pricing-এ click করলে কী হয় তা নিশ্চিতভাবে দেখা যায়নি; তাই সেগুলোকে কার্যকর ভান করে নতুন page-এ লিংক করা হয়নি।
5. Exact font rendering, browser chrome, Telegram status bar, keyboard এবং pixel-perfect line wrapping ডিভাইস/Telegram client অনুযায়ী বদলাবে।

## Build ও Run

### Local
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # এরপর প্রয়োজনীয় মান বসান; dotenv স্বয়ংক্রিয় লোড হয় না, shell environment-এ export করুন
python app.py
```

`TOKEN` না থাকলেও web app চলবে; Telegram bot নিষ্ক্রিয় থাকবে। `BASE_URL`/`WEB_APP_URL` public HTTPS URL হওয়া দরকার Telegram Web App-এর জন্য। `BOT_BANNER_URL` ঐচ্ছিক, কিন্তু দিলে direct public HTTPS image URL ব্যবহার করুন।

### Render
1. ZIP extract করে ফাইলগুলো GitHub repository root-এ রাখুন।
2. Render-এ Docker Web Service তৈরি করুন। `render.yaml` ব্যবহার করলে environment values পূরণ করুন।
3. `TOKEN`, `BASE_URL`, `WEB_APP_URL`, এবং persistent data দরকার হলে `DATABASE_URL` সেট করুন। `BASE_URL`/`WEB_APP_URL`-এ আপনার Render HTTPS domain দিন।
4. ঐচ্ছিকভাবে `BOT_BANNER_URL` দিন।
5. deploy শেষে `/health` খুলে database status যাচাই করুন এবং নিজের তৈরি short link দিয়ে end-to-end test করুন।
6. Render log-এ `Telegram bot polling started` দেখুন। Free plan-এ sleep/restart হতে পারে; 24/7 uptime নিশ্চিত নয়।

## অতিরিক্ত পরিবর্তন: Direct Redirect
- `/s/<code>` এখন সাধারণ ভিজিটরের জন্য কোনো Continue পেজ, countdown, notification বা JavaScript delay দেখায় না; সরাসরি HTTP 302 redirect দেয়।
- Facebook/Twitter/Telegram/WhatsApp-এর মতো social preview crawler-কে Open Graph metadata দেওয়া হয়, যাতে শেয়ার করা লিংকের image preview তৈরি হতে পারে।
- সাধারণ ভিজিটরের redirect-এর সময় `views` ও `clicks` একবার করে বাড়ে। Crawler preview fetch-কে click হিসেবে গণনা করা হয় না।
- সীমাবদ্ধতা: Telegram/Facebook-এর নির্দিষ্ট সব User-Agent ভিন্ন হতে পারে; প্ল্যাটফর্ম preview cache করে রাখতে পারে। বাস্তব deployed app-এ live test করা প্রয়োজন।
