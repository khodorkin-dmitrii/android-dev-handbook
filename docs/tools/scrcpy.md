# scrcpy: Android Screen Mirroring

## Practical guide

### What it is and when to use it

`scrcpy` is a free, open-source tool that mirrors an Android screen on a computer and lets you control it with a mouse and keyboard over USB or TCP/IP. It works on Windows, macOS, and Linux without root or manually installing an app on the phone.

Use it to check UI on a physical device, give demonstrations, record bug reproduction steps, or operate a phone from your computer. This guide focuses on USB and Windows.

### Install on Windows

Run in PowerShell or CMD:

```powershell
winget install --exact Genymobile.scrcpy
```

WinGet installs ADB and the required dependencies alongside scrcpy. Open a new terminal after installation and check:

```powershell
scrcpy --version
```

Alternatively, download the Windows ZIP for your architecture from the official [GitHub Releases](https://github.com/Genymobile/scrcpy/releases), extract it, and open a terminal in the extracted directory. In PowerShell, replace `scrcpy` with `.\scrcpy.exe` in the commands below if it is not in `PATH`. For the bundled ADB, use `.\adb.exe` if needed.

For other platforms, follow the official [macOS](https://github.com/Genymobile/scrcpy/blob/master/doc/macos.md) or [Linux](https://github.com/Genymobile/scrcpy/blob/master/doc/linux.md) instructions.

### Prepare the phone

1. Enable **Developer options**, usually by tapping **Build number** several times. The location depends on the manufacturer.
2. Enable **USB debugging**.
3. Connect the phone with a USB data cable.
4. Unlock the phone and accept the RSA debugging authorization prompt for this computer.
5. Check the connection:

```powershell
adb devices
```

The expected device status is `device`. Selecting MTP/File transfer is not a requirement.

### Start mirroring

Start without audio:

```powershell
scrcpy --no-audio
```

To try a higher frame-rate limit:

```powershell
scrcpy --video-codec=h264 --max-fps=120 --max-size=1920 --video-bit-rate=16M --no-audio --print-fps
```

| Option | Meaning |
|---|---|
| `--video-codec=h264` | Select H.264, which is also the default codec. |
| `--max-fps=120` | Set an upper limit, not a guarantee of 120 FPS. |
| `--max-size=1920` | Limit video dimensions while preserving the aspect ratio; the result is not necessarily 1920×1080. |
| `--video-bit-rate=16M` | Set a target video bit rate of 16 Mbit/s. |
| `--no-audio` | Disable audio forwarding. |
| `--print-fps` | Print the capture frame rate in the terminal. |

The frame rate is variable and may be low on a static screen because new frames are produced when screen content changes. This number does not replace profiling the application's frames.

The screen appears in a separate window. Control it with your mouse and keyboard or continue using the phone directly. Close the window or press `Ctrl+C` in the terminal to stop.

### More useful commands

```powershell
# Less demanding profile
scrcpy --max-fps=60 --max-size=1280 --video-bit-rate=8M --no-audio

# Record the screen without audio
scrcpy --no-audio --record=demo.mp4

# Select a device by its serial from adb devices
scrcpy --serial=SERIAL --no-audio

# Help
scrcpy --help
```

Replace `SERIAL` with the device serial. A relative recording path such as `demo.mp4` is resolved against the terminal's current directory.

To turn the recording into a short GIF, follow [FFmpeg for App Demos](ffmpeg.md).

### Troubleshooting

* **Command not found:** open a new terminal, check `PATH`, or run `.\scrcpy.exe` from the extracted directory.
* **`unauthorized`:** unlock the phone and accept the debugging authorization prompt.
* **Device missing:** check USB debugging, the data cable, and the USB port; install the manufacturer's Windows USB driver if needed.
* **Multiple devices or emulators:** select one with `--serial`.
* **Low FPS or noticeable delay:** reduce the resolution and FPS limit; try the less demanding profile above. Increasing bit rate alone does not increase FPS.
* **Screen visible but input fails on some Xiaomi devices:** check the separate **USB debugging (Security Settings)** option. The official documentation requires a reboot after enabling it.

### Official sources

* [scrcpy repository](https://github.com/Genymobile/scrcpy) - overview, requirements, and documentation for advanced features.
* [Releases](https://github.com/Genymobile/scrcpy/releases) - official downloads.
* Installation: [Windows](https://github.com/Genymobile/scrcpy/blob/master/doc/windows.md), [macOS](https://github.com/Genymobile/scrcpy/blob/master/doc/macos.md), [Linux](https://github.com/Genymobile/scrcpy/blob/master/doc/linux.md).
* [Video options](https://github.com/Genymobile/scrcpy/blob/master/doc/video.md) - sizing, codecs, bit rate, and FPS.
* [Connection](https://github.com/Genymobile/scrcpy/blob/master/doc/connection.md) - device selection and TCP/IP setup.

### See also

* [Tools Overview](overview.md)
* [Performance Profiling and Benchmarking](performance-profiling.md) - measuring application performance beyond the mirroring FPS counter.
