import io
import time
import easyocr
from gtts import gTTS
import pygame

def get_ordered_text(image_path: str, y_threshold: int = 15) -> list[str]:
    reader = easyocr.Reader(['te', 'en'], gpu=True)
    results = reader.readtext(image_path, detail=1)

    items = []
    for bbox, text, prob in results:
        x_min = bbox[0][0]
        y_min = bbox[0][1]
        y_max = bbox[2][1]
        height = y_max - y_min
        items.append({
            'x': x_min,
            'y': y_min,
            'height': height,
            'text': text.strip()
        })

    items.sort(key=lambda item: item['y'])

    lines = []
    for item in items:
        matched_line = None
        for line in lines:
            avg_y = sum(w['y'] for w in line) / len(line)
            if abs(item['y'] - avg_y) <= y_threshold:
                matched_line = line
                break

        if matched_line is not None:
            matched_line.append(item)
        else:
            lines.append([item])

    ordered_sentences = []
    for line in lines:
        line.sort(key=lambda w: w['x'])
        line_text = " ".join(w['text'] for w in line)
        ordered_sentences.append(line_text)

    return ordered_sentences


def speak_text(text: str, lang: str = 'te'):
    if not text.strip():
        print("No text available to read.")
        return

    print("Generating voice audio...")
    tts = gTTS(text=text, lang=lang, slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)


    pygame.mixer.init()
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()

    print("Reading aloud...")
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)



ordered_lines = get_ordered_text('sample2.png', y_threshold=15)

for line_idx, line in enumerate(ordered_lines, 1):
    print(f"Line {line_idx}: {line}")

# Combine ordered lines and read aloud
full_text = " ".join(ordered_lines)
speak_text(full_text, lang='te')