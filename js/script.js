const origTextarea = document.getElementById('orig');
const pajTextarea = document.getElementById('paj');
const thoughtsTextarea = document.getElementById('thoughs');
const translateButton = document.getElementById('translate-button');

translateButton.addEventListener('click', async () => {
    const text = origTextarea.value.trim();
    if (!text) return;

    translateButton.disabled = true;
    translateButton.textContent = 'Translating...';
    pajTextarea.value = '';
    thoughtsTextarea.value = '';

    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();

        pajTextarea.value = data.translation || 'Error translating';
        thoughtsTextarea.value = data.raw || '';

    } catch (error) {
        pajTextarea.value = 'Error: Could not connect to server';
        thoughtsTextarea.value = error.toString();
    }

    translateButton.disabled = false;
    translateButton.textContent = 'Translate';
});

// Allow Ctrl+Enter to translate
origTextarea.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        translateButton.click();
    }
});