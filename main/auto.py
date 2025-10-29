"""
this is kinda old too i refurbished it recently but its still a bit gross, sorry :(
"""

# default modules
import argparse
import cv2
import logging
import numpy as np
import os
import random
import sys
import time

# REQUIRED MODULES
import pyautogui
import pytesseract
from pynput.keyboard import Controller, Key

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from manual import n_valid_words, complexity

####################################################################################################
# Logging and ArgParse

# Add a debug argument parser - when specified, print debug statements
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

# Logging
logging.basicConfig(format='(%(asctime)s.%(msecs)03d) %(levelname)s\t %(message)s', datefmt='%H:%M:%S')
if args.debug:
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)



####################################################################################################


global USED_WORDS
USED_WORDS = []

keyboard_controller = Controller()


def is_playing_currently() -> bool:
    """Get a screenshot of the screen and check if the player is currently playing."""

    screenshot = pyautogui.screenshot(region=(750, 750, 100, 400))
    # text = get_text(screenshot)
    text = pytesseract.image_to_string(screenshot)
    return "Quick!" in text


def sharpen_image(img: Image.Image) -> Image.Image:
    """Sharpen and preprocess an image for OCR on boxed capital letters."""

    img = img.convert('L')
    img = img.resize((img.width * 5, img.height * 5), resample=Image.Resampling.LANCZOS)

    img = img.point(lambda x: 255 if x < 30 else 0) # Reverse point to remove boxes

    np_img = np.array(img, dtype=np.uint8) # uint8 for OpenCV

    # Erode to reduce box outlines
    kernel = np.ones((4, 4), np.uint8)
    np_img = cv2.erode(np_img, kernel, iterations=3)

    # Slight dilation to restore letter thickness
    np_img = cv2.dilate(np_img, np.ones((4, 4), np.uint8), iterations=5)
    
    # Gaussian blur
    np_img = cv2.GaussianBlur(np_img, (5, 5), sigmaX=7.0)

    img = Image.fromarray(np_img) # Back to PIL

    return img


def get_image() -> Image.Image:
    """Get a screenshot of the screen and preprocess it for OCR."""

    screenshot = pyautogui.screenshot(region=(925, 760, 110, 90))
    screenshot = sharpen_image(screenshot)
    # screenshot.save(os.path.dirname(__file__) + f'/images/{time.asctime()}.png')
    return screenshot


def read_combination(image: Image.Image, config: str) -> str:
    """Read the combination of letters from the game."""

    logging.info(f"Config: {config}")

    text = pytesseract.image_to_string(image, config=config)

    text = text.lower().strip().replace(' ', '')
    return text


def select_valid_word(comb: str) -> str | None:
    """Select a word from a list of valid words.

    Args:
        comb (str): The combination of letters to match.

    Returns:
        str: The selected word.
        None: If no valid words are found.
    """

    words = list(n_valid_words(100, comb))

    # Remove words that have already been used
    words = [word for word in words if word not in USED_WORDS]

    if len(words) == 0:
        return None

    # Sort words by length
    words.sort(key=len, reverse=True)
    words = words[:20] # Keep only the top 20 longest words

    # Sort by complexity and keep the top 3
    words.sort(key=complexity, reverse=True)
    words = words[:3]
    
    return random.choice(words) # Return a random word


def send_word(word: str) -> None:
    """Send a word to the game."""

    for char in word:
        keyboard_controller.press(char)
        keyboard_controller.release(char)
        time.sleep(random.uniform(0.0, 0.02))  # Random delay between 10-50ms per character
    keyboard_controller.press(Key.enter)
    keyboard_controller.release(Key.enter)
        

###################################################################################################


CONFIGS = [
    # TIER 1: Standard high-accuracy configs
    r'--psm 7 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    r'--psm 8 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    
    # TIER 2: Alternative segmentation modes
    r'--psm 13 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',  # Raw line
    r'--psm 6 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',   # Uniform block
    
    # TIER 3: Engine combinations
    # r'--psm 8 --oem 2 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',   # LSTM + Legacy
    # r'--psm 7 --oem 2 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    
    # TIER 4: Tuned parameters for difficult text
    r'--psm 8 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ textord_min_linesize=0.3',
    r'--psm 8 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ textord_force_make_prop_words=F',
    r'--psm 8 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ textord_noise_rej=0',
    
    # TIER 5: Legacy engine only
    # r'--psm 8 --oem 0 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    # r'--psm 7 --oem 0 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    # r'--psm 13 --oem 0 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    
    # TIER 6: Minimal processing modes
    r'--psm 10 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',  # Single character
    r'--psm 6 --oem 1',  # Uniform block, no whitelist
    r'--psm 7 --oem 1',  # Single line, no whitelist
    r'--psm 8 --oem 1',  # Single word, no whitelist
    
    # TIER 7: Aggressive/raw modes
    r'--psm 13 --oem 1',  # Raw line, no whitelist
    r'--psm 12 --oem 1',  # Sparse text
    # r'--psm 6 --oem 0',   # Uniform block, legacy, no whitelist
    # r'--psm 7 --oem 0',   # Single line, legacy, no whitelist
    
    # TIER 8: Last resort - no configuration
    r'',  # Default Tesseract settings
]


def main() -> None:
    """The main program."""

    global USED_WORDS

    while True:
        if is_playing_currently():
            print()
            logging.info("Playing detected.")

            word = None
            config_index = 0

            image = get_image()

            logging.info("Image clipped and sharpened.")

            while word is None and config_index < len(CONFIGS):
                custom_config = CONFIGS[config_index]
                config_index += 1
                comb = read_combination(image, custom_config)

                if comb == '':
                    continue

                logging.info(f"Comb: {comb}")

                word = select_valid_word(comb)
                if word is None:
                    logging.warning("No valid words found. Retrying...")
                else:
                    break
            
            if word is None:
                logging.error("No valid words found.")
            else:
                logging.info(f"{word} selected. Sending...")
                send_word(word)

                USED_WORDS.append(word)

        else:
            print(".", end='', flush=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\nGoodbye!")