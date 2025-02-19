document.getElementById('myForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Réinitialiser les messages d'erreur
    clearErrors();

    // Récupération des valeurs
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const url = document.getElementById('url').value;
    const prompt = document.getElementById('prompt').value;

    // Validation
    let isValid = true;

    if (!validateEmail(email)) {
        showError('emailError', 'Veuillez entrer un email valide');
        isValid = false;
    }

    if (!validatePhone(phone)) {
        showError('phoneError', 'Le numéro doit contenir 10 chiffres');
        isValid = false;
    }

    if (!validateUrl(url)) {
        showError('urlError', 'Veuillez entrer une URL valide');
        isValid = false;
    }

    if (prompt.trim() === '') {
        showError('promptError', 'Veuillez remplir ce champ');
        isValid = false;
    }

    if (isValid) {
        // Envoi des données (à adapter selon vos besoins)
        const formData = {
            email,
            phone,
            url,
            prompt
        };
        
        console.log('Données soumises:', formData);
        alert('Formulaire soumis avec succès !');
        this.reset();
    }
});

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^\d{10}$/;
    return re.test(phone);
}

function validateUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function clearErrors() {
    const errors = document.getElementsByClassName('error-message');
    for (let error of errors) {
        error.textContent = '';
        error.style.display = 'none';
    }
}