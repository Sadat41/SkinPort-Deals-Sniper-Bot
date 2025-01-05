import asyncio
import discord
from discord.ext import commands
from skinport import Client
from skinport.enums import Currency, AppID, Locale
import aiohttp
import time

# Key information
DISCORD_BOT_TOKEN = "Your_Discord_Bot_Token"  # Replace with your bot token
API_URL = "https://api.skinport.com/v1/sales/history"

# Discord ssers to notify
USER_IDS_TO_NOTIFY = [
    "User_ID_1",  # User 1 
    "User_ID_2",  # User 2
    "User_ID_3",  # User 3
]

# Channel ID to notify
CHANNEL_ID_TO_NOTIFY = "Discord_Channel_ID" # trade channel

# Discord bot intents
intents = discord.Intents.default()
intents.messages = True
intents.members = True  # Required to fetch users
bot = commands.Bot(command_prefix="!", intents=intents)

# Rate limit management
rate_limit_counter = 0
rate_limit_start_time = time.time()


# Fetch Historical Data
async def fetch_historical_data(market_hash_name):
    """Fetch historical data for an item from the Skinport API."""
    global rate_limit_counter, rate_limit_start_time

    # Check if 5 minutes have passed to reset the counter
    if time.time() - rate_limit_start_time > 300:  # 5 minutes = 300 seconds
        print("Resetting rate limit counter...")
        rate_limit_counter = 0
        rate_limit_start_time = time.time()

    # Enforce rate limit
    if rate_limit_counter >= 8:
        wait_time = 300 - (time.time() - rate_limit_start_time)
        print(f"Rate limit reached. Waiting for {wait_time:.2f} seconds...")
        await asyncio.sleep(wait_time)
        rate_limit_counter = 0
        rate_limit_start_time = time.time()

    # Proceed with the request
    params = {
        "app_id": 730,
        "currency": "CAD",
        "market_hash_name": market_hash_name,
    }
    headers = {"Accept-Encoding": "br"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, headers=headers) as response:
                if response.status == 200:
                    rate_limit_counter += 1
                    print(f"API request successful. Total requests in window: {rate_limit_counter}")
                    return await response.json()
                elif response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    print(f"Rate limit exceeded (429). Retrying in {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                else:
                    print(f"Failed to fetch historical data: {response.status}")
                    return None
    except Exception as e:
        print(f"Error during API request: {e}")
        return None


# Send Discord Notification
async def send_discord_notification(users, channel_id, item, historical_data):
    """Send a DM to multiple users and post in a channel with historical data."""
    avg_prices = {
        "24h": historical_data["last_24_hours"]["avg"] if historical_data["last_24_hours"] else None,
        "7d": historical_data["last_7_days"]["avg"] if historical_data["last_7_days"] else None,
        "30d": historical_data["last_30_days"]["avg"] if historical_data["last_30_days"] else None,
        "90d": historical_data["last_90_days"]["avg"] if historical_data["last_90_days"] else None,
    }

    # Normalize prices and calculate discount
    sale_price = item["salePrice"] / 100
    suggested_price = item["suggestedPrice"] / 100
    discount = ((suggested_price - sale_price) / suggested_price) * 100
    wear = item.get("wear", "Unknown")
    pattern = item.get("pattern", "Unknown")
    market_hash_name = item["marketHashName"]

    # Skip if sale price is <= 100
    if sale_price <= 100:
        print(f"Sale price for {market_hash_name} is <= 100. Skipping.")
        return

    # Format avg prices, falling back to "N/A" if None
    avg_prices_formatted = {
        key: f"{value:.2f} CAD" if value is not None else "N/A"
        for key, value in avg_prices.items()
    }

    # Create the embed
    embed = discord.Embed(
        title="🔥🚀 New Deal Detected 🔥🚀",
        description=(
            f"**💎 __Skin:__ {market_hash_name}**\n\n"
            f"**👀 Pattern:** {pattern}\n"
            f"**💰 Price:** {sale_price:.2f} CAD\n"
            f"**⚠️ Suggested Price:** {suggested_price:.2f} CAD\n"
            f"**🤑 Discount:** {discount:.2f}%\n"
            f"**☢️ Wear:** {wear if isinstance(wear, str) else f'{wear:.6f}'}"
        ),
        color=0xFF5733,
    )

    # Add fields for links
    embed.add_field(
        name="🔍 Inspect Link",
        value=f"[Inspect in Game]({item.get('link', 'N/A')})",
        inline=True,
    )

    # Add historical average prices
    embed.add_field(
        name="📊 Avg Prices",
        value=(
            f"**24h:** {avg_prices_formatted['24h']}\n"
            f"**7d:** {avg_prices_formatted['7d']}\n"
            f"**30d:** {avg_prices_formatted['30d']}\n"
            f"**90d:** {avg_prices_formatted['90d']}\n"
        ),
        inline=False,
    )

    # Add footer with branding
    embed.set_footer(
        text="🚨 Powered by SkinPort Sniper",
        icon_url="https://skinport.com/favicon.ico",
    )

    # Send to users
    for user_id in users:
        try:
            user = await bot.fetch_user(user_id)
            print(f"Attempting to send DM to {user.name} (ID: {user_id})...")
            await user.send(embed=embed)
            print(f"Notification sent to {user.name}")
        except Exception as e:
            print(f"Failed to send DM to user ID {user_id}: {e}")

    # Send to channel
    try:
        channel = bot.get_channel(channel_id)
        if channel:
            # Send the embed
            await channel.send(embed=embed)
            # Send the raw SkinPort link for preview
            await channel.send(f"https://skinport.com/item/{item['url']}")
            print(f"Notification sent to channel {channel.name}")
        else:
            print(f"Channel with ID {channel_id} not found.")
    except Exception as e:
        print(f"Failed to send message to channel ID {channel_id}: {e}")


# Sale Feed Listener
async def on_sale_feed(data):
    """Process sale feed data."""
    print("Full data received from SkinPort:", data)

    for sale in data.get("sales", []):
        market_hash_name = sale.get("marketHashName")
        raw_sale_price = sale.get("salePrice", 0)
        sale_price = raw_sale_price / 100

        print(f"Checking sale: {market_hash_name}, Sale Price: {sale_price:.2f} CAD")

        # Skip if sale price is <= 100
        if sale_price <= 100:
            print(f"Sale price for {market_hash_name} is <= 100. Skipping.")
            continue

        # Fetch historical data
        historical_data = await fetch_historical_data(market_hash_name)

        if historical_data:
            avg_7d = historical_data[0].get("last_7_days", {}).get("avg", None)
            if avg_7d:
                print(f"7-day average price for {market_hash_name} is {avg_7d:.2f} CAD")

                # Calculate discount
                suggested_price = sale.get("suggestedPrice", 0) / 100
                discount = ((suggested_price - sale_price) / suggested_price) * 100

                print(f"Discount for {market_hash_name}: {discount:.2f}%")

                # Add minimum discount condition (20%)
                if discount < 20:
                    print(f"Discount {discount:.2f}% for {market_hash_name} is less than 20%. Skipping.")
                    continue

                if sale_price < avg_7d:
                    print(f"Sale price {sale_price:.2f} is less than the 7-day average {avg_7d:.2f}. Notification condition met.")
                    await send_discord_notification(USER_IDS_TO_NOTIFY, CHANNEL_ID_TO_NOTIFY, sale, historical_data[0])
                else:
                    print(f"Sale price {sale_price:.2f} is NOT less than the 7-day average {avg_7d:.2f}. Skipping notification.")
            else:
                print(f"No 7-day average price available for {market_hash_name}. Skipping notification.")
        else:
            print(f"Failed to fetch historical data for {market_hash_name}. Skipping notification.")



# Discord Bot Parameters
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    client = Client()

    @client.listen("saleFeed")
    async def sale_feed_listener(data):
        await on_sale_feed(data)

    try:
        print("Connecting to SkinPort...")
        await client.connect(app_id=AppID.csgo, currency=Currency.cad, locale=Locale.en)
        print("Connected to SkinPort successfully.")
    except Exception as e:
        print(f"Error while connecting to SkinPort: {e}")
    finally:
        if client.ws:
            await client.disconnect()


# Launch the bot
if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
