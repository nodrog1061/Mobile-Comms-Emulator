#!/usr/bin/env python3
"""
ConvoKit Reddit Corpus Converter
Downloads the Reddit Corpus (small) from ConvoKit and converts it to JSON format
for use with the messaging screenshot generator tool.

SUBREDDIT FILTERING: Edit the ALLOWED_SUBREDDITS list below to control which
subreddits are included in the output.
"""

import json
import random
from convokit import Corpus, download

# ============================================================================
# CONFIGURATION: Edit these settings
# ============================================================================

# Set to None to include ALL subreddits, or provide a list to filter
# Examples:
#   None - Include all subreddits
#   ["AskReddit", "pics", "funny"] - Only these subreddits
#   ["gaming", "pcmasterrace", "buildapc"] - Tech-focused
ALLOWED_SUBREDDITS = ['guns', 'Drugs','unitedkingdom', 'tifu']  # Change this to filter by subreddit

# Maximum number of conversations to extract
MAX_CONVERSATIONS = 1000

# Maximum messages per conversation
MAX_MESSAGES_PER_CONVERSATION = 15

# Minimum messages required to include a conversation
MIN_MESSAGES_PER_CONVERSATION = 3

# Maximum character length per message
MAX_MESSAGE_LENGTH = 200

# ============================================================================

def clean_reddit_text(text):
    """Remove Reddit-specific formatting and clean up text"""
    import re
    
    # Remove [deleted] and [removed]
    if text.lower().strip() in ['[deleted]', '[removed]', 'deleted', 'removed']:
        return None
    
    # Remove bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Remove italic: *text* or _text_ (but not at word boundaries)
    text = re.sub(r'\*([^\*]+?)\*', r'\1', text)
    text = re.sub(r'\b_([^_]+?)_\b', r'\1', text)
    
    # Remove strikethrough: ~~text~~
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    
    # Remove quotes: > text
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    
    # Remove code blocks: `code` or ```code```
    text = re.sub(r'`{1,3}(.+?)`{1,3}', r'\1', text, flags=re.DOTALL)
    
    # Remove links: [text](url) - keep the text
    text = re.sub(r'\[([^\]]+?)\]\([^\)]+?\)', r'\1', text)
    
    # Remove Reddit-specific mentions: /r/subreddit, u/username, r/subreddit
    text = re.sub(r'/r/\w+', '', text)
    text = re.sub(r'\br/\w+', '', text)
    text = re.sub(r'u/\w+', '', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    
    # Remove excessive newlines and replace with space
    text = re.sub(r'\n+', ' ', text)
    
    # Remove excessive spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    # Return None if empty or too short after cleaning
    if not text or len(text) < 3:
        return None
    
    return text


def extract_conversations_from_convokit():
    """Download and process Reddit corpus (small) from ConvoKit with balanced subreddit distribution"""
    
    print("Downloading Reddit corpus (small) from ConvoKit...")
    print("This may take a few minutes on first run...")
    
    # Download the corpus
    corpus = Corpus(filename=download("reddit-corpus-small"))
    
    print(f"\nCorpus loaded successfully!")
    corpus.print_summary_stats()
    
    if ALLOWED_SUBREDDITS:
        print(f"\nFiltering for subreddits: {', '.join(ALLOWED_SUBREDDITS)}")
    else:
        print("\nIncluding all subreddits (no filtering)")
    
    # First pass: organize conversations by subreddit
    conversations_by_subreddit = {}
    
    for conv_id in corpus.get_conversation_ids():
        convo = corpus.get_conversation(conv_id)
        subreddit = convo.meta.get("subreddit", "unknown")
        
        # Filter by subreddit if specified
        if ALLOWED_SUBREDDITS and subreddit not in ALLOWED_SUBREDDITS:
            continue
        
        # Get all utterances in conversation
        utterances = convo.get_chronological_utterance_list()
        
        if len(utterances) < MIN_MESSAGES_PER_CONVERSATION:
            continue
        
        # Process messages
        messages = []
        for utt in utterances[:MAX_MESSAGES_PER_CONVERSATION]:
            text = utt.text
            
            if not text:
                continue
            
            # Clean Reddit formatting
            cleaned_text = clean_reddit_text(text)
            
            if not cleaned_text:
                continue
            
            # Limit message length
            if len(cleaned_text) > MAX_MESSAGE_LENGTH:
                cleaned_text = cleaned_text[:MAX_MESSAGE_LENGTH-3] + '...'
                
            # Determine if sent or received (alternate for realistic feel)
            sender = "sent" if len(messages) % 2 == 0 else "received"
            
            messages.append({
                "sender": sender,
                "text": cleaned_text
            })
        
        # Only include conversations with enough valid messages
        if len(messages) >= MIN_MESSAGES_PER_CONVERSATION:
            convo_data = {
                "id": conv_id,
                "subreddit": subreddit,
                "title": convo.meta.get("title", ""),
                "messages": messages
            }
            
            # Add to subreddit bucket
            if subreddit not in conversations_by_subreddit:
                conversations_by_subreddit[subreddit] = []
            conversations_by_subreddit[subreddit].append(convo_data)
    
    # Second pass: balanced sampling across subreddits
    print(f"\nFound conversations in {len(conversations_by_subreddit)} subreddits")
    
    # Calculate how many to take from each subreddit for balanced distribution
    subreddits_list = list(conversations_by_subreddit.keys())
    num_subreddits = len(subreddits_list)
    
    if num_subreddits == 0:
        print("⚠️  No conversations found matching criteria!")
        return []
    
    # Target: Equal distribution across subreddits
    per_subreddit = MAX_CONVERSATIONS // num_subreddits
    remainder = MAX_CONVERSATIONS % num_subreddits
    
    conversations = []
    subreddit_counts = {}
    
    for i, subreddit in enumerate(subreddits_list):
        available = conversations_by_subreddit[subreddit]
        
        # Take equal amount from each, plus 1 extra for first few subreddits (to handle remainder)
        target = per_subreddit + (1 if i < remainder else 0)
        
        # Sample from this subreddit
        sample_size = min(target, len(available))
        sampled = random.sample(available, sample_size)
        
        conversations.extend(sampled)
        subreddit_counts[subreddit] = sample_size
    
    # Shuffle to mix subreddits
    random.shuffle(conversations)
    
    # Print distribution
    print(f"\nExtracted {len(conversations)} conversations with balanced distribution:")
    print(f"\nSubreddit distribution:")
    for subreddit, count in sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(conversations) * 100) if conversations else 0
        print(f"  {subreddit:<40} {count:>4} conversations ({percentage:>5.1f}%)")
    
    return conversations

def list_available_subreddits():
    """List all subreddits available in the corpus"""
    
    print("Loading corpus to find available subreddits...")
    corpus = Corpus(filename=download("reddit-corpus-small"))
    
    subreddits = set()
    subreddit_counts = {}
    
    for conv_id in corpus.get_conversation_ids():
        convo = corpus.get_conversation(conv_id)
        subreddit = convo.meta.get("subreddit", "unknown")
        subreddits.add(subreddit)
        subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
    
    print(f"\n{'='*60}")
    print(f"Found {len(subreddits)} subreddits in the corpus")
    print(f"{'='*60}\n")
    
    # Sort by number of conversations
    sorted_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("Subreddit (Number of conversations):")
    print("-" * 60)
    for subreddit, count in sorted_subreddits:
        print(f"  {subreddit:<40} {count:>5} conversations")
    
    print("\n" + "="*60)
    print("To filter by specific subreddits, edit ALLOWED_SUBREDDITS")
    print("at the top of this script.")
    print("="*60)
    
    return list(subreddits)

def save_to_json(conversations, output_file="reddit_conversations.json"):
    """Save conversations to JSON file"""
    
    output = {
        "source": "ConvoKit Reddit Corpus (small)",
        "total_conversations": len(conversations),
        "conversations": conversations
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(conversations)} conversations to {output_file}")
    print(f"File size: {len(json.dumps(output)) / 1024:.2f} KB")

def create_sample_csv(conversations, output_file="sample_messages.csv"):
    """Create a sample CSV file from conversations for testing"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("sender,message\n")
        
        # Get 50 random messages
        sample_convo = random.choice(conversations)
        for msg in sample_convo['messages'][:20]:
            # Escape commas and quotes for CSV
            text = msg['text'].replace('"', '""').replace('\n', ' ')
            f.write(f'{msg["sender"]},"{text}"\n')
    
    print(f"Created sample CSV: {output_file}")

if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("ConvoKit Reddit Corpus Converter")
    print("="*60)
    
    # Check for --list-subreddits argument
    if len(sys.argv) > 1 and sys.argv[1] == "--list-subreddits":
        list_available_subreddits()
        sys.exit(0)
    
    try:
        # Extract conversations
        conversations = extract_conversations_from_convokit()
        
        if len(conversations) == 0:
            print("\n⚠️  WARNING: No conversations matched your filters!")
            print("Try changing ALLOWED_SUBREDDITS or running with --list-subreddits")
            sys.exit(1)
        
        # Save to JSON
        save_to_json(conversations)
        
        # Create sample CSV
        create_sample_csv(conversations)
        
        print("\n" + "="*60)
        print("SUCCESS! Files created:")
        print("  - reddit_conversations.json (for web tool)")
        print("  - sample_messages.csv (for testing)")
        print("="*60)
        print("\nNext steps:")
        print("1. Use reddit_conversations.json in your updated web tool")
        print("2. Or upload sample_messages.csv to test the CSV import feature")
        print("\nTo see all available subreddits, run:")
        print("  python convokit_converter.py --list-subreddits")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure ConvoKit is installed:")
        print("  pip install convokit")