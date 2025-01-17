window.onload = function ()
{
    const convertButton = document.getElementById('convert-button');
    const inputText = document.getElementById('input-text');
    const outputText = document.getElementById('output-text');
    const settingsForm = document.getElementById('settings-form');

    convertButton.addEventListener('click', () =>
    {
        const inputData = {
            text: inputText.value,
            width: document.getElementById('width').value,
            monospace: document.getElementById('monospace').checked,
            inverted: document.getElementById('inverted').checked,
            greyscaleMode: document.getElementById('greyscale-mode').value,
            fontName: document.getElementById('font-name').value,
        };

        fetch('/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inputData),
        })
            .then(response => response.json())
            .then(data =>
            {
                outputText.value = data.brailleText;
            })
            .catch(error => console.error(error));
    });
};