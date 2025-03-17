from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import os
import tempfile

# Register Century Schoolbook fonts from C:\Windows\Fonts
try:
    pdfmetrics.registerFont(TTFont("CenturySchoolbook", "C:/Windows/Fonts/CENSCBK.TTF"))  # Regular
    # Optional: Register variants if you want bold/italic support later
    # pdfmetrics.registerFont(TTFont("CenturySchoolbook-Bold", "C:/Windows/Fonts/CENSCBKB.TTF"))  # Bold (adjust filename if different)
    # pdfmetrics.registerFont(TTFont("CenturySchoolbook-Italic", "C:/Windows/Fonts/CENSCBKI.TTF"))  # Italic (adjust filename)
    # pdfmetrics.registerFont(TTFont("CenturySchoolbook-BoldItalic", "C:/Windows/Fonts/CENSCBKBI.TTF"))  # Bold Italic (adjust filename)
    FONT_NAME = "CenturySchoolbook"
    print("Century Schoolbook font registered successfully.")
except Exception as e:
    print(f"Failed to register Century Schoolbook: {e}. Falling back to Helvetica.")
    FONT_NAME = "Helvetica"

# Card dimensions (2.5" x 3.5")
CARD_WIDTH, CARD_HEIGHT = 2.5 * inch, 3.5 * inch
PAGE_WIDTH, PAGE_HEIGHT = letter

# Define Stag Green (#2E8B57, a forest-inspired color)
stag_green = Color(0.18, 0.545, 0.341)

# Card content (derived from your novena prompts and new temptations)
virtue_cards = [
    ("Day 1 Lauds", "40M trafficking victims - pray to start your fight today!"),
    ("Day 1 Sext", "Porn drives demand - commit to saying no now."),
    ("Day 1 Compline", "Rest in victory. Were you porn-free today? Y/N"),
    ("Day 2 Prime", "Purity is power - stay strong this morning."),
    ("Day 2 None", "Every 'no' weakens exploitation - reflect on this."),
    ("Day 3 Terce", "Porn’s progressive - pray to cut it off today."),
    ("Day 4 Sext", "Addiction funds evil - starve it with your choice."),
    ("Day 5 Prime", "Neural pathways rewiring - affirm your progress."),
    ("Day 6 Sext", "Your eyes hold power - choose life over death."),
    ("Day 7 Terce", "Brain chemistry normalizing - note one change."),
    ("Day 8 Sext", "Community shield strengthening - help another today."),
    ("Day 9 Vespers", "Celebrate then sharpen your sword for tomorrow.")
]
temptation_cards = [
    ("Temptation", "An urge strikes. Resist it or lose a day’s progress."),
    ("Temptation", "A friend shares illicit content. Say no or lose a day."),
    ("Temptation", "Fatigue weakens your will. Rest well or lose a day."),
    ("Temptation", "Old habits call. Replace them or lose a day."),
    ("Temptation", "A lie justifies relapse. Reject it or lose a day.")
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
    c.setFont(FONT_NAME, 10)
    wrapped_lines = wrap_text(text, CARD_WIDTH - 20, FONT_NAME, 10, c)
    for i, line in enumerate(wrapped_lines[:4]):
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
    c.setFillColor(stag_green)
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
    c.setFillColor(stag_green)
    c.drawString(1 * inch, PAGE_HEIGHT - 1 * inch, "StagQuest: How to Play")
    c.setFont(FONT_NAME, 11)
    c.setFillColorRGB(0, 0, 0)
    instructions = [
        "StagQuest is a solo or small-group card game to build virtue and resist temptation over 9 days. Inspired by a novena, you’ll grow your Stag’s Family Strength by completing daily Virtue Cards and overcoming Temptation Cards. Perfect for adults seeking to break free from pornography and become family leaders.",
        "How to Play:",
        "1. Setup: Print this PDF, cut out the Virtue Cards, Temptation Cards, and Stag Tracker.",
        "2. Start: Shuffle the Virtue and Temptation decks. Set your Stag Tracker to Family Strength 0.",
        "3. Daily Draw: Each 'day' (turn), draw a Virtue Card and complete its task (pray, reflect, act).",
        "4. Temptation Test: Every 3rd day (turns 3, 6, 9), draw a Temptation Card. Resist it (say 'Y') or lose a day’s progress (say 'N').",
        "5. Track Progress: Mark successful days on your Stag Tracker. Personalize it with drawings (e.g., antlers).",
        "6. Win: After 9 days, if you have 9 successful days, increase Family Strength by 1 and claim your Virtuous Stag badge!"
    ]
    y_pos = PAGE_HEIGHT - 1.5 * inch
    for line in instructions:
        wrapped_lines = wrap_text(line, PAGE_WIDTH - 2 * inch, FONT_NAME, 11, c)
        for wrapped_line in wrapped_lines:
            c.drawString(1 * inch, y_pos, wrapped_line)
            y_pos -= 15
        y_pos -= 5
    c.showPage()

    # Page 3-4: Virtue Cards
    for i, (title, text) in enumerate(virtue_cards):
        page = 2 + (i // 4)
        if i % 4 == 0 and i > 0:
            c.showPage()
        x = (i % 2) * (CARD_WIDTH + 20) + 1.75 * inch
        y = PAGE_HEIGHT - ((i % 4 // 2) + 1) * (CARD_HEIGHT + 20) - 1 * inch
        draw_card(c, x, y, title, text)
    c.showPage()

    # Page 5: Temptation Cards
    for i, (type, text) in enumerate(temptation_cards):
        x = (i % 2) * (CARD_WIDTH + 20) + 1.75 * inch
        y = PAGE_HEIGHT - ((i % 4 // 2) + 1) * (CARD_HEIGHT + 20) - 1 * inch
        draw_card(c, x, y, type, text)
    c.showPage()

    # Page 6: Stag Tracker and Badge
    c.setFont(FONT_NAME, 12)
    c.setFillColor(stag_green)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1 * inch, "Stag Tracker")
    c.setFont(FONT_NAME, 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT - 1.4 * inch, "Goal: 9 Successful Days")
    c.rect(2 * inch, PAGE_HEIGHT - 2 * inch, 4.5 * inch, 0.5 * inch)
    c.setFont(FONT_NAME, 9)
    for i in range(9):
        c.drawString(2.1 * inch + (i * 0.45 * inch), PAGE_HEIGHT - 1.8 * inch, f"Day {i+1}: ___")

    badge_width, badge_height = 3.5 * inch, 1.5 * inch
    badge_x, badge_y = (PAGE_WIDTH - badge_width) / 2, 6 * inch
    c.rect(badge_x, badge_y, badge_width, badge_height)
    c.setFont(FONT_NAME, 14)
    c.setFillColor(stag_green)
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 0.4 * inch, "Virtuous Stag Badge")
    c.setFont(FONT_NAME, 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 0.7 * inch, "Awarded to: ________________")
    c.drawCentredString(PAGE_WIDTH/2, badge_y + badge_height - 1.0 * inch, "Family Strength Gained!")

    c.setFont(FONT_NAME, 11)
    c.setFillColor(stag_green)
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