# ACRCloud API Setup Guide

## Why ACRCloud?

ACRCloud uses **Shazam-like technology** for music identification. It's one of the best free APIs for identifying songs by audio.

- **Free Tier**: 1,000 requests/month (usually enough for personal use)
- **Accuracy**: 95%+ for commercial releases
- **Speed**: Very fast (< 1 second per request)
- **Coverage**: Billions of tracks including live performances

## Step 1: Sign Up for Free Account

1. Go to: https://www.acrcloud.com/
2. Click **"Sign Up"** (top right)
3. Fill in your details:
   - Email
   - Password
   - Country
4. Choose **"Personal"** plan
5. Verify your email

## Step 2: Create an Application

1. Log in to your ACRCloud dashboard
2. Go to **"Projects"** → **"Add Project"**
3. Fill in project details:
   - **Project Name**: e.g., "Music Metadata Fixer"
   - **Platform**: Select "Other"
   - **Service Region**: Choose closest to you

4. You'll get:
   - **Access Key** (looks like: `abc123def456`)
   - **Access Secret** (looks like: `xyz789uvw123`)

## Step 3: Add to Config File

Edit your `config.json`:

```json
{
  "acrcloud": {
    "enabled": true,
    "access_key": "YOUR_ACCESS_KEY_HERE",
    "access_secret": "YOUR_ACCESS_SECRET_HERE"
  }
}
```

**Example with fake credentials**:
```json
{
  "acrcloud": {
    "enabled": true,
    "access_key": "abc123def456xyz789uvw123",
    "access_secret": "secret123xyz789abc456def"
  }
}
```

## Step 4: Test Configuration

```bash
cd /home/amir/Documents/Meta

python3 << 'EOF'
import json
from pathlib import Path

# Check if config exists
config_file = Path("config.json")
if config_file.exists():
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    acrcloud = config.get("acrcloud", {})
    
    if acrcloud.get("enabled"):
        print("✓ ACRCloud is enabled")
        print(f"  Access Key: {acrcloud.get('access_key', 'NOT SET')[:20]}...")
        print(f"  Access Secret: {acrcloud.get('access_secret', 'NOT SET')[:20]}...")
    else:
        print("→ ACRCloud is disabled in config")
else:
    print("✗ config.json not found")
EOF
```

## Step 5: Test with Song Identification

```bash
cd /home/amir/Documents/Meta

python3 << 'EOF'
from song_metadata_fixer_v2 import SongMetadataFixer
from pathlib import Path

fixer = SongMetadataFixer()

# Test with your music file
test_file = Path("your_song.mp3")

if test_file.exists():
    result = fixer.identify_and_fill_metadata(test_file)
    print(f"Result: {result.message}")
    
    # Get metadata
    metadata = fixer.get_metadata(test_file)
    print(f"\nMetadata:")
    print(f"  Title: {metadata.get('title')}")
    print(f"  Artist: {metadata.get('artist')}")
    print(f"  Album: {metadata.get('album')}")
else:
    print(f"❌ File not found: {test_file}")
EOF
```

## Checking Your API Usage

1. Log in to ACRCloud dashboard
2. Go to **"Account"** → **"Usage"**
3. See how many requests you've used this month

**Free tier limits**:
- 1,000 requests/month
- That's about 30 songs/day - plenty for personal use!

## Troubleshooting

### "ACRCloud API returned error"

**Possible causes**:
1. Invalid credentials - Check Access Key and Secret
2. API disabled - Make sure `"enabled": true` in config.json
3. Rate limit exceeded - Wait until next month (free tier resets monthly)
4. Network issue - Check internet connection

### "Can't connect to ACRCloud"

**Solutions**:
1. Check internet connection: `ping acrcloud.com`
2. Check credentials: Make sure they're copied exactly
3. Try API directly: Test at https://www.acrcloud.com/tools/recognizer

### "Still not identifying songs"

**Try these**:
1. Use longer audio clips (30+ seconds)
2. Use clean, high-quality MP3s
3. Combine with AI suggestions for refinement
4. Manually review results with confidence < 85%

## Alternatives to ACRCloud

If ACRCloud doesn't work for you, these are free alternatives:

### 1. **Spotify Search API** (Built-in)
- No API key needed
- Unlimited free requests
- Good for popular music
- Already integrated

### 2. **MusicBrainz Acoustic ID** (Built-in)
- Free and open-source
- Very reliable
- Good for all genres
- May need `chromaprint` library

### 3. **Last.fm API** (Free tier)
- 60 requests/minute
- Excellent metadata
- Good for discovering moods/tags
- Requires free API key

## API Cost Comparison

| Service | Free Tier | Cost | Best For |
|---------|-----------|------|----------|
| ACRCloud | 1,000/mo | $9.99+/mo | Shazam-like accuracy |
| Spotify | Unlimited | Free | Popular music |
| MusicBrainz | Unlimited | Free | All genres |
| Last.fm | 60/min | Free | Metadata enrichment |

## Privacy & Security Notes

✅ **Safe**:
- Your music file is analyzed locally or sent to API
- No personal data stored
- Standard HTTPS encryption
- ACRCloud has privacy policy

⚠️ **Be Aware**:
- API requests include audio fingerprint
- ACRCloud logs usage (standard practice)
- Keep API credentials private (treat like passwords)

## Rate Limit Strategy

Free tier: 1,000 requests/month

**Recommended usage**:
- Process ~30 songs/day
- Leave 33-day buffer
- Don't process entire library at once

**To stay within limits**:
1. Process in batches (50 songs at a time)
2. Wait between batches
3. Use local MusicBrainz for some songs
4. Enable caching (when implemented)

## Common Questions

**Q: Do I need ACRCloud?**
A: No, it's optional. System works with MusicBrainz + Spotify + AI.

**Q: What if I exceed 1,000 requests?**
A: Requests will fail gracefully, falls back to other methods.

**Q: Can I upgrade?**
A: Yes, paid plans have higher limits ($9.99/mo = 100,000 requests).

**Q: Is it safe to share my API key?**
A: No! Treat it like a password. Don't commit to git.

**Q: How accurate is ACRCloud?**
A: 95%+ for commercial releases, 85%+ for live/remixes.

## Next Steps

1. ✓ Install system (already done)
2. ⏳ Set up ACRCloud (optional)
3. → Configure Spotify (if needed)
4. → Batch process music library
5. → Combine with AI + cover art

---

*ACRCloud Setup Guide*  
*Last Updated: November 2025*
