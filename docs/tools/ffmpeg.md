# FFmpeg for App Demos

Use FFmpeg to turn an Android screen recording into a short looping GIF for a README or documentation. To capture the source MP4 from a physical device, see [scrcpy: Android Screen Mirroring](scrcpy.md).

## Prepare a GIF

### Install on Windows

Install FFmpeg with WinGet in PowerShell or CMD.

```powershell
winget install --exact --id Gyan.FFmpeg
```

Open a new terminal and verify the installation.

```powershell
ffmpeg -version
```

The official [FFmpeg downloads page](https://ffmpeg.org/download.html) lists builds and packages for Windows, macOS, and Linux.

### Convert MP4 to GIF

Open PowerShell or CMD in the directory containing `audioDemo.mp4`.

1. Generate a palette from the frames that will go into the GIF.

    ```powershell
    ffmpeg -i audioDemo.mp4 -vf "fps=16,scale=500:-1:flags=lanczos,palettegen=max_colors=48" -frames:v 1 -update 1 palette.png
    ```

2. Apply the palette and save the GIF.

    ```powershell
    ffmpeg -i audioDemo.mp4 -i palette.png -filter_complex "[0:v]fps=16,scale=500:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer" audioDemo.gif
    ```

| Setting | Effect |
|---|---|
| `fps=16` | Sets the frame rate to 16 FPS. |
| `scale=500:-1` | Sets the width to 500 px and calculates the height to preserve the aspect ratio. |
| `flags=lanczos` | Selects the Lanczos scaling algorithm. |
| `max_colors=48` | Limits the number of colors used in the palette. |
| `dither=bayer` | Uses ordered dithering to approximate intermediate shades. It can leave a visible pattern on gradients. |

**Keep FPS and scaling identical in both commands.** The palette is built from the frames that go into the GIF. Regenerate it if the source video changes.

### Adjust size and quality

Start with 16 FPS, 500 px, and 48 colors for a short UI demo.

- If small text is hard to read, try increasing the width.
- If gradients look rough, try `max_colors=64` or `max_colors=96`, regenerate the palette, and compare the results.
- If the GIF is too large, shorten the clip first, then try reducing the width or FPS.

Before publishing, compare the GIF and MP4 file sizes and check which formats the platform accepts. Use MP4 when the demo needs audio.

For more options, see the [FFmpeg filter documentation](https://ffmpeg.org/ffmpeg-filters.html).
