# برنامه تشخیص برج فلکی بر اساس تاریخ تولد
print("🌟" * 30)
print("🔮 به برنامه فال و برج فلکی خوش اومدی!")
print("🌟" * 30)

# گرفتن اطلاعات
name = input("\nاسمت چیه؟ ")
day = int(input("روز تولدت (عدد): "))
month = input("ماه تولدت (عدد 1-12 یا اسم ماه): ")

# تبدیل ماه به عدد اگه اسم وارد شده باشه
if month.isdigit():
    month = int(month)
else:
    # تبدیل اسم ماه به عدد
    month = month.lower()
    if month in ["فروردین", "farvardin", "1"]:
        month = 1
    elif month in ["اردیبهشت", "ordibehesht", "2"]:
        month = 2
    elif month in ["خرداد", "khordad", "3"]:
        month = 3
    elif month in ["تیر", "tir", "4"]:
        month = 4
    elif month in ["مرداد", "mordad", "5"]:
        month = 5
    elif month in ["شهریور", "shahrivar", "6"]:
        month = 6
    elif month in ["مهر", "mehr", "7"]:
        month = 7
    elif month in ["آبان", "aban", "8"]:
        month = 8
    elif month in ["آذر", "azar", "9"]:
        month = 9
    elif month in ["دی", "dey", "10"]:
        month = 10
    elif month in ["بهمن", "bahman", "11"]:
        month = 11
    elif month in ["اسفند", "esfand", "12"]:
        month = 12
    else:
        print("❌ ماه رو درست وارد کن!")
        month = 0

# تشخیص برج فلکی (بر اساس ماه و روز)
zodiac = ""
if month == 1:
    if day >= 20:
        zodiac = "دلو ♒"
    else:
        zodiac = "بز ♑"
elif month == 2:
    if day >= 19:
        zodiac = "حوت ♓"
    else:
        zodiac = "دلو ♒"
elif month == 3:
    if day >= 21:
        zodiac = "حمل ♈"
    else:
        zodiac = "حوت ♓"
elif month == 4:
    if day >= 20:
        zodiac = "ثور ♉"
    else:
        zodiac = "حمل ♈"
elif month == 5:
    if day >= 21:
        zodiac = "جوزا ♊"
    else:
        zodiac = "ثور ♉"
elif month == 6:
    if day >= 21:
        zodiac = "سرطان ♋"
    else:
        zodiac = "جوزا ♊"
elif month == 7:
    if day >= 23:
        zodiac = "اسد ♌"
    else:
        zodiac = "سرطان ♋"
elif month == 8:
    if day >= 23:
        zodiac = "سنبله ♍"
    else:
        zodiac = "اسد ♌"
elif month == 9:
    if day >= 23:
        zodiac = "میزان ♎"
    else:
        zodiac = "سنبله ♍"
elif month == 10:
    if day >= 23:
        zodiac = "عقرب ♏"
    else:
        zodiac = "میزان ♎"
elif month == 11:
    if day >= 22:
        zodiac = "قوس ♐"
    else:
        zodiac = "عقرب ♏"
elif month == 12:
    if day >= 22:
        zodiac = "جدی ♑"
    else:
        zodiac = "قوس ♐"

# نمایش نتیجه با پیام شخصیت‌سازی شده
print("\n" + "=" * 40)
print(f"✨ {name} جان، برج تو: {zodiac}")
print("=" * 40)

# شخصیت‌شناسی بر اساس برج
if zodiac == "حمل ♈" or zodiac == "اسد ♌" or zodiac == "قوس ♐":
    print("🔥 تو از گروه آتش هستی! پرانرژی، شجاع و ریسک‌پذیر!")
    if zodiac == "حمل ♈":
        print("💪 پیشگام و رهبر به دنیا اومدی!")
    elif zodiac == "اسد ♌":
        print("👑 عاشق دیده شدن و درخشیدن هستی!")
    else:
        print("🏹 آزاد و ماجراجو! هیچ چیزی نمی‌تونه متوقف‌ت کنه!")

elif zodiac == "ثور ♉" or zodiac == "سنبله ♍" or zodiac == "جدی ♑":
    print("🌍 تو از گروه خاک هستی! عملی، منطقی و با پشتکار!")
    if zodiac == "ثور ♉":
        print("🌸 اهل هنر، طبیعت و لذت‌های زندگی!")
    elif zodiac == "سنبله ♍":
        print("🔍 دقیق، منظم و کمال‌گرا!")
    else:
        print("🏔️ جاه‌طلب و محکم! هیچ‌وقت تسلیم نمی‌شی!")

elif zodiac == "جوزا ♊" or zodiac == "میزان ♎" or zodiac == "دلو ♒":
    print("🌪️ تو از گروه هوا هستی! باهوش، اجتماعی و ایده‌پرداز!")
    if zodiac == "جوزا ♊":
        print("🗣️ فوق‌العاده کنجکاو و عاشق یادگیری!")
    elif zodiac == "میزان ♎":
        print("⚖️ عاشق زیبایی، عدالت و روابط اجتماعی!")
    else:
        print("💡 یه متفکر نوآور! آینده‌نگری عالی داری!")

else:  # سرطان, عقرب, حوت
    print("🌊 تو از گروه آب هستی! احساساتی، شهودی و عمیق!")
    if zodiac == "سرطان ♋":
        print("🏠 خانواده‌دوست و بسیار مهربون!")
    elif zodiac == "عقرب ♏":
        print("🔮 رازآلود، جذاب و قدرتمند!")
    else:
        print("🎨 خیال‌پرداز و فوق‌العاده خلاق!")

# توصیه روزانه با if-elif
print("\n📝 توصیه ویژه برای امروز:")
if zodiac in ["حمل ♈", "اسد ♌", "قوس ♐"]:
    print("   انرژی‌ات رو روی یه پروژه جدید متمرکز کن! 💥")
elif zodiac in ["ثور ♉", "سنبله ♍", "جدی ♑"]:
    print("   امروز یه کار عملی رو به پایان برسون! ✅")
elif zodiac in ["جوزا ♊", "میزان ♎", "دلو ♒"]:
    print("   با یه دوست قدیمی ارتباط بگیر! 📱")
else:
    print("   به حس درونت گوش بده و یه کار هنری انجام بده! 🎨")

print("\n" + "🌟" * 30)
print("🔮 فال تو امروز: روز خوبی در انتظارته!")
print("🌟" * 30)
