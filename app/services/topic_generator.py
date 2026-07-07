import logging
import random
from typing import List

logger = logging.getLogger(__name__)

GENERATOR = None

try:
    from transformers import pipeline, set_seed
    set_seed(42)
    logger.info("Initializing GPT-2 text generation pipeline...")
    GENERATOR = pipeline(
        "text-generation", 
        model="gpt2",
        device=-1 # Deploy to CPU by default
    )
    logger.info("GPT-2 pipeline loaded successfully.")
except Exception as e:
    logger.warning(
        f"Failed to load GPT-2 pipeline: {e}. "
        "Falling back to template-based conversation prompt generator."
    )
    GENERATOR = None


def generate_topics(event_themes: List[str], user_interests: List[str]) -> List[str]:
    """
    Generates 2-3 conversation starters matching the event themes and user interests.
    Guides generative GPT-2 Small using prompt design.
    """
    themes_str = ", ".join(event_themes)
    interests_str = ", ".join(user_interests)
    
    # Prompt template designed to guide GPT-2 Small text completion
    prompt = (
        f"Event Themes: {themes_str}. User Interests: {interests_str}.\n"
        "Here are 3 distinct, professional networking conversation starters:\n"
        "1. \""
    )
    
    starters = []

    if GENERATOR is not None:
        try:
            # Generate text using GPT-2
            res = GENERATOR(
                prompt, 
                max_new_tokens=60, 
                num_return_sequences=1,
                pad_token_id=50256, # set end of text token identifier
                temperature=0.8,
                top_k=50,
                top_p=0.9
            )
            generated_text = res[0]["generated_text"]
            
            # Extract generation part after the prompt
            new_text = generated_text[len(prompt):].strip()
            
            # Parse numbered lines or paragraphs
            lines = new_text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Remove common numbering prefix: "1. ", "2. ", "3. ", "1: ", "- " etc.
                cleaned = line
                for prefix in ["1.", "2.", "3.", "1:", "2:", "3:", "-", "*"]:
                    if cleaned.startswith(prefix):
                        cleaned = cleaned[len(prefix):].strip()
                # Remove surrounding quotes if they exist
                if cleaned.startswith('"') and cleaned.endswith('"'):
                    cleaned = cleaned[1:-1]
                elif cleaned.startswith('"'):
                    cleaned = cleaned[1:]
                elif cleaned.endswith('"'):
                    cleaned = cleaned[:-1]
                
                cleaned = cleaned.strip()
                if cleaned and len(cleaned) > 10:
                    starters.append(cleaned)
        except Exception as e:
            logger.error(f"Error during GPT-2 generation: {e}. Falling back to templates...")
            starters = []

    # If generators failed or produced too few inputs, run template-based fallback
    if len(starters) < 2:
        starters = generate_template_starters(event_themes, user_interests)

    # Return at most 3 items, ensuring they are unique and cleaned
    unique_starters = []
    for s in starters:
        if s not in unique_starters:
            unique_starters.append(s)
    
    return unique_starters[:3]


def generate_template_starters(themes: List[str], interests: List[str]) -> List[str]:
    """
    Fallback deterministic prompt generator.
    Combines themes and interests to produce 3 natural dialogue openers.
    """
    t_val = themes[0] if themes else "innovation"
    i_val = interests[0] if interests else "connecting with others"
    
    t_val_sec = themes[1] if len(themes) > 1 else ""
    i_val_sec = interests[1] if len(interests) > 1 else ""

    starters = []
    
    # Template 1
    if i_val_sec:
         starters.append(
             f"Hi! I was reading up on the intersection of {t_val} and {i_val}. "
             f"I read that you have background in {i_val_sec}. How do you see these fields merging in the next wave?"
         )
    else:
         starters.append(
             f"Hi there! I'm interested in {i_val} and noticed the event covers a lot of {t_val}. "
             f"Have you seen some interesting applications of this recently?"
         )
         
    # Template 2
    if t_val_sec:
         starters.append(
             f"With all the discussion here regarding {t_val} and {t_val_sec}, "
             f"I find myself thinking about how we can leverage {i_val} to address current challenges. What's your perspective?"
         )
    else:
         starters.append(
             f"Hello! I'm attending because of the focus on {t_val}. I'm trying to view it through the lens of {i_val}. "
             f"Are you working on something in this space as well?"
         )

    # Template 3
    starters.append(
        f"Excuse me, I'm quite curious about the sessions on {t_val}. "
        f"Since my interests align with {i_val}, I'd love to hear what key elements you think practitioners should focus on."
    )

    return starters
