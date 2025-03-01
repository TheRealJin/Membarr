@commands.Cog.listener()
async def on_member_update(self, before, after):
    if plex_roles is None and emby_roles is None:
        return

    roles_in_guild = after.guild.roles
    role = None

    plex_processed = False
    emby_processed = False

    # Check Plex roles (if enabled)
    if plex_configured and USE_PLEX:
        for role_for_app in plex_roles:
            for role_in_guild in roles_in_guild:
                if role_in_guild.name == role_for_app:
                    role = role_in_guild

                # Plex role was added
                if role is not None and (role in after.roles and role not in before.roles):
                    email = await self.getemail(after)
                    if email is not None:
                        await embedinfo(after, "Got it! We will be adding your email to Plex shortly!")
                        if plexhelper.plexadd(plex, email, Plex_LIBS):
                            db.save_user_email(str(after.id), email)
                            await asyncio.sleep(5)
                            await embedinfo(after, 'You have been added to Plex! Log in to Plex and accept the invite!')
                        else:
                            await embedinfo(after, 'There was an error adding this email address. Message the server admin.')
                    plex_processed = True
                    break

                # Plex role was removed
                elif role is not None and (role not in after.roles and role in before.roles):
                    try:
                        user_id = after.id
                        email = db.get_useremail(user_id)
                        plexhelper.plexremove(plex, email)
                        deleted = db.remove_email(user_id)
                        if deleted:
                            print(f"Removed Plex email {after.name} from db")
                        else:
                            print("Cannot remove Plex from this user.")
                        await embedinfo(after, "You have been removed from Plex")
                    except Exception as e:
                        print(e)
                        print(f"{email} Cannot remove this user from Plex.")
                    plex_processed = True
                    break
            if plex_processed:
                break

    role = None
    # Check Emby roles (if enabled)
    if emby_configured and USE_EMBY:
        for role_for_app in emby_roles:
            for role_in_guild in roles_in_guild:
                if role_in_guild.name == role_for_app:
                    role = role_in_guild

                # Emby role was added
                if role is not None and (role in after.roles and role not in before.roles):
                    print("Emby role added")
                    try:
                        # Send a DM to the user asking for their Emby username
                        await embedinfo(after, "Welcome to the server! Please reply with your Emby username to be added to the Emby server.")
                        await embedinfo(after, "If you do not respond within 24 hours, the request will be cancelled, and the server admin will need to add you manually.")

                        # Wait for the user's response
                        username = await self.getusername(after)
                        if username is not None:
                            await embedinfo(after, "Got it! We will be creating your Emby account shortly!")
                            password = emby.generate_password(16)  # Generate a random password
                            if emby.add_user(EMBY_SERVER_URL, EMBY_API_KEY, username, password, emby_libs):
                                db.save_user_emby(str(after.id), username)
                                await asyncio.sleep(5)
                                await embedcustom(after, "You have been added to Emby!", {'Username': username, 'Password': f"||{password}||"})
                                await embedinfo(after, f"Go to {EMBY_EXTERNAL_URL} to log in!")
                            else:
                                await embedinfo(after, 'There was an error adding this user to Emby. Message the server admin.')
                    except Exception as e:
                        print(f"Error sending DM or handling response: {e}")
                    emby_processed = True
                    break

                # Emby role was removed
                elif role is not None and (role not in after.roles and role in before.roles):
                    print("Emby role removed")
                    try:
                        user_id = after.id
                        username = db.get_emby_username(user_id)
                        emby.remove_user(EMBY_SERVER_URL, EMBY_API_KEY, username)
                        deleted = db.remove_emby(user_id)
                        if deleted:
                            print(f"Removed Emby from {after.name}")
                        else:
                            print("Cannot remove Emby from this user")
                        await embedinfo(after, "You have been removed from Emby")
                    except Exception as e:
                        print(e)
                        print(f"{username} Cannot remove this user from Emby.")
                    emby_processed = True
                    break
            if emby_processed:
                break
