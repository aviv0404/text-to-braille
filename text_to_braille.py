from PIL import Image, ImageDraw, ImageFont
import matplotlib.font_manager as fm
import numpy as np

settings = {
    "width": 30,
    "dithering": False,
    "monospace": True,
    "inverted": False,
    "greyscale_mode": "luminance",  # possible values: luminance, lightness, average, value
    "font_name": "arialbi.ttf",
}


def text_to_image(
    text, output_file="text_image.png", font_name="DUBAI-BOLD.TTF", text_size=500
):
    # Load a font and set the size
    # font = ImageFont.load_default()  # Default font
    font = ImageFont.truetype(font_name, size=text_size)  # Use this for custom fonts

    # Create a temporary draw object to calculate text size using textbbox
    temp_img = Image.new("RGB", (0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    text_bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width, text_height = (
        text_bbox[2] - text_bbox[0],
        text_bbox[3] - text_bbox[1],
    )

    # Create the image with the exact dimensions of the text
    img = Image.new("RGB", (text_width, text_height), color="white")
    draw = ImageDraw.Draw(img)

    # Draw the text
    draw.text((0, -text_bbox[1]), text, fill="black", font=font)

    return img


def create_image_canvas(image: Image):
    canvas = Image.new("RGBA", (1, 1), (255, 255, 255, 255))

    width, height = image.size
    if width != (settings["width"] * 2):
        width = settings["width"] * 2
        height = int(width * image.height / image.width)
        if width == 62 or width == 60:
            height = 12

    # nearest multiple
    canvas = Image.new(
        "RGBA", (width - (width % 2), height - (height % 4)), (255, 255, 255, 255)
    )

    ctx = canvas.load()
    for x in range(canvas.width):
        for y in range(canvas.height):
            ctx[x, y] = (255, 255, 255, 255)  # get rid of alpha

    image = image.resize((canvas.width, canvas.height), Image.Resampling.NEAREST)
    canvas.paste(image, (0, 0))

    return canvas


def pixels_to_character(pixels_lo_hi):  # expects a list of 8 bools
    shift_values = [
        0,
        1,
        2,
        6,
        3,
        4,
        5,
        7,
    ]  # correspond to dots in braille chars compared to the given array
    codepoint_offset = 0
    for i in range(len(pixels_lo_hi)):
        codepoint_offset += int(pixels_lo_hi[i]) << shift_values[i]

    if codepoint_offset == 0 and not settings["monospace"]:  # pixels were all blank
        codepoint_offset = 4  # 0x2800 is a blank braille char, 0x2804 is a single dot
    return chr(0x2800 + codepoint_offset)


def to_greyscale(r, g, b):
    if settings["greyscale_mode"] == "luminance":
        return (0.22 * r) + (0.72 * g) + (0.06 * b)

    elif settings["greyscale_mode"] == "lightness":
        rgb_array = np.array([r, g, b])
        return np.mean(np.clip(rgb_array, 0, 255))

    elif settings["greyscale_mode"] == "average":
        rgb_array = np.array([r, g, b])
        return np.mean(np.clip(rgb_array, 0, 255))

    elif settings["greyscale_mode"] == "value":
        return max(r, g, b)

    else:
        print("Greyscale mode is not valid")
        return 0


def image_to_braille(image: Image):
    canvas = create_image_canvas(image)
    width, height = canvas.size
    image_data = np.array(canvas)

    output = ""

    for y in range(0, height, 4):
        for x in range(0, width, 2):
            braille_info = [0, 0, 0, 0, 0, 0, 0, 0]
            dot_index = 0
            for dx in range(2):
                for dy in range(4):
                    pixel = image_data[y + dy, x + dx]
                    if pixel[3] >= 128:  # account for alpha
                        grey = to_greyscale(pixel[0], pixel[1], pixel[2])
                        if settings["inverted"]:
                            if grey >= 128:
                                braille_info[dot_index] = 1
                        else:
                            if grey <= 128:
                                braille_info[dot_index] = 1
                        dot_index += 1
            output += pixels_to_character(braille_info)
        output += "\n"

    return output


def text_to_braille(text, font_name="arialbd.ttf", text_size=500):
    image = text_to_image(text, font_name=font_name, text_size=text_size)
    return image_to_braille(image)
