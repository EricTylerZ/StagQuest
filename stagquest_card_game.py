from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import os
import tempfile

# Register Century Schoolbook font
try:
    pdfmetrics.registerFont(TTFont("CenturySchoolbook", "C:/Windows/Fonts/CENSCBK.TTF"))
    FONT_NAME = "CenturySchoolbook"
    print("Century Schoolbook font registered successfully.")
except Exception as e:
    print(f"Failed to register Century Schoolbook: {e}. Falling back to Helvetica.")
    FONT_NAME = "Helvetica"

# Card dimensions (2.5" x 3.5", standard poker size)
CARD_WIDTH, CARD_HEIGHT = 2.5 * inch, 3.5 * inch
PAGE_WIDTH, PAGE_HEIGHT = letter

# Define Royal Turquoise (#00918b)
royal_turquoise = Color(0, 0.569, 0.545)

# Virtue Deck (18 cards, prayer-time names)
virtue_cards = [
    ("Lauds Prayer", "40M are trafficked—addiction fuels this. Pray to break free today."),
    ("Prime Resolve", "Porn’s a $150B industry exploiting kids. Commit to purity now."),
    ("Terce Strength", "Temptation rewires your brain—fight it to reclaim your mind."),
    ("Sext Reflection", "76% of trafficking victims are under 18. Reflect on who you protect."),
    ("None Cut", "Porn’s progressive—each view deepens the trap. Pray to sever it."),
    ("Vespers Stand", "9,000 illicit parlors thrive on demand. Stand against it today."),
    ("Compline Rest", "Addiction funds evil—every ‘no’ saves lives. Rest in this victory."),
    ("Lauds Hope", "A child sold every 2 min—your virtue restores hope. Plan one good deed."),
    ("Prime Focus", "Dopamine spikes blind you—resist to heal your soul."),
    ("Terce Shield", "2.5M trafficked yearly—your fight shields them. Pray for strength."),
    ("Sext Vision", "Your eyes choose life or death—guard them to lead your family."),
    ("None Break", "Porn drives 42% of family trafficking. Break the cycle now."),
    ("Vespers Renewal", "Habits form in weeks—renew your will to defy lust’s pull."),
    ("Compline Peace", "Each clean day cuts traffickers’ cash. Note your progress."),
    ("Lauds Rally", "14M new victims annually—rally your spirit to end this."),
    ("Prime Triumph", "Virtue builds a shield—help another resist temptation today."),
    ("Terce Legacy", "Onchain or off, your quest frees souls. Pray for vigilance."),
    ("Sext Growth", "Your stag grows horns—celebrate each win with family purpose.")
]

# Temptation Deck (5 cards)
temptation_cards = [
    ("Temptation", "An urge strikes—resist it or lose a day’s progress."),
    ("Temptation", "Illicit content tempts you—say no or lose a day."),
    ("Temptation", "Fatigue clouds your will—rest well or lose a day."),
    ("Temptation", "Old habits whisper—replace them or lose a day."),
    ("Temptation", "A lie justifies relapse—reject it or lose a day.")
]

# Fun Facts for Virtue Card pages
fun_facts = [
    "Fun Fact: Terce (9am) marks Christ’s trial in the Divine Office.",
    "Fun Fact: Prime (6am) starts the daily office, a call to purpose.",
    "Fun Fact: Novenas are 9-day prayers, echoing the Apostles’ wait."
]

def wrap_text(text, width, font, font_size, c):
    c.setFont(font, font_size)
    words = text.split()
    lines = []
    current_line = []
    current_width = 0
    for word in words:
        word_width = c.stringWidth(word + " ", font, font_size)
        if current_width + word_width <= width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_width = word_width
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def draw_card(c, x, y, title, text):
    c.setFont(FONT_NAME, 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x + 10, y + CARD_HEIGHT - 20, title)
    c.setFont(FONT_NAME, 10)  # Increased from 9 to 10
    wrapped_lines = wrap_text(text, CARD_WIDTH - 20, FONT_NAME, 10, c)
    for i, line in enumerate(wrapped_lines[:4]):  # 4 lines max to fit
        c.drawString(x + 10, y + CARD_HEIGHT - 40 - i * 12, line)
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT)

def create_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_file.name)
    return temp_file.name

def create_pdf():
    c = canvas.Canvas("stagquest_card_game.pdf", pagesize=letter)
    c.setTitle("StagQuest: A Virtue-Building Card Game")

    # Page 1: Cover
    c.setFont(FONT_NAME, 20)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2, "StagQuest: A Card Game")
    c.setFont(FONT_NAME, 12)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2 - 30, "A Zoseco Journey to Virtue")
    c.setFont(FONT_NAME, 11)
    c.drawCentredString(PAGE_WIDTH/2, 1.8 * inch, "Join the Quest – Get in Touch!")
    c.setFont(FONT_NAME, 9)
    c.setFillColorRGB(0, 0, 0)
    contact_text = [
        "Text/Voicemail: (219) 488-2689",
        "Email: info@zoseco.com",
        "Join our Discord:",
        "https://discord.com/invite/zZhtw9WVNv"
    ]
    y_pos = 1.6 * inch
    for line in contact_text:
        c.drawCentredString(PAGE_WIDTH/2, y_pos, line)
        y_pos -= 18
    qr_file = create_qr_code("https://discord.com/invite/zZhtw9WVNv")
    c.drawImage(qr_file, 5.5 * inch, 0.8 * inch, 1 * inch, 1 * inch)
    os.remove(qr_file)
    c.showPage()

    # Page 2: Instructions
    c.setFont(FONT_NAME, 16)
    c.setFillColor(royal_turquoise)
    c.drawString(1 * inch, PAGE_HEIGHT - 1 * inch, "StagQuest: How to Play")
    c.setFont(FONT_NAME, 11)
    c.setFillColorRGB(0, 0, 0)
    instructions = [
        "StagQuest is a 9-day solo or small-group card game to build virtue and resist addiction, inspired by a novena. Grow your Stag’s Family Strength with two decks: Virtue (daily draws) and Temptation (challenges on days 3, 6, 9).",
        "How to Play:",
        "1. Setup: Print and cut out the Virtue Deck (18 cards), Temptation Deck (5 cards), and Stag Tracker.",
        "2. Start: Shuffle both decks separately. Set your Stag Tracker to Family Strength 0.",
        "3. Daily Draw: Each day, draw 2 Virtue Cards from the Virtue Deck. Complete their tasks (pray, reflect, act).",
        "4. Temptation Test: On days 3, 6, and 9, draw 1 Temptation Card. Resist it (say 'Y') or lose a day’s progress (say 'N').",
        "5. Track Your Novena: On the Stag Tracker, mark a check for each day you complete both Virtue tasks and resist Temptation (if drawn). One 'N' means no check for that day.",
        "6. Win: After 9 days, if you have 9 checks, increase Family Strength by 1 and claim your Virtuous Stag badge!",
        "Tips: Personalize your Stag Tracker with drawings (e.g., antlers). Suggest new cards on our Discord—share addiction facts or virtue ideas!"
    ]
    y_pos = PAGE_HEIGHT - 1.5 * inch
    for line in instructions:
        wrapped_lines = wrap_text(line, PAGE_WIDTH - 2 * inch, FONT_NAME, 11, c)
        for wrapped_line in wrapped_lines:
            c.drawString(1 * inch, y_pos, wrapped_line)
            y_pos -= 15
        y_pos -= 5
    c.showPage()

    # Pages 3-5: Virtue Deck (18 cards, 4 per page, 2 extra on last)
    for i, (title, text) in enumerate(virtue_cards):
        if i % 4 == 0 and i > 0:
            c.showPage()
        x = (i % 2) * (CARD_WIDTH + 20) + 1.75 * inch
        y = PAGE_HEIGHT - (((i % 4) // 2) + 1) * (CARD_HEIGHT + 20) - 1 * inch
        draw_card(c, x, y, title, text)
        # Add fun facts to bottom of Virtue pages
        if i == 3 or i == 7 or i == 11:  # After 4th card on each page
            c.setFont(FONT_NAME, 9)
            c.setFillColorRGB(0, 0, 0)
            fact_index = (i // 4) % len(fun_facts)
            c.drawCentredString(PAGE_WIDTH/2, 0.5 * inch, fun_facts[fact_index])
    c.showPage()

    # Page 6: Temptation Deck (5 cards, adjusted layout)
    for i, (title, text) in enumerate(temptation_cards):
        if i == 0:
            x = 1.75 * inch
            y = PAGE_HEIGHT - 1.5 * inch - CARD_HEIGHT  # Increased top margin
        elif i == 1:
            x = 1.75 * inch + CARD_WIDTH + 20
            y = PAGE_HEIGHT - 1.5 * inch - CARD_HEIGHT
        elif i == 2:
            x = 1.75 * inch
            y = PAGE_HEIGHT - 2.5 * inch - 2 * CARD_HEIGHT
        elif i == 3:
            x = 1.75 * inch + CARD_WIDTH + 20
            y = PAGE_HEIGHT - 2.5 * inch - 2 * CARD_HEIGHT
        elif i == 4:
            x = (PAGE_WIDTH - CARD_WIDTH) / 2
            y = PAGE_HEIGHT - 3.5 * inch - 3 * CARD_HEIGHT  # Adjusted to fit
        draw_card(c, x, y, title, text)
    c.showPage()

    # Page 7: Stag Tracker and Badge
    c.setFont(FONT_NAME, 12)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1 * inch, "Stag Tracker")
    c.setFont(FONT_NAME, 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1.4 * inch, "Goal: 9 Successful Days")
    c.rect(2 * inch, PAGE_HEIGHT - 2 * inch, 4.5 * inch, 0.5 * inch)
    c.setFont(FONT_NAME, 9)
    for i in range(9):
        c.drawString(2.1 * inch + (i * 0.45 * inch), PAGE_HEIGHT - 1.8 * inch, f"Day {i+1}: ___")
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 2.3 * inch, "Family Strength: ___")

    badge_width, badge_height = 3.5 * inch, 1.5 * inch
    badge_x, badge_y = (PAGE_WIDTH - badge_width) / 2, 6 * inch
    c.rect(badge_x, badge_y, badge_width, badge_height)
    c.setFont(FONT_NAME, 14)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 0.4 * inch, "Virtuous Stag Badge")
    c.setFont(FONT_NAME, 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 0.7 * inch, "Awarded to: ________________")
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 1.0 * inch, "Family Strength Gained!")

    c.setFont(FONT_NAME, 11)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, 1.8 * inch, "Join the Quest – Get in Touch!")
    c.setFont(FONT_NAME, 9)
    c.setFillColorRGB(0, 0, 0)
    contact_text = [
        "Text/Voicemail: (219) 488-2689",
        "Email: info@zoseco.com",
        "Join our Discord:",
        "https://discord.com/invite/zZhtw9WVNv"
    ]
    y_pos = 1.6 * inch
    for line in contact_text:
        c.drawCentredString(PAGE_WIDTH/2, y_pos, line)
        y_pos -= 18
    qr_file = create_qr_code("https://discord.com/invite/zZhtw9WVNv")
    c.drawImage(qr_file, 5.5 * inch, 0.8 * inch, 1 * inch, 1 * inch)
    os.remove(qr_file)
    c.showPage()

    c.save()

if __name__ == "__main__":
    create_pdf()
    print("PDF created as 'stagquest_card_game.pdf'!")