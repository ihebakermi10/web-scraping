document.getElementById('myForm').addEventListener('submit', function(e) {
  e.preventDefault();
  
  clearErrors();
  const statusMessage = document.getElementById('statusMessage');
  statusMessage.textContent = 'Veuillez patienter...';
  
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value; 
  const url = document.getElementById('url').value;
  const mailAgent = document.getElementById('mailAgent').checked;
  
  let isValid = true;
  if (!validateEmail(email)) {
    showError('emailError', 'Veuillez entrer un email valide');
    isValid = false;
  }
  if (!validateUrl(url)) {
    showError('urlError', 'Veuillez entrer une URL valide');
    isValid = false;
  }
  
  if (isValid) {
    const formData = {
      email: email,
      numero: phone,   
      url: url,
      mail_agent: mailAgent  
    };
  
    fetch("http://127.0.0.1:8080/submit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(formData)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Erreur HTTP ' + response.status + ' : ' + response.statusText);
      }
      return response.json();
    })
    .then(data => {
      console.log('Réponse du backend:', data);
      statusMessage.textContent = 'Formulaire soumis avec succès!';
      alert('Formulaire soumis avec succès !');
      document.getElementById('myForm').reset();
    })
    .catch(error => {
      console.error('Erreur:', error);
      statusMessage.textContent = 'Une erreur est survenue lors de la soumission du formulaire.';
      alert('Erreur : ' + error.message);
    });
  } else {
    statusMessage.textContent = '';
  }
});

function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
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
