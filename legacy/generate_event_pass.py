from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
from websocket_comfyUI import get_custom_avatar, get_random_avatar


def get_pillar_template(pillar):
    script_dir = os.path.dirname(__file__)
    template_base_path = os.path.join(script_dir, "Templates\\")
    template_path = template_base_path + f"{pillar}_TEMPLATE.png"
    
    return template_path

    # mapPillarToTemplate = {'ASD': template_base_path+"ASD_TEMPLATE.png", 'EPD': template_base_path+"EPD_TEMPLATE.png", 'ESD': template_base_path+"ESD_TEMPLATE.png", 'DAI': template_base_path+"DAI_TEMPLATE.png", 'CSD': template_base_path+"CSD_TEMPLATE.png", 'SUTD': template_base_path+"SUTD_TEMPLATE.png"}

def create_event_pass(pillar, chatID, name=None, customAvatar = False, avatar_type="Male", personal_interest=None):
    template_path = get_pillar_template(pillar)
    if customAvatar:
        avatar_name, tagline, avatar_path = get_custom_avatar(avatar_type, personal_interest)
    else:
        avatar_name, tagline, avatar_path = get_random_avatar(avatar_type, personal_interest)

    # Load the template and avatar
    try:
        template = Image.open(template_path)
        avatar = Image.open(avatar_path)
    except IOError as e:
        print(f"Error loading images: {e}")
        return None
    
    # Create new pass
    pass_width, pass_height = template.size
    event_pass = Image.new('RGB', (pass_width, pass_height), 'white')
    event_pass.paste(template, (0, 0))

    # Resize avatar
    avatar_resized = avatar.resize((420, 420))
    
    # Create circular mask
    mask = Image.new('L', avatar_resized.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, mask.size[0], mask.size[1]), fill=255)
    
    # Apply mask to avatar
    output = Image.new('RGBA', avatar_resized.size, (0, 0, 0, 0))
    output.paste(avatar_resized, (0, 0))
    output.putalpha(mask)

    # Paste onto event pass
    event_pass.paste(output, (330, 666), output)

    # Add text elements
    draw = ImageDraw.Draw(event_pass)

    # Load a font
    try:
        name_font = ImageFont.truetype("Garet-Heavy.ttf", 45)
        avatar_font = ImageFont.truetype("Garet-Heavy.ttf", 35)
        catchphrase_font = ImageFont.truetype("Garet-Book.ttf", 42)
    except IOError:
        print("Font file not found. Using default font.")
        font = ImageFont.load_default(50)
        print('font',font)
    
    # Function to draw centered text
    def draw_right_centered_text(draw, text, font, y, image_width):
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = ((image_width - text_width) / 2 ) #+ 240
        text_position = (x, y)

        # Draw the text
        draw.text(text_position, text, fill="black", font=font)

    if (name==None):
        name = "Alex Tan"

    # Add centered text to event pass
    draw_right_centered_text(draw, name, name_font, 1132, pass_width)
    draw_right_centered_text(draw, avatar_name, avatar_font, 1299, pass_width)
    draw_right_centered_text(draw, f'"{tagline}"', catchphrase_font, 1369, pass_width)


    # Generate QR code
    qr_data = "SUTD_OH2025_" + chatID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill='black', back_color='white')

    # Resize QR code
    qr_img_resized = qr_img.resize((400, 400))

    # Calculate position to center the QR code
    qr_x = (pass_width - qr_img_resized.width) // 2  # Adjust the x position as needed
    qr_y = 1517 #(pass_height - qr_img_resized.height) // 2  # Adjust the y position as needed

    # Paste QR code onto event pass
    event_pass.paste(qr_img_resized, (qr_x, qr_y))
    script_dir = os.path.dirname(__file__)
    output_path = os.path.join(script_dir, f"FinalPass\\{chatID}_event_pass.png")

    try:
        event_pass.save(output_path)
        print(f"Event pass saved to {output_path}")
    except IOError as e:
        print(f"Error saving event pass: {e}")
        return None

    return output_path, event_pass
    

pillar = input("Enter pillar: ")
chatID = input("Enter chatid: ")
output_path, event_pass = create_event_pass(pillar, chatID, name="Alex Tan", customAvatar = True, avatar_type="Panda", personal_interest="computer scientist")
print(output_path)
if event_pass:
    event_pass.show()
else:
    print("Failed to create event pass.")