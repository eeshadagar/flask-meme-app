from flask import Flask, render_template, request, send_file, redirect, url_for
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import random

app = Flask(__name__)
def get_random_meme():
    try:
        response = requests.get("https://api.imgflip.com/get_memes")
        data = response.json()  # Convert response to JSON
        print("API Response:", data)  # Debugging: Print full API response

        if data.get("success"):  # Ensure response is successful
            memes = data.get("data", {}).get("memes", [])  # Avoid KeyError
            if memes:
                return random.choice(memes)["url"]

        print("Error: No memes found in response.")
        return None

    except requests.exceptions.RequestException as e:
        print("Error fetching meme:", e)
        return None

# Function to overlay text on meme
def generate_meme(image_url, top_text, bottom_text):
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content))

    draw = ImageDraw.Draw(img)

    # Load font (ensure "impact.ttf" is available in your project directory)
    try:
        font = ImageFont.truetype("impact.ttf", size=int(img.width / 10))  # Adjust size dynamically
    except:
        font = ImageFont.truetype("arial.ttf", size=int(img.width / 10))

    # Function to center text
    def draw_text(draw, text, position):
        """Draws text with shadow for better visibility"""
        text_width, text_height = draw.textsize(text, font=font)
        x = (img.width - text_width) / 2  # Center text horizontally
        y = position
        # Shadow effect
        draw.text((x+2, y+2), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")

    # Draw top text
    if top_text:
        draw_text(draw, top_text.upper(), 10)  # Position at top

    # Draw bottom text
    if bottom_text:
        draw_text(draw, bottom_text.upper(), img.height - text_height - 10)  # Position at bottom

    # Save meme to BytesIO
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

@app.route("/get_meme")
def get_meme():
    meme_url = get_random_meme()
    if meme_url:
        return {"success": True, "meme_url": meme_url}
    return {"success": False, "error": "Failed to fetch meme"}, 500

@app.route("/", methods=["GET", "POST"])
def index():
    meme_url = get_random_meme()  # Get a new random meme

    if request.method == "POST":
        action = request.form.get("action")

        if action == "Generate":
            return redirect(url_for("index"))  # Refresh page to get a new meme

        top_text = request.form.get("topText", "")
        bottom_text = request.form.get("bottomText", "")
        image_url = request.form.get("imageURL", meme_url)

        # Generate meme with text
        meme_img = generate_meme(image_url, top_text, bottom_text)
        return send_file(meme_img, mimetype="image/png", as_attachment=True, download_name="meme.png")

    return render_template("index.html", meme_url=meme_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
