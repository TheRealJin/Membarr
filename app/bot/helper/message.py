import discord

# Helper functions for sending messages and embeds
async def embederror(recipient, message, ephemeral=True):
    """
    Sends an error message as an embed.
    """
    embed = discord.Embed(title="ERROR", description=message, color=0xf50000)
    await send_embed(recipient, embed, ephemeral)

async def embedinfo(recipient, message, ephemeral=True):
    """
    Sends an informational message as an embed.
    """
    embed = discord.Embed(title=message, color=0x00F500)
    await send_embed(recipient, embed, ephemeral)

async def embedcustom(recipient, title, fields, ephemeral=True):
    """
    Sends a custom embed with fields.
    """
    embed = discord.Embed(title=title)
    for k in fields:
        embed.add_field(name=str(k), value=str(fields[k]), inline=True)
    await send_embed(recipient, embed, ephemeral)

async def send_info(recipient, message, ephemeral=True):
    """
    Sends a plain text message.
    """
    if isinstance(recipient, discord.InteractionResponse):
        await recipient.send_message(message, ephemeral=ephemeral)
    elif isinstance(recipient, discord.User) or isinstance(recipient, discord.member.Member) or isinstance(recipient, discord.Webhook):
        await recipient.send(message)

async def send_embed(recipient, embed, ephemeral=True):
    """
    Sends an embed message.
    """
    if isinstance(recipient, discord.User) or isinstance(recipient, discord.member.Member) or isinstance(recipient, discord.Webhook):
        await recipient.send(embed=embed)
    elif isinstance(recipient, discord.InteractionResponse):
        await recipient.send_message(embed=embed, ephemeral=ephemeral)

# Emby-specific messaging functions
async def embed_emby_info(recipient, username, password, ephemeral=True):
    """
    Sends an embed with Emby account details.
    """
    fields = {
        "Username": username,
        "Password": f"||{password}||"  # Password is masked
    }
    await embedcustom(recipient, "Emby Account Created", fields, ephemeral)

async def embed_emby_removed(recipient, username, ephemeral=True):
    """
    Sends an embed confirming Emby account removal.
    """
    await embedinfo(recipient, f"Emby user '{username}' has been removed.", ephemeral)

# Plex-specific messaging functions
async def embed_plex_info(recipient, email, ephemeral=True):
    """
    Sends an embed with Plex account details.
    """
    await embedinfo(recipient, f"Plex invite sent to {email}.", ephemeral)

async def embed_plex_removed(recipient, email, ephemeral=True):
    """
    Sends an embed confirming Plex account removal.
    """
    await embedinfo(recipient, f"Plex user '{email}' has been removed.", ephemeral)

# Jellyfin-specific messaging functions
async def embed_jellyfin_info(recipient, username, password, ephemeral=True):
    """
    Sends an embed with Jellyfin account details.
    """
    fields = {
        "Username": username,
        "Password": f"||{password}||"  # Password is masked
    }
    await embedcustom(recipient, "Jellyfin Account Created", fields, ephemeral)

async def embed_jellyfin_removed(recipient, username, ephemeral=True):
    """
    Sends an embed confirming Jellyfin account removal.
    """
    await embedinfo(recipient, f"Jellyfin user '{username}' has been removed.", ephemeral)
