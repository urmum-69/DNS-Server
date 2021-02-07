str2hax DNS Server [![Actions Status](https://github.com/urmum-69/strhax-DNS-Server/workflows/Build/badge.svg)](https://github.com/urmum-69/str2hax-DNS-Server/actions)
===

This DNS Server will run locally on your computer and allow you to use str2hax even if your ISP blocks connections to custom DNS Servers.

## Setup

Setup process is the same as shown on our guide
https://wii.guide/str2hax

You will only need to enter different values for the custom DNS Settings in your Wii.

After running the script, enter the value it outputs for the primary DNS, instead of 97.74.103.14


# Running on Windows:

Run the .exe provided [on the releases page](https://github.com/urmum-69/str2hax-DNS-Server/releases). If your antivirus notifies you about the .exe file, allow it and run it. If it doesn't work, you should also allow communication for this this .exe in your firewall settings.

# Running on Linux/macOS:

You will need to install Python 3 and run these commands in the Terminal.

> pip install dnslib requests

To run it, simply type in:

> sudo python3 RiiConnect24-DNS-Server.py

Replace `python3` with the name/path to your Python binary if necessary

# How to use it?

On screen, you will see the IP Address assigned to your computer by the DHCP Server on your NAT (router).

If your Wii is connected to the same network as your PC, it will be able to connect to the server on your PC.

<p align="center">
  <img src="https://i.imgur.com/oageZQ3.jpg">
<i>My local IP Address, yours will be different.</i>
</p>


# Compiling on Windows

To compile this app on Windows, you will need to run these two commands (Important: Pyinstaller currently fails to build with Python 3.8, use Python 3.7.5):
>pip install dnslib requests pyinstaller

Once it's done installing, run:
>pyinstaller RiiConnect24-DNS-Server.spec

| Tip: You may need to edit str2hax-DNS-Server.spec so the compiling process works on your computer.

# Need more help?
You can talk to us over on the [RiiConnect24 Discord server](https://discord.gg/b4Y7jfD), where people can try and help you out!
