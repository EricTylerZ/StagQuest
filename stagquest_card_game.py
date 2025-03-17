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

# Virtue Deck (18 cards, prayer-time names, with fun facts at bottom)
virtue_cards = [
    ("Lauds Prayer", "40M are trafficked—addiction fuels this. Pray to break free today.\n*Fun Fact:* Lauds (dawn) praises the new day."),
    ("Prime Resolve", "Porn’s a $150B industry exploiting kids. Commit to purity now."),
    ("Terce Strength", "Temptation rewires your brain—fight it to reclaim your mind.\n*Fun Fact:* Terce (9am) marks Christ’s trial."),
    ("Sext Reflection", "76% of trafficking victims are under 18. Reflect on who you protect."),
    ("None Cut", "Porn’s progressive—each view deepens the trap. Pray to sever it.\n*Fun Fact:* None (3pm) recalls Christ’s crucifixion."),
    ("Vespers Stand", "9,000 illicit parlors thrive on demand. Stand against it today."),
    ("Compline Rest", "Addiction funds evil—every ‘no’ saves lives. Rest in this victory.\n*Fun Fact:* Compline (night) seals the day in peace."),
    ("Lauds Hope", "A child sold every 2 min—your virtue restores hope. Plan one good deed."),
    ("Prime Focus", "Dopamine spikes blind you—resist to heal your soul."),
    ("Terce Shield", "2.5M trafficked yearly—your fight shields them. Pray for strength."),
    ("Sext Vision", "Your eyes choose life or death—guard them to lead your family."),
    ("None Break", "Porn drives 42% of family trafficking. Break the cycle now.\n*Fun Fact:* None (3pm) recalls Christ’s crucifixion."),
    ("Vespers Renewal", "Habits form in weeks—renew your will to defy lust’s pull.\n*Fun Fact:* Vespers (evening) reflects on the day."),
    ("Compline Peace", "Each clean day cuts traffickers’ cash. Note your progress."),
    ("Lauds Rally", "14M new victims annually—rally your spirit to end this."),
    ("Prime Triumph", "Virtue builds a shield—help another resist temptation today."),
    ("Terce Legacy", "2.5M trafficked yearly—your vigilance shields them. Pray to endure.\n*Fun Fact:* Terce also recalls the Spirit’s descent at Pentecost."),
    ("Sext Growth", "Each win cuts evil’s cash—grow strong for your family.")
]

# Temptation Deck (5 cards)
temptation_cards = [
    ("Temptation", "An urge strikes—resist it or lose a day’s progress."),
    ("Temptation", "Illicit content tempts you—say no or lose a day."),
    ("Temptation", "Fatigue clouds your will—rest well or lose a day."),
    ("Temptation", "Old habits whisper—replace them or lose a day."),
    ("Temptation", "A lie justifies relapse—reject it or lose a day.")
]

def wrap_text(text, width, font, font_size, c, centered=False):
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
    if centered:
        return [(line, c.stringWidth(line, font, font_size)) for line in lines]
    return lines

def draw_card(c, x, y, title, text):
    # Split text and fun fact if present
    if "\n*Fun Fact:*" in text:
        main_text, fun_fact = text.split("\n*Fun Fact:*", 1)
        fun_fact = "*Fun Fact:*" + fun_fact
    else:
        main_text, fun_fact = text, None
    
    # Centered title
    c.setFont(FONT_NAME, 12)
    c.setFillColorRGB(0, 0, 0)
    title_width = c.stringWidth(title, FONT_NAME, 12)
    c.drawString(x + (CARD_WIDTH - title_width) / 2, y + CARD_HEIGHT - 20, title)
    
    # Centered main text
    c.setFont(FONT_NAME, 10)
    wrapped_main = wrap_text(main_text, CARD_WIDTH - 20, FONT_NAME, 10, c, centered=True)
    for i, (line, line_width) in enumerate(wrapped_main[:3]):  # 3 lines for main text
        c.drawString(x + (CARD_WIDTH - line_width) / 2, y + CARD_HEIGHT - 40 - i * 12, line)
    
    # Fun fact at bottom if present
    if fun_fact:
        c.setFont(FONT_NAME, 8)
        wrapped_fact = wrap_text(fun_fact, CARD_WIDTH - 20, FONT_NAME, 8, c, centered=True)
        for j, (fact_line, fact_width) in enumerate(wrapped_fact[:2]):  # 2 lines for fun fact
            c.drawString(x + (CARD_WIDTH - fact_width) / 2, y + 10 + j * 10, fact_line)
    
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
    c.setFont(FONT_NAME, 9)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2 - 45, "Version 0.2")
    c.setFont(FONT_NAME, 11)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, 1.8 * inch, "Join the Quest – Get in Touch!")
    c.setFont(FONT_NAME, 9)
    c.setFillColorRGB(0, 0, 0)
    contact_text = [
        "Text/Voicemail: (219) 488-2689",
        "Email: info@zoseco.com",
        "Join our Discord: https://discord.com/invite/zZhtw9WVNv",
        "Support the cause: https://pay.zaprite.com/pl_4LxYdtCRsZ"
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
        "1. Setup: Print and cut out the Virtue Deck (18 cards), Temptation Deck (5 cards), and Stag Pouch sheet.",
        "2. Start: Shuffle both decks separately. Set your Stag Pouch with two slots: one for Virtue Cards, one for Temptation Cards.",
        "3. Daily Draw: Each day, draw 2 Virtue Cards from the Virtue Deck. Complete their tasks (pray, reflect, act).",
        "4. Temptation Test: On days 3, 6, and 9, draw 1 Temptation Card. Resist it (say 'Y') or lose a day’s progress (say 'N').",
        "5. Track Your Quest: For each successful day (tasks completed and Temptation resisted), place a Virtue Card in the Virtue Pouch. If you fail, place a Temptation Card in the Temptation Pouch.",
        "6. Win: After 9 days, if your Virtue Pouch has 9 cards and your Temptation Pouch has 0, increase Family Strength by 1 and claim your Virtuous Stag badge!",
        "Tips: Personalize your Stag Pouch or cards with drawings (e.g., antlers). Join our Discord to get an NFT when StagQuest launches online, and suggest new cards—share ideas and win points if approved! Support the cause at https://pay.zaprite.com/pl_4LxYdtCRsZ."
    ]
    y_pos = PAGE_HEIGHT - 1.5 * inch
    for line in instructions:
        wrapped_lines = wrap_text(line, PAGE_WIDTH - 2 * inch, FONT_NAME, 11, c)
        for wrapped_line in wrapped_lines:
            c.drawString(1 * inch, y_pos, wrapped_line)
            y_pos -= 15
        y_pos -= 5
    c.showPage()

    # Pages 3-5: Virtue Deck (18 cards, 4 per page, 5th Temptation on Page 5)
    for i, (title, text) in enumerate(virtue_cards):
        if i % 4 == 0 and i > 0:
            c.showPage()
        x = (i % 2) * (CARD_WIDTH + 20) + 1.75 * inch
        y = PAGE_HEIGHT - (((i % 4) // 2) + 1) * (CARD_HEIGHT + 20) - 1 * inch
        draw_card(c, x, y, title, text)
        # Add 5th Temptation Card to Page 5, positioned higher
        if i == 17:  # Last Virtue Card
            temptation_x = (PAGE_WIDTH - CARD_WIDTH) / 2
            temptation_y = y - CARD_HEIGHT - 0.5 * inch  # Above last Virtue Card
            if temptation_y < 1 * inch:  # If too low, adjust
                temptation_y = 1 * inch
            draw_card(c, temptation_x, temptation_y, temptation_cards[4][0], temptation_cards[4][1])
    c.showPage()

    # Page 6: Temptation Deck (first 4 cards)
    for i, (title, text) in enumerate(temptation_cards[:4]):
        x = (i % 2) * (CARD_WIDTH + 20) + 1.75 * inch
        y = PAGE_HEIGHT - (((i % 4) // 2) + 1) * (CARD_HEIGHT + 20) - 1 * inch
        draw_card(c, x, y, title, text)
    c.showPage()

    # Page 7: Stag Pouch and Badge
    c.setFont(FONT_NAME, 12)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1 * inch, "Stag Pouch")
    c.setFont(FONT_NAME, 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1.4 * inch, "Two Pouches: Virtue and Temptation")
    c.setFont(FONT_NAME, 9)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1.6 * inch, "Cut and sew dashed lines, leaving top open")
    
    # Draw two large pouches
    for i in range(2):
        x = 1.5 * inch + i * (3.5 * inch + 0.5 * inch)
        y = PAGE_HEIGHT - 3 * inch
        c.setDash(2, 2)
        c.rect(x, y, 3.5 * inch, 4 * inch)  # Larger pouch for multiple cards
        c.setDash()
        c.drawCentredString(x + 1.75 * inch, y + 4.25 * inch, ["Virtue Pouch", "Temptation Pouch"][i])
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 5.5 * inch, "Family Strength: ___")

    badge_width, badge_height = 3.5 * inch, 1.5 * inch
    badge_x, badge_y = (PAGE_WIDTH - badge_width) / 2, 2 * inch
    c.rect(badge_x, badge_y, badge_width, badge_height)
    c.setFont(FONT_NAME, 14)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 0.4 * inch, "Virtuous Stag Badge")
    c.setFont(FONT_NAME, 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 0.7 * inch, "Awarded to: ________________")
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 1.0 * inch, "Family Strength Gained!")
    c.showPage()

    c.save()

if __name__ == "__main__":
    create_pdf()
    print("PDF created as 'stagquest_card_game.pdf'!")