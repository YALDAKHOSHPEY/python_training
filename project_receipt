print("=" * 35)
print("      COFFEE SHOP ORDER")
print("=" * 35)

# دریافت اطلاعات
customer_name = input("Customer Name: ").strip().title()
drink = input("Drink Name: ").strip().title()

price = float(input("Price ($): "))
quantity = int(input("Quantity: "))
discount = float(input("Discount (%): "))

# محاسبات
subtotal = price * quantity
discount_amount = subtotal * (discount / 100)

after_discount = subtotal - discount_amount

tax = after_discount * 0.09

final_price = after_discount + tax

preparation_time = quantity * 3

# خروجی
print("\n" + "=" * 35)
print("           RECEIPT")
print("=" * 35)

print(f"Customer      : {customer_name}")
print(f"Drink         : {drink}")
print(f"Price         : ${price:.2f}")
print(f"Quantity      : {quantity}")
print(f"Name Length   : {len(customer_name)}")
print("-" * 35)
print(f"Subtotal      : ${subtotal:.2f}")
print(f"Discount      : {discount}%")
print(f"Discount Amt  : -${discount_amount:.2f}")
print(f"After Discount: ${after_discount:.2f}")
print(f"Tax (9%)      : +${tax:.2f}")
print("-" * 35)
print(f"Final Price   : ${final_price:.2f}")
print(f"Ready In      : {preparation_time} minutes")
print("=" * 35)

print(f"\nThank you, {customer_name}! ☕")
print("Have a nice day!")
