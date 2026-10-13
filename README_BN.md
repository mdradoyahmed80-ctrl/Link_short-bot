# LinkShotnerPro — Professional Fixed Build

এই build-এ Copy Short Link-এর clipboard fallback, স্পষ্ট missing-link পেজ, redirect fallback, health check এবং PostgreSQL database support যোগ করা হয়েছে।

## GitHub/Render-এ deploy
1. ZIP Extract করে ফোল্ডারের ভেতরের ফাইলগুলো GitHub repository-র root-এ upload/replace করুন। ZIP-কে ZIP হিসেবেই repository-তে রাখবেন না।
2. Render-এ Web Service deploy করুন (Docker)।
3. Environment Variables সেট করুন:
   - `TOKEN`: BotFather-এর Telegram bot token
   - `BASE_URL`: আপনার Render public HTTPS URL
   - `WEB_APP_URL`: একই public HTTPS URL
   - `APP_NAME`: `LinkShotnerPro`
   - `ADMIN_TOKEN`: চাইলে link creation-এর জন্য secret token; খালি রাখলে বন্ধ
   - `DATABASE_URL`: **স্থায়ী short link-এর জন্য সুপারিশকৃত** PostgreSQL connection URL
4. Deploy-এর পর `https://YOUR-SERVICE.onrender.com/health` খুলুন। `status: ok` এবং `database: connected` দেখা উচিত।
5. একটি নতুন short link তৈরি করুন, copy করুন, খুলুন। এরপর Render service restart করে আবার একই লিংক খুলে persistence পরীক্ষা করুন।

## 404 সমস্যার স্থায়ী সমাধান
`404 / Link not found` মানে বর্তমান database-এ ওই short code-এর record নেই। কোডের পরিবর্তন হারানো record ফিরিয়ে আনতে পারে না। পুরোনো লিংকের ডেটা যদি আগের ephemeral SQLite ফাইলেই ছিল এবং সেটি মুছে গিয়ে থাকে, পুরোনো short code পুনরুদ্ধারের backup ছাড়া সম্ভব নাও হতে পারে। নতুন লিংকগুলো restart/redeploy-এর পরও রাখতে PostgreSQL ব্যবহার করুন।

### PostgreSQL কীভাবে যুক্ত করবেন
Render Dashboard-এ PostgreSQL database তৈরি করুন (যে plan আপনার অ্যাকাউন্টে উপলভ্য), তারপর database-এর connection URL কপি করে Web Service-এর `DATABASE_URL` environment variable-এ দিন। একই provider-এর internal connection URL থাকলে সেটি ব্যবহার করুন। Save করে redeploy করুন। Secret URL GitHub-এ দেবেন না।

`DATABASE_URL` না দিলে অ্যাপ local SQLite ব্যবহার করবে। Render-এর ephemeral filesystem-এ SQLite ডেটা redeploy/replacement-এর পর স্থায়ী নয়। Render free web service-এ persistent disk উপলভ্য নাও হতে পারে; তাই persistent storage-এর জন্য PostgreSQL সবচেয়ে সহজ বিকল্প।

## Copy বাটন
HTTPS-এ Clipboard API ব্যবহার হবে। সেটি ব্যর্থ হলে browser fallback copy চেষ্টা করবে; তাতেও বাধা এলে লিংকটি select করে দেবে—মোবাইলে long-press করে Copy বেছে নিন।

## Telegram bot
`TOKEN` সেট থাকলে Telegram polling একই service process-এ চালু হবে। Logs-এ `Telegram bot polling started.` দেখুন।

## নিরাপত্তা ও uptime
- Telegram token বা database URL GitHub-এ commit করবেন না।
- Free hosting sleep/restart হতে পারে; 24/7 uptime নিশ্চিত নয়।
- শুধু আপনার অনুমোদিত destination URL ও image ব্যবহার করুন।


## Telegram-এ /start কমান্ড অটোমেটিক দেখানোর ব্যবস্থা
এই ভার্সনে বট চালু হলে Telegram Bot API-তে `/start`, `/help`, `/webapp` কমান্ড সেট করা হয়। ইউজার মেসেজ বক্সে `/` টাইপ করলে Telegram-এর command suggestion-এ `/start` দেখাতে পারে। বটের Menu Button-এও `Link Shortner` Web App যুক্ত করার চেষ্টা করা হয়। এটি কাজ করতে `TOKEN` (অথবা `BOT_TOKEN`) এবং HTTPS `WEB_APP_URL`/`BASE_URL` অবশ্যই Render-এ সেট করতে হবে। Telegram-এর UI/ক্লায়েন্ট অনুযায়ী command suggestion দেখা ভিন্ন হতে পারে।

## নতুন Web App ফিচার
- `🔥 Viral Hot Video` সেকশন থেকে নির্দিষ্ট external URL নতুন ট্যাবে খোলে।
- Advanced Guide ও feature cards যুক্ত।
- Short link তৈরি হলে Copy Short Link বাটন; clipboard API না চললে manual copy fallback।
- `/health` endpoint দিয়ে deployment/database health পরীক্ষা।
- স্থায়ী ডেটার জন্য Render PostgreSQL-এর `DATABASE_URL` ব্যবহার করার পরামর্শ দেওয়া হচ্ছে; SQLite ফাইল ephemeral hosting-এ হারিয়ে যেতে পারে।
