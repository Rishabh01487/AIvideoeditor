# Background Music Assets

This directory contains background music files used by the AI video editor for different moods.

## Required Files

Create audio files in this directory with the following names:

- **upbeat.mp3** - Upbeat, energetic background music
- **calm.mp3** - Calm, relaxing background music
- **cinematic.mp3** - Cinematic, dramatic background music

## How to Add Music Files

1. Download royalty-free music from services like:
   - [Pixabay Music](https://pixabay.com/music/)
   - [Free Music Archive](https://freemusicarchive.org/)
   - [YouTube Audio Library](https://www.youtube.com/audiolibrary)
   - [Incompetech](https://incompetech.com/)

2. Convert to MP3 format if needed:
   ```bash
   ffmpeg -i input.wav -c:a libmp3lame -q:a 4 output.mp3
   ```

3. Place the files in this directory with the appropriate names

## Notes

- If music files are not found, the system will continue without background music
- Audio files should be at least as long as the longest video you plan to edit
- MP3 format is recommended for compatibility
- Higher quality files (192kbps or higher) are recommended

## Example Usage

When a user's editing prompt includes "upbeat music", the system will automatically:
1. Check for `upbeat.mp3` in this directory
2. Loop it to match the video duration
3. Blend it with the video's original audio (if any)

If the file doesn't exist, the music feature gracefully skips without crashing.
