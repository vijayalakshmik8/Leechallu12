# Render Deployment (Malayalam)

## GitHub / Render
1. ഈ പ്രോജക്ട് ഒരു **Private GitHub repository**-ലേക്ക് അപ്‌ലോഡ് ചെയ്യുക.
2. https://render.com തുറന്ന് GitHub വഴി Sign in ചെയ്യുക.
3. **New + → Blueprint** തിരഞ്ഞെടുക്കുക; repository connect ചെയ്ത് `render.yaml` deploy ചെയ്യുക.
4. Render ചോദിക്കുന്ന Environment Variables നൽകുക.

## ആവശ്യമായ Environment Variables
- `API_ID` — my.telegram.org-ൽ നിന്നുള്ള Telegram API ID
- `API_HASH` — Telegram API Hash
- `BOT_TOKEN` — @BotFather നൽകിയ bot token
- `DATABASE_CHANNEL_ID` — Database channel ID; ബോട്ടിന് Post permission വേണം
- `LOG_CHANNEL_ID` — Log channel ID; ബോട്ടിന് Post permission വേണം
- `ALLOWED_GROUP_ID` — അനുവദിച്ച ഗ്രൂപ്പിന്റെ ID

`F_SUB_CHANNEL_1`, `F_SUB_CHANNEL_2` എന്നിവയ്ക്ക് YAML-ൽ നിലവിലെ default values നൽകിയിട്ടുണ്ട്.

## ശ്രദ്ധിക്കുക
- Dockerfile FFmpeg/FFprobe ഇൻസ്റ്റാൾ ചെയ്യുന്നു. Start command `python bot.py` ആണ്; Dockerfile ഇത് സ്വയം നടത്തും.
- Render Free Web Service idle ആയാൽ sleep ചെയ്യാം. 24/7 പ്രവർത്തനത്തിന് സ്ഥിരമായി പ്രവർത്തിക്കുന്ന paid instance തിരഞ്ഞെടുക്കുക.
- Render-ന്റെ സാധാരണ filesystem സ്ഥിരമായ storage അല്ല; GoFile tracker പോലുള്ള local data restart/redeploy കഴിഞ്ഞും വേണമെങ്കിൽ persistent disk/external storage വേണം.
- ZIP-ൽ `cookies.txt`, `instagram_com_cookies.txt`, `terabox.app_cookies.txt` ഉണ്ട്. ഇവയിൽ login/session വിവരങ്ങൾ ഉണ്ടായേക്കാം. Public GitHub-ൽ ഇടരുത്; Private repo മാത്രം ഉപയോഗിക്കുക. ഇതിനകം public ആയി പോയിട്ടുണ്ടെങ്കിൽ ബന്ധപ്പെട്ട sessions revoke/refresh ചെയ്യുക.
- Bot token/API hash/cookies ആരുമായും പങ്കിടരുത്.
