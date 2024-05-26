document.addEventListener('DOMContentLoaded', () => {
    const textForm = document.getElementById('text-form');
    const output = document.getElementById('output');

    textForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const action = event.submitter.getAttribute('data-action');
        processText(action);
    });

    async function processText(action) {
        const content = document.querySelector('textarea[name="content"]').value;

        output.innerHTML = 'Processing...';

        const response = await fetch(`/api/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ contents: content })
        });

        const result = await response.json();

        if (result.error) {
            output.innerHTML = `<div class="error">Error: ${result.error}</div>`;
        } else {
            displayResult(result);
        }
    }

    function displayResult(result) {
        const output = document.getElementById('output');
        let html = '<div class="result">';
        
        if (result.errors && result.errors.length > 0) {
            html += '<h3>Errors:</h3><ul>';
            result.errors.forEach(error => {
                html += `<li>${error}</li>`;
            });
            html += '</ul>';
        }
        
        if (result.corrected_text) {
            html += `<h3>Corrected Text:</h3><p>${result.corrected_text}</p>`;
        }
        
        html += '</div>';
        
        output.innerHTML = html;
    }
});
