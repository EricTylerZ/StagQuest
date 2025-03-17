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

# Constants
MARGIN = 0.75 * inch
QR_SIZE = 1.5 * inch
POUCH_WIDTH = 3.5 * inch
POUCH_HEIGHT = 4 * inch
POUCH_SPACING = 0.5 * inch
CARD_WIDTH, CARD_HEIGHT = 2.5 * inch, 3.5 * inch
PAGE_WIDTH, PAGE_HEIGHT = letter
royal_turquoise = Color(0, 0.569, 0.545)

# Virtue Deck (22 cards now, no Temptation Cards)
virtue_cards = [
    ("Lauds Prayer", "40M are trafficked—addiction fuels this. Pray to break free today.\n*Fun Fact:* Lauds (dawn) praises the new day."),
    ("Prime Resolve", "Porn’s a $150B industry exploiting kids. Commit to purity now.\n*Fun Fact:* Prime (6am) starts the day’s work."),
    ("Terce Strength", "Temptation rewires your brain—fight it to reclaim your mind.\n*Fun Fact:* Terce (9am) marks Christ’s trial."),
    ("Sext Reflection", "76% of trafficking victims are under 18. Reflect on who you protect."),
    ("None Cut", "Porn’s progressive—each view deepens the trap. Pray to sever it.\n*Fun Fact:* None (3pm) recalls Christ’s crucifixion."),
    ("Vespers Stand", "9,000 illicit parlors thrive on demand. Stand against it today."),
    ("Compline Rest", "Addiction funds evil—every ‘no’ saves lives. Rest in this victory.\n*Fun Fact:* Compline (night) seals the day in peace."),
    ("Lauds Hope", "A child sold every 2 min—your virtue restores hope. Plan one good deed."),
    ("Prime Focus", "Dopamine spikes blind you—resist to heal your soul."),
    ("Terce Shield", "2.5M trafficked yearly—your fight shields them. Pray for strength.\n*Fun Fact:* Terce also recalls the Spirit’s descent."),
    ("Sext Vision", "Your eyes choose life or death—guard them to lead your family."),
    ("None Break", "Porn drives 42% of family trafficking. Break the cycle now."),
    ("Vespers Renewal", "Habits form in weeks—renew your will to defy lust’s pull.\n*Fun Fact:* Vespers (evening) reflects on the day."),
    ("Compline Peace", "Each clean day cuts traffickers’ cash. Note your progress."),
    ("Lauds Rally", "14M new victims annually—rally your spirit to end this."),
    ("Prime Triumph", "Virtue builds a shield—help another resist temptation today."),
    ("Terce Legacy", "Your vigilance leaves a legacy—pray to endure."),
    ("Sext Growth", "Each win cuts evil’s cash—grow strong for your family."),
    ("None Victory", "Resist today to weaken exploitation’s grip. Celebrate the win."),
    ("Vespers Guard", "Guard your heart—evil preys on weakness. Stand firm."),
    ("Compline Joy", "A pure day protects the vulnerable. Rest in joy."),
    ("Lauds Rise", "Rise each day to fight for the exploited—start with prayer.")
]

# Helper Functions
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

def create_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_file.name)
    return temp_file.name

def draw_qr_with_label(c, url, label, x, y):
    qr_file = create_qr_code(url)
    c.drawImage(qr_file, x, y, QR_SIZE, QR_SIZE)
    os.remove(qr_file)
    c.setFont(FONT_NAME, 10)
    label_width = c.stringWidth(label, FONT_NAME, 10)
    c.drawString(x + (QR_SIZE - label_width) / 2, y - 0.2 * inch, label)  # Label below QR

def draw_card(c, x, y, title, text):
    # Split text and fun fact
    parts = text.split("\n*Fun Fact:*", 1)
    main_text = parts[0].strip()
    fun_fact = "*Fun Fact:*" + parts[1].strip() if len(parts) > 1 else None
    
    # Draw title
    c.setFont(FONT_NAME, 12)
    c.setFillColorRGB(0, 0, 0)
    title_width = c.stringWidth(title, FONT_NAME, 12)
    c.drawString(x + (CARD_WIDTH - title_width) / 2, y + CARD_HEIGHT - 20, title)
    
    # Draw main text
    c.setFont(FONT_NAME, 10)
    wrapped_main = wrap_text(main_text, CARD_WIDTH - 20, FONT_NAME, 10, c, centered=True)
    main_lines = min(4, len(wrapped_main))  # Increased to 4 lines for more space
    main_y = y + CARD_HEIGHT - 40 - (main_lines - 1) * 12 / 2  # Center vertically
    for i in range(main_lines):
        line, line_width = wrapped_main[i]
        c.drawString(x + (CARD_WIDTH - line_width) / 2, main_y - i * 12, line)
    
    # Draw fun fact at bottom
    if fun_fact:
        c.setFont(FONT_NAME, 8)
        wrapped_fact = wrap_text(fun_fact, CARD_WIDTH - 20, FONT_NAME, 8, c, centered=True)
        fact_lines = min(2, len(wrapped_fact))
        fact_y = y + 10  # Start at bottom
        for j in range(fact_lines):
            fact_line, fact_width = wrapped_fact[j]
            c.drawString(x + (CARD_WIDTH - fact_width) / 2, fact_y + j * 10, fact_line)
    
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT)

# Page Functions
def draw_cover_page(c):
    c.setFont(FONT_NAME, 20)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2, "StagQuest: A Card Game")
    c.setFont(FONT_NAME, 12)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2 - 30, "A Zoseco Journey to Virtue")
    c.setFont(FONT_NAME, 9)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2 - 45, "Version 0.3")
    
    # QR Codes at bottom
    discord_x = MARGIN
    donation_x = PAGE_WIDTH - MARGIN - QR_SIZE
    qr_y = MARGIN + 0.2 * inch  # Adjusted for label below
    draw_qr_with_label(c, "https://discord.com/invite/zZhtw9WVNv", "Join Discord", discord_x, qr_y)
    draw_qr_with_label(c, "https://pay.zaprite.com/pl_4LxYdtCRsZ", "Support the Cause", donation_x, qr_y)

def draw_instructions_page(c):
    c.setFont(FONT_NAME, 16)
    c.setFillColor(royal_turquoise)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN, "StagQuest: How to Play")
    c.setFont(FONT_NAME, 11)
    c.setFillColorRGB(0, 0, 0)
    instructions = [
        "StagQuest is a 9-day solo or small-group card game to build virtue and resist addiction, inspired by a novena. Grow your Stag’s Family Strength with the Virtue Deck (daily draws).",
        "How to Play:",
        "1. Setup: Print and cut out the Virtue Deck (22 cards) and Stag Pouch sheet.",
        "2. Start: Shuffle the Virtue Deck. Set your Stag Pouch with two slots: Virtue and Temptation.",
        "3. Daily Draw: Each day, draw 1 Virtue Card. Complete its task (pray, reflect, act).",
        "4. Track Your Quest: If you succeed, place the Virtue Card in the Virtue Pouch. If you fail, place it in the Temptation Pouch.",
        "5. Win: After 9 days, if your Virtue Pouch has 9 cards and Temptation Pouch has 0, claim your Virtuous Stag badge!",
        "Tips: Personalize your Stag Pouch or cards with drawings (e.g., antlers). Join our Discord or support the cause via the QR codes!"
    ]
    y_pos = PAGE_HEIGHT - MARGIN - 20
    for line in instructions:
        wrapped_lines = wrap_text(line, PAGE_WIDTH - 2 * MARGIN, FONT_NAME, 11, c)
        for wrapped_line in wrapped_lines:
            c.drawString(MARGIN, y_pos, wrapped_line)
            y_pos -= 15
        y_pos -= 5
    
    # QR Codes at bottom
    discord_x = MARGIN
    donation_x = PAGE_WIDTH - MARGIN - QR_SIZE
    qr_y = MARGIN + 0.2 * inch
    draw_qr_with_label(c, "https://discord.com/invite/zZhtw9WVNv", "Join Discord", discord_x, qr_y)
    draw_qr_with_label(c, "https://pay.zaprite.com/pl_4LxYdtCRsZ", "Support the Cause", donation_x, qr_y)

def draw_virtue_cards_pages(c):
    for i, (title, text) in enumerate(virtue_cards):
        if i % 4 == 0 and i > 0:
            c.showPage()
        x = MARGIN + (i % 2) * (CARD_WIDTH + 20)
        y = PAGE_HEIGHT - MARGIN - ((i % 4) // 2 + 1) * (CARD_HEIGHT + 20)
        draw_card(c, x, y, title, text)
    c.showPage()

def draw_pouch_page(c):
    c.setFont(FONT_NAME, 12)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - MARGIN, "Stag Pouch")
    
    # Instructions
    c.setFont(FONT_NAME, 10)
    instructions = [
        "Cut along dashed lines.",
        "Sew/glue sides and bottom to form pouches.",
        "Leave top open for daily cards."
    ]
    y_pos = PAGE_HEIGHT - MARGIN - 20
    for line in instructions:
        c.drawCentredString(PAGE_WIDTH/2, y_pos, line)
        y_pos -= 12
    
    # Pouches
    pouch_y = y_pos - 20
    total_pouch_width = 2 * POUCH_WIDTH + POUCH_SPACING
    start_x = (PAGE_WIDTH - total_pouch_width) / 2
    for i in range(2):
        x = start_x + i * (POUCH_WIDTH + POUCH_SPACING)
        y = pouch_y - POUCH_HEIGHT
        c.setDash(2, 2)
        c.rect(x, y, POUCH_WIDTH, POUCH_HEIGHT)
        c.setDash()
        label = ["Virtue Pouch", "Temptation Pouch"][i]
        c.setFont(FONT_NAME, 10)
        label_width = c.stringWidth(label, FONT_NAME, 10)
        c.drawString(x + (POUCH_WIDTH - label_width) / 2, y + POUCH_HEIGHT + 5, label)
    
    # Family Strength
    c.setFont(FONT_NAME, 10)
    c.drawCentredString(PAGE_WIDTH/2, y - 20, "Family Strength: ___")
    
    # Badge
    badge_width, badge_height = 3.5 * inch, 1.5 * inch
    badge_y = y - 40 - badge_height
    c.rect((PAGE_WIDTH - badge_width) / 2, badge_y, badge_width, badge_height)
    c.setFont(FONT_NAME, 14)
    c.setFillColor(royal_turquoise)
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 0.4 * inch, "Virtuous Stag Badge")
    c.setFont(FONT_NAME, 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 0.7 * inch, "Awarded to: ________________")
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 1.0 * inch, "Family Strength Gained!")
    
    # QR Codes at bottom
    discord_x = MARGIN
    donation_x = PAGE_WIDTH - MARGIN - QR_SIZE
    qr_y = MARGIN + 0.2 * inch
    draw_qr_with_label(c, "https://discord.com/invite/zZhtw9WVNv", "Join Discord", discord_x, qr_y)
    draw_qr_with_label(c, "https://pay.zaprite.com/pl_4LxYdtCRsZ", "Support the Cause", donation_x, qr_y)

def create_pdf():
    c = canvas.Canvas("stagquest_card_game.pdf", pagesize=letter)
    draw_cover_page(c)
    c.showPage()
    draw_instructions_page(c)
    c.showPage()
    draw_virtue_cards_pages(c)
    draw_pouch_page(c)
    c.save()

if __name__ == "__main__":
    create_pdf()
    print("PDF created as 'stagquest_card_game.pdf'!")