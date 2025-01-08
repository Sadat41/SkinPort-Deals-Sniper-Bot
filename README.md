# SkinPort Deal Notifier Bot

A **Python** script that leverages the **SkinPort API** and **Discord Bot API** to monitor **SkinPort’s live Sale Feed** for deals on CS2 items. The bot evaluates deals dynamically based on a configurable **discount percentage** and historical price data, then sends detailed notifications to Discord users and channels.

---

## 📚 Overview

This bot utilizes the **SkinPort API wrapper** to connect to the **Sale Feed (Live)** via WebSocket and the `/v1/sales/history` endpoint to fetch historical price data for specific in-game items sold on SkinPort. The bot dynamically evaluates deals based on a specified discount percentage and notifies users when the criteria are met.

### Key Features
- **Real-Time Monitoring**: Continuously monitors SkinPort’s live Sale Feed for new deals.
- **Dynamic Discount Evaluation**: Allows configuration of the minimum discount percentage to trigger notifications.
- **Historical Price Analysis**: Fetches aggregated price data for the past 24 hours, 7 days, 30 days, and 90 days.
- **Discord Notifications**: Sends detailed notifications to Discord users and server channels, including:
  - Sale price, suggested price, and discount percentage.
  - Historical price data.
  - Link to the item page and additional details.

---

## 🚀 Installation

### Prerequisites
- Python 3.13+
- A Discord bot token ([create one here](https://discordpy.readthedocs.io/en/stable/discord.html)).
- Access to the SkinPort API ([documentation](https://docs.skinport.com/)).
- Skinport API Wraper ([Github Repo Link](https://github.com/PaxxPatriot/skinport.py)).
  
### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/SkinPort-Deal-Notifier-Bot.git
cd SkinPort-Deal-Notifier-Bot
```
### Step 2: Install Dependencies
#### Run the following command to install the required libraries:
```bash
pip install discord.py aiohttp skinport
```
### Step 3: Configure the Script
#### Open the script file and replace:
* 'DISCORD_BOT_TOKEN' with your Discord bot token.
* Add your desired 'USER_IDS_TO_NOTIFY' and 'CHANNEL_ID_TO_NOTIFY'.

### Step 4: Run the Script
```bash
python script.py
```

---
## 📋 Example Notification
![SkinPort Bot Example](https://raw.githubusercontent.com/Sadat41/SkinPort-Discord-Notification-Bot/refs/heads/main/image.png)
---
## ⚙️ Configuration
### Discount Condition
#### The bot dynamically evaluates deals based on a configurable discount percentage. You can modify the condition in the script to match your preferences:
```python
# Example: Minimum discount to notify
if discount < 20:
    print(f"Discount {discount:.2f}% is less than the minimum threshold. Skipping.")
    continue
```
---
## 🤝 Contributions
Contributions are welcome! To contribute:
1. Fork this repository.
2. Create a feature branch:
```bash
git checkout -b feature-name
```
3. Push your changes and open a pull request.


