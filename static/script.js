settings = {
    "width": 31,
    "monospace": true,
    "inverted": false,
    "greyscale_mode": "luminance",
    "font_name": "arialbd.ttf",
    "font_size": 500
};
window.onload = async function ()
{
    const inputText = document.getElementById('input-text');
    const getFontsButton = document.getElementById('get-fonts-button');

    inputText.addEventListener('input', async () =>
    {
        updateOutput();
    });

    getFontsButton.addEventListener('click', async () =>
    {
        await updateFontList();
    });


    // add event listeners to the settings elements
    document.querySelectorAll('.setting').forEach(setting =>
    {
        if (setting.type === 'checkbox')
        {
            setting.addEventListener('change', updateOutput);
        } else
        {
            setting.addEventListener('input', updateOutput);
        }
    });

};

async function updateFontList()
{
    // get font list
    const fontSelect = document.getElementById('font-name');
    const fontList = await window.queryLocalFonts();
    // delete first child and populate with new options
    fontSelect.removeChild(fontSelect.firstChild);
    fontList.forEach(font => fontSelect.innerHTML += `<option value="${font.fullName}">${font.fullName}</option>`);
}

async function updateOutput()
{
    const outputText = document.getElementById('output-text');
    const inputText = document.getElementById('input-text');

    // get settings data
    const inputData = {
        text: inputText.value,
        width: +document.getElementById('width').value,
        monospace: document.getElementById('monospace').checked,
        inverted: document.getElementById('inverted').checked,
        greyscaleMode: document.getElementById('greyscale-mode').value,
        fontName: document.getElementById('font-name').value,
    };

    // update settings
    settings.width = inputData.width;
    settings.monospace = inputData.monospace;
    settings.inverted = inputData.inverted;
    settings.greyscale_mode = inputData.greyscaleMode;
    settings.font_name = inputData.fontName;

    // update output
    if (inputData.text === '')
    {
        outputText.value = '';
        return;
    }
    outputText.value = await textToBraille(inputData.text, settings.font_name, settings.font_size);
}


function createImageCanvas(image)
{
    return new Promise((resolve, reject) =>
    {
        const canvas = document.createElement('canvas');

        let width = image.width;
        let height = image.height;
        if (image.width != (settings.width * 2))
        {
            width = settings.width * 2;
            height = width * image.height / image.width;
        }
        if (settings.width === 30 || settings.width === 31)
        {
            height = 12;
        }

        //nearest multiple
        canvas.width = width - (width % 2);
        canvas.height = height - (height % 4);

        ctx = canvas.getContext("2d");
        ctx.fillStyle = "#FFFFFF"; //get rid of alpha
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.mozImageSmoothingEnabled = false;
        ctx.webkitImageSmoothingEnabled = false;
        ctx.msImageSmoothingEnabled = false;
        ctx.imageSmoothingEnabled = false;

        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
        resolve(canvas);
    });
}

function pixelsToCharacter(pixels_lo_hi)
{ //expects an array of 8 bools
    //Codepoint reference - https://www.ssec.wisc.edu/~tomw/java/unicode.html#x2800
    const shift_values = [0, 1, 2, 6, 3, 4, 5, 7]; //correspond to dots in braille chars compared to the given array
    let codepoint_offset = 0;
    for (const i in pixels_lo_hi)
    {
        codepoint_offset += (+pixels_lo_hi[i]) << shift_values[i];
    }

    if (codepoint_offset === 0 && settings.monospace === false)
    { //pixels were all blank
        codepoint_offset = 4; //0x2800 is a blank braille char, 0x2804 is a single dot
    }
    return String.fromCharCode(0x2800 + codepoint_offset);
}

function toGreyscale(r, g, b)
{
    switch (settings.greyscale_mode)
    {
        case "luminance":
            return (0.22 * r) + (0.72 * g) + (0.06 * b);

        case "lightness":
            return (Math.max(r, g, b) + Math.min(r, g, b)) / 2;

        case "average":
            return (r + g + b) / 3;

        case "value":
            return Math.max(r, g, b);

        default:
            console.error("Greyscale mode is not valid");
            return 0;
    }
}

async function imageToBraille(canvas)
{
    const newCanvas = await createImageCanvas(canvas)
    const ctx = newCanvas.getContext("2d");
    const width = newCanvas.width;
    const height = newCanvas.height;

    let image_data = [];
    image_data = new Uint8Array(ctx.getImageData(0, 0, width, height).data.buffer);

    let output = "";

    for (let imgy = 0; imgy < height; imgy += 4)
    {
        for (let imgx = 0; imgx < width; imgx += 2)
        {
            const braille_info = [0, 0, 0, 0, 0, 0, 0, 0];
            let dot_index = 0;
            for (let x = 0; x < 2; x++)
            {
                for (let y = 0; y < 4; y++)
                {
                    const index = (imgx + x + width * (imgy + y)) * 4;
                    const pixel_data = image_data.slice(index, index + 4); //ctx.getImageData(imgx+x,imgy+y,1,1).data
                    if (pixel_data[3] >= 128)
                    { //account for alpha
                        const grey = toGreyscale(pixel_data[0], pixel_data[1], pixel_data[2]);
                        if (settings.inverted)
                        {
                            if (grey >= 128) braille_info[dot_index] = 1;
                        } else
                        {
                            if (grey <= 128) braille_info[dot_index] = 1;
                        }
                    }
                    dot_index++;
                }
            }
            output += pixelsToCharacter(braille_info);
        }
        output += "\n";
    }

    return output;
}

function textToImage(text, font, fontSize)
{
    return new Promise((resolve, reject) =>
    {
        try
        {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            // calculate exact dimensions of the text
            ctx.font = `${fontSize}px ${font}`;
            const textMetrics = ctx.measureText(text);
            const textWidth = Math.ceil(textMetrics.actualBoundingBoxLeft + textMetrics.actualBoundingBoxRight);
            const textHeight = Math.ceil(textMetrics.actualBoundingBoxAscent - textMetrics.actualBoundingBoxDescent);

            // resize the canvas to match the text dimensions
            canvas.width = textWidth;
            canvas.height = textHeight;

            // white background
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // draw the text properly aligned
            ctx.font = `${fontSize}px ${font}`;
            ctx.textBaseline = 'alphabetic';
            ctx.fillStyle = 'black';
            ctx.fillText(text, textMetrics.actualBoundingBoxLeft, textHeight);

            resolve(canvas);
        } catch (error)
        {
            reject(error);
        }
    });
}

async function textToBraille(text, font, fontSize)
{
    const image = await textToImage(text, font, fontSize);
    return await imageToBraille(image);
}