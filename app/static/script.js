/**
 * Menteez — Student Wellness Analytics
 * Client-side Form Handling, Validation, API Client, and Gauge Animation
 */

// DOM Elements
const form = document.getElementById('predict-form');
const submitBtn = document.getElementById('submit-btn');
const stressInput = document.getElementById('stress_level');
const resetBtn = document.getElementById('reset-btn');
const errorRetryBtn = document.getElementById('error-retry-btn');
const getSignalBtn = document.getElementById('get-signal-btn');

// Info modal elements
const infoDialog = document.getElementById('info-dialog');
const dialogTitle = document.getElementById('dialog-title');
const dialogBody = document.getElementById('dialog-body');
const dialogClose = document.getElementById('dialog-close');
const dialogOkBtn = document.getElementById('dialog-ok-btn');

// Band Color Palettes
const bandTheme = {
  Struggling: {
    color: '#E0806B', // Soft Coral
    bubbleA: '#E0806B',
    bubbleB: '#F0D876',
    bubbleC: '#6E8FD1'
  },
  Managing: {
    color: '#EBCB6B', // Soft Mustard Yellow
    bubbleA: '#EBCB6B',
    bubbleB: '#6E8FD1',
    bubbleC: '#BFE3D0'
  },
  Steady: {
    color: '#9B9CE6', // Soft Periwinkle / Lavender
    bubbleA: '#6E8FD1',
    bubbleB: '#E0806B',
    bubbleC: '#EBCB6B'
  },
  Thriving: {
    color: '#7678D7', // Vibrant Wellness Lavender
    bubbleA: '#6E8FD1',
    bubbleB: '#BFE3D0',
    bubbleC: '#EBCB6B'
  }
};

// Modal Content Definitions
const modalContent = {
  'how-it-works': {
    title: 'How it works',
    html: `
      <p><strong>Menteez</strong> analyzes key lifestyle, academic, and digital habit indicators—such as daily screen time, phone unlocks, sleep quality, and perceived stress—to generate an estimated mental health signal score between 0 and 10.</p>
      <p>The prediction is powered by a machine learning model trained on student wellness patterns, evaluating how routine daily habits interact with student wellbeing.</p>
    `
  },
  'about': {
    title: 'About Menteez',
    html: `
      <p>Menteez was created to give students a gentle, non-clinical mirror into their daily rhythms. We believe small, mindful adjustments in screen habits and sleep routines compound into meaningful improvements in wellbeing.</p>
      <p>Our philosophy is rooted in self-awareness, balance, and positive habit formation.</p>
    `
  },
  'privacy': {
    title: 'Privacy & Data Care',
    html: `
      <p>Your inputs are processed in-memory solely to compute your wellness signal. We do not store, sell, or profile your personal demographic data.</p>
      <p>All evaluations remain completely private to your session.</p>
    `
  }
};

// -----------------------------------------------------------------------------
// State Management
// -----------------------------------------------------------------------------
function setState(state) {
  ['idle', 'loading', 'result', 'error'].forEach((s) => {
    const el = document.getElementById(`state-${s}`);
    if (el) {
      el.hidden = (s !== state);
    }
  });
}

function setSubmitLoading(isLoading) {
  if (!submitBtn) return;
  submitBtn.classList.toggle('loading', isLoading);
  submitBtn.disabled = isLoading;
}

// -----------------------------------------------------------------------------
// Field Error Handling
// -----------------------------------------------------------------------------
function clearFieldError(fieldId) {
  const input = document.getElementById(fieldId);
  const field = input?.closest('.field');
  if (field) {
    field.classList.remove('field-error');
    const errorEl = field.querySelector('.error-msg');
    if (errorEl) errorEl.textContent = '';
  }
}

function setFieldError(fieldId, message) {
  const input = document.getElementById(fieldId);
  const field = input?.closest('.field');
  if (field) {
    field.classList.add('field-error');
    const errorEl = field.querySelector('.error-msg');
    if (errorEl) errorEl.textContent = message;
  }
}

function clearAllErrors() {
  document.querySelectorAll('.field').forEach((f) => f.classList.remove('field-error'));
  document.querySelectorAll('.error-msg').forEach((e) => {
    e.textContent = '';
  });
}

// -----------------------------------------------------------------------------
// Form Validation
// -----------------------------------------------------------------------------
function validateFormData(data) {
  let isValid = true;

  const numericRanges = {
    age: { min: 10, max: 100, label: 'Age (10–100)' },
    avg_daily_usage_hours: { min: 0, max: 24, label: 'Screen time (0–24 hrs)' },
    daily_unlocks: { min: 0, max: 1000, label: 'Daily unlocks (≥ 0)' },
    study_hours: { min: 0, max: 24, label: 'Study hours (0–24 hrs)' },
    physical_activity_hours: { min: 0, max: 24, label: 'Activity hours (0–24 hrs)' },
    sleep_hours_per_night: { min: 0, max: 24, label: 'Sleep hours (0–24 hrs)' }
  };

  Object.entries(numericRanges).forEach(([fieldId, rules]) => {
    const val = data[fieldId];
    if (isNaN(val) || val === null || val === '') {
      isValid = false;
      setFieldError(fieldId, 'This field is required.');
    } else if (val < rules.min || val > rules.max) {
      isValid = false;
      setFieldError(fieldId, `Must be between ${rules.min} and ${rules.max}.`);
    }
  });

  const textFields = ['gender', 'country', 'academic_level', 'most_used_platform', 'purpose_of_use'];
  textFields.forEach((fieldId) => {
    const val = String(data[fieldId] || '').trim();
    if (!val) {
      isValid = false;
      setFieldError(fieldId, 'Please select or enter an option.');
    }
  });

  if (!data.stress_level) {
    isValid = false;
    setFieldError('stress_level', 'Please select your stress level.');
  }

  return isValid;
}

// -----------------------------------------------------------------------------
// Render Results & Score Donut Animation
// -----------------------------------------------------------------------------
function renderResult(score, band, context) {
  const scoreNumEl = document.getElementById('score-number');
  const scoreBandEl = document.getElementById('score-band');
  const scoreContextEl = document.getElementById('score-context');

  if (scoreNumEl) scoreNumEl.textContent = score.toFixed(1);
  if (scoreBandEl) scoreBandEl.textContent = band;
  if (scoreContextEl) scoreContextEl.textContent = context || 'Your daily rhythm looks balanced.';

  const ratio = Math.max(0.0, Math.min(1.0, score / 10.0));
  const theme = bandTheme[band] || bandTheme.Steady;

  // Update CSS Variables for SVG circular progress
  document.documentElement.style.setProperty('--score-ratio', ratio);
  document.documentElement.style.setProperty('--ring-color', theme.color);
}

// -----------------------------------------------------------------------------
// Reset View
// -----------------------------------------------------------------------------
function resetView() {
  if (form) form.reset();
  if (stressInput) stressInput.value = 'Medium';
  
  // Set default active button to Medium
  document.querySelectorAll('#stress_level_group .seg-btn').forEach((btn) => {
    const isMedium = btn.dataset.value === 'Medium';
    btn.classList.toggle('active', isMedium);
    btn.setAttribute('aria-checked', isMedium ? 'true' : 'false');
  });

  clearAllErrors();
  setState('idle');
}

// -----------------------------------------------------------------------------
// Event Listeners
// -----------------------------------------------------------------------------

// 1. Stress Segmented Button Clicks
document.querySelectorAll('#stress_level_group .seg-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#stress_level_group .seg-btn').forEach((b) => {
      b.classList.remove('active');
      b.setAttribute('aria-checked', 'false');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-checked', 'true');
    if (stressInput) {
      stressInput.value = btn.dataset.value;
    }
    clearFieldError('stress_level');
  });
});

// 2. Real-time Clear Field Errors on input/change
document.querySelectorAll('input, select').forEach((input) => {
  input.addEventListener('input', () => clearFieldError(input.id));
  input.addEventListener('change', () => clearFieldError(input.id));
});

// 3. Form Submit Handler
if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAllErrors();

    const rawData = Object.fromEntries(new FormData(form).entries());

    // Cast numeric fields
    const numericKeys = [
      'age',
      'avg_daily_usage_hours',
      'daily_unlocks',
      'study_hours',
      'physical_activity_hours',
      'sleep_hours_per_night'
    ];

    const data = { ...rawData };
    numericKeys.forEach((k) => {
      data[k] = (data[k] === '' || data[k] === undefined) ? NaN : Number(data[k]);
    });

    if (!validateFormData(data)) {
      return;
    }

    setState('loading');
    setSubmitLoading(true);

    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));

        // Surface FastAPI 422 validation issues if present
        if (res.status === 422 && Array.isArray(err.detail)) {
          err.detail.forEach((issue) => {
            const fieldId = issue?.loc?.[issue.loc.length - 1];
            if (fieldId && document.getElementById(fieldId)) {
              setFieldError(fieldId, issue.msg || 'Invalid value.');
            }
          });
        }

        throw new Error(err.detail ? (typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail)) : 'Prediction failed');
      }

      const result = await res.json();
      renderResult(result.mental_health_score, result.band, result.context);
      setState('result');
    } catch (err) {
      console.error('Prediction request error:', err);
      const errCopy = document.getElementById('error-copy');
      if (errCopy) {
        errCopy.textContent = 'Something went wrong reading your signal. Please check your inputs and try again.';
      }
      setState('error');
    } finally {
      setSubmitLoading(false);
    }
  });
}

// 4. Action Buttons
if (resetBtn) resetBtn.addEventListener('click', resetView);
if (errorRetryBtn) errorRetryBtn.addEventListener('click', () => setState('idle'));

if (getSignalBtn) {
  getSignalBtn.addEventListener('click', () => {
    const firstInput = document.getElementById('age');
    if (firstInput) {
      firstInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      firstInput.focus();
    }
  });
}

// 5. Navbar Info Modal Handlers
document.querySelectorAll('.nav-link[data-modal]').forEach((link) => {
  link.addEventListener('click', () => {
    const modalKey = link.getAttribute('data-modal');
    const content = modalContent[modalKey];
    if (content && infoDialog) {
      dialogTitle.textContent = content.title;
      dialogBody.innerHTML = content.html;
      infoDialog.showModal();
    }
  });
});

if (dialogClose) {
  dialogClose.addEventListener('click', () => infoDialog?.close());
}
if (dialogOkBtn) {
  dialogOkBtn.addEventListener('click', () => infoDialog?.close());
}
if (infoDialog) {
  infoDialog.addEventListener('click', (e) => {
    const rect = infoDialog.getBoundingClientRect();
    const isInDialog = (
      rect.top <= e.clientY &&
      e.clientY <= rect.top + rect.height &&
      rect.left <= e.clientX &&
      e.clientX <= rect.left + rect.width
    );
    if (!isInDialog) {
      infoDialog.close();
    }
  });
}

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
  // Sync stress level default
  const activeBtn = document.querySelector('#stress_level_group .seg-btn.active');
  if (activeBtn && stressInput) {
    stressInput.value = activeBtn.dataset.value;
  }
});
