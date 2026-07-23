# بازی حدس عدد با مقایسه‌های پیشرفته
import random

secret = random.randint(1, 100)
attempts = 0

print("🎯 عددی بین 1 تا 100 حدس بزن!")

while True:
    guess = int(input("حدست: "))
    attempts += 1
    
    # مقایسه‌های مختلف
    if guess == secret:
        print(f"🎉 آفرین! در {attempts} تلاش پیدا کردی!")
        break
    elif guess > secret:
        print("📈 برو پایین‌تر!")
    else:
        print("📉 برو بالاتر!")
    
    # مقایسه تعداد تلاش‌ها
    if attempts >= 5:
        print(f"💡 راهنمایی: عدد بین {secret-5} و {secret+5} هست")
    if attempts >= 10:
        print(f"😅 عدد {secret} بود! بازی تموم!")
        break
