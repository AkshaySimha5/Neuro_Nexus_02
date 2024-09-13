from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        for i, entry in enumerate(transcript):
            print(f"{i+1}. {entry['text']} (Start: {entry['start']}s, Duration: {entry['duration']}s)")
    except Exception as e:
        print(f"Error fetching transcript: {e}")

# Example usage: replace 'VIDEO_ID' with the YouTube video's ID
video_id = '2TL3DgIMY1g'  # Example: 'Ks-_Mh1QhMc'
get_transcript(video_id)
