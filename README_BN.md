# LinkShotnerPro — One-Token Standard Deployment

এই প্যাকেজটি এমনভাবে সাজানো হয়েছে যাতে Render-এ সাধারণ সেটআপে শুধু `TOKEN` দিতে হয়। একই Docker Web Service-এ ওয়েবসাইট ও Telegram bot চালু হয়। Render-এর `RENDER_EXTERNAL_URL` থেকে public URL স্বয়ংক্রিয়ভাবে নেওয়া হয়, তাই `BASE_URL` এবং `WEB_APP_URL` আলাদা করে দেওয়া বাধ্যতামূলক নয়।

## ১) GitHub-এ আপলোড
1. ZIP Extract করুন।
2. ভেতরের ফাইলগুলো repository-র root-এ upload করুন; ZIP-কে ZIP হিসেবেই রাখবেন না।
3. আসল bot token কখনো GitHub-এ commit করবেন না।

## ২) Render-এ Deploy
1. Render Dashboard → New + → Blueprint।
2. GitHub repository connect করুন এবং `render.yaml` deploy করুন।
3. Render চাইলে শুধু `TOKEN` দিন: BotFather-এর আসল Telegram Bot Token।
4. Deploy শেষ হলে Render Logs দেখুন। `Telegram bot polling started.` দেখা গেলে bot polling শুরু হয়েছে।
5. Telegram-এ bot খুলে `/start` পাঠান।

## Environment Variables
- Required: `TOKEN` — BotFather থেকে পাওয়া আসল Token।
- Optional: `BASE_URL`, `WEB_APP_URL`, `APP_NAME`, `ADMIN_TOKEN`, `DATABASE_PATH`। সাধারণ Render deployment-এ URL Render থেকে স্বয়ংক্রিয়ভাবে শনাক্ত হয় এবং অ্যাপের নাম `LinkShotnerPro`।
- `ADMIN_TOKEN` ফাঁকা থাকলে admin-token check বন্ধ থাকে; চাইলে Render-এ একটি লম্বা secret সেট করুন।

## Runtime
Dockerfile Python 3.12 ব্যবহার করে এবং `python app.py` চালায়। Flask web app ও Telegram long polling একই process/container-এ চলে; আলাদা Background Worker দরকার নেই এই প্যাকেজের জন্য।

## সীমাবদ্ধতা
- Render Free service সবসময় 24/7 চালু থাকার নিশ্চয়তা দেয় না।
- SQLite data local container storage-এ থাকলে redeploy/restart-এ হারাতে পারে; persistent storage/PostgreSQL ব্যবহার করুন যদি data স্থায়ী রাখা জরুরি হয়।
- Token গোপন রাখুন। প্রকাশ হয়ে গেলে BotFather থেকে revoke/rotate করুন।
