from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import asyncio
import requests

API_TOKEN = "7827525317:AAFJ78u1Ws4H-Vk___jcjn7CZx8wlfH0Bm4"
WEATHER_API_KEY = "fb09e2009249fa7e2e63e51479c5fa63"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Foydalanuvchiga ko‘rinadigan viloyatlar
cities = [
    "Toshkent", "Samarqand", "Buxoro", "Xorazm",
    "Andijon", "Farg‘ona", "Namangan", "Qashqadaryo",
    "Surxondaryo", "Jizzax", "Sirdaryo", "Navoiy",
    "Qoraqalpog‘iston"
]

# API uchun to‘g‘ri inglizcha nomlar
CITY_MAP = {
    "Toshkent": "Tashkent",
    "Samarqand": "Samarkand",
    "Buxoro": "Bukhara",
    "Xorazm": "Urgench",
    "Andijon": "Andijan",
    "Farg‘ona": "Fergana",
    "Namangan": "Namangan",
    "Qashqadaryo": "Qarshi",
    "Surxondaryo": "Termez",
    "Jizzax": "Jizzakh",
    "Sirdaryo": "Gulistan",
    "Navoiy": "Navoi",
    "Qoraqalpog‘iston": "Nukus"
}

# Tarjima lug‘ati
DESCRIPTION_TRANSLATE = {
    "clear sky": "Ochiq osmon",
    "few clouds": "Biroz bulutli",
    "scattered clouds": "Tarqoq bulutli",
    "broken clouds": "Qalin bulutli",
    "overcast clouds": "Qop-qora bulutli",
    "shower rain": "Jala",
    "rain": "Yomg‘ir",
    "light rain": "Yengil yomg‘ir",
    "moderate rain": "O‘rtacha yomg‘ir",
    "thunderstorm": "Momaqaldiroq",
    "snow": "Qor",
    "mist": "Tuman",
    "haze": "Tutun",
    "fog": "Qalin tuman"
}

def get_weather_emoji(temp, desc):
    desc = desc.lower()
    if "rain" in desc or "yomg" in desc:
        return "🌧"
    elif "cloud" in desc or "bulut" in desc:
        return "☁️"
    elif "snow" in desc or "qor" in desc:
        return "❄️"
    elif "storm" in desc or "chaqmoq" in desc:
        return "⛈"
    elif temp >= 30:
        return "🔥"
    elif temp >= 20:
        return "☀️"
    elif temp >= 10:
        return "🌤"
    else:
        return "🥶"

BRAND = "\n\n🌐 WeatherBot by Ilyosbek"

def translate_description(desc_en):
    return DESCRIPTION_TRANSLATE.get(desc_en.lower(), desc_en.capitalize())

# /start komandasi
@dp.message(Command("start"))
async def start(message: types.Message):
    main_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌤 Bugungi kun", callback_data="choose_today")],
            [InlineKeyboardButton(text="📆 5 kunlik prognoz", callback_data="choose_forecast")]
        ]
    )

    loc_btn = KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)
    reply_kb = ReplyKeyboardMarkup(keyboard=[[loc_btn]], resize_keyboard=True)

    await message.answer(
        "👋 Salom! Bu bot orqali 🌤 **ob-havo ma’lumotlarini** olasiz.\n\n"
        "⬇️ Quyidagi menyudan tanlang:",
        reply_markup=main_kb
    )
    await message.answer("📍 Lokatsiya yuborsangiz → ob-havo avtomatik chiqadi:", reply_markup=reply_kb)

# Lokatsiya orqali ob-havo
@dp.message(F.location)
async def get_weather_by_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=en"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        await message.answer("❌ Lokatsiya bo‘yicha ob-havo topilmadi.")
    else:
        city = response['name']
        temp = response['main']['temp']
        desc_en = response['weather'][0]['description']
        desc = translate_description(desc_en)
        emoji = get_weather_emoji(temp, desc_en)

        await message.answer(
            f"📍 Joylashuv bo‘yicha: **{city}**\n"
            f"{emoji} Holati: {desc}\n"
            f"🌡 Harorat: {temp}°C"
            f"{BRAND}"
        )

# Callback tugmalar
@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data

    if data == "choose_today":
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=city, callback_data=f"today_{city}")]
                for city in cities
            ]
        )
        await callback_query.message.answer("🌤 Qaysi viloyat uchun bugungi ob-havo kerak?", reply_markup=kb)

    elif data == "choose_forecast":
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=city, callback_data=f"forecast_{city}")]
                for city in cities
            ]
        )
        await callback_query.message.answer("📆 Qaysi viloyat uchun 5 kunlik prognoz kerak?", reply_markup=kb)

    elif data.startswith("today_"):
        city = data.replace("today_", "")
        api_city = CITY_MAP.get(city, city)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={api_city}&appid={WEATHER_API_KEY}&units=metric&lang=en"
        response = requests.get(url).json()

        if response.get("cod") != 200:
            await callback_query.message.answer("❌ Shahar topilmadi.")
        else:
            temp = response['main']['temp']
            desc_en = response['weather'][0]['description']
            desc = translate_description(desc_en)
            emoji = get_weather_emoji(temp, desc_en)

            await callback_query.message.answer(
                f"🌍 {city}\n"
                f"{emoji} Holati: {desc}\n"
                f"🌡 Harorat: {temp}°C"
                f"{BRAND}"
            )

    elif data.startswith("forecast_"):
        city = data.replace("forecast_", "")
        api_city = CITY_MAP.get(city, city)
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={api_city}&appid={WEATHER_API_KEY}&units=metric&lang=en"
        response = requests.get(url).json()

        if response.get("cod") != "200":
            await callback_query.message.answer("❌ Shahar topilmadi.")
        else:
            forecast_text = f"📆 **{city} – 5 kunlik prognoz:**\n\n"
            forecasts = response['list']

            days = {}
            for f in forecasts:
                date = f['dt_txt'].split(" ")[0]
                time = f['dt_txt'].split(" ")[1]
                if time == "12:00:00" and date not in days:
                    temp = f['main']['temp']
                    desc_en = f['weather'][0]['description']
                    desc = translate_description(desc_en)
                    emoji = get_weather_emoji(temp, desc_en)
                    days[date] = f"📅 {date}\n{emoji} {desc}\n🌡 {temp}°C\n"

            for d in days.values():
                forecast_text += d + "\n"

            forecast_text += BRAND
            await callback_query.message.answer(forecast_text)

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
