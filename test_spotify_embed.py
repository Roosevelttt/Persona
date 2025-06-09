#!/usr/bin/env python3
"""
Test script for Spotify embed functionality.
This script tests the embed HTML generation and validation functions.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_spotify_embed_html, validate_spotify_track_id


def test_spotify_track_id_validation():
    """Test the Spotify track ID validation function."""
    print("🧪 Testing Spotify Track ID Validation...")
    
    # Valid track IDs (22 characters, alphanumeric)
    valid_ids = [
        "4uLU6hMCjMI75M1A2tKUQC",  # Example valid ID
        "26cvTWJq2E1QqN4jyH2OTU",  # From cache data
        "1ZPVEo8RfmrEz8YAD5n6rW",  # From cache data
    ]
    
    # Invalid track IDs
    invalid_ids = [
        "",                        # Empty string
        None,                      # None value
        "short",                   # Too short
        "this_is_way_too_long_to_be_valid_id",  # Too long
        "4uLU6hMCjMI75M1A2tKUQ!",  # Contains special character
        "4uLU6hMCjMI75M1A2tKUQ",   # Too short by 1 character
    ]
    
    print("✅ Testing valid IDs:")
    for track_id in valid_ids:
        result = validate_spotify_track_id(track_id)
        print(f"   {track_id}: {'✅ Valid' if result else '❌ Invalid'}")
        assert result, f"Expected {track_id} to be valid"
    
    print("\n❌ Testing invalid IDs:")
    for track_id in invalid_ids:
        result = validate_spotify_track_id(track_id)
        print(f"   {track_id}: {'✅ Valid' if result else '❌ Invalid'}")
        assert not result, f"Expected {track_id} to be invalid"
    
    print("\n✅ All validation tests passed!")


def test_embed_html_generation():
    """Test the Spotify embed HTML generation."""
    print("\n🧪 Testing Spotify Embed HTML Generation...")
    
    test_track_id = "4uLU6hMCjMI75M1A2tKUQC"
    
    # Test light theme
    html_light = create_spotify_embed_html(test_track_id, theme="0")
    print("✅ Light theme HTML generated")
    
    # Test dark theme
    html_dark = create_spotify_embed_html(test_track_id, theme="1")
    print("✅ Dark theme HTML generated")
    
    # Verify HTML contains expected elements
    expected_elements = [
        f"https://open.spotify.com/embed/track/{test_track_id}",
        "iframe",
        "width=\"100%\"",
        "height=\"152\"",
        "border-radius",
    ]
    
    for element in expected_elements:
        assert element in html_light, f"Expected '{element}' in light theme HTML"
        assert element in html_dark, f"Expected '{element}' in dark theme HTML"
    
    print("✅ HTML structure validation passed!")
    
    # Save sample HTML for manual inspection
    with open("sample_embed_light.html", "w", encoding="utf-8") as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Spotify Embed Test - Light Theme</title>
</head>
<body>
    <h1>Spotify Embed Test - Light Theme</h1>
    {html_light}
</body>
</html>
        """)
    
    with open("sample_embed_dark.html", "w", encoding="utf-8") as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Spotify Embed Test - Dark Theme</title>
    <style>body {{ background-color: #121212; color: white; }}</style>
</head>
<body>
    <h1>Spotify Embed Test - Dark Theme</h1>
    {html_dark}
</body>
</html>
        """)
    
    print("✅ Sample HTML files created: sample_embed_light.html, sample_embed_dark.html")


def test_with_cache_data():
    """Test with actual song data from cache."""
    print("\n🧪 Testing with Cache Data...")
    
    try:
        from data_manager import DataManager
        
        data_manager = DataManager()
        cached_songs = data_manager.load_cached_songs()
        
        if cached_songs:
            print(f"✅ Loaded {len(cached_songs)} songs from cache")
            
            # Test with first few songs
            test_count = 0
            for song_id, song_data in cached_songs.items():
                if test_count >= 3:  # Test only first 3 songs
                    break
                
                print(f"\n🎵 Testing song: {song_data['name']} by {song_data['artist']}")
                
                # Validate ID
                is_valid = validate_spotify_track_id(song_id)
                print(f"   ID validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
                
                # Generate embed HTML
                if is_valid:
                    html = create_spotify_embed_html(song_id)
                    print(f"   Embed HTML: ✅ Generated ({len(html)} characters)")
                else:
                    print(f"   Embed HTML: ❌ Skipped (invalid ID)")
                
                # Check preview URL availability
                has_preview = bool(song_data.get('preview_url'))
                print(f"   Preview URL: {'✅ Available' if has_preview else '❌ Not available'}")
                
                test_count += 1
            
            print("\n✅ Cache data tests completed!")
        else:
            print("⚠️ No cached songs found - run the main app first to populate cache")
    
    except Exception as e:
        print(f"❌ Error testing with cache data: {e}")


def main():
    """Run all tests."""
    print("🚀 Starting Spotify Embed Functionality Tests\n")
    
    try:
        test_spotify_track_id_validation()
        test_embed_html_generation()
        test_with_cache_data()
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Run 'streamlit run app.py' to test the full integration")
        print("   2. Open sample_embed_*.html files in browser to preview embeds")
        print("   3. Check that Spotify embed player loads correctly in the app")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
