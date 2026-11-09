# rkn-s1 — aiTrends 2D Studio

> تحويل أي تعليق صوتي إلى فيديو متحرك سينمائي بأسلوب Stick Figure

Turn any voiceover into a fully animated, cinematic stick-figure video: black stick figures with glowing rim light acting out the narration in moody 2.5D sets, giant face close-ups, freeze-frame moments, animated numbers and charts, blueprint-style explainers and low-poly 3D orbit shots — with generated music and sound effects.

**كل إطار يُرسم بالكود** (HTML Canvas + Three.js) ويُلتقط إطاراً بإطار. لا يُستخدم أي نموذج توليد صور أو فيديو بالذكاء الاصطناعي، لذلك تبقى الشخصيات متسقة والنصوص حادة.

---

## المميزات | Features

| الميزة | Feature |
|--------|---------|
| شخصيات Stick Figure متسقة | Consistent stick-figure characters |
| 5 أنماط بصرية جاهزة | 5 switchable visual styles |
| نسب 16:9 و 9:16 | 16:9 and 9:16 aspect ratios |
| دقة من 720p إلى 4K | 720p → 4K resolution |
| توقيت تلقائي بـ Whisper | Auto timestamps with Whisper |
| موسيقى وتأثيرات صوتية مولّدة | Generated music & SFX |
| لا حاجة لمفاتيح API | No API keys required |

### الأنماط البصرية | Visual Styles
- **Cinematic Dusk** — ظلال بنفسجية، إضاءة كهرمانية
- **Midnight Blue** — أزرق بارد، مناسب للليل والتشويق
- **Golden Hour** — برتقالي ودافئ، حنين وإلهام
- **Neon Noir** — أسود عميق مع وردي وفيروزي (سايبر/جريمة)
- **Soft Storybook** — باستيل خفيف، مناسب للعائلات

---

## الأوامر | Commands (Claude Plugin)

| الأمر | الوظيفة |
|-------|---------|
| `/new-video` | إعداد المشروع + توقيت السرد + تخطيط اللقطات |
| `/video-styles` | عرض الـ 5 أنماط واختيار واحد أو تخصيص |
| `/render-video` | بناء المشاهد + معاينة + رندر نهائي |
| `/video-sound` | الموسيقى + التأثيرات + المزج النهائي |

أو ببساطة: **"Make a 2D video from this voiceover"** لتشغيل الأنبوب كاملاً.

---

## هيكل المستودع | Repository Structure

```
rkn-s1/
├── README.md
├── .gitignore
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── make-2d-video/          # الأنبوب الكامل + المراجع + المحرك
│   │   ├── SKILL.md
│   │   ├── kit/                # الاستوديو (محرك + أدوات + مثال)
│   │   └── references/         # دليل الأسلوب، API، التثبيت...
│   ├── new-video/
│   ├── video-styles/
│   ├── render-video/
│   └── video-sound/
```

---

## التثبيت السريع | Quick Setup

```bash
# 1. استنساخ المستودع
git clone https://github.com/mimr5445-dev/rkn-s1.git
cd rkn-s1

# 2. نسخ الاستوديو إلى مجلد العمل
cp -r skills/make-2d-video/kit aitrends-2d-studio
cd aitrends-2d-studio

# 3. تثبيت الاعتماديات
npm install
npx playwright install chromium
pip install numpy scipy faster-whisper

# 4. التحقق
python tools/doctor.py
node render.mjs --project examples/reaction-time --sheet --scale 0.3
```

راجع `skills/make-2d-video/references/install.md` للتفاصيل الكاملة.

---

## المدخلات | Inputs

- **صوت (Voiceover)** بأي صيغة شائعة
- **نص (Script)** اختياري: SRT / VTT / JSON / TXT أو نص عادي
- نسبة العرض، الدقة، تعليقات محروقة اختيارياً
- موسيقى حسب المزاج أو ملف خاص بك أو بدون

---

## أوقات الرندر | Render Times

على جهاز سحابي صغير (2 نواة):
- **720p** ≈ 2 إطار/ثانية
- **1080p** ≈ ضعف الوقت
- **4K** ≈ 8 أضعاف

جهاز مكتبي حديث أسرع بـ 3–5 مرات.

---

## الحالة | Status

- الإصدار: **0.1.0**
- المصدر الأصلي: إضافة Claude Plugin من aiTrends
- جاري التطوير والتحسين على هذا المستودع

---

## المساهمة | Contributing

نرحب بالمساهمات! افتح Issue أو Pull Request.

---

## الترخيص | License

كل الحقوق محفوظة. لا يحق لأحد الاستخدام أو النسخ أو التعديل أو التوزيع إلا بإذن كتابي مسبق من صاحب الحقوق. انظر ملف `LICENSE`.

All rights reserved. No use, copying, modification, or distribution without prior written permission. See `LICENSE`.
