import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
import io
import numpy as np

def remove_image_background(image_file):
    try:
        image_file.seek(0)
        input_image = image_file.read()
        output_image = remove(input_image)
        return Image.open(io.BytesIO(output_image))
    except Exception as e:
        st.error(f"Error removing background: {e}")
        return None

def add_text_behind_image(image, text, font_name, font_size, font_color):
    try:
        # Ensure the image has an alpha channel
        image = image.convert("RGBA")

        # Create a black background with the same size as the image
        background_layer = Image.new("RGBA", image.size, (0, 0, 0, 255))  # Black background
        text_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))  # Transparent text layer
        draw = ImageDraw.Draw(text_layer)

        # Load the specified font (with fallback to default)
        try:
            font = ImageFont.truetype(font_name, font_size)
        except:
            font = ImageFont.load_default()

        # Calculate text bounding box
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]

        # Calculate position at the top (5% padding from the top)
        x = (image.size[0] - text_width) // 2
        y = image.size[1] // 15  # 5% from the top

        # Draw text on the transparent text layer
        draw.text((x, y), text, fill=font_color, font=font)

        # Merge the text layer with the background layer
        background_with_text = Image.alpha_composite(background_layer, text_layer)

        # Composite the original image on top of the background
        final_image = Image.alpha_composite(background_with_text, image)
        return final_image
    except Exception as e:
        st.error(f"Error adding text: {e}")
        return None


# Streamlit App
st.title("Text-Behind-Image Editor")
st.write("Upload an image, remove its background, and add text behind it!")

# File upload
uploaded_file = st.file_uploader("Upload your image", type=["jpg", "jpeg", "png"])
text_input = st.text_input("Enter text to display behind the image", "Your Text Here")

# Font customization
font_name = st.selectbox("Select Font", ["arial.ttf", "times.ttf", "georgia.ttf"])
font_size = st.slider("Select Font Size", min_value=10, max_value=200, value=100)
font_color = st.color_picker("Select Font Color", "#FFFFFF")

if uploaded_file is not None:
    try:
        # Display original image
        original_image = Image.open(uploaded_file)
        st.image(original_image, caption="Original Image", use_column_width=True)

        # Remove background
        st.write("Removing background...")
        bg_removed_image = remove_image_background(uploaded_file)

        if bg_removed_image:
            st.image(bg_removed_image, caption="Background Removed", use_column_width=True)

            # Add text behind the image
            st.write("Adding text behind the image...")
            final_image = add_text_behind_image(bg_removed_image, text_input, font_name, font_size, tuple(int(font_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,))

            if final_image:
                st.image(final_image, caption="Final Image", use_column_width=True)

                # Provide download option
                final_image_bytes = io.BytesIO()
                final_image.save(final_image_bytes, format="PNG")
                final_image_bytes.seek(0)
                st.download_button(
                    label="Download Image",
                    data=final_image_bytes,
                    file_name="text_behind_image.png",
                    mime="image/png"
                )
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error(str(e))