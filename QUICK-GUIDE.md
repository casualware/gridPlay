# gridPlay Visual Quick Guide

For firmware **0.9.4-preview**. These screen illustrations follow the current layout; they are not photographs or device screenshots. Mint outlines highlight controls. Battery values and inst names are examples, and the QR and access code are placeholders.

![Six illustrated screens with the main gridPlay controls](images/quick-guide.png)

[Open full-size image](images/quick-guide.png) · [Complete user manual](USER-MANUAL.md) · [Install on a new tile](https://casualware.github.io/gridPlay/)

1. **Start:** From Home, choose **GPT Live** for standalone Wi-Fi use. Join and Create belong to the older USB companion workflow.
2. **Connect:** Open **Settings → Wi-Fi setup**, join the tile’s temporary Wi-Fi, and open **http://192.168.4.1** to select your home network.
3. **Set the key:** While on home Wi-Fi, open **Settings → API key**. On a phone on the same network, scan the setup QR, then enter the temporary code shown on your tile. You can also set the key during hotspot setup.
4. **Talk:** Choose **New inst** or **Reconnect**. Wait for **Listening**, then speak. Green means listening, pink means speaking, and purple means working. **Mute** toggles the microphone; **Stop** ends the conversation.
5. **See the scene:** Tap **Inst**, scan the actual QR on your tile, and keep the paired browser open. Tap **Back to GPT Live** to continue talking. The name under the orb identifies your inst.
6. **Update:** Stop GPT Live, connect reliable power, and open **Settings → Device details → Updates → Check again**. Tap **Install update** when a version is offered, and keep power connected through restart.

**Battery:** The status bar shows a percentage and charging indicator. Amber means 20% or less; red means 10% or less when not charging. Battery status requires 0.9.3-preview or later.

**Remember:** A temporary API key is cleared on restart. Remembered keys survive restart but are stored without flash encryption. Insts in this preview are public. First-time browser installation erases the tile; ordinary Wi-Fi updates retain saved settings.

## Individual screen images

[Home](images/home.png) · [Settings](images/settings.png) · [API key](images/api-key.png) · [GPT Live](images/gpt-live.png) · [Inst QR](images/inst.png) · [Updates](images/updates.png)
