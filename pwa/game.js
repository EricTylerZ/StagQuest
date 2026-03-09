// StagQuest PWA - 9-Day Novena Tracker
// Fight human trafficking through daily prayer and personal discipline

(function () {
  'use strict';

  const { HOURS, VIRTUE_CARDS, registerQuestions, getCurrentHour, getCardForHour } = STAGQUEST_DATA;

  // ===== Persistence =====
  const SAVE_KEY = 'stagquest_novena';

  function loadState() {
    try { return JSON.parse(localStorage.getItem(SAVE_KEY)); } catch { return null; }
  }

  function saveState() {
    if (state) localStorage.setItem(SAVE_KEY, JSON.stringify(state));
  }

  // ===== Game State =====
  let state = null;

  function newState() {
    return {
      day: 1,
      totalDays: 9,
      prayersToday: {},    // hourId -> true
      cardsCompleted: 0,
      questionsCorrect: 0,
      questionsTotal: 0,
      meritEarned: 0,
      currentCard: null,
      currentQuestion: null,
      waitingForAnswer: false,
      dayComplete: false,
      novenaComplete: false,
      lastPlayedDate: new Date().toDateString(),
      progressState: typeof TeachingModule !== 'undefined' ? TeachingModule.createProgressState() : null
    };
  }

  // ===== Game Logic =====

  function prayHour(hourId) {
    if (state.prayersToday[hourId]) return; // already prayed
    state.prayersToday[hourId] = true;
    state.meritEarned += 1;

    // Draw a virtue card for this hour
    const card = getCardForHour(hourId);
    state.currentCard = card;

    // Load a question
    if (typeof TeachingModule !== 'undefined') {
      state.currentQuestion = TeachingModule.getRandomQuestion({
        state: state.progressState,
        category: 'stagquest',
        preferUnmastered: true
      });
    }
    state.waitingForAnswer = true;

    saveState();
    updateUI();
  }

  function answerQuestion(idx) {
    if (!state.waitingForAnswer) return;

    state.questionsTotal++;
    const correct = state.currentQuestion && idx === state.currentQuestion.correct;

    if (correct) {
      state.questionsCorrect++;
      state.meritEarned += 1;
      state.cardsCompleted++;
      if (typeof TeachingModule !== 'undefined' && state.currentQuestion) {
        TeachingModule.incrementProgress(
          state.progressState,
          state.currentQuestion.category,
          state.currentQuestion.topic,
          state.currentQuestion.subtopic
        );
      }
    }

    state.waitingForAnswer = false;
    state.currentCard = null;
    state.currentQuestion = null;

    // Check if all 7 hours prayed
    if (Object.keys(state.prayersToday).length >= 7) {
      state.dayComplete = true;
    }

    saveState();
    updateUI();
    return correct;
  }

  function advanceDay() {
    if (!state.dayComplete) return;

    state.day++;
    state.prayersToday = {};
    state.dayComplete = false;
    state.lastPlayedDate = new Date().toDateString();

    if (state.day > state.totalDays) {
      completeNovena();
    } else {
      saveState();
      updateUI();
    }
  }

  function completeNovena() {
    state.novenaComplete = true;
    state.meritEarned += 9; // Novena completion bonus

    // Submit to Sentinel Ops
    if (typeof SentinelAPI !== 'undefined' && SentinelAPI.isLoggedIn()) {
      SentinelAPI.submitMerit(state.meritEarned, {
        game_name: 'StagQuest',
        won: true,
        days_completed: state.totalDays,
        questions_correct: state.questionsCorrect,
        questions_total: state.questionsTotal,
        cards_completed: state.cardsCompleted
      }).catch(() => {});
    }

    saveState();
    updateUI();
  }

  // ===== UI =====

  function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
  }

  function updateUI() {
    if (!state) return;

    if (state.novenaComplete) {
      showScreen('complete-screen');
      renderComplete();
      return;
    }

    showScreen('game-screen');

    // Status
    const statusEl = document.getElementById('game-status');
    if (statusEl) {
      const prayerCount = Object.keys(state.prayersToday).length;
      statusEl.innerHTML = `
        <span class="status-day">Day ${state.day} / ${state.totalDays}</span>
        <span class="status-prayers">Prayers: ${prayerCount} / 7</span>
        <span class="status-merit">Merit: ${state.meritEarned}</span>
      `;
    }

    // Card/question overlay
    if (state.waitingForAnswer && state.currentCard) {
      renderCardOverlay();
      return;
    }

    // Day complete?
    if (state.dayComplete) {
      renderDayComplete();
      return;
    }

    // Hour buttons
    renderHourButtons();
  }

  function renderHourButtons() {
    const area = document.getElementById('prayer-area');
    const currentHour = getCurrentHour();

    let html = `<p class="current-hour">Current hour: <strong>${currentHour.name}</strong> (${currentHour.label})</p>`;
    html += '<div class="hours-grid">';

    HOURS.forEach(h => {
      const done = state.prayersToday[h.id];
      const isCurrent = h.id === currentHour.id;
      html += `<button class="hour-btn ${done ? 'done' : ''} ${isCurrent ? 'current' : ''}"
        onclick="StagQuestGame.prayHour('${h.id}')" ${done ? 'disabled' : ''}>
        <span class="hour-name">${h.name}</span>
        <span class="hour-label">${h.label}</span>
        ${done ? '<span class="hour-check">&#10003;</span>' : ''}
      </button>`;
    });

    html += '</div>';
    area.innerHTML = html;
  }

  function renderCardOverlay() {
    const area = document.getElementById('prayer-area');
    const card = state.currentCard;
    const q = state.currentQuestion;
    const hour = HOURS.find(h => h.id === card.hour);

    let html = `<div class="card-overlay">`;
    // Prayer
    html += `<div class="prayer-box">
      <h3>${hour.name} \u2014 ${hour.label}</h3>
      <p class="prayer-text">${hour.prayer}</p>
    </div>`;

    // Virtue card
    html += `<div class="virtue-card">
      <h4>${card.title}</h4>
      <p>${card.text}</p>
      ${card.fact ? `<p class="fun-fact">${card.fact}</p>` : ''}
    </div>`;

    // Question
    if (q) {
      html += `<div class="question-box">
        <p class="question-text">${q.question}</p>
        <div class="answers">`;
      q.answers.forEach((a, i) => {
        html += `<button class="btn btn-answer" onclick="StagQuestGame.answer(${i})">${a}</button>`;
      });
      html += '</div></div>';
    } else {
      html += `<button class="btn btn-primary" onclick="StagQuestGame.answer(0)">Continue</button>`;
    }

    html += '</div>';
    area.innerHTML = html;
  }

  function renderDayComplete() {
    const area = document.getElementById('prayer-area');
    const prayerCount = Object.keys(state.prayersToday).length;

    let html = '<div class="day-complete">';
    html += `<h3>Day ${state.day} Complete!</h3>`;
    html += `<p>All 7 prayers completed. ${state.questionsCorrect} questions answered correctly today.</p>`;

    if (state.day < state.totalDays) {
      html += `<p class="next-day">Come back tomorrow for Day ${state.day + 1}.</p>`;
      html += `<button class="btn btn-primary" onclick="StagQuestGame.advanceDay()">Continue to Day ${state.day + 1}</button>`;
    } else {
      html += `<button class="btn btn-primary" onclick="StagQuestGame.advanceDay()">Complete Novena!</button>`;
    }
    html += '</div>';
    area.innerHTML = html;
  }

  function renderComplete() {
    const el = document.getElementById('complete-content');
    if (!el) return;

    el.innerHTML = `
      <h2>Novena Complete!</h2>
      <p class="complete-subtitle">9 days of prayer and discipline. Every "no" to temptation saved lives.</p>
      <div class="badge">
        <div class="badge-border">
          <h3>StagQuest Warrior</h3>
          <p>Days: ${state.totalDays} | Cards: ${state.cardsCompleted}</p>
          <p>Questions: ${state.questionsCorrect} / ${state.questionsTotal}</p>
          <p>EZ Merit Earned: ${state.meritEarned}</p>
        </div>
      </div>
      <div class="novena-prayer">
        <h4>Prayer of the Warrior</h4>
        <p>Lord, for 9 days I have fought against the chains of addiction that enslave millions.<br>
        Accept my small victories as prayers for the 40 million trafficked.<br>
        Strengthen me to continue this fight every day.<br>
        Break every chain. Free every captive.<br>
        Through Christ our Lord, who sets all prisoners free.<br>
        Amen.</p>
      </div>
      <button class="btn btn-primary" onclick="StagQuestGame.restart()">Start New Novena</button>
    `;
  }

  // ===== Sentinel Login =====

  function setupSentinel() {
    if (typeof SentinelAPI === 'undefined') return;

    const statusEl = document.getElementById('sentinel-status');
    if (SentinelAPI.isLoggedIn()) {
      statusEl.textContent = `Logged in as ${SentinelAPI.getStoredName() || SentinelAPI.getRoleId()}`;
      statusEl.className = 'sentinel-online';
    }

    document.getElementById('sentinel-login-btn')?.addEventListener('click', async () => {
      const roleId = document.getElementById('sentinel-role-id').value.trim();
      if (!roleId) return;
      try {
        await SentinelAPI.login(roleId);
        statusEl.textContent = `Logged in as ${SentinelAPI.getStoredName()}`;
        statusEl.className = 'sentinel-online';
      } catch (e) {
        statusEl.textContent = `Login failed: ${e.message}`;
      }
    });

    document.getElementById('sentinel-register-btn')?.addEventListener('click', async () => {
      const name = document.getElementById('sentinel-reg-name').value.trim();
      if (!name) return;
      try {
        await SentinelAPI.register(name, '1.0');
        statusEl.textContent = `Registered as ${name}`;
        statusEl.className = 'sentinel-online';
      } catch (e) {
        statusEl.textContent = `Register failed: ${e.message}`;
      }
    });

    document.getElementById('sentinel-toggle-register')?.addEventListener('click', e => {
      e.preventDefault();
      document.getElementById('sentinel-login-form').classList.toggle('hidden');
      document.getElementById('sentinel-register-form').classList.toggle('hidden');
    });
  }

  // ===== Init =====

  function init() {
    registerQuestions();
    setupSentinel();

    // Check for saved state
    const saved = loadState();
    if (saved && !saved.novenaComplete) {
      state = saved;
      // Check if it's a new calendar day
      if (saved.lastPlayedDate !== new Date().toDateString() && saved.dayComplete) {
        state.day++;
        state.prayersToday = {};
        state.dayComplete = false;
        state.lastPlayedDate = new Date().toDateString();
        if (state.day > state.totalDays) {
          completeNovena();
          return;
        }
      }
      showScreen('game-screen');
      updateUI();
    }

    // Start button
    document.getElementById('start-btn')?.addEventListener('click', () => {
      state = newState();
      saveState();
      showScreen('game-screen');
      updateUI();
    });

    // Continue button (if saved)
    const continueBtn = document.getElementById('continue-btn');
    if (continueBtn) {
      if (saved && !saved.novenaComplete) {
        continueBtn.classList.remove('hidden');
        continueBtn.addEventListener('click', () => {
          state = saved;
          showScreen('game-screen');
          updateUI();
        });
      }
    }

    // Rules
    document.getElementById('rules-btn')?.addEventListener('click', () => showScreen('rules-screen'));

    // Back buttons
    document.querySelectorAll('.back-btn').forEach(btn => {
      btn.addEventListener('click', () => showScreen(btn.dataset.target));
    });
  }

  function restart() {
    localStorage.removeItem(SAVE_KEY);
    state = null;
    showScreen('title-screen');
  }

  window.StagQuestGame = {
    init,
    prayHour,
    answer: answerQuestion,
    advanceDay,
    restart
  };

  document.addEventListener('DOMContentLoaded', init);
})();
