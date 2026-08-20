document.getElementById('year').textContent = new Date().getFullYear();

// Mobile nav toggle
const menuBtn = document.getElementById('menuBtn');
const navLinks = document.getElementById('navLinks');
menuBtn.addEventListener('click', () => {
  const isOpen = navLinks.classList.toggle('open');
  menuBtn.setAttribute('aria-expanded', isOpen);
});
navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  navLinks.classList.remove('open');
  menuBtn.setAttribute('aria-expanded', 'false');
}));

// ---------------------------------------------------------------------
// Photo uploads — sent to the server (POST /upload/<photo_id>), which
// resizes/compresses and saves them to disk. Works from any device,
// including a phone camera or photo library, and is visible to every
// visitor once uploaded (unlike the old browser-only localStorage version).
// ---------------------------------------------------------------------
document.querySelectorAll('[data-photo-id]').forEach(el => {
  const id = el.dataset.photoId;
  const input = el.querySelector('.photo-input');
  const label = el.querySelector('.photo-add-label');
  if (!input) return;

  const showMessage = (text, isError) => {
    if (!label) return;
    const original = label.textContent;
    label.textContent = text;
    label.style.opacity = '1';
    label.style.color = isError ? '#f28b8b' : '';
    setTimeout(() => {
      label.textContent = original;
      label.style.opacity = '';
      label.style.color = '';
    }, 2500);
  };

  input.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('photo', file);

    try {
      const res = await fetch(`/upload/${id}`, { method: 'POST', body: formData });
      const data = await res.json();

      if (res.ok && data.url) {
        el.style.backgroundImage = `url(${data.url})`;
        el.classList.add('has-photo');
        if (label) showMessage('Saved ✓', false);
      } else {
        showMessage(data.message || 'Upload failed', true);
      }
    } catch (err) {
      showMessage('Network error', true);
    } finally {
      input.value = '';
    }
  });
});

// ---------------------------------------------------------------------
// Enquiry form
// ---------------------------------------------------------------------
const form = document.getElementById('contactForm');
const formStatus = document.getElementById('formStatus');
const ageField = document.getElementById('ageField');
const ageInput = document.getElementById('age');

form.querySelectorAll('input[name="batch"]').forEach(radio => {
  radio.addEventListener('change', () => {
    const isKids = radio.value === 'Kids batch' && radio.checked;
    if (isKids) {
      ageField.hidden = false;
      ageInput.required = true;
    } else if (document.querySelector('input[name="batch"]:checked')?.value !== 'Kids batch') {
      ageField.hidden = true;
      ageInput.required = false;
      ageInput.value = '';
    }
  });
});

// Sends the enquiry via FormSubmit.co — see README for the one-time
// activation step required before submissions start arriving by email.
const FORM_ENDPOINT = 'https://formsubmit.co/ajax/jamdance.be@gmail.com';

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = form.querySelector('button[type="submit"]');
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Sending...';
  formStatus.textContent = '';
  formStatus.className = 'form-status';

  const batch = form.querySelector('input[name="batch"]:checked')?.value || '';
  const payload = {
    email: form.email.value,
    whatsapp: form.whatsapp.value,
    registration_for: batch,
    child_age: batch === 'Kids batch' ? form.age.value : 'N/A',
    query: form.message.value,
    _subject: 'New JAM Dance Academy Enquiry',
    _template: 'table',
    _captcha: 'false',
    _autoresponse: "Thanks for reaching out to JAM Dance Academy! We've received your enquiry and will get back to you shortly. In the meantime, feel free to follow us on Instagram @jamdance.be. — Team JAM"
  };

  try {
    const res = await fetch(FORM_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      formStatus.textContent = "Thanks! We've received your enquiry and sent you a confirmation email.";
      formStatus.classList.add('ok');
      form.reset();
      ageField.hidden = true;
      ageInput.required = false;
    } else {
      formStatus.textContent = 'Something went wrong — please email us directly at jamdance.be@gmail.com.';
      formStatus.classList.add('err');
    }
  } catch (err) {
    formStatus.textContent = 'Network error — please email us directly at jamdance.be@gmail.com.';
    formStatus.classList.add('err');
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
});
