import os
import requests
import time
import concurrent.futures

# Telegram bot details
TELEGRAM_BOT_TOKEN = "7859722593:AAGJrtKuWjWOaXMP94b7QmKFAD52GkhAo7k"
TELEGRAM_CHAT_ID = '1916073059'

def send_telegram_message(message):
    """Send a message to the Telegram bot asynchronously."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(requests.post, url, json=payload, timeout=10)

# Function to fetch Bybit candle data
def fetch_bybit_data(symbol, interval, limit=100):
    """Fetch the last 100 candles for a given symbol and timeframe."""
    url = "https://api.bybit.com/v5/market/kline"
    params = {"category": "linear", "symbol": symbol, "interval": interval, "limit": limit}
    
    for attempt in range(2):  # Reduced retries for speed
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("retCode") == 0:
                return data["result"]["list"]
        except requests.exceptions.RequestException:
            time.sleep(1)
    return None

# Function to check 3-candle setup
def check_3_candle_setup(symbol, timeframe, candles):
    """Checks for the 3-candle pattern in the given candles."""
    if not candles or len(candles) < 4:
        return

    for i in range(min(20, len(candles) - 3)):  # Stop early if not enough candles
        c1, c2, c3, c4 = candles[i + 3], candles[i + 2], candles[i + 1], candles[i]
        open1, high1, low1, close1, vol1 = map(float, c1[1:6])
        open2, high2, low2, close2, vol2 = map(float, c2[1:6])
        open3, high3, low3, close3, vol3 = map(float, c3[1:6])
        open4, high4, low4, close4, vol4 = map(float, c4[1:6])

        # Calculate rejection candle properties
        rej_body1 = abs(close1 - open1)
        upper_wick1, lower_wick1 = high1 - max(close1, open1), min(close1, open1) - low1
        bullish_rejection1 = upper_wick1 > 2 * lower_wick1 and upper_wick1 > rej_body1
        bearish_rejection1 = lower_wick1 > 2 * upper_wick1 and lower_wick1 > rej_body1

        # Expansion conditions
        expansion2 = abs(close2 - open2) >= 4 * rej_body1
        expansion4 = abs(close4 - open4) >= 4 * rej_body1

        # Calculate rejection for candle 3
        rej_body3 = abs(close3 - open3)
        upper_wick3, lower_wick3 = high3 - max(close3, open3), min(close3, open3) - low3
        bullish_rejection3 = upper_wick3 > 2 * lower_wick3 and upper_wick3 > rej_body3
        bearish_rejection3 = lower_wick3 > 2 * upper_wick3 and lower_wick3 > rej_body3

        # Final conditions for bullish and bearish expansion
        bullish_signal = (
            expansion2 and expansion4 and
            (close2 > open2) and (close4 > open4) and
            (close2 > high1) and (vol1 < vol2 < vol3 < vol4) and
            bearish_rejection1 and bullish_rejection3 and
            (close4 > high3) and (low2 > low1)
        )

        bearish_signal = (
            expansion2 and expansion4 and
            (close2 < open2) and (close4 < open4) and
            (close2 < low1) and (vol1 < vol2 < vol3 < vol4) and
            bullish_rejection1 and bearish_rejection3 and
            (close4 < low3) and (high1 > high2)
        )

        if bullish_signal or bearish_signal:
            signal_type = "BUY" if bullish_signal else "SELL"
            message = (f"{symbol} ({timeframe}): {signal_type} at index {i}\n"
                       f"High: {high3:.2f}, Low: {low3:.2f}\nVolume1: {vol1:.2f}")
            print(message)
            send_telegram_message(message)

# Function to process a single symbol for a given timeframe
def process_symbol(symbol, timeframe, interval):
    candles = fetch_bybit_data(symbol, interval)
    if candles:
        check_3_candle_setup(symbol, timeframe, candles)

# Timeframes mapping
timeframes = {
    "1h": "60", "2h": "120", "4h": "240",
    "6h": "360", "12h": "720", "1D": "1440",
}



# List of USDT pairs (example list; update as needed)
usdt_pairs = [
    "10000000AIDOGEUSDT",
    "1000000BABYDOGEUSDT",
    "1000000CHEEMSUSDT",
    "1000000MOGUSDT",
    "1000000PEIPEIUSDT",
    "10000COQUSDT",
    "10000ELONUSDT",
    "10000LADYSUSDT",
    "10000QUBICUSDT",
    "10000SATSUSDT",
    "10000WENUSDT",
    "10000WHYUSDT",
    "1000APUUSDT",
    "1000BONKUSDT",
    "1000BTTUSDT",
    "1000CATSUSDT",
    "1000CATUSDT",
    "1000FLOKIUSDT",
    "1000LUNCUSDT",
    "1000MUMUUSDT",
    "1000NEIROCTOUSDT",
    "1000PEPEUSDT",
    "1000RATSUSDT",
    "1000TOSHIUSDT",
    "1000TURBOUSDT",
    "1000XECUSDT",
    "1000XUSDT",
    "1INCHUSDT",
    "A8USDT",
    "AAVEUSDT",
    "ACEUSDT",
    "ACHUSDT",
    "ACTUSDT",
    "ACXUSDT",
    "ADAUSDT",
    "AERGOUSDT",
    "AEROUSDT",
    "AEVOUSDT",
    "AGIUSDT",
    "AGLDUSDT",
    "AI16ZUSDT",
    "AIOZUSDT",
    "AIUSDT",
    "AIXBTUSDT",
    "AKTUSDT",
    "ALCHUSDT",
    "ALEOUSDT",
    "ALGOUSDT",
    "ALICEUSDT",
    "ALPACAUSDT",
    "ALPHAUSDT",
    "ALTUSDT",
    "ALUUSDT",
    "AMBUSDT",
    "ANIMEUSDT",
    "ANKRUSDT",
    "APEUSDT",
    "API3USDT",
    "APTUSDT",
    "ARBUSDT",
    "ARCUSDT",
    "ARKMUSDT",
    "ARKUSDT",
    "ARPAUSDT",
    "ARUSDT",
    "ASTRUSDT",
    "ATAUSDT",
    "ATHUSDT",
    "ATOMUSDT",
    "AUCTIONUSDT",
    "AUDIOUSDT",
    "AVAAIUSDT",
    "AVAILUSDT",
    "AVAUSDT",
    "AVAXUSDT",
    "AVLUSDT",
    "AXLUSDT",
    "AXSUSDT",
    "B3USDT",
    "BADGERUSDT",
    "BAKEUSDT",
    "BALUSDT",
    "BANANAUSDT",
    "BANDUSDT",
    "BANUSDT",
    "BATUSDT",
    "BBUSDT",
    "BCHUSDT",
    "BEAMUSDT",
    "BELUSDT",
    "BERAUSDT",
    "BICOUSDT",
    "BIGTIMEUSDT",
    "BIOUSDT",
    "BLASTUSDT",
    "BLUEUSDT",
    "BLURUSDT",
    "BNBUSDT",
    "BNTUSDT",
    "BNXUSDT",
    "BOBAUSDT",
    "BOMEUSDT",
    "BRETTUSDT",
    "BROCCOLIUSDT",
    "BSVUSDT",
    "BSWUSDT",
    "BTCUSDT",
    "BTCUSDT-04APR25",
    "BTCUSDT-11APR25",
    "BUZZUSDT",
    "C98USDT",
    "CAKEUSDT",
    "CARVUSDT",
    "CATIUSDT",
    "CELOUSDT",
    "CELRUSDT",
    "CETUSUSDT",
    "CFXUSDT",
    "CGPTUSDT",
    "CHESSUSDT",
    "CHILLGUYUSDT",
    "CHRUSDT",
    "CHZUSDT",
    "CKBUSDT",
    "CLOUDUSDT",
    "COMBOUSDT",
    "COMPUSDT",
    "COOKIEUSDT",
    "COOKUSDT",
    "COREUSDT",
    "COSUSDT",
    "COTIUSDT",
    "COWUSDT",
    "CROUSDT",
    "CRVUSDT",
    "CTCUSDT",
    "CTKUSDT",
    "CTSIUSDT",
    "CVCUSDT",
    "CVXUSDT",
    "CYBERUSDT",
    "DASHUSDT",
    "DATAUSDT",
    "DBRUSDT",
    "DEEPUSDT",
    "DEGENUSDT",
    "DENTUSDT",
    "DEXEUSDT",
    "DGBUSDT",
    "DODOUSDT",
    "DOGEUSDT",
    "DOGSUSDT",
    "DOGUSDT",
    "DOTUSDT",
    "DRIFTUSDT",
    "DUCKUSDT",
    "DUSKUSDT",
    "DYDXUSDT",
    "DYMUSDT",
    "EDUUSDT",
    "EGLDUSDT",
    "EIGENUSDT",
    "ENAUSDT",
    "ENJUSDT",
    "ENSUSDT",
    "EOSUSDT",
    "ETCUSDT",
    "ETHBTCUSDT",
    "ETHFIUSDT",
    "ETHUSDT",
    "ETHUSDT-04APR25",
    "ETHUSDT-11APR25",
    "ETHWUSDT",
    "FARTCOINUSDT",
    "FBUSDT",
    "FIDAUSDT",
    "FILUSDT",
    "FIOUSDT",
    "FIREUSDT",
    "FLMUSDT",
    "FLOCKUSDT",
    "FLOWUSDT",
    "FLRUSDT",
    "FLUXUSDT",
    "FORTHUSDT",
    "FOXYUSDT",
    "FTNUSDT",
    "FUELUSDT",
    "FUSDT",
    "FWOGUSDT",
    "FXSUSDT",
    "GALAUSDT",
    "GASUSDT",
    "GEMSUSDT",
    "GIGAUSDT",
    "GLMRUSDT",
    "GLMUSDT",
    "GMEUSDT",
    "GMTUSDT",
    "GMXUSDT",
    "GNOUSDT",
    "GOATUSDT",
    "GODSUSDT",
    "GOMININGUSDT",
    "GPSUSDT",
    "GRASSUSDT",
    "GRIFFAINUSDT",
    "GRTUSDT",
    "GTCUSDT",
    "GUSDT",
    "HBARUSDT",
    "HEIUSDT",
    "HFTUSDT",
    "HIFIUSDT",
    "HIGHUSDT",
    "HIPPOUSDT",
    "HIVEUSDT",
    "HMSTRUSDT",
    "HNTUSDT",
    "HOOKUSDT",
    "HOTUSDT",
    "HPOS10IUSDT",
    "HYPEUSDT",
    "ICPUSDT",
    "ICXUSDT",
    "IDEXUSDT",
    "IDUSDT",
    "ILVUSDT",
    "IMXUSDT",
    "INJUSDT",
    "IOSTUSDT",
    "IOTAUSDT",
    "IOTXUSDT",
    "IOUSDT",
    "IPUSDT",
    "JAILSTOOLUSDT",
    "JASMYUSDT",
    "JELLYJELLYUSDT",
    "JOEUSDT",
    "JSTUSDT",
    "JTOUSDT",
    "JUPUSDT",
    "JUSDT",
    "KAIAUSDT",
    "KAITOUSDT",
    "KASUSDT",
    "KAVAUSDT",
    "KDAUSDT",
    "KMNOUSDT",
    "KNCUSDT",
    "KOMAUSDT",
    "KSMUSDT",
    "L3USDT",
    "LAIUSDT",
    "LDOUSDT",
    "LEVERUSDT",
    "LINAUSDT",
    "LINKUSDT",
    "LISTAUSDT",
    "LOOKSUSDT",
    "LPTUSDT",
    "LQTYUSDT",
    "LRCUSDT",
    "LSKUSDT",
    "LTCUSDT",
    "LUCEUSDT",
    "LUMIAUSDT",
    "LUNA2USDT",
    "MAGICUSDT",
    "MAJORUSDT",
    "MANAUSDT",
    "MANEKIUSDT",
    "MANTAUSDT",
    "MASAUSDT",
    "MASKUSDT",
    "MAVIAUSDT",
    "MAVUSDT",
    "MAXUSDT",
    "MBLUSDT",
    "MBOXUSDT",
    "MDTUSDT",
    "MELANIAUSDT",
    "MEMEFIUSDT",
    "MEMEUSDT",
    "MERLUSDT",
    "METISUSDT",
    "MEUSDT",
    "MEWUSDT",
    "MICHIUSDT",
    "MINAUSDT",
    "MKRUSDT",
    "MNTUSDT",
    "MOBILEUSDT",
    "MOCAUSDT",
    "MONUSDT",
    "MOODENGUSDT",
    "MORPHOUSDT",
    "MOTHERUSDT",
    "MOVEUSDT",
    "MOVRUSDT",
    "MTLUSDT",
    "MVLUSDT",
    "MYRIAUSDT",
    "MYROUSDT",
    "NCUSDT",
    "NEARUSDT",
    "NEIROETHUSDT",
    "NEOUSDT",
    "NFPUSDT",
    "NKNUSDT",
    "NMRUSDT",
    "NOTUSDT",
    "NSUSDT",
    "NTRNUSDT",
    "NULSUSDT",
    "OGNUSDT",
    "OGUSDT",
    "OLUSDT",
    "OMGUSDT",
    "OMNIUSDT",
    "OMUSDT",
    "ONDOUSDT",
    "ONEUSDT",
    "ONGUSDT",
    "ONTUSDT",
    "OPUSDT",
    "ORBSUSDT",
    "ORCAUSDT",
    "ORDERUSDT",
    "ORDIUSDT",
    "OSMOUSDT",
    "OXTUSDT",
    "PAXGUSDT",
    "PEAQUSDT",
    "PENDLEUSDT",
    "PENGUUSDT",
    "PEOPLEUSDT",
    "PERPUSDT",
    "PHAUSDT",
    "PHBUSDT",
    "PIPPINUSDT",
    "PIRATEUSDT",
    "PIXELUSDT",
    "PLUMEUSDT",
    "PNUTUSDT",
    "POLUSDT",
    "POLYXUSDT",
    "PONKEUSDT",
    "POPCATUSDT",
    "PORTALUSDT",
    "POWRUSDT",
    "PRCLUSDT",
    "PRIMEUSDT",
    "PROMUSDT",
    "PROSUSDT",
    "PUFFERUSDT",
    "PYRUSDT",
    "PYTHUSDT",
    "QIUSDT",
    "QNTUSDT",
    "QTUMUSDT",
    "QUICKUSDT",
    "RADUSDT",
    "RAREUSDT",
    "RAYDIUMUSDT",
    "RDNTUSDT",
    "RENDERUSDT",
    "RENUSDT",
    "REQUSDT",
    "REXUSDT",
    "REZUSDT",
    "RIFSOLUSDT",
    "RIFUSDT",
    "RLCUSDT",
    "RONINUSDT",
    "ROSEUSDT",
    "RPLUSDT",
    "RSRUSDT",
    "RSS3USDT",
    "RUNEUSDT",
    "RVNUSDT",
    "SAFEUSDT",
    "SAGAUSDT",
    "SANDUSDT",
    "SCAUSDT",
    "SCRTUSDT",
    "SCRUSDT",
    "SCUSDT",
    "SDUSDT",
    "SEIUSDT",
    "SENDUSDT",
    "SFPUSDT",
    "SHELLUSDT",
    "SHIB1000USDT",
    "SKLUSDT",
    "SLERFUSDT",
    "SLFUSDT",
    "SLPUSDT",
    "SNTUSDT",
    "SNXUSDT",
    "SOLAYERUSDT",
    "SOLOUSDT",
    "SOLUSDT",
    "SOLUSDT-04APR25",
    "SOLUSDT-11APR25",
    "SOLVUSDT",
    "SONICUSDT",
    "SPECUSDT",
    "SPELLUSDT",
    "SPXUSDT",
    "SSVUSDT",
    "STEEMUSDT",
    "STGUSDT",
    "STMXUSDT",
    "STORJUSDT",
    "STPTUSDT",
    "STRKUSDT",
    "STXUSDT",
    "SUIUSDT",
    "SUNDOGUSDT",
    "SUNUSDT",
    "SUPERUSDT",
    "SUSDT",
    "SUSHIUSDT",
    "SWARMSUSDT",
    "SWEATUSDT",
    "SWELLUSDT",
    "SXPUSDT",
    "SYNUSDT",
    "SYSUSDT",
    "TAIKOUSDT",
    "TAIUSDT",
    "TAOUSDT",
    "THETAUSDT",
    "THEUSDT",
    "TIAUSDT",
    "TLMUSDT",
    "TNSRUSDT",
    "TOKENUSDT",
    "TONUSDT",
    "TRBUSDT",
    "TROYUSDT",
    "TRUMPUSDT",
    "TRUUSDT",
    "TRXUSDT",
    "TSTBSCUSDT",
    "TUSDT",
    "TWTUSDT",
    "UMAUSDT",
    "UNIUSDT",
    "UROUSDT",
    "USDCUSDT",
    "USDEUSDT",
    "USTCUSDT"
]


start_time = time.time()
print("\nStarting signal analysis...\n")

# Determine maximum workers using os.cpu_count()
cpu_cores = min(10, os.cpu_count() or 4)

with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_cores) as executor:
    futures = []
    for tf_name, interval in timeframes.items():
        print(f"\nProcessing timeframe: {tf_name} ({interval} min)")
        for symbol in usdt_pairs:
            futures.append(executor.submit(process_symbol, symbol, tf_name, interval))

    for future in concurrent.futures.as_completed(futures):
        future.result()  # Ensure all tasks complete

print(f"\nProcessing complete. Time taken: {time.time() - start_time:.2f} seconds")